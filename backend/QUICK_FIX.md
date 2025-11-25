# Quick Fix - Model Waste Classification

## ✅ Đã hoàn thành

1. **Download model waste classification:**
   - Model: `yolov8n-waste-12cls-best.pt` (48.84 MB)
   - Location: `backend/models/best.pt`
   - Classes: 12 classes (battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass)

2. **Cập nhật class mapping:**
   - `biological` → `organic`
   - `plastic` → `plastic`
   - `metal` → `metal`
   - `paper` → `paper`
   - `cardboard` → `paper`
   - `brown-glass`, `green-glass`, `white-glass` → `other`
   - `trash`, `battery`, `clothes`, `shoes` → `other`

3. **Backend đã được cấu hình:**
   - Model sẽ tự động load từ `models/best.pt`
   - Class mapping đã được cập nhật
   - API sẽ trả về classes đúng

## 🔄 Các bước tiếp theo

### 1. Restart Backend

**QUAN TRỌNG:** Backend đang chạy với model cũ (YOLOv8n). Cần restart để load model mới:

```bash
# Stop backend hiện tại (Ctrl+C)
# Restart backend
cd backend
python api.py
```

Bạn sẽ thấy:
```
Trying to load model: models/best.pt
✅ Model loaded successfully: models/best.pt

============================================================
Model loaded successfully!
============================================================
Model classes: ['battery', 'biological', 'brown-glass', 'cardboard', 'clothes', 'green-glass', 'metal', 'paper', 'plastic', 'shoes', 'trash', 'white-glass']
Total classes: 12
SUCCESS: This is a waste classification model!
Class mapping:
  - battery              -> other
  - biological           -> organic
  - brown-glass          -> other
  - cardboard            -> paper
  - clothes              -> other
  - green-glass          -> other
  - metal                -> metal
  - paper                -> paper
  - plastic              -> plastic
  - shoes                -> other
  - trash                -> other
  - white-glass          -> other
============================================================
```

### 2. Test API

```bash
curl http://localhost:8000/health
```

Response sẽ có:
```json
{
  "status": "ok",
  "model_loaded": true,
  "class_names": ["battery", "biological", "brown-glass", ...],
  "total_classes": 12,
  "is_waste_model": true
}
```

### 3. Test trên App

1. **Reload app trên device**
2. **Mở camera screen**
3. **Hướng camera vào rác thải**
4. **Kiểm tra classification:**
   - Phải thấy: `Hữu cơ`, `Nhựa`, `Kim loại`, `Giấy` (không phải chỉ "Khác")
   - Confidence phải cao hơn (> 50%)

## 🎯 Kết quả mong đợi

### Trước khi fix:
- Tất cả vật thể → "Khác"
- Confidence thấp (27%, 41%, 64%)
- Model: YOLOv8n (COCO dataset)

### Sau khi fix:
- Vật thể được phân loại đúng:
  - Rác hữu cơ → "Hữu cơ" (biological)
  - Chai nhựa → "Nhựa" (plastic)
  - Lon kim loại → "Kim loại" (metal)
  - Giấy, bìa carton → "Giấy" (paper, cardboard)
  - Thủy tinh, pin, quần áo → "Khác" (glass, battery, clothes)
- Confidence cao hơn (> 50%)
- Model: Waste classification model (12 classes)

## 📝 Lưu ý

1. **Model size:** 48.84 MB (lớn hơn YOLOv8n)
2. **Load time:** Model sẽ mất vài giây để load khi start backend
3. **Memory:** Cần đủ RAM (2-4GB) để load model
4. **Performance:** Inference có thể chậm hơn một chút nhưng chính xác hơn nhiều

## 🔍 Troubleshooting

### Model vẫn trả về "Khác"

1. **Kiểm tra model đã được load chưa:**
   ```bash
   curl http://localhost:8000/health
   ```
   - Nếu `is_waste_model: false` → Model chưa được load đúng
   - Kiểm tra log khi start backend

2. **Kiểm tra file model:**
   ```bash
   dir backend\models
   ```
   - Phải có file `best.pt`

3. **Kiểm tra class mapping:**
   - Xem log khi start backend
   - Kiểm tra mapping có đúng không

### Backend không start được

1. **Kiểm tra model file:**
   - File có tồn tại không
   - File có bị corrupt không
   - Thử download lại

2. **Kiểm tra RAM:**
   - Model cần ~2-4GB RAM
   - Đóng các ứng dụng khác nếu cần

3. **Kiểm tra log:**
   - Xem error message cụ thể
   - Kiểm tra ultralytics version

## ✅ Checklist

- [x] Model đã được download
- [x] Class mapping đã được cập nhật
- [x] Backend đã được cấu hình
- [ ] Backend đã được restart
- [ ] Model đã được load thành công
- [ ] API trả về classes đúng
- [ ] App phân loại rác thải chính xác

## 🚀 Next Steps

Sau khi model hoạt động:
1. Test với nhiều loại rác thải khác nhau
2. Điều chỉnh confidence threshold nếu cần
3. Fine-tune model với dataset của bạn (nếu cần)
4. Deploy backend lên cloud

