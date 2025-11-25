# Hướng dẫn Start Backend với Model Waste Classification

## ✅ Model đã được download

- Model file: `backend/models/best.pt` (48.84 MB)
- Model classes: 12 classes (battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass)
- Class mapping: Đã được cấu hình

## 🚀 Các bước start backend

### 1. Stop backend hiện tại (nếu đang chạy)

Nhấn `Ctrl+C` trong terminal đang chạy backend.

### 2. Start backend mới

```bash
cd backend
python api.py
```

### 3. Kiểm tra model đã được load

Bạn sẽ thấy log như sau:
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

INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. Test API

Mở trình duyệt hoặc dùng curl:
```bash
curl http://localhost:8000/health
```

Response phải có:
```json
{
  "status": "ok",
  "model_loaded": true,
  "class_names": ["battery", "biological", "brown-glass", ...],
  "total_classes": 12,
  "is_waste_model": true
}
```

## ✅ Kết quả mong đợi

### Trước (với YOLOv8n):
- Classes: person, laptop, keyboard, mouse, car, ...
- Tất cả → "Khác"
- Confidence thấp

### Sau (với waste model):
- Classes: battery, biological, cardboard, metal, paper, plastic, ...
- Phân loại đúng: organic, plastic, metal, paper, other
- Confidence cao hơn

## 🔄 Test trên App

1. **Reload app trên device**
2. **Mở camera screen**
3. **Hướng camera vào rác thải:**
   - Chai nhựa → "Nhựa" (plastic)
   - Lon kim loại → "Kim loại" (metal)
   - Giấy, bìa carton → "Giấy" (paper, cardboard)
   - Rác hữu cơ → "Hữu cơ" (biological)
   - Thủy tinh, pin → "Khác" (glass, battery)
4. **Kiểm tra confidence:**
   - Phải cao hơn (> 50%)
   - Không còn thấy "Khác" với confidence thấp

## 🎯 Class Mapping

| Model Class | App Class | Label |
|-------------|-----------|-------|
| biological | organic | Hữu cơ |
| plastic | plastic | Nhựa |
| metal | metal | Kim loại |
| paper | paper | Giấy |
| cardboard | paper | Giấy |
| brown-glass, green-glass, white-glass | other | Khác |
| trash, battery, clothes, shoes | other | Khác |

## 📝 Lưu ý

1. **Model size:** 48.84 MB - cần vài giây để load
2. **Memory:** Cần ~2-4GB RAM
3. **Performance:** Inference có thể chậm hơn YOLOv8n một chút nhưng chính xác hơn nhiều
4. **Confidence:** Đã được điều chỉnh để phù hợp với waste model

## 🔍 Troubleshooting

### Model không load được

- Kiểm tra file `backend/models/best.pt` có tồn tại không
- Kiểm tra file size (phải ~48 MB)
- Xem log để biết lỗi cụ thể

### Vẫn trả về "Khác"

- Kiểm tra model đã được load đúng chưa (xem log)
- Kiểm tra class mapping có đúng không
- Test với ảnh rác thải rõ ràng
- Kiểm tra confidence threshold (có thể cần điều chỉnh)

### Backend chậm

- Model waste classification lớn hơn YOLOv8n
- Inference sẽ chậm hơn một chút
- Có thể giảm image size hoặc sử dụng GPU

