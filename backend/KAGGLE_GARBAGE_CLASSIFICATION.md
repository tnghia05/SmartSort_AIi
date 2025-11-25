# Dataset: Garbage Classification (12 classes) - Kaggle

## Thông tin Dataset

- **URL:** https://www.kaggle.com/datasets/mostafaabla/garbage-classification
- **Tên:** Garbage Classification (12 classes)
- **Kích thước:** 250.51 MB
- **Số files:** 15.5k files
- **Format:** Classification (folders by class)
- **Classes:** ✅ **ĐÚNG 12 CLASSES** - Phù hợp 100% với model!

## Classes trong Dataset

| Class | Số files | Phù hợp với Model |
|-------|----------|-------------------|
| battery | 945 | ✅ battery |
| biological | 985 | ✅ biological |
| brown-glass | 607 | ✅ brown-glass |
| cardboard | 891 | ✅ cardboard |
| clothes | 5,325 | ✅ clothes |
| green-glass | 629 | ✅ green-glass |
| metal | 769 | ✅ metal |
| paper | 1,050 | ✅ paper |
| plastic | 865 | ✅ plastic |
| shoes | 1,977 | ✅ shoes |
| trash | 697 | ✅ trash |
| white-glass | 775 | ✅ white-glass |

**Tổng:** ~15,500 files

## ⚠️ Lưu ý Quan Trọng

### Dataset này là CLASSIFICATION, không phải Object Detection!

**Cấu trúc:**
```
garbage_classification/
├── battery/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── biological/
├── brown-glass/
└── ...
```

**Vấn đề:**
- ❌ **KHÔNG có bounding boxes** (chỉ có class labels)
- ❌ **KHÔNG thể train YOLOv8 trực tiếp** cho object detection
- ✅ **Có thể dùng cho classification** (không cần bboxes)

## Giải pháp

### Option 1: Dùng cho Classification (Không phải Detection)

Nếu chỉ cần classification (không cần bounding boxes):
- ✅ Dataset này hoàn hảo!
- ✅ Đúng 12 classes
- ✅ Nhiều ảnh (15.5k)
- ✅ Không cần convert

**Train classification model:**
- Dùng ResNet, EfficientNet, etc.
- Không dùng YOLOv8 (vì YOLOv8 là detection)

### Option 2: Convert sang Object Detection (Cần annotate)

Nếu cần object detection (có bounding boxes):
- ⚠️ Cần annotate lại toàn bộ ảnh
- ⚠️ Mất rất nhiều thời gian (15.5k ảnh!)
- ⚠️ Cần tool annotation (LabelImg, Roboflow, etc.)

**Không khuyến nghị** vì:
- Mất quá nhiều thời gian
- Có thể tìm dataset detection sẵn

### Option 3: Combine với Dataset Detection

- Download dataset này (classification)
- Tìm dataset detection khác (có bboxes)
- Combine để tăng số lượng ảnh

## Cách Download

### Bước 1: Cài đặt Kaggle API

```bash
pip install kaggle
```

### Bước 2: Setup Kaggle Credentials

1. **Lấy API credentials:**
   - Vào: https://www.kaggle.com/settings
   - Scroll xuống "API"
   - Click "Create New Token"
   - Download file `kaggle.json`

2. **Đặt credentials:**
   - **Windows:** `C:\Users\<username>\.kaggle\kaggle.json`
   - **Linux/Mac:** `~/.kaggle/kaggle.json`

3. **Set permissions (Linux/Mac):**
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

### Bước 3: Download Dataset

**Cách 1: Dùng Script (Khuyến nghị)**

```bash
cd E:\Code\rac\backend
python download_dataset.py
# Chọn option 2 (Kaggle)
# Nhập: mostafaabla/garbage-classification
# Output: E:\Code\rac\backend\dataset
```

**Cách 2: Dùng Kaggle CLI**

```bash
kaggle datasets download -d mostafaabla/garbage-classification
unzip garbage-classification.zip -d dataset
```

**Cách 3: Download thủ công**

1. Vào: https://www.kaggle.com/datasets/mostafaabla/garbage-classification
2. Click "Download" button
3. Extract file zip
4. Đặt vào `E:\Code\rac\backend\dataset`

## Cấu trúc sau khi Download

```
dataset/
├── garbage_classification/
│   ├── battery/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ... (945 files)
│   ├── biological/
│   │   └── ... (985 files)
│   ├── brown-glass/
│   │   └── ... (607 files)
│   ├── cardboard/
│   │   └── ... (891 files)
│   ├── clothes/
│   │   └── ... (5325 files)
│   ├── green-glass/
│   │   └── ... (629 files)
│   ├── metal/
│   │   └── ... (769 files)
│   ├── paper/
│   │   └── ... (1050 files)
│   ├── plastic/
│   │   └── ... (865 files)
│   ├── shoes/
│   │   └── ... (1977 files)
│   ├── trash/
│   │   └── ... (697 files)
│   └── white-glass/
│       └── ... (775 files)
```

## Sử dụng Dataset

### Nếu dùng cho Classification:

1. **Train classification model:**
   ```python
   # Sử dụng ResNet, EfficientNet, etc.
   # Không dùng YOLOv8 (vì YOLOv8 là detection)
   ```

2. **Split train/val/test:**
   - Tự động split từ folders
   - Hoặc dùng script prepare_dataset.py

### Nếu cần Object Detection:

1. **Annotate lại ảnh:**
   - Dùng LabelImg: https://github.com/HumanSignal/labelImg
   - Format: YOLO
   - Mất rất nhiều thời gian!

2. **Hoặc tìm dataset detection khác:**
   - Xem: `BETTER_DATASET_SOURCES.md`
   - Tìm dataset có bounding boxes sẵn

## Ưu và Nhược điểm

### ✅ Ưu điểm:
- **Đúng 12 classes** - Phù hợp 100% với model
- **Nhiều ảnh** - 15.5k files
- **Dễ download** - Có Kaggle API
- **Miễn phí** - Free to use
- **Chất lượng tốt** - Từ Kaggle community

### ⚠️ Nhược điểm:
- **Classification only** - Không có bounding boxes
- **Không thể train YOLOv8** trực tiếp cho detection
- **Cần annotate lại** nếu muốn detection (mất thời gian)

## Khuyến nghị

### ✅ Dùng dataset này nếu:
- Muốn train **classification model** (không cần bboxes)
- Muốn dataset **đúng 12 classes**
- Muốn **nhiều ảnh** (15.5k)

### ⚠️ Không dùng nếu:
- Cần **object detection** (có bounding boxes)
- Muốn train **YOLOv8** cho detection
- Không muốn annotate lại

## Next Steps

1. ✅ **Download dataset** (dùng script hoặc thủ công)
2. ✅ **Kiểm tra cấu trúc** (12 folders)
3. ✅ **Quyết định:**
   - Classification → Train classification model
   - Detection → Tìm dataset detection khác hoặc annotate lại

## Lưu ý cho App hiện tại

App hiện tại đang dùng **YOLOv8 cho object detection** (có bounding boxes). 

Nếu dùng dataset này:
- ⚠️ Cần thay đổi app sang **classification** (không có bboxes)
- ⚠️ Hoặc tìm dataset **detection** khác
- ⚠️ Hoặc annotate lại dataset này (mất thời gian)




