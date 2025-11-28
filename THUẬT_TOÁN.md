# THUẬT TOÁN TRONG SMART SORT AI
## Tài liệu Chi tiết về Các Thuật toán và Kỹ thuật được Sử dụng

---

## 📋 MỤC LỤC

1. [Object Detection - YOLOv8](#1-object-detection---yolov8)
2. [Image Preprocessing](#2-image-preprocessing)
3. [Region of Interest (ROI) Detection](#3-region-of-interest-roi-detection)
4. [Post-Processing Algorithms](#4-post-processing-algorithms)
5. [Material Classification Heuristics](#5-material-classification-heuristics)
6. [Optimization Techniques](#6-optimization-techniques)

---

## 1. OBJECT DETECTION - YOLOv8

### 1.1. YOLOv8 Architecture

**YOLOv8 (You Only Look Once version 8)** là state-of-the-art object detection model được phát triển bởi Ultralytics.

#### Đặc điểm:
- **Single-stage detector**: Phát hiện và phân loại trong 1 lần forward pass
- **Anchor-free**: Không cần anchor boxes như các phiên bản trước
- **Real-time performance**: 30+ FPS với GPU
- **Multi-object detection**: Phát hiện nhiều vật thể cùng lúc

#### Input/Output:
```
Input: Ảnh RGB (640x640 pixels - configurable)
Output: 
  - Bounding boxes (x1, y1, x2, y2)
  - Class labels (Glass, Metal, Paper, Plastic, Waste)
  - Confidence scores (0.0 - 1.0)
```

### 1.2. Model Training

- **Dataset**: Waste classification dataset (5 classes)
- **Backbone**: CSPDarknet53
- **Loss Function**: Combined classification + localization loss
- **Optimizer**: AdamW with learning rate scheduling

---

## 2. IMAGE PREPROCESSING

### 2.1. CLAHE (Contrast Limited Adaptive Histogram Equalization)

**Mục đích**: Tăng cường độ tương phản của ảnh để model nhận diện tốt hơn

**Thuật toán**:
```python
1. Chuyển ảnh từ BGR sang LAB color space
2. Tách channel L (Luminance - độ sáng)
3. Áp dụng CLAHE lên channel L với:
   - clipLimit = 2.0 (giới hạn tăng cường)
   - tileGridSize = (8, 8) (chia ảnh thành grid 8x8)
4. Merge lại các channels và chuyển về BGR
```

**Tại sao dùng CLAHE thay vì HE thông thường?**
- CLAHE tránh over-enhancement (tăng cường quá mức)
- Adaptive: Mỗi vùng ảnh được xử lý riêng biệt
- Phù hợp với ảnh có ánh sáng không đều

### 2.2. Bilateral Filter

**Mục đích**: Làm mịn ảnh nhưng giữ lại edges (biên)

**Thuật toán**:
```python
BilateralFilter(image, d, sigmaColor, sigmaSpace)
- d: Kích thước kernel (3 hoặc 5 tùy kích thước ảnh)
- sigmaColor: Độ mịn màu sắc (50)
- sigmaSpace: Độ mịn không gian (50)
```

**Công thức**:
```
BF[I]p = (1/Wp) * Σ I(q) * f(||I(p) - I(q)||) * g(||p - q||)

Trong đó:
- f: Hàm Gaussian cho độ khác biệt màu sắc
- g: Hàm Gaussian cho khoảng cách không gian
- Wp: Normalization factor
```

**Tại sao dùng Bilateral Filter?**
- Giảm nhiễu (noise) mà không làm mờ edges
- Tốt hơn Gaussian Blur thông thường
- Giữ lại chi tiết quan trọng cho object detection

---

## 3. REGION OF INTEREST (ROI) DETECTION

### 3.1. ROI Cropping Algorithm

**Mục đích**: Cắt ảnh về vùng trung tâm để loại bỏ background, tăng tốc độ xử lý

**Thuật toán**:
```python
def crop_to_detection_roi(image_rgb, roi_scale=0.95):
    height, width = image.shape[:2]
    
    # Tính toán ROI dimensions
    roi_height = height * roi_scale  # Ví dụ: 95% chiều cao
    roi_width = width * roi_scale    # 95% chiều rộng
    
    # Tính offset để center ROI
    offset_y = (height - roi_height) // 2
    offset_x = (width - roi_width) // 2
    
    # Crop ảnh
    cropped = image[offset_y:offset_y+roi_height, 
                    offset_x:offset_x+roi_width]
    
    return cropped, metadata
```

**Lợi ích**:
- ✅ Giảm 10-20% thời gian xử lý
- ✅ Loại bỏ background noise (tường, người, etc.)
- ✅ Focus vào vùng có khả năng chứa vật thể cao nhất

### 3.2. Full-Frame Fallback

**Khi nào dùng?**
- Khi phát hiện bounding box lớn (area > 55% của ảnh)
- ROI có thể đã cắt mất phần vật thể

**Logic**:
```python
if bbox_area >= FULL_FRAME_AREA_TRIGGER (0.55):
    # Run detection lại trên toàn bộ ảnh
    fallback_detections = run_detection_pass(image, use_roi=False)
    # Merge với detections ban đầu
```

---

## 4. POST-PROCESSING ALGORITHMS

### 4.1. Non-Maximum Suppression (NMS) - Merge Duplicate Detections

**Mục đích**: Loại bỏ các bounding box trùng lặp, giữ lại box có confidence cao nhất

**Thuật toán**:
```python
def merge_duplicate_detections(detections):
    # 1. Group detections theo class
    by_class = group_by_class(detections)
    
    merged = []
    for each class:
        # 2. Sort theo confidence (cao → thấp)
        sorted_dets = sort_by_confidence(class_detections)
        
        # 3. Với mỗi detection:
        for det1 in sorted_dets:
            if det1 already used: continue
            
            # 4. Tìm các detection overlap
            for det2 in remaining_detections:
                iou = calculate_iou(det1, det2)
                if iou > IOU_THRESHOLD (0.4):
                    # Mark det2 as duplicate
                    mark_as_used(det2)
            
            merged.append(det1)
    
    return merged
```

### 4.2. Intersection over Union (IoU)

**Công thức tính IoU**:
```
IoU = Area of Intersection / Area of Union

Trong đó:
- Intersection = Diện tích phần giao nhau giữa 2 box
- Union = Tổng diện tích 2 box - Intersection
```

**Implementation**:
```python
def calculate_iou(bbox1, bbox2):
    # Tìm intersection rectangle
    x1_inter = max(bbox1.x1, bbox2.x1)
    y1_inter = max(bbox1.y1, bbox2.y1)
    x2_inter = min(bbox1.x2, bbox2.x2)
    y2_inter = min(bbox1.y2, bbox2.y2)
    
    # Tính intersection area
    if x2_inter <= x1_inter or y2_inter <= y1_inter:
        return 0.0
    
    inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    
    # Tính union area
    area1 = (bbox1.x2 - bbox1.x1) * (bbox1.y2 - bbox1.y1)
    area2 = (bbox2.x2 - bbox2.x1) * (bbox2.y2 - bbox2.y1)
    union_area = area1 + area2 - inter_area
    
    return inter_area / union_area if union_area > 0 else 0.0
```

**Threshold**: `IOU_THRESHOLD = 0.4`
- Nếu IoU > 0.4: Coi như duplicate, giữ box có confidence cao hơn

### 4.3. Temporal Filtering

**Mục đích**: Lọc các detection không ổn định qua nhiều frames (video stream)

**Thuật toán**:
```python
# Maintain detection history
_temporal_detection_history = []  # Queue của các frames gần đây

def apply_temporal_filtering(current_detections):
    # 1. Thêm current frame vào history
    _temporal_detection_history.append(current_detections)
    
    # 2. Giữ chỉ TEMPORAL_HISTORY_SIZE frames (mặc định: 6)
    if len(history) > TEMPORAL_HISTORY_SIZE:
        history.pop(0)  # Remove oldest
    
    # 3. Với mỗi detection hiện tại:
    stable_detections = []
    for det in current_detections:
        class_name = det.class
        
        # 4. Đếm số frames gần đây có class này
        class_match_count = 0
        for frame in recent_frames[-TEMPORAL_STABILITY_THRESHOLD:]:
            if class_name in frame:
                class_match_count += 1
        
        # 5. Chỉ giữ nếu xuất hiện >= TEMPORAL_STABILITY_THRESHOLD lần
        if class_match_count >= TEMPORAL_STABILITY_THRESHOLD:
            stable_detections.append(det)
    
    return stable_detections
```

**Parameters**:
- `TEMPORAL_HISTORY_SIZE = 6`: Giữ 6 frames gần nhất
- `TEMPORAL_STABILITY_THRESHOLD = 1`: Class phải xuất hiện ít nhất 1 lần trong history

**Lợi ích**: Loại bỏ false positives, giữ lại detections ổn định

### 4.4. Noise Filtering

**Mục đích**: Loại bỏ các detection không đáng tin cậy

**Các bộ lọc**:

1. **Minimum Bounding Box Area**:
   ```python
   if bbox_area < MIN_BBOX_AREA (0.003 = 0.3% của ảnh):
       filter_out()
   ```
   - Loại bỏ box quá nhỏ (thường là noise)

2. **Maximum Detections per Frame**:
   ```python
   if num_detections > MAX_DETECTIONS_PER_FRAME (8):
       # Áp dụng dynamic threshold
       dynamic_threshold = average_confidence * 0.9
       keep_only_top_N_with_threshold()
   ```
   - Giới hạn số lượng detection
   - Tự động tăng threshold nếu quá nhiều detection

3. **Large Bbox Confidence Boost**:
   ```python
   if bbox_area >= FULL_FRAME_AREA_TRIGGER:
       confidence += LARGE_BBOX_CONF_BOOST (0.15)
   ```
   - Tăng confidence cho box lớn (có thể là vật thể chính)

---

## 5. MATERIAL CLASSIFICATION HEURISTICS

### 5.1. Paper Detection Heuristic

**Mục đích**: Phát hiện vật thể giống giấy (paper-like objects)

**Đặc điểm của giấy**:
- Sáng (brightness > 165)
- Độ tương phản thấp (contrast < 45)
- Độ bão hòa màu thấp (saturation < 60)
- Edge density thấp (< 0.08)
- Hình chữ nhật (aspect ratio 0.4 - 2.5)

**Thuật toán**:
```python
def detect_paper_like_object(crop_image):
    gray = convert_to_grayscale(crop_image)
    hsv = convert_to_hsv(crop_image)
    
    # Tính toán features
    mean_brightness = mean(gray)
    contrast = std(gray)
    mean_saturation = mean(hsv.saturation)
    edges = canny_edge_detection(gray)
    edge_density = mean(edges > 0)
    aspect_ratio = height / width
    
    # Decision tree
    if (mean_brightness > 165 AND
        contrast < 45 AND
        mean_saturation < 60 AND
        edge_density < 0.08 AND
        0.4 <= aspect_ratio <= 2.5):
        return True
    return False
```

### 5.2. Material Classification Heuristic

**Mục đích**: Phân loại vật liệu từ hình ảnh crop (plastic/glass/metal/ceramic)

**Features sử dụng**:
1. **Brightness** (HSV Value channel)
2. **Color variance** (phương sai màu sắc)
3. **Edge density** (mật độ biên - Canny edges)
4. **Saturation** (độ bão hòa màu)

**Decision Rules**:

```python
def classify_material_heuristic(crop, object_class):
    if object_class == 'cup':
        if edge_density > 0.15:
            # Nhiều edges → thủy tinh
            if mean_brightness > 140:
                return 'glass'
            else:
                return 'metal'
        elif color_variance > 600 or saturation > 50:
            return 'plastic'
        else:
            return 'glass'
    
    elif object_class == 'bottle':
        if edge_density > 0.12 and brightness > 140:
            return 'glass'
        elif brightness < 90:
            return 'metal'
        else:
            return 'plastic'
    
    elif object_class == 'bowl':
        if edge_density > 0.1 and brightness > 130:
            return 'glass'
        elif color_variance < 400:
            return 'ceramic'
        else:
            return 'plastic'
```

### 5.3. Edge Refinement với Canny + Contours

**Mục đích**: Tinh chỉnh bounding box dựa trên biên thực tế của vật thể

**Thuật toán**:
```python
def refine_bbox_with_edges(image, bbox):
    # 1. Crop vùng quanh bbox
    crop = image[bbox.y1:bbox.y2, bbox.x1:bbox.x2]
    
    # 2. Edge detection
    gray = convert_to_grayscale(crop)
    blur = gaussian_blur(gray, kernel=(3,3))
    edges = canny_edge_detection(blur, low=40, high=140)
    edges = dilate(edges, kernel=(3,3))
    
    # 3. Tìm contours
    contours = find_contours(edges, RETR_EXTERNAL)
    
    # 4. Chọn contour lớn nhất
    best_contour = max(contours, key=contourArea)
    
    # 5. Tính bounding rect của contour
    x, y, w, h = boundingRect(best_contour)
    
    # 6. Refine bbox với margin
    refined_x1 = max(original_x1, x - margin)
    refined_y1 = max(original_y1, y - margin)
    refined_x2 = min(original_x2, x + w + margin)
    refined_y2 = min(original_y2, y + h + margin)
    
    return refined_bbox
```

**Lợi ích**: Bounding box sát hơn với vật thể thực tế

---

## 6. OPTIMIZATION TECHNIQUES

### 6.1. Grid Detection (Fallback)

**Mục đích**: Phát hiện vật thể ở rìa ảnh khi ROI detection miss

**Khi nào dùng?**
- Khi số detection < GRID_DETECTION_TRIGGER (3)

**Thuật toán**:
```python
def run_grid_detection(image, rows=1, cols=1):
    height, width = image.shape[:2]
    
    # Chia ảnh thành grid
    tile_height = height / rows
    tile_width = width / cols
    
    detections = []
    for row in range(rows):
        for col in range(cols):
            # Tính tile coordinates với overlap
            x1 = col * tile_width - overlap
            y1 = row * tile_height - overlap
            x2 = (col+1) * tile_width + overlap
            y2 = (row+1) * tile_height + overlap
            
            # Run detection trên tile
            tile_detections = detect_on_tile(image[x1:x2, y1:y2])
            detections.extend(tile_detections)
    
    return detections
```

### 6.2. FP16 Inference

**Mục đích**: Giảm memory và tăng tốc độ với GPU

**Cách hoạt động**:
- Model weights: 32-bit float → 16-bit float
- Giảm 50% memory usage
- Tăng ~1.5-2x tốc độ inference
- Độ chính xác giảm không đáng kể

**Implementation**:
```python
if USE_FP16 and GPU_available:
    model.model.half()  # Convert to FP16
```

### 6.3. CLAHE Caching

**Mục đích**: Tránh tạo lại CLAHE object cho mỗi ảnh

**Implementation**:
```python
_clahe_cache = None

def get_clahe():
    global _clahe_cache
    if _clahe_cache is None:
        _clahe_cache = cv2.createCLAHE(clipLimit=2.0, 
                                        tileGridSize=(8, 8))
    return _clahe_cache
```

### 6.4. Thread Pool Executor

**Mục đích**: Xử lý nhiều request đồng thời

**Implementation**:
```python
executor = ThreadPoolExecutor(max_workers=4)

# Async processing
result = await executor.submit(_process_image_sync, image_data)
```

---

## 📊 TÓM TẮT PIPELINE

```
Input Image
    ↓
1. ROI Cropping (95% center)
    ↓
2. Image Preprocessing
   - CLAHE (contrast enhancement)
   - Bilateral Filter (noise reduction)
    ↓
3. YOLOv8 Inference
   - Object detection
   - Class prediction
   - Confidence scoring
    ↓
4. Post-Processing
   - Merge duplicates (NMS with IoU)
   - Filter noise (size, count)
   - Temporal filtering (video)
    ↓
5. Material Classification (if needed)
   - Heuristic-based
   - Paper detection
   - Material inference
    ↓
6. Edge Refinement (optional)
   - Canny edge detection
   - Contour-based refinement
    ↓
Output: Detections with bounding boxes, classes, guidance
```

---

## 🔢 THAM SỐ QUAN TRỌNG

| Parameter | Giá trị | Mô tả |
|-----------|---------|-------|
| `MIN_CONFIDENCE` | 0.6 | Ngưỡng tin cậy tối thiểu |
| `IOU_THRESHOLD` | 0.4 | Ngưỡng IoU để merge duplicates |
| `ROI_SCALE` | 0.95 | Tỷ lệ ROI (95% ảnh) |
| `YOLO_IMAGE_SIZE` | 640 | Kích thước ảnh input cho YOLO |
| `MAX_DETECTIONS_PER_FRAME` | 8 | Số detection tối đa mỗi frame |
| `MIN_BBOX_AREA` | 0.003 | Diện tích bbox tối thiểu (0.3%) |
| `TEMPORAL_HISTORY_SIZE` | 6 | Số frames lưu trong history |
| `TEMPORAL_STABILITY_THRESHOLD` | 1 | Số frames class phải xuất hiện |

---

## 📚 TÀI LIỆU THAM KHẢO

1. **YOLOv8 Paper**: https://github.com/ultralytics/ultralytics
2. **CLAHE Algorithm**: Adaptive Histogram Equalization
3. **Bilateral Filter**: Tomasi & Manduchi (1998)
4. **Non-Maximum Suppression**: Neubeck & Van Gool (2006)
5. **Canny Edge Detection**: Canny (1986)

---

**Tài liệu này mô tả các thuật toán chính được sử dụng trong SmartSort AI để đạt được hiệu quả và độ chính xác cao trong việc phát hiện và phân loại rác thải.**



