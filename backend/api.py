import asyncio
import base64
import io
import json
import os
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from fastapi import Body, FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from ultralytics import YOLO
import uvicorn

# Try to import PyTorch (GPU support) and CLIP (optional)
try:
    import torch
    TORCH_AVAILABLE = True
    print("✅ PyTorch available")
except ImportError:
    torch = None
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available. Install with: pip install torch torchvision torchaudio")

try:
    import clip
    CLIP_AVAILABLE = True
    print("✅ CLIP available for material classification")
except ImportError:
    CLIP_AVAILABLE = False
    print("⚠️ CLIP not available. Install with: pip install clip-by-openai")
    print("   Will use heuristic-based material classification instead.")

app = FastAPI(title="SmartSort AI - Trash Detection API")

# CORS middleware - Cho phép React Native app gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production, nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLOv8 model từ Hugging Face
# Model sẽ được download tự động lần đầu tiên
# Thử các cách load model khác nhau
model = None
model_paths = [
    'models/best.pt',  # Waste classification model (download using download_waste_model.py)
    'models/waste-classification-yolov8-ken.pt',  # Alternative name
    'kendrickfff/waste-classification-yolov8-ken',  # Hugging Face model ID (may not work directly)
    'yolov8n.pt',  # Fallback to default YOLOv8n if waste model not found
]

for model_path in model_paths:
    try:
        print(f"Trying to load model: {model_path}")
        model = YOLO(model_path)
        print(f"✅ Model loaded successfully: {model_path}")
        break
    except Exception as e:
        print(f"❌ Error loading model {model_path}: {e}")
        continue

if model is None:
    print("⚠️ Warning: No model loaded. API will return errors for detection requests.")
    print("Please check the model path or install the model manually.")
else:
    USE_FP16 = os.getenv("USE_FP16", "false").strip().lower() in {"1", "true", "yes"}
    if TORCH_AVAILABLE and torch.cuda.is_available():
        try:
            model.to("cuda")
            if hasattr(model, "model"):
                if USE_FP16:
                    model.model.half()
                    print(f"🚀 Using GPU acceleration: {torch.cuda.get_device_name(0)} (FP16)")
                else:
                    model.model.float()
                    print(f"🚀 Using GPU acceleration: {torch.cuda.get_device_name(0)} (FP32)")
        except Exception as e:
            print(f"⚠️ Failed to move model to GPU: {e}")
            print("ℹ️ Falling back to CPU inference.")
            model.to("cpu")
            print("ℹ️ Running inference on CPU.")
    else:
        print("ℹ️ Running inference on CPU.")

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
        "action": "Làm sạch sơ rồi cho vào thùng tái chế (nhựa, kim loại, giấy, thủy tinh).",
        "description": "Rác có thể tái chế để tạo ra sản phẩm mới.",
        "icon": "♻️",
        "color": "#1e88e5"
    },
    "residual": {
        "bin": "Thùng rác thường",
        "action": "Buộc kín và cho vào thùng rác chung.",
        "description": "Rác khó tái chế như ly giấy bẩn, túi nilon lẫn thức ăn.",
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

# Print model classes when loaded
if model is not None:
    classes = list(model.names.values())
    loaded_class_set = {cls.lower() for cls in classes}
    if loaded_class_set == MOONDREAM_CLASS_SET:
        IS_MOONDREAM_MODEL = True
        print("🧠 Detected Moondream 12-class waste model – textile override disabled.")
    print(f"\n{'='*60}")
    print(f"Model loaded successfully!")
    print(f"{'='*60}")
    print(f"Model classes: {classes}")
    print(f"Total classes: {len(model.names)}")
    
    # Check if this is a waste classification model
    is_waste_model = any(keyword in str(classes).lower() 
                         for keyword in ['organic', 'plastic', 'metal', 'paper', 'waste', 'trash', 'biological', 'cardboard'])
    
    if is_waste_model:
        print("SUCCESS: This is a waste classification model!")
        print("Class mapping:")
        for cls in classes:
            mapped = map_class_name(cls)
            print(f"  - {cls:20} -> {mapped}")
    else:
        print("WARNING: This appears to be a COCO model, not a waste classification model.")
        print("You need to use a model trained for waste classification.")
    print(f"{'='*60}\n")

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

# Detection heuristics / thresholds
# Giảm xuống 0.3 để tăng độ nhạy phát hiện tối đa (từ 0.5)
# Có thể tăng lại nếu có quá nhiều false positives
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.8"))
# Tăng FPS để phát hiện nhanh hơn (từ 5 lên 10)
REALTIME_MAX_FPS = float(os.getenv("REALTIME_MAX_FPS", "30"))
REALTIME_CLIENT_TIMEOUT = float(os.getenv("REALTIME_CLIENT_TIMEOUT", "10"))
# Giảm IoU threshold để merge ít hơn, giữ lại nhiều detection hơn (từ 0.5 xuống 0.4)
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.4"))
# Img size ảnh gửi vào YOLO – 320 cho realtime (480 quá chậm với model mới)
YOLO_IMAGE_SIZE = int(os.getenv("YOLO_IMAGE_SIZE", "320"))

# CLIP model for material classification (lazy load)
clip_model = None
clip_device = None
clip_preprocess = None

def load_clip_model():
    """Lazy load CLIP model for material classification"""
    global clip_model, clip_device, clip_preprocess
    if not CLIP_AVAILABLE or clip_model is not None:
        return clip_model is not None
    
    try:
        clip_device = "cuda" if torch.cuda.is_available() else "cpu"
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=clip_device)
        clip_model.eval()
        print("✅ CLIP model loaded for material classification")
        return True
    except Exception as e:
        print(f"⚠️ Failed to load CLIP model: {e}")
        return False

