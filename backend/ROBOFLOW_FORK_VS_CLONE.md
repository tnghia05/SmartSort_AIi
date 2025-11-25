# Fork Dataset vs Clone Dataset - Nên chọn gì?

## Khi click "Use this Dataset"

Bạn sẽ thấy 2 options:
1. **Fork Dataset**
2. **Clone Dataset**

## Fork Dataset

### Là gì?
- Tạo bản copy của dataset trong workspace của bạn
- Bạn có thể **edit, annotate, và train** trên bản copy này
- Dataset gốc không bị ảnh hưởng

### Khi nào dùng?
- ✅ Muốn **sửa annotations** (ví dụ: sửa quần áo từ "biological" → "clothes")
- ✅ Muốn **thêm classes** mới
- ✅ Muốn **train và lưu model** trên Roboflow
- ✅ Muốn **quản lý dataset** trong workspace của bạn

### Cách dùng:
1. Click "Fork Dataset"
2. Dataset sẽ được copy vào workspace của bạn
3. Có thể edit annotations
4. Có thể train trực tiếp trên Roboflow

## Clone Dataset

### Là gì?
- Copy **images** vào một project khác của bạn
- Không tạo bản copy riêng của dataset
- Chỉ copy images để sử dụng

### Khi nào dùng?
- ✅ Muốn **download về máy** để train local/Colab
- ✅ Muốn **combine với dataset khác**
- ✅ Không cần edit annotations
- ✅ Chỉ cần images để train

### Cách dùng:
1. Click "Clone Dataset"
2. Chọn project đích (hoặc tạo mới)
3. Images sẽ được copy vào project đó
4. Có thể download từ project đó

## Khuyến nghị cho bạn

### ✅ Chọn "Fork Dataset" nếu:
- Muốn sửa annotations (quần áo → biological)
- Muốn train trên Roboflow
- Muốn quản lý dataset trong workspace

### ✅ Chọn "Clone Dataset" nếu:
- Chỉ muốn download về máy để train trên Colab
- Không cần sửa annotations
- Muốn train local

## Cách Download để Train trên Colab

### Option 1: Fork rồi Download (Khuyến nghị nếu muốn sửa)

1. **Fork Dataset:**
   - Click "Use this Dataset" → "Fork Dataset"
   - Dataset sẽ vào workspace của bạn

2. **Sửa annotations (nếu cần):**
   - Vào dataset đã fork
   - Sửa các annotations sai (quần áo → biological)

3. **Download:**
   - Vào dataset đã fork
   - Click "Download Dataset"
   - Chọn YOLOv8 format
   - Download về máy

### Option 2: Clone rồi Download (Nhanh hơn nếu không sửa)

1. **Clone Dataset:**
   - Click "Use this Dataset" → "Clone Dataset"
   - Chọn project đích (hoặc tạo mới)

2. **Download:**
   - Vào project đã clone
   - Click "Download Dataset"
   - Chọn YOLOv8 format
   - Download về máy

### Option 3: Download trực tiếp (Nhanh nhất - Khuyến nghị)

**Không cần Fork hay Clone!**

1. **Click "Use this Dataset"** → Chọn bất kỳ option nào
2. **Hoặc click "Download Dataset"** trực tiếp (nếu có button)
3. **Chọn YOLOv8 format**
4. **Download về máy**

Sau đó dùng script để download:
```bash
cd backend
python download_dataset.py
# Chọn option 3 (Roboflow)
# Workspace: cavaale
# Project: waste-es2rg
# Version: 1
```

## Khuyến nghị cuối cùng

### ✅ **Chọn "Fork Dataset"** nếu:
- Muốn sửa annotations sau này
- Muốn train trên Roboflow
- Muốn quản lý dataset

### ✅ **Hoặc download trực tiếp** (nhanh nhất):
- Click "Download Dataset" (nếu có button)
- Hoặc dùng script `download_dataset.py`
- Không cần Fork hay Clone

## Next Steps

Sau khi Fork/Clone hoặc Download:

1. ✅ Download dataset về máy
2. ✅ Validate: `python prepare_dataset.py`
3. ✅ Train: Xem `TRAIN_QUICK_START.md`

