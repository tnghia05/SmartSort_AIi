import asyncio
import base64
import io
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from fastapi import Body, FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from ultralytics import YOLO
import uvicorn

from settings import (
    EDGE_REFINE_MARGIN,
    EDGE_REFINE_MIN_AREA,
    ENABLE_EDGE_REFINEMENT,
    CLOTHES_ASPECT_CONF_BOOST,
    CLOTHES_ASPECT_MAX,
    CLOTHES_ASPECT_MIN,
    DETECTION_ROI_SCALE,
    ENABLE_BILATERAL_FILTER,
    ENABLE_CLAHE,
    ENABLE_FULL_FRAME_FALLBACK,
    ENABLE_GRID_DETECTION,
    ENABLE_TEMPORAL_FILTERING,
    GRID_COLS,
    GRID_DETECTION_TRIGGER,
    GRID_MAX_TILES,
    GRID_OVERLAP,
    GRID_ROWS,
    IOU_THRESHOLD,
    LARGE_BBOX_CONF_BOOST,
    MAX_DETECTION_AREA,
    MAX_DETECTIONS_PER_FRAME,
    MIN_BBOX_AREA,
    MIN_CONFIDENCE,
    MODEL_PATHS,
    REALTIME_CLIENT_TIMEOUT,
    REALTIME_MAX_FPS,
    TEMPORAL_HISTORY_SIZE,
    TEMPORAL_STABILITY_THRESHOLD,
    ENABLE_CLASS_SIGNATURE_FILTER,
    IGNORED_CLASSES,
    USE_FP16,
    YOLO_IMAGE_SIZE,
    FULL_FRAME_AREA_TRIGGER,
)

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import PyTorch (GPU support) and CLIP (optional)
try:
    import torch
    TORCH_AVAILABLE = True
    logger.info("✅ PyTorch available")
except ImportError:
    torch = None
    TORCH_AVAILABLE = False
    logger.warning("⚠️ PyTorch not available. Install with: pip install torch torchvision torchaudio")

app = FastAPI(title="SmartSort AI - Trash Detection API")

# Thread pool for CPU-intensive operations (model inference, image processing)
# Use a limited pool to prevent resource exhaustion
executor = ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 2))

# CORS middleware - Cho phép React Native app gọi API
# In production, set ALLOWED_ORIGINS environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if "*" in allowed_origins:
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in allowed_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB default
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", 10))  # Max 10 images per batch
ENABLE_PAPER_HEURISTICS = os.getenv("ENABLE_PAPER_HEURISTICS", "true").strip().lower() == "true"

# Simple in-memory rate limiter
_rate_limit_store = {}
_rate_limit_cleanup_interval = 60  # Clean up old entries every 60 seconds
_last_cleanup = time.time()