# Classes that need material classification (can be made from different materials)
MATERIAL_CLASSES = ['cup', 'bottle', 'bowl', 'wine glass', 'vase', 'container']

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

# Material options for classification
MATERIAL_OPTIONS = [
    "plastic cup", "glass cup", "metal cup", "paper cup",
    "plastic bottle", "glass bottle", "metal bottle",
    "plastic bowl", "glass bowl", "metal bowl", "ceramic bowl",
    "glass wine glass", "plastic wine glass",
    "glass vase", "ceramic vase", "plastic vase",
    "plastic container", "glass container", "metal container", "paper container"
]

def classify_material_heuristic(crop_image: np.ndarray, object_class: str) -> Optional[str]:
    """
    Classify material using heuristics (color, transparency, edges)
    Returns material name or None if cannot determine
    """
    if object_class.lower() not in [c.lower() for c in MATERIAL_CLASSES]:
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

def classify_material_clip(crop_image: Image.Image, object_class: str) -> Optional[str]:
    """
    Classify material using CLIP model
    Returns material name or None if cannot determine
    """
    if not load_clip_model() or object_class.lower() not in [c.lower() for c in MATERIAL_CLASSES]:
        return None
    
    try:
        # Filter material options for this object class
        relevant_materials = [m for m in MATERIAL_OPTIONS if object_class.lower() in m.lower()]
        if not relevant_materials:
            return None
        
        # Preprocess image
        image_tensor = clip_preprocess(crop_image).unsqueeze(0).to(clip_device)
        text_tokens = clip.tokenize(relevant_materials).to(clip_device)
        
        # Get predictions
        with torch.no_grad():
            image_features = clip_model.encode_image(image_tensor)
            text_features = clip_model.encode_text(text_tokens)
            
            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Calculate similarity
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            probs = similarity[0].cpu().numpy()
            
            # Get best match
            best_idx = np.argmax(probs)
            best_prob = probs[best_idx]
            
            # Only return if confidence is high enough
            if best_prob > 0.3:
                material = relevant_materials[best_idx].split()[0]  # Extract material (plastic/glass/metal)
                return material
    except Exception as e:
        print(f"⚠️ CLIP classification error: {e}")
    
    return None

