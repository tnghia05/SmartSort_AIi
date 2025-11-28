"""Centralized configuration for backend services."""
from __future__ import annotations

import os
from typing import Sequence


def _env_bool(key: str, default: str = "false") -> bool:
    """Parse boolean-like environment flags."""
    return os.getenv(key, default).strip().lower() in {"1", "true", "yes"}


MODEL_PATHS: Sequence[str] = (
    "models/best.pt",
    "models/waste-classification-yolov8-ken.pt",
    "kendrickfff/waste-classification-yolov8-ken",
    "yolov8n.pt",
)

USE_FP16 = _env_bool("USE_FP16")

MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.3"))
REALTIME_MAX_FPS = float(os.getenv("REALTIME_MAX_FPS", "30"))
REALTIME_CLIENT_TIMEOUT = float(os.getenv("REALTIME_CLIENT_TIMEOUT", "10"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.4"))
YOLO_IMAGE_SIZE = int(os.getenv("YOLO_IMAGE_SIZE", "640"))
DETECTION_ROI_SCALE = float(os.getenv("DETECTION_ROI_SCALE", "0.95"))
ENABLE_CLAHE = _env_bool("ENABLE_CLAHE", "true")
ENABLE_BILATERAL_FILTER = _env_bool("ENABLE_BILATERAL_FILTER", "true")
MAX_DETECTION_AREA = float(os.getenv("MAX_DETECTION_AREA", "0.5"))
ENABLE_GRID_DETECTION = _env_bool("ENABLE_GRID_DETECTION", "false")
GRID_ROWS = int(os.getenv("GRID_ROWS", "1"))
GRID_COLS = int(os.getenv("GRID_COLS", "1"))
GRID_OVERLAP = float(os.getenv("GRID_OVERLAP", "0.0"))
GRID_DETECTION_TRIGGER = int(os.getenv("GRID_DETECTION_TRIGGER", "3"))
GRID_MAX_TILES = int(os.getenv("GRID_MAX_TILES", "1"))
ENABLE_FULL_FRAME_FALLBACK = _env_bool("ENABLE_FULL_FRAME_FALLBACK", "true")
FULL_FRAME_AREA_TRIGGER = float(os.getenv("FULL_FRAME_AREA_TRIGGER", "0.55"))
LARGE_BBOX_CONF_BOOST = float(os.getenv("LARGE_BBOX_CONF_BOOST", "0.15"))
CLOTHES_ASPECT_MIN = float(os.getenv("CLOTHES_ASPECT_MIN", "0.4"))
CLOTHES_ASPECT_MAX = float(os.getenv("CLOTHES_ASPECT_MAX", "1.8"))
CLOTHES_ASPECT_CONF_BOOST = float(os.getenv("CLOTHES_ASPECT_CONF_BOOST", "0.05"))
ENABLE_EDGE_REFINEMENT = _env_bool("ENABLE_EDGE_REFINEMENT", "false")
EDGE_REFINE_MIN_AREA = float(os.getenv("EDGE_REFINE_MIN_AREA", "0.02"))
EDGE_REFINE_MARGIN = float(os.getenv("EDGE_REFINE_MARGIN", "0.02"))
MAX_DETECTIONS_PER_FRAME = int(os.getenv("MAX_DETECTIONS_PER_FRAME", "8"))
MIN_BBOX_AREA = float(os.getenv("MIN_BBOX_AREA", "0.003"))
ENABLE_TEMPORAL_FILTERING = _env_bool("ENABLE_TEMPORAL_FILTERING", "false")
TEMPORAL_STABILITY_THRESHOLD = int(os.getenv("TEMPORAL_STABILITY_THRESHOLD", "1"))
TEMPORAL_HISTORY_SIZE = int(os.getenv("TEMPORAL_HISTORY_SIZE", "6"))
ENABLE_CLASS_SIGNATURE_FILTER = _env_bool("ENABLE_CLASS_SIGNATURE_FILTER", "false")
IGNORED_CLASSES = os.getenv("IGNORED_CLASSES", "shoes,cloth").split(",")

__all__ = [
    "MODEL_PATHS",
    "USE_FP16",
    "MIN_CONFIDENCE",
    "REALTIME_MAX_FPS",
    "REALTIME_CLIENT_TIMEOUT",
    "IOU_THRESHOLD",
    "YOLO_IMAGE_SIZE",
    "DETECTION_ROI_SCALE",
    "ENABLE_CLAHE",
    "ENABLE_BILATERAL_FILTER",
    "MAX_DETECTION_AREA",
    "ENABLE_GRID_DETECTION",
    "GRID_ROWS",
    "GRID_COLS",
    "GRID_OVERLAP",
    "GRID_DETECTION_TRIGGER",
    "GRID_MAX_TILES",
    "ENABLE_FULL_FRAME_FALLBACK",
    "FULL_FRAME_AREA_TRIGGER",
    "LARGE_BBOX_CONF_BOOST",
    "CLOTHES_ASPECT_MIN",
    "CLOTHES_ASPECT_MAX",
    "CLOTHES_ASPECT_CONF_BOOST",
    "ENABLE_EDGE_REFINEMENT",
    "EDGE_REFINE_MIN_AREA",
    "EDGE_REFINE_MARGIN",
    "MAX_DETECTIONS_PER_FRAME",
    "MIN_BBOX_AREA",
    "ENABLE_TEMPORAL_FILTERING",
    "TEMPORAL_STABILITY_THRESHOLD",
    "TEMPORAL_HISTORY_SIZE",
    "ENABLE_CLASS_SIGNATURE_FILTER",
    "IGNORED_CLASSES",
]

