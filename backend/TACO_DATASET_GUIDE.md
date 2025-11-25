# Hướng Dẫn Download và Sử dụng TACO Dataset

## TACO Dataset - Trash Annotations in Context

**URL:** http://tacodataset.org/

## Thông tin Dataset

- **Số ảnh:** 1500+ images
- **Classes:** 60 classes waste items
- **Format:** COCO format (JSON)
- **Object Detection:** ✅ Có bounding boxes
- **License:** CC BY 4.0 (miễn phí)
- **Chất lượng:** ⭐⭐⭐⭐⭐ (Từ research paper)

## Tại sao chọn TACO?

- ✅ **Chuyên biệt về waste** - Chỉ tập trung vào rác thải
- ✅ **Chất lượng cao** - Từ research paper, đã được review
- ✅ **Object Detection** - Có bounding boxes (không phải classification)
- ✅ **Nhiều classes** - 60 classes (có thể map về 12 classes)
- ✅ **Miễn phí** - Free to use

## Cách Download

### Bước 1: Truy cập TACO Website

1. Vào: http://tacodataset.org/
2. Click "Download" hoặc "Get the Dataset"

### Bước 2: Download Annotations

1. Download file annotations (COCO format JSON)
2. Download images (có thể download từng batch)

### Bước 3: Cấu trúc Dataset

```
taco_dataset/
├── annotations/
│   └── annotations.json (COCO format)
├── images/
│   ├── batch_1/
│   ├── batch_2/
│   └── ...
```

## Convert COCO → YOLO Format

### Script tự động (sẽ tạo):

```bash
cd backend
python convert_coco_to_yolo.py \
    --coco_path taco_dataset/annotations/annotations.json \
    --output_dir dataset \
    --class_mapping taco_to_yolo_mapping.json
```

### Mapping 60 classes → 12 classes

TACO có 60 classes, cần map về 12 classes của model:

```json
{
  "Aluminium foil": "metal",
  "Can": "metal",
  "Bottle": "plastic",
  "Plastic bag": "plastic",
  "Cardboard": "paper",
  "Paper": "paper",
  "Glass bottle": "glass",
  "Battery": "battery",
  "Clothes": "clothes",
  "Shoes": "shoes",
  "Organic waste": "biological",
  "Trash": "trash",
  // ... map các classes khác
}
```

## Classes trong TACO

TACO có 60 classes, bao gồm:
- Metal: Aluminium foil, Can, etc.
- Plastic: Bottle, Plastic bag, etc.
- Paper: Cardboard, Paper, etc.
- Glass: Glass bottle, etc.
- Organic: Organic waste, etc.
- Other: Battery, Clothes, Shoes, Trash, etc.

## Sử dụng với Model hiện tại

### Option 1: Map về 12 classes

1. Download TACO dataset
2. Convert COCO → YOLO
3. Map 60 classes → 12 classes
4. Train model với 12 classes

### Option 2: Train với 60 classes

1. Download TACO dataset
2. Convert COCO → YOLO
3. Update model để hỗ trợ 60 classes
4. Train model mới

## Ưu và Nhược điểm

### Ưu điểm:
- ✅ Chất lượng cao (từ research)
- ✅ Object Detection (có bboxes)
- ✅ Chuyên biệt về waste
- ✅ Miễn phí

### Nhược điểm:
- ⚠️ Ít ảnh hơn (1500 vs 20k+)
- ⚠️ Cần convert format
- ⚠️ Cần map classes

## So sánh với Roboflow

| Tiêu chí | TACO | Roboflow |
|----------|------|----------|
| Chất lượng | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Số ảnh | 1500+ | 20k+ |
| Object Detection | ✅ | ⚠️ Nhiều classification |
| Format | COCO | YOLO sẵn |
| Classes | 60 | 6-12 |
| Dễ dùng | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Khuyến nghị

### ✅ Dùng TACO nếu:
- Muốn dataset chất lượng cao từ research
- Không ngại convert format
- Muốn nhiều classes (60)

### ✅ Dùng Roboflow nếu:
- Muốn dễ dàng (YOLO sẵn)
- Muốn nhiều ảnh (20k+)
- Không cần quá nhiều classes

## Next Steps

1. ✅ Download TACO dataset
2. ✅ Convert COCO → YOLO
3. ✅ Map classes
4. ✅ Train model




