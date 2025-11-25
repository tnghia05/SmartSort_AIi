# Hướng Dẫn Download Dataset "waste" by CavaAle

## Thông tin Dataset

- **Workspace:** `cavaale`
- **Project:** `waste-es2rg`
- **URL:** https://universe.roboflow.com/cavaale/waste-es2rg
- **Số ảnh:** **28642 images** (RẤT NHIỀU!)
- **Classes:** 6 classes (biological, glass, metal, paper, plastic, trash)
- **Split:** Train (19840), Val (5929), Test (2873)

## Lưu ý về Annotation

⚠️ **Đã phát hiện:**
- Một số quần áo (clothes) được label là "biological"
- Có thể có annotations không chính xác

**Nhưng:**
- Với 28642 images, số lượng annotations sai sẽ không ảnh hưởng nhiều
- Model vẫn sẽ học tốt từ đa số annotations đúng
- Có thể review và filter sau khi download nếu cần

## Các bước Download

### Bước 1: Lấy API Key

1. **Đăng nhập Roboflow:**
   - Click "Sign In" (góc trên bên phải)
   - Đăng nhập hoặc đăng ký

2. **Lấy API Key:**
   - Click avatar → Settings → API
   - Copy API Key

### Bước 2: Lấy thông tin Dataset

Từ URL:
```
https://universe.roboflow.com/cavaale/waste-es2rg
```

**Thông tin:**
- **Workspace:** `cavaale`
- **Project:** `waste-es2rg`
- **Version:** `1` (xem trong "Versions" section)

### Bước 3: Click "Use this Dataset"

1. Click button **"Use this Dataset"** (màu tím, góc trên bên phải)
2. Chọn format: **YOLOv8**
3. Xem **version number** (thường là 1)

### Bước 4: Download bằng Script

```bash
cd backend
python download_dataset.py
```

**Nhập thông tin:**
```
Enter choice (1-4): 3
Enter Roboflow workspace: cavaale
Enter project name: waste-es2rg
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

Mapping đơn giản vì dataset có đúng 6 classes chính:

```python
WASTE_CLASS_MAPPING = {
    # Dataset classes → Model classes (6 classes chính)
    'biological': 'organic',
    'glass': 'glass',
    'metal': 'metal',
    'paper': 'paper',
    'plastic': 'plastic',
    'trash': 'other',
    
    # Classes không có trong dataset
    'battery': 'other',
    'cardboard': 'paper',  # Có thể map từ paper
    'clothes': 'other',
    'shoes': 'other',
    'brown-glass': 'glass',
    'green-glass': 'glass',
    'white-glass': 'glass',
}
```

## Kết quả mong đợi

Với **28642 images**, model sẽ detect RẤT TỐT:

### ✅ Sẽ detect tốt:
- **Biological** → "Hữu cơ" (nhiều ảnh)
- **Glass** → "Thủy tinh" (nhiều ảnh)
- **Metal** → "Kim loại" (nhiều ảnh)
- **Paper** → "Giấy" (nhiều ảnh)
- **Plastic** → "Nhựa" (nhiều ảnh)
- **Trash** → "Khác" (nhiều ảnh)

### ⚠️ Sẽ không detect được:
- Battery (không có trong dataset)
- Clothes (không có, và một số được label sai là biological)
- Shoes (không có)

## Review Annotations (Tùy chọn)

Sau khi download, có thể review:

1. **Tìm ảnh quần áo:**
   - Search trong dataset: "clothes" hoặc "textile"
   - Kiểm tra xem có được label là "biological" không

2. **Filter nếu cần:**
   - Có thể filter bỏ một số annotations sai
   - Hoặc sửa lại labels

3. **Hoặc chấp nhận:**
   - Với 29k images, số lượng sai sẽ không ảnh hưởng nhiều
   - Model vẫn sẽ học tốt

## Next Steps

1. ✅ Lấy API key
2. ✅ Download dataset (28642 images - sẽ mất vài phút)
3. ✅ Validate dataset
4. ✅ Review annotations (tùy chọn)
5. ✅ Train model (xem `TRAIN_QUICK_START.md`)

## Ước tính thời gian

- **Download:** 5-10 phút (tùy tốc độ mạng)
- **Validate:** 1-2 phút
- **Train:** 2-4 giờ (với 29k images, cần nhiều thời gian hơn)

## Lưu ý

- Dataset lớn (29k images) nên download sẽ lâu hơn
- Cần đủ dung lượng ổ cứng (ước tính 2-5 GB)
- Training sẽ mất nhiều thời gian hơn (2-4 giờ thay vì 1-2 giờ)