def classify_material(crop_image: np.ndarray, object_class: str) -> Optional[str]:
    """
    Classify material of an object (plastic/glass/metal/ceramic/paper)
    Tries CLIP first, falls back to heuristics
    """
    # DISABLED: CLIP is too slow (100-500ms), using only heuristics for performance
    # Uncomment below to enable CLIP:
    
    # # Convert numpy array to PIL Image for CLIP
    # crop_pil = Image.fromarray(cv2.cvtColor(crop_image, cv2.COLOR_BGR2RGB))
    # # Try CLIP first (more accurate)
    # material = classify_material_clip(crop_pil, object_class)
    # # Fallback to heuristics
    # if material is None:
    #     material = classify_material_heuristic(crop_image, object_class)
    # return material
    
    # Use only heuristics (fast, ~1-5ms)
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
    """
    if len(detections) <= 1:
        return detections
    
    # Sort by confidence (highest first)
    sorted_detections = sorted(detections, key=lambda x: x["confidence"], reverse=True)
    merged = []
    used = [False] * len(sorted_detections)
    
    for i, det1 in enumerate(sorted_detections):
        if used[i]:
            continue
        
        # Check for overlaps with other detections
        for j in range(i + 1, len(sorted_detections)):
            if used[j]:
                continue
            
            det2 = sorted_detections[j]
            
            # Only merge if same class and high IoU
            if det1["class"] == det2["class"]:
                iou = calculate_iou(det1["bbox"], det2["bbox"])
                if iou > IOU_THRESHOLD:
                    # Keep the one with higher confidence (det1, since sorted)
                    used[j] = True
                    # Merge bbox to cover both (optional - currently just keep det1)
                    # Could also average or take union of bboxes
        
        merged.append(det1)
        used[i] = True
    
    return merged


def process_image_for_detection(image_data: bytes) -> Dict:
    """
    Process image data and run detection
    Returns detection results
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Read image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_np = np.array(image)
        
        # Convert RGB to BGR (YOLO expects BGR)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Run inference with lower confidence threshold for better sensitivity
        # Dùng imgsz 320 mặc định để giảm thời gian inference (~120ms thay vì 180ms ở 480)
        print(f"🔍 Running detection with conf={MIN_CONFIDENCE}, imgsz={YOLO_IMAGE_SIZE}")
        results = model(image_bgr, conf=MIN_CONFIDENCE, imgsz=YOLO_IMAGE_SIZE)  # configurable confidence
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    # Get bounding box coordinates (normalized 0-1)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get image dimensions for normalization
                    img_height, img_width = image_np.shape[:2]
                    
                    # Normalize coordinates to 0-1 range
                    x1_norm = float(x1 / img_width)
                    y1_norm = float(y1 / img_height)
                    x2_norm = float(x2 / img_width)
                    y2_norm = float(y2 / img_height)
                    
                    # Get class and confidence
                    cls = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    
                    # Get class name
                    class_name = model.names[cls]
                    original_class = class_name.lower()
                    adjusted_class = CLASS_NORMALIZATION.get(original_class, original_class)
                    mapped_class = map_class_name(adjusted_class)
                    
                    # Log all detections before filtering (for debugging)
                    if conf >= 0.2:  # Log even low confidence detections
                        print(f"   Raw detection: {class_name} ({conf:.3f})")
                    
                    if conf >= MIN_CONFIDENCE:
                        adjusted_class = CLASS_NORMALIZATION.get(original_class, original_class)
                        
                        # Try to classify material for objects that can be made from different materials
                        material = None
                        final_class = adjusted_class
                        
                        if adjusted_class.lower() in [c.lower() for c in MATERIAL_CLASSES]:
                            try:
                                # Crop bounding box from image
                                x1_int = max(0, int(x1))
                                y1_int = max(0, int(y1))
                                x2_int = min(img_width, int(x2))
                                y2_int = min(img_height, int(y2))
                                
                                crop = image_bgr[y1_int:y2_int, x1_int:x2_int]
                                
                                # Only classify if crop is large enough
                                if crop.size > 0 and crop.shape[0] > 20 and crop.shape[1] > 20:
                                    material = classify_material(crop, adjusted_class)
                                    
                                    # Debug logging (có thể comment sau)
                                    if material and adjusted_class.lower() == 'cup':
                                        print(f"🔍 Material classification: {adjusted_class} → {material}")
                                    
                                    if material:
                                        # Update class name to include material
                                        final_class = f"{adjusted_class}-{material}"
                                        # Update mapping for material-specific classes
                                        if material in ['glass', 'brown-glass', 'green-glass', 'white-glass']:
                                            mapped_class = 'recyclable'  # Glass is recyclable
                                        elif material == 'plastic':
                                            mapped_class = 'recyclable'  # Plastic is recyclable
                                        elif material == 'metal':
                                            mapped_class = 'recyclable'  # Metal is recyclable
                                        elif material == 'paper':
                                            mapped_class = 'recyclable'  # Paper is recyclable
                                        elif material == 'ceramic':
                                            mapped_class = 'residual'  # Ceramic usually goes to residual
                            except Exception as e:
                                print(f"⚠️ Error classifying material: {e}")
                                # Continue without material classification
                        
                        # If no material detected, use original mapping
                        if not material:
                            inferred_material = infer_material_from_class(adjusted_class)
                            if inferred_material:
                                material = inferred_material
                        
                        if not material:
                            mapped_class = map_class_name(adjusted_class)

                        detections.append({
                            "bbox": {
                                "x1": x1_norm,
                                "y1": y1_norm,
                                "x2": x2_norm,
                                "y2": y2_norm
                            },  # Normalized [0-1]
                            "bbox_pixels": {
                                "x1": float(x1),
                                "y1": float(y1),
                                "x2": float(x2),
                                "y2": float(y2)
                            },  # Pixel coordinates
                            "class": final_class,  # Includes material if detected (e.g., "cup-plastic")
                            "class_group": mapped_class,
                            "class_original": original_class,  # Original YOLO prediction
                            "material": material,  # Detected material (plastic/glass/metal/ceramic/paper)
                            "confidence": conf,
                            "guidance": get_disposal_guidance(mapped_class)
                        })
        
        # Merge duplicate detections before returning
        detections = merge_duplicate_detections(detections)
        
        return build_detection_response(detections)
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


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
        print("Client disconnected immediately after accept")
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
                print(f"📥 Received frame: {len(image_bytes)} bytes")
            except Exception as decode_error:
                await websocket.send_json({"type": "error", "message": f"Invalid base64 image: {decode_error}"})
                continue

            try:
                result = process_image_for_detection(image_bytes)
                detection_count = result.get("count", 0)
                detections = result.get("detections", [])
                print(f"🔍 Detection result: {detection_count} objects found")
                if detection_count > 0:
                    for det in detections:
                        print(f"   - {det.get('class', 'unknown')}: {det.get('confidence', 0):.2f}")
                else:
                    print("   ⚠️ No detections (confidence threshold might be too high)")
                try:
                    await websocket.send_json({
                        "type": "detections",
                        "timestamp": time.time(),
                        **result
                    })
                except (WebSocketDisconnect, ConnectionError) as send_error:
                    # Client disconnected, exit gracefully
                    print(f"Client disconnected during send: {send_error}")
                    break
            except HTTPException as api_error:
                try:
                    await websocket.send_json({"type": "error", "message": api_error.detail})
                except (WebSocketDisconnect, ConnectionError):
                    print("Client disconnected while sending error")
                    break
            except Exception as infer_error:
                try:
                    await websocket.send_json({"type": "error", "message": str(infer_error)})
                except (WebSocketDisconnect, ConnectionError):
                    print("Client disconnected while sending error")
                    break

    except WebSocketDisconnect:
        return

