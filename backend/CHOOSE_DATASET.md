# Hướng Dẫn Chọn Dataset Waste Classification

## Tiêu chí chọn dataset

1. **Số lượng ảnh:** Càng nhiều càng tốt (tối thiểu 1000+)
2. **Số classes:** Phù hợp với 12 classes của model hiện tại
3. **Có model sẵn:** Dataset có model đã train sẵn (bonus)
4. **YOLO format:** Dataset có YOLO format sẵn

## Phân tích các dataset trong kết quả

### Dataset 1: "Waste" by IPCVHome
- **Ảnh:** 1160 images
- **Model:** Có (1 model)
- **Tags:** CardboardBoxes, GlassBottles, GlassJars
- **Đánh giá:** ⚠️ Ít classes, có thể không đủ 12 classes

### Dataset 2: "Waste Classification" by Masks
- **Ảnh:** 4366 images
- **Model:** Không
- **Tags:** Aluminium, Carton, E-waste, Glass, C...
- **Đánh giá:** ✅ Nhiều ảnh, có nhiều classes

### Dataset 3: "Waste Classi" by bottle
- **Ảnh:** 3353 images
- **Model:** Không
- **Tags:** can, Color Glass Bottles, HDPE, PET
- **Đánh giá:** ⚠️ Ít classes (chủ yếu về chai lọ)

### Dataset 4: "Waste Classification" by GaCha ⭐ (Khuyến nghị)
- **Ảnh:** 9161 images (NHIỀU NHẤT)
- **Model:** Có (1 model)
- **Tags:** Metallic Waste, Organic Waste, Paper Wa...
- **Đánh giá:** ✅✅ Tốt nhất - nhiều ảnh, có model, nhiều classes

## Khuyến nghị: Dataset 4 (by GaCha)

**Lý do:**
1. ✅ **Nhiều ảnh nhất** (9161) - đủ để train tốt
2. ✅ **Có model sẵn** - có thể tham khảo
3. ✅ **Nhiều classes** - Metallic, Organic, Paper, và có thể có thêm
4. ✅ **Chất lượng cao** - có model nghĩa là đã được test

## Cách kiểm tra dataset

Khi click vào dataset, kiểm tra:

1. **Classes:** Xem có đủ 12 classes không:
   - battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass

2. **Format:** Xem có YOLO format không (thường có sẵn)

3. **Split:** Xem có train/val split chưa

4. **License:** Kiểm tra license có cho phép sử dụng không

## Các bước tiếp theo

### Bước 1: Click vào dataset (khuyến nghị: Dataset 4 by GaCha)

### Bước 2: Kiểm tra thông tin
- Xem danh sách classes
- Xem số lượng ảnh mỗi class
- Xem format (YOLO)

### Bước 3: Lấy thông tin từ URL
URL sẽ có dạng:
```
https://universe.roboflow.com/[workspace]/[project]/[version]
```

Ví dụ:
```
https://universe.roboflow.com/gacha/waste-classification/1
```

Trong đó:
- **Workspace:** `gacha` (tên creator)
- **Project:** `waste-classification` (tên project)
- **Version:** `1` (số version)

### Bước 4: Lấy API Key
1. Đăng nhập Roboflow (nếu chưa)
2. Click avatar → Settings → API
3. Copy API key

### Bước 5: Download
```bash
cd backend
python download_dataset.py
# Chọn option 3 (Roboflow)
# Nhập thông tin từ URL
```

## Alternative: Nếu dataset không phù hợp

Nếu dataset không có đủ 12 classes, có thể:

1. **Combine nhiều dataset:**
   - Download dataset 4 (nhiều ảnh)
   - Download thêm dataset khác (bổ sung classes)
   - Merge lại

2. **Sử dụng Kaggle:**
   - TrashNet (6 classes)
   - Cần convert format

3. **Tạo dataset riêng:**
   - Thu thập ảnh
   - Annotate bằng LabelImg

## Next Steps

1. ✅ Click vào dataset 4 (by GaCha)
2. ✅ Kiểm tra classes và format
3. ✅ Lấy thông tin từ URL
4. ✅ Download bằng script

