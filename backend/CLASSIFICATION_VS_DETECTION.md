# Classification vs Object Detection - Vấn đề Dataset

## Vấn đề hiện tại

Dataset "waste" by CavaAle trên Roboflow là **CLASSIFICATION** project, không phải **OBJECT DETECTION**.

### Classification:
- ✅ Chỉ có class labels (biological, glass, metal, paper, plastic, trash)
- ❌ **KHÔNG có bounding boxes**
- Format: Images trong folders theo class

### Object Detection (YOLOv8 cần):
- ✅ Có bounding boxes (x, y, width, height)
- ✅ Có class labels
- Format: Images + .txt files với annotations

## Tại sao không dùng được?

YOLOv8 cần **bounding boxes** để train object detection model. Dataset classification không có bounding boxes, nên:
- ❌ Không thể train YOLOv8 trực tiếp
- ❌ Cần convert hoặc tìm dataset detection khác

## Giải pháp

### Option 1: Tìm Dataset Object Detection (Khuyến nghị)

Tìm dataset có **bounding boxes** trên Roboflow:

1. **Vào Roboflow Universe:**
   - https://universe.roboflow.com
   - Search: "waste detection" hoặc "trash detection"
   - **Filter:** Project Type = "Object Detection"

2. **Dataset phù hợp:**
   - Phải có **bounding boxes**
   - Format: YOLOv8
   - Classes: waste-related (plastic, metal, paper, etc.)

3. **Download:**
   - Dùng script với format `yolov8`
   - Hoặc download thủ công

### Option 2: Convert Classification → Detection

**Không khuyến nghị** vì:
- ⚠️ Cần annotate lại toàn bộ ảnh (28k+ ảnh!)
- ⚠️ Mất rất nhiều thời gian
- ⚠️ Cần tool annotation (LabelImg, Roboflow, etc.)

### Option 3: Dùng Classification Model (Không phải YOLOv8)

Nếu chỉ cần classification (không cần bounding boxes):
- ✅ Dùng ResNet, EfficientNet, etc.
- ✅ Train với classification dataset
- ❌ Không có bounding boxes trong app

## Tìm Dataset Object Detection

### Trên Roboflow:

1. **Search với keywords:**
   - "waste detection"
   - "trash detection"
   - "recyclable waste detection"
   - "garbage detection"

2. **Filter:**
   - Project Type: **Object Detection**
   - Format: **YOLOv8** (hoặc YOLO)
   - Image Count: **5000+** (nhiều ảnh hơn = tốt hơn)

3. **Kiểm tra:**
   - Xem preview images → có bounding boxes không?
   - Xem classes → có phù hợp không?
   - Xem số lượng ảnh → càng nhiều càng tốt

### Dataset đề xuất:

1. **"Waste Classification" by Masks:**
   - URL: https://universe.roboflow.com/masks/waste-classification
   - 9161 images
   - Object Detection
   - Xem: `backend/DATASET_MASKS_ANALYSIS.md`

2. **Tìm dataset khác:**
   - Xem: `backend/ALTERNATIVE_DATASETS.md`
   - Xem: `backend/FIND_LARGE_DATASET.md`

## Next Steps

1. ✅ **Tìm dataset OBJECT DETECTION** trên Roboflow
2. ✅ **Download với format YOLOv8**
3. ✅ **Train model**

## Lưu ý

- ⚠️ Dataset classification **KHÔNG thể train YOLOv8** trực tiếp
- ✅ Cần dataset có **bounding boxes**
- ✅ Tìm trên Roboflow với filter "Object Detection"




