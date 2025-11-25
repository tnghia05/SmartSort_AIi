# Ước Tính Kích Thước Dataset

## Dataset "waste" by CavaAle

- **Số ảnh:** 28642 images
- **Format:** YOLO (images + labels)
- **Image size:** 640x640 (theo preprocessing)

## Ước tính kích thước

### Tính toán:

**Mỗi ảnh (640x640, JPEG quality 80-90%):**
- Kích thước trung bình: **50-150 KB** mỗi ảnh
- Với 28642 ảnh: **1.4 - 4.3 GB** chỉ riêng images

**Labels (YOLO format .txt):**
- Mỗi file .txt: **1-5 KB** (rất nhỏ)
- Với 28642 labels: **~30-150 MB**

**Tổng cộng:**
- **Images:** 1.4 - 4.3 GB
- **Labels:** ~30-150 MB
- **Metadata:** ~10-50 MB
- **TOTAL:** **~1.5 - 4.5 GB**

### Kích thước thực tế có thể:
- **Tối thiểu:** ~1.5 GB (nếu ảnh nén tốt)
- **Trung bình:** ~2-3 GB
- **Tối đa:** ~4-5 GB (nếu ảnh chất lượng cao)

## Lưu ý

### ⚠️ Dataset khá nặng!

1. **Cần đủ dung lượng ổ cứng:**
   - Ít nhất **5 GB** trống (để an toàn)
   - Tốt nhất **10 GB** trống

2. **Download sẽ lâu:**
   - Với tốc độ 10 Mbps: **~30-60 phút**
   - Với tốc độ 50 Mbps: **~6-12 phút**
   - Với tốc độ 100 Mbps: **~3-6 phút**

3. **Upload lên Colab:**
   - Upload 2-3 GB sẽ mất **10-30 phút**
   - Hoặc mount Google Drive (nhanh hơn)

## Giải pháp

### Option 1: Download đầy đủ (Khuyến nghị)

**Ưu điểm:**
- ✅ Đủ ảnh để train tốt
- ✅ Model sẽ chính xác hơn

**Nhược điểm:**
- ⚠️ Nặng (2-4 GB)
- ⚠️ Download lâu

### Option 2: Download một phần (Nếu thiếu dung lượng)

Có thể:
1. **Chỉ download train set** (19840 images) → ~1-2 GB
2. **Hoặc download sample** (5000-10000 images) → ~500 MB - 1 GB

**Cách làm:**
- Fork dataset
- Xóa một số ảnh trong val/test
- Export lại với ít ảnh hơn

### Option 3: Train trực tiếp trên Roboflow

**Ưu điểm:**
- ✅ Không cần download
- ✅ Train trên cloud (GPU free)
- ✅ Không tốn dung lượng máy

**Nhược điểm:**
- ⚠️ Cần tài khoản Roboflow Pro (có thể có giới hạn)
- ⚠️ Không kiểm soát hoàn toàn

## Khuyến nghị

### ✅ Nếu có đủ dung lượng (5+ GB):
- **Download đầy đủ** (28642 images)
- Train với toàn bộ dataset
- Model sẽ tốt nhất

### ⚠️ Nếu thiếu dung lượng:
- **Download train set** (19840 images) → ~1-2 GB
- Hoặc **download sample** (10000 images) → ~500 MB - 1 GB
- Vẫn đủ để train tốt

## Kiểm tra dung lượng

### Windows:
```powershell
# Kiểm tra dung lượng ổ C
Get-PSDrive C | Select-Object Used,Free
```

### Hoặc:
- Click chuột phải ổ C → Properties
- Xem dung lượng trống

## Next Steps

1. ✅ Kiểm tra dung lượng ổ cứng
2. ✅ Nếu đủ (5+ GB) → Download đầy đủ
3. ✅ Nếu thiếu → Download train set hoặc sample
4. ✅ Train model