def check_rate_limit(client_id: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
    """
    Simple rate limiter using sliding window.
    Returns True if request is allowed, False if rate limit exceeded.
    """
    global _last_cleanup
    
    now = time.time()
    
    # Cleanup old entries periodically
    if now - _last_cleanup > _rate_limit_cleanup_interval:
        _last_cleanup = now
        # Remove entries older than window_seconds
        cutoff = now - window_seconds
        for key in list(_rate_limit_store.keys()):
            _rate_limit_store[key] = [ts for ts in _rate_limit_store[key] if ts > cutoff]
            if not _rate_limit_store[key]:
                del _rate_limit_store[key]
    
    # Get or create client's request timestamps
    if client_id not in _rate_limit_store:
        _rate_limit_store[client_id] = []
    
    # Remove timestamps outside the window
    cutoff = now - window_seconds
    _rate_limit_store[client_id] = [ts for ts in _rate_limit_store[client_id] if ts > cutoff]
    
    # Check if limit exceeded
    if len(_rate_limit_store[client_id]) >= max_requests:
        return False
    
    # Add current request timestamp
    _rate_limit_store[client_id].append(now)
    return True

def get_client_id(request: Request) -> str:
    """Get client identifier for rate limiting."""
    # Use IP address as identifier
    if request.client:
        return request.client.host
    return "unknown"

# Temporal filtering: track detections across frames
_temporal_detection_history: List[List[Dict]] = []
_last_class_signature: Optional[str] = None

def get_class_signature(detections: List[Dict]) -> str:
    """Get unique signature from detected classes (sorted set of class names)."""
    classes = sorted(set(det.get("class", "") for det in detections))
    return "|".join(classes)

def should_send_detection(detections: List[Dict]) -> bool:
    """
    Check if detection should be sent based on class signature change.
    Similar to streamlit app's unique_classes logic.
    """
    if not ENABLE_CLASS_SIGNATURE_FILTER:
        return True
    
    global _last_class_signature
    current_signature = get_class_signature(detections)
    
    if current_signature != _last_class_signature:
        _last_class_signature = current_signature
        return True
    
    return False

def apply_temporal_filtering(detections: List[Dict]) -> List[Dict]:
    """
    Filter detections based on temporal stability.
    Optimized: check class presence across frames (like streamlit app).
    """
    if not ENABLE_TEMPORAL_FILTERING or not detections:
        return detections
    
    global _temporal_detection_history
    
    # Add current frame detections to history
    _temporal_detection_history.append(detections)
    
    # Keep only recent history
    if len(_temporal_detection_history) > TEMPORAL_HISTORY_SIZE:
        _temporal_detection_history.pop(0)
    
    # Need at least TEMPORAL_STABILITY_THRESHOLD frames
    if len(_temporal_detection_history) < TEMPORAL_STABILITY_THRESHOLD:
        return detections
    
    # For each detection, check if CLASS appears in recent frames
    stable_detections = []
    for det in detections:
        det_class = det.get("class", "")
        
        # Count how many recent frames have this CLASS (not exact bbox match)
        class_match_count = 0
        for past_frame in _temporal_detection_history[-TEMPORAL_STABILITY_THRESHOLD:]:
            if any(past_det.get("class") == det_class for past_det in past_frame):
                class_match_count += 1
        
        # Keep if class appears in at least threshold frames
        if class_match_count >= TEMPORAL_STABILITY_THRESHOLD:
            stable_detections.append(det)
        else:
            logger.debug(f"Filtering out unstable class: {det_class} (frame_count: {class_match_count}/{TEMPORAL_STABILITY_THRESHOLD})")
    
    return stable_detections

# Load YOLOv8 model từ Hugging Face
# Model sẽ được download tự động lần đầu tiên
# Thử các cách load model khác nhau
model = None

for model_path in MODEL_PATHS:
    try:
        logger.info(f"Trying to load model: {model_path}")
        model = YOLO(model_path)
        logger.info(f"✅ Model loaded successfully: {model_path}")
        break
    except Exception as e:
        logger.warning(f"❌ Error loading model {model_path}: {e}")
        continue

if model is None:
    logger.warning("⚠️ Warning: No model loaded. API will return errors for detection requests.")
    logger.warning("Please check the model path or install the model manually.")
else:
    if TORCH_AVAILABLE and torch.cuda.is_available():
        try:
            model.to("cuda")
            if hasattr(model, "model"):
                if USE_FP16:
                    model.model.half()
                    logger.info(f"🚀 Using GPU acceleration: {torch.cuda.get_device_name(0)} (FP16)")
                else:
                    model.model.float()
                    logger.info(f"🚀 Using GPU acceleration: {torch.cuda.get_device_name(0)} (FP32)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to move model to GPU: {e}")
            logger.info("ℹ️ Falling back to CPU inference.")
            model.to("cpu")
            logger.info("ℹ️ Running inference on CPU.")
    else:
        logger.info("ℹ️ Running inference on CPU.")

# Map class names từ model về các class trong app
# Waste classification model has 12 classes (Moondream dataset)
MOONDREAM_CLASSES = [
    'battery',
    'biological',
    'brown-glass',
    'cardboard',
    'clothes',
    'green-glass',
    'metal',
    'paper',
    'plastic',
    'shoes',
    'trash',
    'white-glass',
]
MOONDREAM_CLASS_SET = {cls.lower() for cls in MOONDREAM_CLASSES}
IS_MOONDREAM_MODEL = False

# Classes to ignore entirely (not useful for recycling guidance)
# Now configurable via settings
IGNORED_CLASS_SET = {cls.lower().strip() for cls in IGNORED_CLASSES if cls.strip()}

# Normalize subclasses vào cùng 1 nhãn hiển thị
CLASS_NORMALIZATION = {
    'brown-glass': 'glass',
    'green-glass': 'glass',
    'white-glass': 'glass'
}

# Mapping classes → nhóm lớn (dùng cho gợi ý thùng xử lý)
WASTE_CLASS_MAPPING = {
    # Hazardous waste
    'battery': 'hazardous',
    
    # Residual / general trash (không tái chế được)
    'can': 'residual',  # Lon nhôm thường không tái chế được ở VN
    'chemical_spray_can': 'residual',  # Bình xịt hóa chất
    'light_bulb': 'residual',  # Bóng đèn
    'paint_bucket': 'residual',  # Xô sơn
    'snack_bag': 'residual',  # Túi snack (thường có lớp nhôm)
    'stick': 'residual',  # Que gỗ
    'straw': 'residual',  # Ống hút
    'trash': 'residual',
    'garbage': 'residual',
    
    # Recyclable materials (tái chế được)
    'cardboard_bowl': 'recyclable',  # Bát giấy
    'cardboard_box': 'recyclable',  # Hộp giấy
    'chemical_plastic_bottle': 'recyclable',  # Chai nhựa hóa chất (rửa sạch có thể tái chế)
    'chemical_plastic_gallon': 'recyclable',  # Can nhựa hóa chất (rửa sạch có thể tái chế)
    'plastic_bag': 'recyclable',  # Túi nhựa
    'plastic_bottle': 'recyclable',  # Chai nhựa
    'plastic_bottle_cap': 'recyclable',  # Nắp chai nhựa
    'plastic_box': 'recyclable',  # Hộp nhựa
    'plastic_cultery': 'recyclable',  # Đồ dùng nhựa (muỗng, nĩa)
    'plastic_cup': 'recyclable',  # Ly nhựa
    'plastic_cup_lid': 'recyclable',  # Nắp ly nhựa
    'reuseable_paper': 'recyclable',  # Giấy tái sử dụng
    'scrap_paper': 'recyclable',  # Giấy vụn
    'scrap_plastic': 'recyclable',  # Nhựa vụn
    
    # Legacy/Moondream classes (backward compatibility)
    'biological': 'organic',
    'organic': 'organic',
    'plastic': 'recyclable',
    'metal': 'recyclable',
    'paper': 'recyclable',
    'cardboard': 'recyclable',
    'brown-glass': 'recyclable',
    'green-glass': 'recyclable',
    'white-glass': 'recyclable',
    'glass': 'recyclable',
    'clothes': 'reusable',
    'shoes': 'reusable',
    
    # COCO classes (fallback if using COCO model)
    'banana': 'organic',
    'apple': 'organic',
    'broccoli': 'organic',
    'carrot': 'organic',
    'pizza': 'organic',
    'donut': 'organic',
    'cake': 'organic',
    'sandwich': 'organic',
    'hot dog': 'organic',
    'food': 'organic',
    'bottle': 'recyclable',
    'cup': 'recyclable',
    'bowl': 'recyclable',
    'book': 'recyclable',
    'newspaper': 'recyclable',
    'magazine': 'recyclable',
}


WASTE_GUIDANCE = {
    "organic": {
        "bin": "Thùng hữu cơ",
        "action": "Bỏ vào thùng rác hữu cơ/compost",
        "description": "Rác có thể phân hủy nhanh như thức ăn thừa, vỏ trái cây.",
        "icon": "🌱",
        "color": "#43a047"
    },
    "recyclable": {
        "bin": "Thùng tái chế",
        "action": "Phân loại theo vật liệu (giấy/nhựa/kim loại/thủy tinh).",
        "description": "Làm sạch và để đúng nơi quy định.",
        "icon": "♻️",
        "color": "#1e88e5"
    },
    "recyclable_paper": {
        "bin": "Thùng giấy / Tái chế",
        "action": "Giữ khô ráo, làm phẳng và xếp gọn.",
        "description": "Giấy báo, thùng carton, vở viết, tờ rơi.",
        "icon": "📄",
        "color": "#3949ab"
    },
    "recyclable_plastic": {
        "bin": "Thùng nhựa / Tái chế",
        "action": "Đổ bỏ chất lỏng, rửa sạch và bóp bẹp.",
        "description": "Chai nước, hộp nhựa, ly nhựa sạch.",
        "icon": "🥤",
        "color": "#039be5"
    },
    "recyclable_metal": {
        "bin": "Thùng kim loại / Tái chế",
        "action": "Làm sạch và ép dẹp lon rỗng.",
        "description": "Lon nước ngọt, hộp đồ hộp, nắp kim loại.",
        "icon": "🥫",
        "color": "#607d8b"
    },
    "recyclable_glass": {
        "bin": "Thùng thủy tinh / Tái chế",
        "action": "Rửa sạch, cẩn thận tránh làm vỡ.",
        "description": "Chai lọ thủy tinh, hũ thực phẩm.",
        "icon": "🍾",
        "color": "#00897b"
    },
    "residual": {
        "bin": "Thùng rác thường",
        "action": "Chỉ bỏ vào đây nếu chắc chắn không tái chế được.",
        "description": "Rác hỗn hợp, giấy ăn bẩn, túi nilon dính bẩn.",
        "icon": "🗑️",
        "color": "#757575"
    },
    "hazardous": {
        "bin": "Thùng rác nguy hại",
        "action": "Đóng kín, giao cho điểm thu gom chất thải nguy hại.",
        "description": "Pin, bóng đèn, hóa chất... cần xử lý đặc biệt.",
        "icon": "⚠️",
        "color": "#f57c00"
    },
    "reusable": {
        "bin": "Khu vực tái sử dụng",
        "action": "Giặt sạch và tái sử dụng hoặc quyên góp.",
        "description": "Quần áo, giày dép có thể dùng lại.",
        "icon": "🔁",
        "color": "#8e24aa"
    }
}


def get_disposal_guidance(group: str) -> Dict[str, str]:
    group_key = (group or "").lower()
    guidance = WASTE_GUIDANCE.get(group_key)
    if guidance:
        return guidance
    return {
        "bin": f"Thùng {group.title() if group else 'phù hợp'}",
        "action": "Kiểm tra quy định địa phương và bỏ đúng thùng.",
        "description": "Không tìm thấy hướng dẫn cụ thể, xử lý theo hướng dẫn chung.",
        "icon": "ℹ️",
        "color": "#546e7a"
    }


def map_class_name(class_name: str) -> str:
    """Map class name từ model về nhóm xử lý (organic/recyclable/...)"""
    class_name_lower = class_name.lower().strip()
    
    # Direct mapping (exact match)
    if class_name_lower in WASTE_CLASS_MAPPING:
        return WASTE_CLASS_MAPPING[class_name_lower]
    
    # Partial matching (for variations like "brown-glass" contains "glass")
    for key, value in WASTE_CLASS_MAPPING.items():
        if key in class_name_lower or class_name_lower in key:
            return value
    
    # Default to 'residual' for unrecognized classes
    return 'residual'

def crop_to_detection_roi(image_rgb: np.ndarray) -> Tuple[np.ndarray, Dict[str, int]]:
    """
    Crop ảnh vào trung tâm để loại bỏ bớt phần nền (người, tường) gây nhiễu.
    Giữ lại metadata để map bbox về hệ tọa độ gốc.
    """
    height, width = image_rgb.shape[:2]
    roi_scale = DETECTION_ROI_SCALE
    
    if roi_scale <= 0 or roi_scale >= 1 or height < 10 or width < 10:
        return image_rgb, {
            "offset_x": 0,
            "offset_y": 0,
            "width": width,
            "height": height
        }
    
    roi_height = max(8, int(height * roi_scale))
    roi_width = max(8, int(width * roi_scale))
    offset_y = max(0, (height - roi_height) // 2)
    offset_x = max(0, (width - roi_width) // 2)
    
    cropped = image_rgb[offset_y:offset_y + roi_height, offset_x:offset_x + roi_width]
    return cropped, {
        "offset_x": offset_x,
        "offset_y": offset_y,
        "width": roi_width,
        "height": roi_height
    }

# Cache CLAHE object to avoid recreating it for each image
_clahe_cache = None

def get_clahe():
    """Get or create CLAHE object (cached for performance)."""
    global _clahe_cache
    if _clahe_cache is None:
        _clahe_cache = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return _clahe_cache

def preprocess_for_detection(image_bgr: np.ndarray) -> np.ndarray:
    """
    Áp dụng tăng cường tương phản + lọc nhiễu nhẹ để YOLO dễ nhận diện hơn.
    Optimized with cached CLAHE object.
    """
    processed = image_bgr
    
    if ENABLE_CLAHE:
        lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = get_clahe()
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        processed = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    if ENABLE_BILATERAL_FILTER:
        # Use smaller kernel for better performance on smaller images
        d = 5 if min(image_bgr.shape[:2]) > 320 else 3
        processed = cv2.bilateralFilter(processed, d, 50, 50)
    
    return processed

# Print model classes when loaded
if model is not None:
    classes = list(model.names.values())
    loaded_class_set = {cls.lower() for cls in classes}
    if loaded_class_set == MOONDREAM_CLASS_SET:
        IS_MOONDREAM_MODEL = True
        logger.info("🧠 Detected Moondream 12-class waste model – textile override disabled.")
    logger.info(f"\n{'='*60}")
    logger.info(f"Model loaded successfully!")
    logger.info(f"{'='*60}")
    logger.info(f"Model classes: {classes}")
    logger.info(f"Total classes: {len(model.names)}")
    
    # Check if this is a waste classification model
    is_waste_model = any(keyword in str(classes).lower() 
                         for keyword in ['organic', 'plastic', 'metal', 'paper', 'waste', 'trash', 'biological', 'cardboard'])
    
    if is_waste_model:
        logger.info("SUCCESS: This is a waste classification model!")
        logger.info("Class mapping:")
        for cls in classes:
            mapped = map_class_name(cls)
            logger.info(f"  - {cls:20} -> {mapped}")
    else:
        logger.warning("WARNING: This appears to be a COCO model, not a waste classification model.")
        logger.warning("You need to use a model trained for waste classification.")
    logger.info(f"{'='*60}\n")

@app.get("/")
async def root():
    return {
        "message": "SmartSort AI - Trash Detection API",
        "status": "running",
        "model_loaded": model is not None
    }

@app.get("/health")
async def health():
    model_info = {}
    if model is not None:
        model_info = {
            "model_loaded": True,
            "class_names": list(model.names.values()),
            "total_classes": len(model.names),
            "is_waste_model": any(keyword in str(model.names.values()).lower() 
                                 for keyword in ['organic', 'plastic', 'metal', 'paper', 'waste', 'trash', 'garbage'])
        }
    else:
        model_info = {
            "model_loaded": False
        }
    
    return {
        "status": "ok",
        **model_info
    }

class Base64ImageRequest(BaseModel):
    image: str  # base64 encoded image
    format: str = "base64"

# Classes that need material classification (can be made from different materials)
MATERIAL_CLASSES = ['cup', 'bottle', 'bowl', 'wine glass', 'vase', 'container']
MATERIAL_CLASS_SET = {cls.lower() for cls in MATERIAL_CLASSES}
PAPER_LIKE_CLASSES = {'clothes', 'cloth', 'fabric', 'towel', 'trash'}
CLOTHES_LIKE_CLASSES = {'clothes', 'cloth', 'fabric', 'towel'}
CLOTHES_LIKE_CLASS_SET = {cls.lower() for cls in CLOTHES_LIKE_CLASSES}

MATERIAL_KEYWORDS = [
    ("plastic", "plastic"),
    ("glass", "glass"),
    ("metal", "metal"),
    ("aluminum", "metal"),
    ("can", "metal"),
    ("paper", "paper"),
    ("cardboard", "paper"),
    ("ceramic", "ceramic"),
    ("cloth", "textile"),
    ("textile", "textile"),
    ("fabric", "textile"),
]

def classify_material_heuristic(crop_image: np.ndarray, object_class: str) -> Optional[str]:
    """
    Classify material using heuristics (color, transparency, edges)
    Returns material name or None if cannot determine
    """
    if object_class.lower() not in MATERIAL_CLASS_SET:
        return None
    
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(crop_image, cv2.COLOR_BGR2HSV)
    
    # Calculate statistics
    mean_brightness = np.mean(hsv[:, :, 2])  # Value channel
    std_brightness = np.std(hsv[:, :, 2])
    
    # Edge detection (glass/metal have more edges)
    gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    # Color variance (glass is more transparent, less color variance)
    color_variance = np.var(crop_image.reshape(-1, 3), axis=0).mean()
    
    # Heuristic rules
    if object_class.lower() == 'cup':
        # Tính thêm saturation để phân biệt metal (xám) vs plastic (có màu)
        mean_saturation = np.mean(hsv[:, :, 1])  # Saturation channel
        
        # Glass: High brightness, high edge density, low color variance (transparent)
        if edge_density > 0.15 and mean_brightness > 150:
            return 'glass'
        elif color_variance < 500 and mean_brightness > 120:
            return 'glass'
        
        # Metal: Đặc trưng bởi màu xám/bạc (saturation thấp), không trong suốt
        # Metal thường có: brightness thấp-trung bình, saturation rất thấp (< 40)
        # và edge density cao (do phản chiếu)
        if mean_brightness < 100:
            # Kiểm tra saturation - metal có saturation rất thấp (xám)
            if mean_saturation < 40 and edge_density > 0.1:
                return 'metal'
            # Nếu có màu sắc (saturation cao) → không phải metal
            elif mean_saturation > 60:
                return 'plastic'
            # Nếu không chắc, kiểm tra thêm
            elif color_variance > 1000:
                # Color variance cao → có màu sắc → plastic
                return 'plastic'
        
        # Plastic: Phổ biến nhất, có thể trong suốt hoặc có màu
        # Plastic trong suốt: brightness trung bình-cao, color variance trung bình
        # Plastic có màu: color variance cao, saturation cao
        if mean_brightness >= 100:
            # Brightness cao → có thể là plastic trong suốt hoặc glass
            if color_variance > 600 or mean_saturation > 50:
                return 'plastic'
            else:
                return 'glass'
        
        # Default: plastic (phổ biến nhất cho cup)
        return 'plastic'
    elif object_class.lower() == 'bottle':
        if edge_density > 0.12 and mean_brightness > 140:
            return 'glass'
        elif mean_brightness < 90:
            return 'metal'
        else:
            return 'plastic'
    elif object_class.lower() == 'bowl':
        if edge_density > 0.1 and mean_brightness > 130:
            return 'glass'
        elif color_variance < 400:
            return 'ceramic'
        else:
            return 'plastic'
    
    return None

def classify_material(crop_image: np.ndarray, object_class: str) -> Optional[str]:
    """
    Classify material of an object (plastic/glass/metal/ceramic/paper)
    Uses heuristics only to avoid heavy dependencies.
    """
    return classify_material_heuristic(crop_image, object_class)


def infer_material_from_class(class_name: str) -> Optional[str]:
    """
    Infer material directly from class name keywords (plastic_bottle → plastic).
    """
    name = (class_name or "").lower()
    for keyword, material in MATERIAL_KEYWORDS:
        if keyword in name:
            return material if material != "textile" else "fabric"
    return None


def calculate_iou(bbox1: Dict[str, float], bbox2: Dict[str, float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    Returns a value between 0 and 1.
    """
    # Calculate intersection area
    x1_inter = max(bbox1["x1"], bbox2["x1"])
    y1_inter = max(bbox1["y1"], bbox2["y1"])
    x2_inter = min(bbox1["x2"], bbox2["x2"])
    y2_inter = min(bbox1["y2"], bbox2["y2"])
    
    if x2_inter <= x1_inter or y2_inter <= y1_inter:
        return 0.0
    
    inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    
    # Calculate union area
    area1 = (bbox1["x2"] - bbox1["x1"]) * (bbox1["y2"] - bbox1["y1"])
    area2 = (bbox2["x2"] - bbox2["x1"]) * (bbox2["y2"] - bbox2["y1"])
    union_area = area1 + area2 - inter_area
    
    if union_area == 0:
        return 0.0
    
    return inter_area / union_area


def merge_duplicate_detections(detections: List[Dict]) -> List[Dict]:
    """
    Merge duplicate detections that have high IoU and same class.
    Keeps the detection with highest confidence.
    Enhanced with per-class NMS and stricter filtering.
    """
    if len(detections) <= 1:
        return detections
    
    # Group by class for better NMS
    by_class: Dict[str, List[Dict]] = {}
    for det in detections:
        cls = det.get("class", "unknown")
        if cls not in by_class:
            by_class[cls] = []
        by_class[cls].append(det)
    
    merged = []
    for cls, cls_detections in by_class.items():
        # Sort by confidence (highest first)
        sorted_dets = sorted(cls_detections, key=lambda x: x["confidence"], reverse=True)
        used = [False] * len(sorted_dets)
        
        for i, det1 in enumerate(sorted_dets):
            if used[i]:
                continue
            
            # Check for overlaps with other detections of same class
            for j in range(i + 1, len(sorted_dets)):
                if used[j]:
                    continue
                
                det2 = sorted_dets[j]
                iou = calculate_iou(det1["bbox"], det2["bbox"])
                if iou > IOU_THRESHOLD:
                    # Keep the one with higher confidence (det1, since sorted)
                    used[j] = True
            
            merged.append(det1)
            used[i] = True
    
    return merged


def filter_noisy_detections(detections: List[Dict]) -> List[Dict]:
    """
    Remove noisy detections based on:
    - Bbox too small (likely noise)
    - Too many detections per frame
    - Dynamic confidence threshold
    """
    if not detections:
        return detections
    
    # Filter out bbox too small
    filtered = []
    for det in detections:
        bbox_area = det.get("bbox_area", 0)
        if bbox_area < MIN_BBOX_AREA:
            logger.debug(f"Filtering out small bbox: {det.get('class')} (area: {bbox_area:.4f})")
            continue
        filtered.append(det)
    
    # If too many detections, apply dynamic confidence boost
    if len(filtered) > MAX_DETECTIONS_PER_FRAME:
        logger.debug(f"Too many detections ({len(filtered)}), applying dynamic threshold")
        # Sort by confidence
        filtered = sorted(filtered, key=lambda x: x["confidence"], reverse=True)
        
        # Calculate dynamic threshold: average of top detections
        top_confs = [d["confidence"] for d in filtered[:MAX_DETECTIONS_PER_FRAME]]
        dynamic_threshold = max(MIN_CONFIDENCE, sum(top_confs) / len(top_confs) * 0.9)
        
        # Keep only top detections and those above dynamic threshold
        filtered = [d for d in filtered if d["confidence"] >= dynamic_threshold][:MAX_DETECTIONS_PER_FRAME]
    
    return filtered


def run_detection_pass(image_rgb: np.ndarray, use_roi: bool = True) -> List[Dict]:
    """
    Run YOLO inference on the provided image with optional ROI cropping.
    """
    original_shape = image_rgb.shape[:2]
    if use_roi:
        image_bgr, roi_meta = prepare_inference_image(image_rgb)
    else:
        roi_meta = {
            "offset_x": 0,
            "offset_y": 0,
            "width": original_shape[1],
            "height": original_shape[0],
        }
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        image_bgr = preprocess_for_detection(image_bgr)

    logger.debug(
        "Running detection pass (use_roi=%s) conf=%s imgsz=%s",
        use_roi,
        MIN_CONFIDENCE,
        YOLO_IMAGE_SIZE,
    )
    results = model(image_bgr, conf=MIN_CONFIDENCE, imgsz=YOLO_IMAGE_SIZE)
    detections = extract_detections(results, image_bgr, original_shape, roi_meta)
    return merge_duplicate_detections(detections)


def _process_image_sync(image_data: bytes) -> Dict:
    """
    Synchronous image processing (runs in thread pool).
    This function contains all blocking operations.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        image_rgb = load_rgb_image(image_data)
        original_shape = image_rgb.shape[:2]

        detections = run_detection_pass(image_rgb, use_roi=True)

        if (
            ENABLE_FULL_FRAME_FALLBACK
            and any(det.get("bbox_area", 0) >= FULL_FRAME_AREA_TRIGGER for det in detections)
        ):
            logger.debug("Large bbox detected – running full-frame fallback")
            fallback = run_detection_pass(image_rgb, use_roi=False)
            if fallback:
                detections = merge_duplicate_detections(detections + fallback)

        if (
            ENABLE_GRID_DETECTION
            and len(detections) < GRID_DETECTION_TRIGGER
        ):
            logger.debug(
                "Running grid detection fallback: base detections=%s (trigger=%s)",
                len(detections),
                GRID_DETECTION_TRIGGER,
            )
            grid_detections = run_grid_detection(image_rgb, original_shape)
            if grid_detections:
                detections.extend(grid_detections)
                detections = merge_duplicate_detections(detections)
        
        # Apply noise filtering
        detections = filter_noisy_detections(detections)
        
        # Apply temporal filtering
        detections = apply_temporal_filtering(detections)
        
        # Clean up memory
        del image_rgb
        
        return build_detection_response(detections)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

async def process_image_for_detection(image_data: bytes) -> Dict:
    """
    Async wrapper for image processing.
    Runs blocking operations in thread pool to avoid blocking event loop.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _process_image_sync, image_data)


async def decode_base64_payload(payload: str) -> bytes:
    """Decode a base64 string that may include a data URL prefix."""
    if ',' in payload:
        payload = payload.split(',')[1]
    return base64.b64decode(payload)


def build_group_summary(detections: List[Dict]) -> Dict[str, Dict]:
    summary: Dict[str, Dict] = {}
    for det in detections:
        group = det.get("class_group", "unknown")
        if group not in summary:
            summary[group] = {
                "count": 0,
                "guidance": get_disposal_guidance(group)
            }
        summary[group]["count"] += 1
    return summary


def build_detection_response(detections: List[Dict], meta: Dict = None) -> Dict:
    """Ensure all detection responses share the same shape."""
    response = {
        "detections": detections,
        "count": len(detections)
    }
    if detections:
        response["group_summary"] = build_group_summary(detections)
    if meta:
        response.update(meta)
    return response


def load_rgb_image(image_data: bytes) -> np.ndarray:
    """Decode raw bytes into an RGB numpy array."""
    # Validate file size
    if len(image_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"Image too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    if len(image_data) < 100:  # Minimum reasonable image size
        raise HTTPException(status_code=400, detail="Image file too small or corrupted")
    
    try:
        image = Image.open(io.BytesIO(image_data))
        # Validate image format
        image.verify()
        image = Image.open(io.BytesIO(image_data))  # Reopen after verify
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {exc}") from exc

    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)


def prepare_inference_image(image_rgb: np.ndarray) -> Tuple[np.ndarray, Dict[str, int]]:
    """Crop and preprocess the RGB image for YOLO inference."""
    roi_image_np, roi_meta = crop_to_detection_roi(image_rgb)
    if roi_meta["offset_x"] or roi_meta["offset_y"]:
        logger.debug(
            f"Cropping ROI: offset=({roi_meta['offset_x']},{roi_meta['offset_y']}), "
            f"size={roi_meta['width']}x{roi_meta['height']}"
        )
    image_bgr = cv2.cvtColor(roi_image_np, cv2.COLOR_RGB2BGR)
    return preprocess_for_detection(image_bgr), roi_meta


def extract_crop_region(
    image_bgr: np.ndarray, x1: float, y1: float, x2: float, y2: float
) -> Optional[np.ndarray]:
    """Extract a crop region for further analysis."""
    x1_int = max(0, int(x1))
    y1_int = max(0, int(y1))
    x2_int = min(image_bgr.shape[1], int(x2))
    y2_int = min(image_bgr.shape[0], int(y2))

    crop = image_bgr[y1_int:y2_int, x1_int:x2_int]
    if crop.size == 0 or crop.shape[0] <= 15 or crop.shape[1] <= 15:
        return None
    return crop


def classify_material_from_crop(
    image_bgr: np.ndarray,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    adjusted_class: str,
    crop_image: Optional[np.ndarray] = None,
) -> Optional[str]:
    """Extract the crop and classify its material when feasible."""
    crop = crop_image if crop_image is not None else extract_crop_region(image_bgr, x1, y1, x2, y2)
    if crop is None:
        return None

    try:
        material = classify_material(crop, adjusted_class)
        if material and adjusted_class.lower() == "cup":
            logger.debug(f"Material classification: {adjusted_class} → {material}")
        return material
    except Exception as exc:
        logger.warning(f"⚠️ Error classifying material: {exc}")
        return None


def detect_paper_like_object(crop_image: np.ndarray) -> bool:
    """Heuristic to detect sheet-like paper objects that are often misclassified."""
    if crop_image is None or crop_image.size == 0:
        return False

    gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(crop_image, cv2.COLOR_BGR2HSV)

    mean_brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    mean_saturation = float(np.mean(hsv[:, :, 1]))

    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.mean(edges > 0))

    height, width = crop_image.shape[:2]
    aspect_ratio = height / max(1, width)

    # Paper characteristics: bright, low saturation, low contrast, low edge density, rectangular
    if (
        mean_brightness > 165
        and contrast < 45
        and mean_saturation < 60
        and edge_density < 0.08
        and 0.4 <= aspect_ratio <= 2.5
    ):
        return True
    return False


def refine_bbox_with_edges(
    image_bgr: np.ndarray,
    x1_abs: float,
    y1_abs: float,
    x2_abs: float,
    y2_abs: float,
) -> Optional[Tuple[float, float, float, float]]:
    """Use edge/contour detection to tighten bbox boundaries."""
    if not ENABLE_EDGE_REFINEMENT:
        return None

    x1_int = max(0, int(x1_abs))
    y1_int = max(0, int(y1_abs))
    x2_int = min(image_bgr.shape[1], int(x2_abs))
    y2_int = min(image_bgr.shape[0], int(y2_abs))

    crop = image_bgr[y1_int:y2_int, x1_int:x2_int]
    if crop.size == 0 or crop.shape[0] < 15 or crop.shape[1] < 15:
        return None

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 40, 140)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    crop_area = float(crop.shape[0] * crop.shape[1])
    best_contour = max(contours, key=cv2.contourArea)
    contour_area = float(cv2.contourArea(best_contour))
    if contour_area < crop_area * EDGE_REFINE_MIN_AREA:
        return None

    rx, ry, rw, rh = cv2.boundingRect(best_contour)

    margin_x = max(EDGE_REFINE_MARGIN * rw, 1.0)
    margin_y = max(EDGE_REFINE_MARGIN * rh, 1.0)

    refined_x1 = max(x1_abs, x1_int + rx - margin_x)
    refined_y1 = max(y1_abs, y1_int + ry - margin_y)
    refined_x2 = min(x2_abs, x1_int + rx + rw + margin_x)
    refined_y2 = min(y2_abs, y1_int + ry + rh + margin_y)

    if refined_x2 - refined_x1 <= 2 or refined_y2 - refined_y1 <= 2:
        return None

    return refined_x1, refined_y1, refined_x2, refined_y2


def run_detection_on_tile(
    image_rgb: np.ndarray,
    tile_coords: Tuple[int, int, int, int],
    original_shape: Tuple[int, int],
) -> List[Dict]:
    """Run detection on a specific tile and map detections back to original coordinates."""
    x1, y1, x2, y2 = tile_coords
    tile_rgb = image_rgb[y1:y2, x1:x2]
    if tile_rgb.size == 0:
        return []

    tile_bgr = cv2.cvtColor(tile_rgb, cv2.COLOR_RGB2BGR)
    tile_bgr = preprocess_for_detection(tile_bgr)

    results = model(tile_bgr, conf=MIN_CONFIDENCE, imgsz=YOLO_IMAGE_SIZE)
    roi_meta = {
        "offset_x": x1,
        "offset_y": y1,
        "width": x2 - x1,
        "height": y2 - y1,
    }
    return extract_detections(results, tile_bgr, original_shape, roi_meta)


def run_grid_detection(image_rgb: np.ndarray, original_shape: Tuple[int, int]) -> List[Dict]:
    """Run additional detections on overlapping tiles to capture edge objects."""
    if not ENABLE_GRID_DETECTION or model is None:
        return []

    height, width = image_rgb.shape[:2]
    rows = max(1, GRID_ROWS)
    cols = max(1, GRID_COLS)
    tile_height = height / rows
    tile_width = width / cols
    overlap_h = int(tile_height * GRID_OVERLAP)
    overlap_w = int(tile_width * GRID_OVERLAP)

    detections: List[Dict] = []
    processed_tiles = 0

    for row in range(rows):
        for col in range(cols):
            if processed_tiles >= GRID_MAX_TILES:
                break
            x1 = int(max(0, col * tile_width - overlap_w))
            y1 = int(max(0, row * tile_height - overlap_h))
            x2 = int(min(width, (col + 1) * tile_width + overlap_w))
            y2 = int(min(height, (row + 1) * tile_height + overlap_h))

            tile_detections = run_detection_on_tile(image_rgb, (x1, y1, x2, y2), original_shape)
            if tile_detections:
                detections.extend(tile_detections)
            processed_tiles += 1
        if processed_tiles >= GRID_MAX_TILES:
            break

    return detections


def extract_detections(
    results,
    image_bgr: np.ndarray,
    original_shape: Tuple[int, int],
    roi_meta: Dict[str, int],
) -> List[Dict]:
    """Convert YOLO raw outputs into API-friendly detections."""
    original_height, original_width = original_shape
    roi_offset_x = roi_meta["offset_x"]
    roi_offset_y = roi_meta["offset_y"]

    detections: List[Dict] = []
    for result in results:
        boxes = getattr(result, "boxes", None)
        if boxes is None or len(boxes) == 0:
            continue

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            conf = float(box.conf[0].cpu().numpy())
            class_name = model.names[cls]
            original_class = class_name.lower()

            if original_class in IGNORED_CLASS_SET:
                logger.debug(f"Ignoring class '{original_class}' (configured)")
                continue

            adjusted_class = CLASS_NORMALIZATION.get(original_class, original_class)
            mapped_class = map_class_name(adjusted_class)

            x1_abs = float(x1 + roi_offset_x)
            y1_abs = float(y1 + roi_offset_y)
            x2_abs = float(x2 + roi_offset_x)
            y2_abs = float(y2 + roi_offset_y)

            x1_norm = float(np.clip(x1_abs / original_width, 0.0, 1.0))
            y1_norm = float(np.clip(y1_abs / original_height, 0.0, 1.0))
            x2_norm = float(np.clip(x2_abs / original_width, 0.0, 1.0))
            y2_norm = float(np.clip(y2_abs / original_height, 0.0, 1.0))

            box_width = max(1e-6, x2_norm - x1_norm)
            box_height = max(1e-6, y2_norm - y1_norm)
            box_area = box_width * box_height
            aspect_ratio = box_width / max(box_height, 1e-6)
            if MAX_DETECTION_AREA > 0 and box_area > MAX_DETECTION_AREA:
                logger.debug(
                    f"Skipping detection '{class_name}' "
                    f"(area {box_area:.2f} > {MAX_DETECTION_AREA})"
                )
                continue

            local_conf_threshold = MIN_CONFIDENCE
            large_bbox = FULL_FRAME_AREA_TRIGGER > 0 and box_area >= FULL_FRAME_AREA_TRIGGER
            if large_bbox:
                local_conf_threshold += LARGE_BBOX_CONF_BOOST

            if original_class in CLOTHES_LIKE_CLASS_SET:
                if aspect_ratio > CLOTHES_ASPECT_MAX or aspect_ratio < CLOTHES_ASPECT_MIN:
                    local_conf_threshold += CLOTHES_ASPECT_CONF_BOOST

            if conf >= 0.2:
                logger.debug(f"Raw detection: {class_name} ({conf:.3f}) threshold={local_conf_threshold:.2f}")
            if conf < local_conf_threshold:
                continue

            material = None
            final_class = adjusted_class
            crop_region: Optional[np.ndarray] = None
            refined_bbox_applied = False
            needs_crop = (
                large_bbox
                or (ENABLE_PAPER_HEURISTICS and adjusted_class.lower() in PAPER_LIKE_CLASSES)
                or adjusted_class.lower() in MATERIAL_CLASS_SET
            )
            if needs_crop:
                crop_region = extract_crop_region(image_bgr, x1, y1, x2, y2)

            if crop_region is not None:
                refined = refine_bbox_with_edges(image_bgr, x1_abs, y1_abs, x2_abs, y2_abs)
                if refined:
                    x1_abs, y1_abs, x2_abs, y2_abs = refined
                    x1_norm = float(np.clip(x1_abs / original_width, 0.0, 1.0))
                    y1_norm = float(np.clip(y1_abs / original_height, 0.0, 1.0))
                    x2_norm = float(np.clip(x2_abs / original_width, 0.0, 1.0))
                    y2_norm = float(np.clip(y2_abs / original_height, 0.0, 1.0))
                    box_width = max(1e-6, x2_norm - x1_norm)
                    box_height = max(1e-6, y2_norm - y1_norm)
                    box_area = box_width * box_height
                    aspect_ratio = box_width / max(box_height, 1e-6)
                    refined_bbox_applied = True


            if (
                large_bbox
                and crop_region is not None
                and detect_paper_like_object(crop_region)
            ):
                adjusted_class = "paper"
                final_class = "paper"
                mapped_class = "recyclable"
                material = "paper"

            if adjusted_class.lower() in MATERIAL_CLASS_SET and material != "paper":
                material = classify_material_from_crop(image_bgr, x1, y1, x2, y2, adjusted_class, crop_region)
                if material:
                    final_class = f"{adjusted_class}-{material}"
                    if material in ["glass", "brown-glass", "green-glass", "white-glass", "plastic", "metal", "paper"]:
                        mapped_class = "recyclable"
                    elif material == "ceramic":
                        mapped_class = "residual"

            if not material:
                inferred_material = infer_material_from_class(adjusted_class)
                if inferred_material:
                    material = inferred_material

            if not material:
                mapped_class = map_class_name(adjusted_class)

            # Determine specific guidance based on material or class
            guidance_key = mapped_class
            class_lower = adjusted_class.lower()
            material_lower = (material or '').lower()
            
            if mapped_class == 'recyclable':
                # Check for paper-related classes
                if material_lower == 'paper' or class_lower in ['paper', 'cardboard'] or 'paper' in class_lower or 'cardboard' in class_lower:
                    guidance_key = 'recyclable_paper'
                # Check for plastic-related classes
                elif material_lower == 'plastic' or class_lower == 'plastic' or 'plastic' in class_lower:
                    guidance_key = 'recyclable_plastic'
                # Check for metal-related classes
                elif material_lower == 'metal' or class_lower == 'metal' or 'metal' in class_lower or 'can' in class_lower:
                    guidance_key = 'recyclable_metal'
                # Check for glass-related classes
                elif material_lower in ['glass', 'brown-glass', 'green-glass', 'white-glass'] or class_lower == 'glass' or 'glass' in class_lower:
                    guidance_key = 'recyclable_glass'

            detections.append(
                {
                    "bbox": {
                        "x1": x1_norm,
                        "y1": y1_norm,
                        "x2": x2_norm,
                        "y2": y2_norm,
                    },
                    "bbox_pixels": {"x1": x1_abs, "y1": y1_abs, "x2": x2_abs, "y2": y2_abs},
                    "class": final_class,
                    "class_group": mapped_class,
                    "class_original": original_class,
                    "material": material,
                    "confidence": conf,
                    "guidance": get_disposal_guidance(guidance_key),
                    "bbox_area": box_area,
                    "aspect_ratio": aspect_ratio,
                    "large_bbox": large_bbox,
                    "refined": refined_bbox_applied,
                }
            )
    return detections


@app.websocket("/ws/detect")
async def detect_trash_stream(websocket: WebSocket):
    """
    Realtime detection over WebSocket.
    Client sends JSON text:
      { "image": "<base64>", "format": "base64" }
    Server replies with detection JSON per frame.
    """
    if model is None:
        await websocket.close(code=1011, reason="Model not loaded")
        return

    await websocket.accept()
    try:
        await websocket.send_json({
            "type": "ready",
            "message": "Realtime detection socket ready",
            "min_confidence": MIN_CONFIDENCE,
            "max_fps": REALTIME_MAX_FPS,
        })
    except (WebSocketDisconnect, ConnectionError):
        logger.info("Client disconnected immediately after accept")
        return

    min_interval = 1.0 / REALTIME_MAX_FPS if REALTIME_MAX_FPS > 0 else 0
    last_frame_ts = 0.0

    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=REALTIME_CLIENT_TIMEOUT)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "warning", "message": "No frames received, closing connection"})
                await websocket.close(code=1000)
                break

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Payload must be JSON text"})
                continue

            base64_string = data.get("image")
            if not base64_string:
                await websocket.send_json({"type": "error", "message": "Missing 'image' field"})
                continue

            now = time.time()
            if min_interval > 0 and now - last_frame_ts < min_interval:
                await asyncio.sleep(min_interval - (now - last_frame_ts))
            last_frame_ts = time.time()

            try:
                image_bytes = await decode_base64_payload(base64_string)
                logger.debug(f"Received frame: {len(image_bytes)} bytes")
            except Exception as decode_error:
                await websocket.send_json({"type": "error", "message": f"Invalid base64 image: {decode_error}"})
                continue

            try:
                result = await process_image_for_detection(image_bytes)
                detection_count = result.get("count", 0)
                detections = result.get("detections", [])
                logger.debug(f"Detection result: {detection_count} objects found")
                if detection_count > 0:
                    for det in detections:
                        logger.debug(f"   - {det.get('class', 'unknown')}: {det.get('confidence', 0):.2f}")
                else:
                    logger.debug("No detections (confidence threshold might be too high)")
                try:
                    await websocket.send_json({
                        "type": "detections",
                        "timestamp": time.time(),
                        **result
                    })
                except (WebSocketDisconnect, ConnectionError) as send_error:
                    # Client disconnected, exit gracefully
                    logger.info(f"Client disconnected during send: {send_error}")
                    break
            except HTTPException as api_error:
                try:
                    await websocket.send_json({"type": "error", "message": api_error.detail})
                except (WebSocketDisconnect, ConnectionError):
                    logger.info("Client disconnected while sending error")
                    break
            except Exception as infer_error:
                logger.error(f"Error in WebSocket detection: {infer_error}", exc_info=True)
                try:
                    await websocket.send_json({"type": "error", "message": str(infer_error)})
                except (WebSocketDisconnect, ConnectionError):
                    logger.info("Client disconnected while sending error")
                    break

    except WebSocketDisconnect:
        return

@app.post("/detect")
async def detect_trash(request: Request, file: UploadFile = File(...)):
    """
    Detect trash objects in image (FormData)
    Accepts multipart/form-data with file field
    
    Returns: List of detections with bounding boxes, classes, and confidence scores
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Rate limiting (optional, can be disabled with env var)
    if os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true":
        client_id = get_client_id(request)
        max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
        window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        if not check_rate_limit(client_id, max_requests, window_seconds):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
            )
    
    try:
        image_bytes = await file.read()
        # Validate file size before processing
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        return await process_image_for_detection(image_bytes)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in detect endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/detect-base64")
async def detect_trash_base64(request: Request, image_data: Base64ImageRequest = Body(...)):
    """
    Detect trash objects in image (Base64)
    Accepts JSON with base64 encoded image
    
    Request body:
    {
        "image": "base64_encoded_string",
        "format": "base64"
    }
    
    Returns: List of detections with bounding boxes, classes, and confidence scores
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Rate limiting (optional, can be disabled with env var)
    if os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true":
        client_id = get_client_id(request)
        max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
        window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        if not check_rate_limit(client_id, max_requests, window_seconds):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
            )
    
    try:
        # Decode base64 image
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,...")
            base64_string = image_data.image
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            image_bytes = base64.b64decode(base64_string)
            
            # Validate decoded size
            if len(image_bytes) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Image too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
        
        return await process_image_for_detection(image_bytes)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in detect-base64 endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/detect-batch")
async def detect_trash_batch(request: Request, files: List[UploadFile] = File(...)):
    """
    Detect trash objects in multiple images (parallelized for better performance)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Rate limiting (optional, can be disabled with env var)
    if os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true":
        client_id = get_client_id(request)
        max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
        window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        if not check_rate_limit(client_id, max_requests, window_seconds):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
            )
    
    # Validate batch size
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum batch size: {MAX_BATCH_SIZE}"
        )
    
    # Read all files first
    file_data = []
    for file in files:
        try:
            image_data = await file.read()
            if len(image_data) > MAX_FILE_SIZE:
                file_data.append({
                    "filename": file.filename,
                    "error": f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                })
            else:
                file_data.append({
                    "filename": file.filename,
                    "data": image_data
                })
        except Exception as e:
            file_data.append({
                "filename": file.filename,
                "error": f"Error reading file: {str(e)}"
            })
    
    # Process all images in parallel
    async def process_single_file(file_info: dict):
        if "error" in file_info:
            return {
                "filename": file_info["filename"],
                "error": file_info["error"]
            }
        try:
            detection_result = await process_image_for_detection(file_info["data"])
            return {
                "filename": file_info["filename"],
                **detection_result
            }
        except HTTPException as api_error:
            return {
                "filename": file_info["filename"],
                "error": api_error.detail
            }
        except Exception as e:
            logger.error(f"Error processing {file_info['filename']}: {e}", exc_info=True)
            return {
                "filename": file_info["filename"],
                "error": str(e)
            }
    
    # Process all files concurrently
    results = await asyncio.gather(*[process_single_file(f) for f in file_data])
    
    return {"results": results}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

