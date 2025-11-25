# Nguồn Dataset Waste Classification

## Tổng quan

Bạn có thể tìm và download dataset waste classification từ nhiều nguồn trên mạng. Dưới đây là danh sách các nguồn phổ biến:

## 1. Roboflow (Khuyến nghị - Dễ nhất)

### Tại sao chọn Roboflow?
- ✅ **YOLO format sẵn có** - Không cần convert
- ✅ **Nhiều dataset** - Hàng trăm dataset waste classification
- ✅ **Dễ download** - Chỉ cần API key
- ✅ **Chất lượng cao** - Đã được annotate sẵn

### Cách download:

1. **Tạo tài khoản Roboflow:**
   - Truy cập: https://roboflow.com
   - Đăng ký tài khoản miễn phí

2. **Tìm dataset:**
   - Search: "waste classification" hoặc "trash"
   - Chọn dataset phù hợp (12 classes hoặc tương tự)

3. **Lấy API key:**
   - Vào Settings → API
   - Copy API key

4. **Download bằng script:**
```bash
cd backend
python download_dataset.py
# Chọn option 3 (Roboflow)
# Nhập workspace, project, version, API key
```

### Dataset phổ biến trên Roboflow:
- Waste Classification Dataset (various versions)
- Trash Detection Dataset
- Recyclable Waste Dataset

## 2. Kaggle

### Dataset phổ biến:

1. **TrashNet** (garythung/trashnet)
   - 6 classes: glass, paper, cardboard, plastic, metal, trash
   - Format: Images với folders
   - Cần convert sang YOLO format

2. **Cách download:**

```bash
# Cài đặt Kaggle API
pip install kaggle

# Setup credentials (xem hướng dẫn Kaggle)
# Download dataset
cd backend
python download_dataset.py
# Chọn option 2 (Kaggle)
# Nhập: garythung/trashnet
```

### Lưu ý:
- TrashNet không có YOLO format sẵn
- Cần convert sang YOLO format (xem `convert_dataset.py`)

## 3. Hugging Face Datasets

### Tìm dataset:
- Truy cập: https://huggingface.co/datasets
- Search: "waste classification" hoặc "trash"

### Download:
```bash
pip install datasets
cd backend
python download_dataset.py
# Chọn option 4 (Hugging Face)
```

## 4. GitHub Repositories

### TrashNet:
- **URL**: https://github.com/garythung/trashnet
- **Format**: Images với folders
- **Classes**: 6 classes
- **Cách download:**
```bash
git clone https://github.com/garythung/trashnet.git
cd trashnet/data
# Cần convert sang YOLO format
```

### TACO (Trash Annotations in Context):
- **URL**: http://tacodataset.org/
- **Format**: COCO format
- **Cần convert** sang YOLO format

## 5. Script tự động

Sử dụng script `download_dataset.py`:

```bash
cd backend
python download_dataset.py
```

Script hỗ trợ:
- Download từ Kaggle
- Download từ Roboflow (YOLO format ready)
- Download từ Hugging Face
- List available datasets

## 6. Convert Dataset sang YOLO Format

Nếu dataset không có YOLO format sẵn, sử dụng script convert:

```bash
cd backend
python convert_dataset.py
```

Script sẽ:
- Convert từ folder structure → YOLO format
- Convert từ COCO format → YOLO format
- Tạo data.yaml tự động

## Khuyến nghị

### Cho người mới bắt đầu:
1. **Roboflow** - Dễ nhất, YOLO format sẵn
2. Download dataset có 12 classes (phù hợp với model hiện tại)
3. Sử dụng script `download_dataset.py`

### Cho người có kinh nghiệm:
1. **Kaggle** - Nhiều dataset, cần convert
2. **TACO** - Dataset lớn, chất lượng cao
3. Combine nhiều dataset để tăng độ đa dạng

## Checklist Dataset

Dataset tốt cần có:
- [ ] Ít nhất 50-100 ảnh mỗi class
- [ ] YOLO format (hoặc có thể convert)
- [ ] 12 classes phù hợp (hoặc có thể map)
- [ ] Chất lượng ảnh tốt
- [ ] Đa dạng về ánh sáng, góc chụp

## Classes cần có

Model hiện tại hỗ trợ 12 classes:
1. battery
2. biological
3. brown-glass
4. cardboard
5. clothes
6. green-glass
7. metal
8. paper
9. plastic
10. shoes
11. trash
12. white-glass

Nếu dataset có classes khác, cần map hoặc train lại với classes mới.

## Next Steps

1. **Chọn nguồn dataset** (khuyến nghị: Roboflow)
2. **Download dataset** (sử dụng script)
3. **Kiểm tra format** (YOLO format)
4. **Convert nếu cần** (sử dụng convert script)
5. **Chuẩn bị train** (xem `TRAIN_QUICK_START.md`)

## Resources

- Roboflow: https://roboflow.com/datasets
- Kaggle: https://www.kaggle.com/datasets
- Hugging Face: https://huggingface.co/datasets
- TrashNet: https://github.com/garythung/trashnet
- TACO: http://tacodataset.org/

