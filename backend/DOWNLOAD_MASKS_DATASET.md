# Hướng Dẫn Download Dataset "Waste Classification" by Masks

## Thông tin Dataset

- **Workspace:** `masks-fwspp`
- **Project:** `waste-classification-awlni`
- **URL:** https://universe.roboflow.com/masks-fwspp/waste-classification-awlni
- **Số ảnh:** 4366 images
- **Classes:** 9 classes (Aluminium, Carton, E-waste, Glass, Organic_Waste, Paper_and_Cardboard, Plastics, Textiles, Wood)

## Lưu ý quan trọng

⚠️ **Pin (battery) được classify là "E-waste"** trong dataset này, không có class "battery" riêng.

Khi sử dụng:
- Pin sẽ được detect là "E-waste" → map thành "other"
- Không có class "battery" riêng như model hiện tại

## Các bước Download

### Bước 1: Lấy API Key

1. **Đăng nhập Roboflow:**
   - Click "Sign In" (góc trên bên phải)
   - Đăng nhập hoặc đăng ký tài khoản

2. **Lấy API Key:**
   - Click avatar (góc trên bên phải)
   - Chọn **Settings**
   - Vào tab **API**
   - Copy **API Key**

### Bước 2: Lấy thông tin Dataset

Từ URL hiện tại:
```
https://universe.roboflow.com/masks-fwspp/waste-classification-awlni
```

**Thông tin:**
- **Workspace:** `masks-fwspp`
- **Project:** `waste-classification-awlni`
- **Version:** Cần click "Use this Dataset" để xem (thường là 1)

### Bước 3: Click "Use this Dataset"

1. Click button **"Use this Dataset"** (màu tím, góc trên bên phải)
2. Chọn format: **YOLOv8** (nếu có)
3. Xem **version number** (thường là 1)

### Bước 4: Download bằng Script

```bash
cd backend
python download_dataset.py
```

**Nhập thông tin:**
```
Enter choice (1-4): 3
Enter Roboflow workspace: masks-fwspp
Enter project name: waste-classification-awlni
Enter version number: 1
Enter Roboflow API key: [paste API key]
Enter output directory (default: 'dataset'): dataset
```

### Bước 5: Kiểm tra Dataset

Sau khi download:

```bash
python prepare_dataset.py
```

Script sẽ:
- Validate structure
- Check image/label matching
- Generate data.yaml
- Show statistics

## Cập nhật Class Mapping

Sau khi download, cần cập nhật `WASTE_CLASS_MAPPING` trong `api.py`:

```python
WASTE_CLASS_MAPPING = {
    # Dataset classes → Model classes
    'aluminium': 'metal',
    'carton': 'paper',
    'e-waste': 'other',  # ⚠️ Pin được classify là E-waste, không có battery riêng
    'glass': 'glass',
    'organic_waste': 'organic',
    'paper_and_cardboard': 'paper',
    'plastics': 'plastic',
    'textiles': 'other',
    'wood': 'other',
    
    # Giữ nguyên các classes khác
    'battery': 'other',  # Sẽ không detect được (không có trong dataset)
    'shoes': 'other',    # Sẽ không detect được
    'trash': 'other',    # Sẽ không detect được
}
```

## Kết quả mong đợi

Sau khi train với dataset này:

### ✅ Sẽ detect được:
- **Plastic** (Plastics) → "Nhựa"
- **Metal** (Aluminium) → "Kim loại"
- **Paper** (Carton, Paper_and_Cardboard) → "Giấy"
- **Organic** (Organic_Waste) → "Hữu cơ"
- **Glass** (Glass) → "Thủy tinh"
- **Other** (E-waste, Textiles, Wood) → "Khác"

### ⚠️ Sẽ không detect được:
- **Battery** riêng (chỉ detect là E-waste → other)
- **Shoes** (không có trong dataset)
- **Trash** (không có trong dataset)

## Alternative: Nếu cần detect Battery riêng

Nếu cần detect pin riêng (không phải E-waste):

1. **Tìm dataset khác có class "battery"**
2. **Hoặc annotate lại:**
   - Download dataset này
   - Tách "E-waste" thành "battery" và "E-waste" khác
   - Annotate lại các ảnh pin

## Next Steps

1. ✅ Lấy API key
2. ✅ Download dataset
3. ✅ Validate dataset
4. ✅ Cập nhật class mapping
5. ✅ Train model (xem `TRAIN_QUICK_START.md`)

