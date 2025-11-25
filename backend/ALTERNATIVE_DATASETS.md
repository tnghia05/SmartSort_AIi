# Alternative Dataset Sources - Nếu Roboflow không truy cập được

## Vấn đề: Roboflow Page Not Found

Nếu gặp lỗi "Page Not Found" khi truy cập Roboflow, thử các cách sau:

## Giải pháp 1: Sử dụng Roboflow Universe

**URL đúng:** https://universe.roboflow.com

1. Truy cập: https://universe.roboflow.com
2. Search: "waste classification"
3. Chọn dataset phù hợp

## Giải pháp 2: Tìm Dataset trực tiếp qua Google

**Search terms:**
- "roboflow waste classification dataset"
- "roboflow trash detection yolo"
- "waste classification yolo dataset"

**Kết quả sẽ dẫn đến:**
- universe.roboflow.com/...
- Các dataset có sẵn với YOLO format

## Giải pháp 3: Sử dụng Kaggle (Không cần API phức tạp)

### Dataset: TrashNet

1. **Truy cập:** https://www.kaggle.com/datasets/garythung/trashnet
2. **Download:**
   - Click "Download" button
   - Extract file zip
   - Dataset có 6 classes: glass, paper, cardboard, plastic, metal, trash

3. **Convert sang YOLO format:**
   - Sử dụng script convert (sẽ tạo sau)
   - Hoặc annotate lại bằng tool như LabelImg

### Dataset khác trên Kaggle

Search: "waste classification" trên Kaggle
- Nhiều dataset miễn phí
- Cần convert format nếu không có YOLO

## Giải pháp 4: Sử dụng Hugging Face

1. **Truy cập:** https://huggingface.co/datasets
2. **Search:** "waste classification"
3. **Download:**
```bash
pip install datasets
python download_dataset.py
# Chọn option 4 (Hugging Face)
```

## Giải pháp 5: Download Dataset có sẵn từ GitHub

### TrashNet (GitHub)

1. **Clone repository:**
```bash
git clone https://github.com/garythung/trashnet.git
cd trashnet/data
```

2. **Cấu trúc:**
```
data/
├── glass/
├── paper/
├── cardboard/
├── plastic/
├── metal/
└── trash/
```

3. **Convert sang YOLO:**
- Cần annotate lại (không có bounding boxes)
- Hoặc sử dụng classification thay vì detection

## Giải pháp 6: Tạo Dataset riêng

Nếu không tìm được dataset phù hợp:

1. **Thu thập ảnh:**
   - Chụp ảnh rác thật
   - Tối thiểu 50-100 ảnh mỗi class

2. **Annotate:**
   - Sử dụng LabelImg: https://github.com/HumanSignal/labelImg
   - Format: YOLO
   - Classes: 12 classes (battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass)

3. **Chuẩn bị:**
```bash
python prepare_dataset.py
```

## Khuyến nghị

### Nếu có thể truy cập Roboflow:
1. ✅ Sử dụng Roboflow Universe (https://universe.roboflow.com)
2. ✅ YOLO format sẵn có
3. ✅ Dễ download

### Nếu không truy cập được Roboflow:
1. ✅ Sử dụng Kaggle (TrashNet)
2. ⚠️ Cần convert format
3. ⚠️ Hoặc tạo dataset riêng

## Quick Start với Kaggle

```bash
# Cài đặt Kaggle API
pip install kaggle

# Setup credentials (xem hướng dẫn Kaggle)
# Download TrashNet
cd backend
python download_dataset.py
# Chọn option 2 (Kaggle)
# Nhập: garythung/trashnet
```

## Next Steps

Sau khi có dataset:
1. Validate: `python prepare_dataset.py`
2. Train: Xem `TRAIN_QUICK_START.md`

