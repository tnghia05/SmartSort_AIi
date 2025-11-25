# Kiểm tra Model hiện tại

## Vấn đề: Model chỉ detect "Khác" (Other)

Nếu app chỉ detect được "Khác" với confidence thấp, có nghĩa là:
1. **Backend đang dùng YOLOv8n mặc định** (model COCO dataset)
2. Model này không được train cho waste classification
3. Model trả về class names như "person", "laptop", "keyboard", "mouse", v.v.
4. Class mapping không match → tất cả thành "other"

## Cách kiểm tra

### 1. Kiểm tra model đang dùng:

```bash
curl http://localhost:8000/health
```

Response sẽ cho biết:
- `class_names`: Danh sách class names mà model hỗ trợ
- `is_waste_model`: `true` nếu là model waste classification, `false` nếu là COCO model

### 2. Xem log khi start backend:

Khi start backend, bạn sẽ thấy:
```
📋 Model classes: ['person', 'bicycle', 'car', ...]
📋 Total classes: 80
💡 Note: If model shows COCO classes (person, car, etc.), it's not a waste classification model.
```

Nếu thấy COCO classes → Model không phải waste classification model.

## Giải pháp

### Giải pháp 1: Download model waste classification từ Hugging Face

1. **Cài đặt huggingface_hub:**
```bash
pip install huggingface_hub
```

2. **Download model:**
```bash
cd backend
python download_waste_model.py
```

3. **Hoặc download thủ công:**
   - Truy cập: https://huggingface.co/kendrickfff/waste-classification-yolov8-ken
   - Download file `best.pt` hoặc `weights/best.pt`
   - Đặt vào `backend/models/best.pt`

4. **Cập nhật api.py:**
```python
model_paths = [
    'models/best.pt',  # Waste classification model
    'yolov8n.pt',  # Fallback
]
```

5. **Restart backend:**
```bash
python api.py
```

### Giải pháp 2: Fine-tune model với dataset của bạn

Xem `SETUP_MODEL.md` để biết cách fine-tune model.

### Giải pháp 3: Sử dụng model khác từ Hugging Face

Tìm model waste classification khác:
- https://huggingface.co/models?search=waste+classification+yolo
- https://huggingface.co/models?search=trash+detection

## Kiểm tra sau khi cập nhật

1. **Restart backend**
2. **Kiểm tra health endpoint:**
```bash
curl http://localhost:8000/health
```

3. **Kiểm tra class names:**
   - Nếu thấy: `['organic', 'plastic', 'metal', 'paper', 'other']` → ✅ Đúng model
   - Nếu thấy: `['person', 'bicycle', 'car', ...]` → ❌ Vẫn là COCO model

4. **Test detection:**
   - Gửi ảnh rác thải
   - Kiểm tra xem class có đúng không (không phải "other")

## Lưu ý

- Model waste classification sẽ lớn hơn YOLOv8n (có thể 50-200MB)
- Cần đủ RAM để load model (2-4GB)
- Model sẽ mất vài giây để load khi start backend
- Inference có thể chậm hơn một chút nhưng chính xác hơn nhiều

## Troubleshooting

### Model không download được
- Kiểm tra kết nối internet
- Kiểm tra quyền truy cập Hugging Face
- Thử download thủ công

### Model load nhưng vẫn trả về "other"
- Kiểm tra class names trong model
- Cập nhật `CLASS_MAPPING` trong `api.py`
- Kiểm tra confidence threshold (có thể quá cao)

### Model quá chậm
- Sử dụng YOLOv8n (nano) thay vì YOLOv8s/m/l/x
- Giảm image size: `model(image, imgsz=416)`
- Sử dụng GPU nếu có

