# Phân Tích Dataset: "Waste Classification" by Masks

## Thông tin Dataset

- **URL:** https://universe.roboflow.com/masks-fwspp/waste-classification-awlni
- **Số ảnh:** 4366 images
- **Classes:** 9 classes
- **License:** CC BY 4.0 (miễn phí sử dụng)
- **Format:** Classification (có thể có YOLO format)

## Classes trong Dataset

1. **Aluminium** → Map thành `metal`
2. **Carton** → Map thành `paper` (cardboard)
3. **E-waste** → Map thành `other`
4. **Glass** → Map thành `glass` (có thể là brown/green/white-glass)
5. **Organic_Waste** → Map thành `organic` (biological)
6. **Paper_and_Cardboard** → Map thành `paper`
7. **Plastics** → Map thành `plastic`
8. **Textiles** → Map thành `other` (clothes)
9. **Wood** → Map thành `other`

## So sánh với Model hiện tại

### Model cần 12 classes:
- battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass

### Dataset có 9 classes:
- Aluminium, Carton, E-waste, Glass, Organic_Waste, Paper_and_Cardboard, Plastics, Textiles, Wood

### Mapping:

| Dataset Class | Model Class | Ghi chú |
|---------------|-------------|---------|
| Aluminium | metal | ✅ Map trực tiếp |
| Carton | paper | ✅ Map trực tiếp (cardboard → paper) |
| E-waste | other | ✅ Map thành other |
| Glass | glass | ✅ Map trực tiếp (có thể là brown/green/white) |
| Organic_Waste | organic | ✅ Map trực tiếp (biological → organic) |
| Paper_and_Cardboard | paper | ✅ Map trực tiếp |
| Plastics | plastic | ✅ Map trực tiếp |
| Textiles | other | ✅ Map thành other (clothes → other) |
| Wood | other | ✅ Map thành other |

### Classes thiếu:
- ⚠️ **battery** - Không có riêng, nhưng có trong "E-waste" (pin được classify là E-waste)
- ❌ **shoes** - Không có trong dataset
- ❌ **trash** - Không có trong dataset
- ⚠️ **brown-glass, green-glass, white-glass** - Chỉ có "Glass" chung

### Lưu ý quan trọng:
- **Pin (battery)** được classify là **"E-waste"** trong dataset này
- Khi map, "E-waste" → "other" (vì không có class "battery" riêng)
- Nếu muốn detect pin riêng, cần dataset khác hoặc annotate lại

## Đánh giá

### ✅ Ưu điểm:
1. **Nhiều ảnh** (4366) - đủ để train
2. **Classes chính có đủ** - plastic, metal, paper, organic, glass
3. **License miễn phí** - CC BY 4.0
4. **Chất lượng tốt** - có nhiều views

### ⚠️ Nhược điểm:
1. **Thiếu 3 classes:** battery, shoes, trash
2. **Glass không phân loại** - không có brown/green/white-glass riêng
3. **Chỉ 9 classes** thay vì 12

## Giải pháp

### Option 1: Sử dụng dataset này (Khuyến nghị)
- ✅ Đủ cho các classes chính
- ✅ Có thể train và map classes
- ⚠️ Classes thiếu sẽ không được detect (battery, shoes, trash)

### Option 2: Combine với dataset khác
- Download dataset này
- Download thêm dataset có battery, shoes, trash
- Merge lại

### Option 3: Tìm dataset khác
- Tìm dataset có đủ 12 classes
- Hoặc tìm dataset có battery, shoes, trash để bổ sung

## Cách Download

### Thông tin từ URL:
```
https://universe.roboflow.com/masks-fwspp/waste-classification-awlni
```

**Phân tích URL:**
- Workspace: `masks-fwspp`
- Project: `waste-classification-awlni`
- Version: Cần click vào "Use this Dataset" để xem version

### Các bước:

1. **Click "Use this Dataset" button** (màu tím, góc trên bên phải)
2. **Chọn format:** YOLOv8 (nếu có)
3. **Xem version number** (thường là 1)
4. **Lấy API key:**
   - Đăng nhập Roboflow
   - Settings → API → Copy API key

5. **Download bằng script:**
```bash
cd backend
python download_dataset.py
# Chọn option 3 (Roboflow)
# Workspace: masks-fwspp
# Project: waste-classification-awlni
# Version: 1 (hoặc số version hiển thị)
# API Key: [paste API key]
```

## Mapping Classes trong Code

Sau khi download, cần cập nhật `WASTE_CLASS_MAPPING` trong `api.py`:

```python
WASTE_CLASS_MAPPING = {
    # Dataset classes → Model classes
    'aluminium': 'metal',
    'carton': 'paper',
    'e-waste': 'other',
    'glass': 'glass',  # Hoặc map thành brown-glass/green-glass/white-glass
    'organic_waste': 'organic',
    'paper_and_cardboard': 'paper',
    'plastics': 'plastic',
    'textiles': 'other',
    'wood': 'other',
    
    # Giữ nguyên các classes khác
    'battery': 'other',  # Sẽ không detect được vì không có trong dataset
    'shoes': 'other',    # Sẽ không detect được
    'trash': 'other',    # Sẽ không detect được
}
```

## Kết luận

### ✅ Nên sử dụng dataset này nếu:
- Bạn chấp nhận pin được detect là "E-waste" (other) thay vì "battery" riêng
- Bạn chấp nhận không detect được shoes, trash
- Các classes chính (plastic, metal, paper, organic, glass) là đủ
- Muốn train nhanh với dataset có sẵn (4366 images)

### ⚠️ Nên tìm dataset khác nếu:
- Cần detect pin riêng (battery class)
- Cần detect shoes, trash
- Cần phân biệt brown/green/white-glass
- Cần đầy đủ 12 classes như model hiện tại

## Next Steps

1. ✅ Click "Use this Dataset"
2. ✅ Chọn YOLOv8 format
3. ✅ Lấy thông tin workspace, project, version
4. ✅ Download bằng script
5. ✅ Cập nhật class mapping trong `api.py`