@app.post("/detect")
async def detect_trash(file: UploadFile = File(...)):
    """
    Detect trash objects in image (FormData)
    Accepts multipart/form-data with file field
    
    Returns: List of detections with bounding boxes, classes, and confidence scores
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        image_bytes = await file.read()
        return process_image_for_detection(image_bytes)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in detect endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/detect-base64")
async def detect_trash_base64(image_data: Base64ImageRequest = Body(...)):
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
    
    try:
        # Decode base64 image
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,...")
            base64_string = image_data.image
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            image_bytes = base64.b64decode(base64_string)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
        
        return process_image_for_detection(image_bytes)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in detect-base64 endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/detect-batch")
async def detect_trash_batch(files: List[UploadFile] = File(...)):
    """
    Detect trash objects in multiple images
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    results = []
    for file in files:
        try:
            # Process each image
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Run inference with higher confidence threshold
            # Use smaller image size for faster inference
            model_results = model(image_bgr, conf=0.5, imgsz=320)
            
            detections = []
            for result in model_results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        conf = float(box.conf[0].cpu().numpy())
                        class_name = model.names[cls]
                        original_class = class_name.lower()
                        mapped_class = map_class_name(class_name)
                        
                        # Filter by confidence - only show high confidence detections
                        if conf >= 0.5:
                            img_height, img_width = image_np.shape[:2]
                            detections.append({
                                "bbox": {
                                    "x1": float(x1 / img_width),
                                    "y1": float(y1 / img_height),
                                    "x2": float(x2 / img_width),
                                    "y2": float(y2 / img_height)
                                },
                                "class": original_class,
                                "class_group": mapped_class,
                                "class_original": original_class,
                                "confidence": conf
                            })
            
            results.append({
                "filename": file.filename,
                "detections": detections,
                "count": len(detections)
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

