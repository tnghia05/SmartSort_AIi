# Quick Start Guide - Train Waste Classification Model

## Tổng quan

Hướng dẫn nhanh 5 bước để train model waste classification. Có 2 options:
1. **Google Colab Web** (truyền thống)
2. **Cursor với Colab Extension** (tiện hơn - khuyến nghị)

## Prerequisites

- [ ] Dataset đã chuẩn bị (xem `DATASET_SOURCES.md`)
- [ ] Google Colab account (free)
- [ ] Cursor với Colab extension (nếu dùng Option 2)

## Option 1: Train trên Google Colab Web

### Bước 1: Chuẩn bị Dataset

**Nếu chưa có dataset:**
```bash
cd backend
python download_dataset.py
# Chọn nguồn (Roboflow khuyến nghị)
```

**Nếu đã có dataset:**
```bash
cd backend
python prepare_dataset.py
# Validate và generate data.yaml
```

### Bước 2: Mở Google Colab

1. Truy cập: https://colab.research.google.com/
2. Tạo notebook mới
3. Upload file `backend/train_waste_model_colab.ipynb` (nếu có)
   - Hoặc copy code từ `TRAIN_MODEL_COLAB.md`

### Bước 3: Upload Dataset

**Cách 1: Upload trực tiếp**
- Click folder icon → Upload
- Upload toàn bộ thư mục `dataset/`

**Cách 2: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
# Copy dataset từ Drive
```

### Bước 4: Chạy Training

Chạy các cells trong notebook:
1. Install ultralytics
2. Load pretrained model
3. Configure training
4. Start training (1-2 giờ)

### Bước 5: Download Model

```python
from google.colab import files
files.download('runs/detect/waste-classification-finetuned/weights/best.pt')
```

## Option 2: Train trên Cursor với Colab Extension (Khuyến nghị)

### Bước 1: Cài Colab Extension

1. Mở Cursor
2. Extensions → Search "Colab"
3. Install "Colab" extension (Google)
4. Extension đã được cài sẵn nếu bạn thấy trong VS Code

### Bước 2: Mở Notebook

1. Mở file `backend/train_waste_model_colab.ipynb` trong Cursor
2. Click "Connect to Colab" (tự động hiện khi mở .ipynb)
3. Chọn Colab server (tự động connect)

### Bước 3: Upload Dataset

**Cách 1: Upload trực tiếp trong notebook**
- Click upload button trong Colab cell
- Upload thư mục `dataset/`

**Cách 2: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
```

**Cách 3: Clone từ GitHub (nếu dataset trên GitHub)**
```python
!git clone https://github.com/your-repo/dataset.git
```

### Bước 4: Chạy Training

1. Chạy cell đầu tiên (Setup)
2. Chạy cell load model
3. Chạy cell upload dataset
4. Chạy cell training (1-2 giờ)
5. Monitor progress trong Cursor

### Bước 5: Download Model

**Cách 1: Download trực tiếp**
```python
from google.colab import files
files.download('runs/detect/waste-classification-finetuned/weights/best.pt')
```

**Cách 2: Copy về local**
- Model sẽ được download về máy
- Di chuyển vào `backend/models/best.pt`

## Checklist Dataset

Trước khi train, đảm bảo:

- [ ] Dataset có YOLO format
- [ ] Ít nhất 50-100 ảnh mỗi class
- [ ] Có file `data.yaml`
- [ ] Images và labels match
- [ ] Annotations valid (0-1 normalized)

**Kiểm tra:**
```bash
cd backend
python prepare_dataset.py
```

## Training Parameters

### Fine-tune (Khuyến nghị):
- **Epochs**: 100
- **Batch size**: 16
- **Image size**: 640
- **Learning rate**: 0.001

### Train từ đầu:
- **Epochs**: 300
- **Batch size**: 16
- **Image size**: 640

## Sau khi Train

### 1. Test Model

```python
# Test với ảnh mẫu
results = model('/content/test_image.jpg')
results[0].show()

# Evaluate
metrics = model.val()
print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

### 2. Download Model

Download `best.pt` về máy

### 3. Sử dụng trong Backend

```bash
# Copy model vào backend
cp best.pt backend/models/best.pt

# Restart backend
cd backend
python api.py
```

### 4. Test trên App

1. Reload app trên device
2. Test với rác thật
3. So sánh với model cũ

## Troubleshooting

### Out of Memory
- Giảm batch size: `batch=8`
- Giảm image size: `imgsz=416`

### Training quá chậm
- Kiểm tra GPU đã được enable chưa
- Giảm số epochs nếu chỉ fine-tune

### Model không tốt
- Tăng số lượng ảnh
- Tăng số epochs
- Cải thiện annotation quality

## Next Steps

1. ✅ Train model
2. ✅ Download model
3. ✅ Test trên backend
4. ✅ Test trên app
5. ✅ So sánh với model cũ

## Resources

- **Dataset Sources**: `DATASET_SOURCES.md`
- **Full Training Guide**: `TRAIN_MODEL_COLAB.md`
- **Dataset Preparation**: `prepare_dataset.py`
- **Download Dataset**: `download_dataset.py`

## Tips

1. **Bắt đầu với dataset nhỏ** (50-100 ảnh/class) để test
2. **Fine-tune từ model hiện tại** thay vì train từ đầu
3. **Monitor training** để tránh overfitting
4. **Test thường xuyên** với validation set
5. **Save checkpoints** để có thể resume training

