# Hướng dẫn Setup Model YOLOv8 từ Hugging Face

## Cách 1: Tải model từ Hugging Face và load trực tiếp

### Bước 1: Tải model từ Hugging Face

Model `kendrickfff/waste-classification-yolov8-ken` có thể được tải từ Hugging Face. Tuy nhiên, Ultralytics YOLO có thể không hỗ trợ load trực tiếp từ Hugging Face model ID.

### Bước 2: Tải model file (.pt) từ Hugging Face

1. Truy cập: https://huggingface.co/kendrickfff/waste-classification-yolov8-ken
2. Tải file model (thường là `best.pt` hoặc `weights/best.pt`)
3. Đặt file model vào thư mục `backend/models/`
4. Cập nhật `api.py` để load model từ file:

```python
model = YOLO('models/best.pt')
```

### Bước 3: Sử dụng YOLOv8 mặc định (Fallback)

Nếu không tải được model từ Hugging Face, API sẽ tự động fallback sang YOLOv8n (nano) mặc định. Model này sẽ được download tự động lần đầu tiên.

**Lưu ý:** YOLOv8n mặc định không được train cho waste classification, nên kết quả sẽ không chính xác. Bạn cần fine-tune model hoặc sử dụng model đã được train sẵn.

## Cách 2: Fine-tune YOLOv8 với dataset của bạn

### Bước 1: Chuẩn bị dataset

1. Chuẩn bị dataset với format YOLO:
   ```
   dataset/
   ├── images/
   │   ├── train/
   │   ├── val/
   │   └── test/
   └── labels/
       ├── train/
       ├── val/
       └── test/
   ```

2. Tạo file `dataset.yaml`:
```yaml
path: /path/to/dataset
train: images/train
val: images/val
test: images/test

names:
  0: organic
  1: plastic
  2: metal
  3: paper
  4: other
```

### Bước 2: Fine-tune model

```python
from ultralytics import YOLO

# Load pre-trained YOLOv8 model
model = YOLO('yolov8n.pt')

# Fine-tune với dataset của bạn
model.train(
    data='dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='waste_classification'
)

# Save model
model.save('models/waste_classification.pt')
```

### Bước 3: Load model trong API

```python
model = YOLO('models/waste_classification.pt')
```

## Cách 3: Sử dụng Google Colab để fine-tune

Xem file `COLAB_FINETUNE_GUIDE.md` (sẽ được tạo sau) để biết hướng dẫn chi tiết.

## Troubleshooting

### Model không load được từ Hugging Face

- Kiểm tra kết nối internet
- Thử tải model file (.pt) trực tiếp từ Hugging Face
- Sử dụng model YOLOv8 mặc định làm fallback

### Model load nhưng không detect được đúng class

- Kiểm tra class names trong model có khớp với mapping trong `api.py`
- Cập nhật `CLASS_MAPPING` trong `api.py` để map đúng class names
- Fine-tune model với dataset của bạn

### Model quá nặng, chạy chậm

- Sử dụng YOLOv8n (nano) thay vì YOLOv8s/m/l/x
- Giảm image size trong inference: `model(image, imgsz=416)`
- Sử dụng GPU để tăng tốc (nếu có)

## Model Classes

Model nên có các class sau:
- `organic` - Rác hữu cơ
- `plastic` - Nhựa
- `metal` - Kim loại
- `paper` - Giấy
- `other` - Khác

Nếu model có class names khác, cần cập nhật `CLASS_MAPPING` trong `api.py`.

