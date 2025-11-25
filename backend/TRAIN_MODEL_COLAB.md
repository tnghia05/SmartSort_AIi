# Hướng dẫn Train Model trên Google Colab

## Khi nào cần train?

Xem `SHOULD_RETRAIN.md` để quyết định có cần train không.

## Prerequisites

1. **Dataset:**
   - Tối thiểu: 50-100 ảnh mỗi class
   - Tổng: 600-1200 ảnh (12 classes)
   - Format: JPG/PNG
   - Annotation: YOLO format (txt files)

2. **Google Colab:**
   - Tài khoản Google
   - Free GPU (T4) đủ để train

3. **Thời gian:**
   - Fine-tune: 1-2 giờ
   - Train từ đầu: 4-8 giờ

## Option 1: Fine-tune Model Hiện Tại (Khuyến nghị)

### Bước 1: Chuẩn bị Dataset

1. **Tạo cấu trúc thư mục:**
```
dataset/
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── val/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── image1.txt
│   │   ├── image2.txt
│   │   └── ...
│   └── val/
│       ├── image1.txt
│       ├── image2.txt
│       └── ...
└── data.yaml
```

2. **Tạo data.yaml:**
```yaml
path: /content/dataset
train: images/train
val: images/val

names:
  0: battery
  1: biological
  2: brown-glass
  3: cardboard
  4: clothes
  5: green-glass
  6: metal
  7: paper
  8: plastic
  9: shoes
  10: trash
  11: white-glass

nc: 12
```

3. **Annotation format (YOLO):**
```
class_id center_x center_y width height
```
Ví dụ: `0 0.5 0.5 0.3 0.4` (battery ở giữa ảnh)

### Bước 2: Upload lên Google Colab

1. **Tạo notebook mới trên Colab**
2. **Upload dataset:**
   - Có thể upload trực tiếp
   - Hoặc upload lên Google Drive và mount

### Bước 3: Train Model

```python
# Install ultralytics
!pip install ultralytics

# Load model hiện tại từ Hugging Face
from ultralytics import YOLO

# Load pretrained model
model = YOLO('kendrickfff/waste-classification-yolov8-ken')

# Hoặc load từ local nếu đã download
# model = YOLO('yolov8n-waste-12cls-best.pt')

# Fine-tune với dataset của bạn
results = model.train(
    data='/content/dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='waste-classification-finetuned',
    project='runs/detect',
    pretrained=True,
    optimizer='AdamW',
    lr0=0.001,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    warmup_momentum=0.8,
    warmup_bias_lr=0.1,
    box=7.5,
    cls=0.5,
    dfl=1.5,
    pose=12.0,
    kobj=1.0,
    label_smoothing=0.0,
    nbs=64,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=0.0,
    translate=0.1,
    scale=0.5,
    shear=0.0,
    perspective=0.0,
    flipud=0.0,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.0,
    copy_paste=0.0
)

# Export model
model.export(format='pt')
```

### Bước 4: Download Model

```python
# Download model
from google.colab import files
files.download('runs/detect/waste-classification-finetuned/weights/best.pt')
```

### Bước 5: Test Model

```python
# Test model
results = model('/content/test_image.jpg')
results[0].show()

# Evaluate
metrics = model.val()
print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

## Option 2: Train từ Đầu (Không khuyến nghị)

### Bước 1: Chuẩn bị Dataset Lớn

- **Tối thiểu**: 1000+ ảnh
- **Khuyến nghị**: 2000+ ảnh
- **Đa dạng**: Nhiều điều kiện ánh sáng, góc chụp, môi trường

### Bước 2: Train từ YOLOv8n

```python
from ultralytics import YOLO

# Load YOLOv8n base model
model = YOLO('yolov8n.pt')

# Train từ đầu
results = model.train(
    data='/content/dataset/data.yaml',
    epochs=300,
    imgsz=640,
    batch=16,
    name='waste-classification-from-scratch',
    project='runs/detect'
)
```

## Tips và Best Practices

### 1. Dataset Quality
- ✅ Ảnh chất lượng cao
- ✅ Đa dạng về ánh sáng, góc chụp
- ✅ Annotation chính xác
- ✅ Cân bằng số lượng ảnh mỗi class

### 2. Training Parameters
- **Epochs**: 100-200 cho fine-tune, 300+ cho train từ đầu
- **Batch size**: 16-32 (tùy GPU memory)
- **Image size**: 640 (có thể tăng lên 1280 nếu GPU đủ mạnh)
- **Learning rate**: 0.001 (có thể điều chỉnh)

### 3. Validation
- Chia dataset: 80% train, 20% validation
- Monitor validation loss
- Early stopping nếu overfitting

### 4. Augmentation
- Horizontal flip
- Rotation
- Brightness/contrast adjustment
- Mosaic (cho YOLOv8)

## Troubleshooting

### Out of Memory
- Giảm batch size (16 → 8)
- Giảm image size (640 → 416)
- Sử dụng gradient accumulation

### Overfitting
- Tăng augmentation
- Tăng dropout
- Giảm learning rate
- Early stopping

### Low Accuracy
- Tăng số lượng ảnh
- Cải thiện annotation quality
- Tăng số epochs
- Tăng image size

## Export và Sử dụng

### Export Model
```python
# Export thành .pt
model.export(format='pt')

# Hoặc export thành .onnx, .tflite, etc.
model.export(format='onnx')
model.export(format='tflite')
```

### Sử dụng trong Backend
1. Download model từ Colab
2. Đặt vào `backend/models/best.pt`
3. Restart backend
4. Test trên app

## Kết luận

### Fine-tune (Khuyến nghị)
- ✅ Nhanh (1-2 giờ)
- ✅ Cần ít dataset (100-500 ảnh)
- ✅ Cải thiện accuracy đáng kể
- ✅ Giữ nguyên 12 classes

### Train từ Đầu
- ❌ Chậm (4-8 giờ)
- ❌ Cần dataset lớn (1000+ ảnh)
- ❌ Phức tạp hơn
- ✅ Kiểm soát hoàn toàn

## Next Steps

1. **Test model hiện tại** với rác thật
2. **Đánh giá kết quả** - xem `SHOULD_RETRAIN.md`
3. **Nếu cần train** → Follow hướng dẫn này
4. **Nếu không cần** → Giữ nguyên model hiện tại

## Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [YOLOv8 Training Guide](https://docs.ultralytics.com/modes/train/)
- [Google Colab](https://colab.research.google.com/)
- [Roboflow (Dataset annotation tool)](https://roboflow.com/)

