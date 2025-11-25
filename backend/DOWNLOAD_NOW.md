# Hướng Dẫn Download Dataset Ngay

## Dataset: "waste" by CavaAle

- **Workspace:** `cavaale`
- **Project:** `waste-es2rg`
- **Version:** `1`
- **Kích thước:** ~2-4 GB
- **Output:** Ổ E (đủ dung lượng)

## Bước 1: Lấy Roboflow API Key

1. **Đăng nhập Roboflow:**
   - Vào: https://app.roboflow.com
   - Đăng nhập hoặc đăng ký

2. **Lấy API Key:**
   - Click avatar (góc trên bên phải)
   - Settings → API
   - Copy API Key

## Bước 2: Download Dataset

### Cách 1: Dùng Script (Khuyến nghị)

```bash
cd E:\Code\rac\backend
python download_dataset.py
```

**Nhập thông tin:**
```
Enter choice (1-4): 3
Enter Roboflow workspace: cavaale
Enter project name: waste-es2rg
Enter version number: 1
Enter Roboflow API key: [paste API key của bạn]
Enter output directory (default: 'dataset'): E:\Code\rac\backend\dataset
```

### Cách 2: Download trực tiếp (Nếu script lỗi)

1. **Vào Roboflow:**
   - https://universe.roboflow.com/cavaale/waste-es2rg
   - Click "Use this Dataset" → "Fork Dataset" (hoặc "Clone Dataset")

2. **Download:**
   - Vào dataset đã fork/clone
   - Click "Download Dataset"
   - Chọn format: **YOLOv8**
   - Download về: `E:\Code\rac\backend\dataset`

## Bước 3: Kiểm tra Dataset

Sau khi download xong:

```bash
cd E:\Code\rac\backend
python prepare_dataset.py
```

Script sẽ:
- ✅ Validate cấu trúc dataset
- ✅ Kiểm tra images/labels matching
- ✅ Tạo `data.yaml` nếu thiếu
- ✅ Hiển thị thống kê

## Bước 4: Train Model

Sau khi dataset OK, train model:

### Option A: Train trên Google Colab (Khuyến nghị)

1. **Upload dataset lên Google Drive:**
   - Tạo folder `waste_dataset` trong Drive
   - Upload folder `dataset` vào đó

2. **Mở Colab notebook:**
   - `backend/train_waste_model_colab.ipynb`
   - Hoặc tạo mới trên Colab

3. **Mount Drive và train:**
   - Xem hướng dẫn trong `TRAIN_QUICK_START.md`

### Option B: Train local (Nếu có GPU)

```bash
cd E:\Code\rac\backend
python train_waste_model.py
```

## Lưu ý

- ⚠️ Download sẽ mất **10-30 phút** (tùy tốc độ mạng)
- ⚠️ Dataset nặng **~2-4 GB**
- ✅ Ổ E đủ dung lượng
- ✅ Sau khi download, có thể xóa để tiết kiệm dung lượng (sau khi train xong)

## Next Steps

1. ✅ Download dataset → `E:\Code\rac\backend\dataset`
2. ✅ Validate: `python prepare_dataset.py`
3. ✅ Train: Xem `TRAIN_QUICK_START.md`




