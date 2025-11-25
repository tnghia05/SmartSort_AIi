# Hướng dẫn Download Model Waste Classification

## Vấn đề hiện tại

Backend đang sử dụng **YOLOv8n mặc định** (COCO dataset) thay vì model waste classification, nên:
- Không phân loại được rác thải đúng cách
- Tất cả vật thể đều thành "Khác" (Other)
- Cần model được train cho waste classification

## Giải pháp: Download Model Waste Classification

### Cách 1: Sử dụng script tự động (Khuyến nghị)

1. **Cài đặt huggingface_hub:**
```bash
cd backend
pip install huggingface-hub
```

2. **Chạy script download:**
```bash
python download_waste_model.py
```

Script sẽ:
- Tự động tạo thư mục `models/`
- Download model từ Hugging Face
- Lưu vào `models/best.pt`

3. **Kiểm tra model đã download:**
```bash
dir models
# Hoặc
ls models
```

4. **Restart backend:**
```bash
python api.py
```

Backend sẽ tự động load model từ `models/best.pt`.

### Cách 2: Download thủ công

1. **Truy cập Hugging Face:**
   - Mở: https://huggingface.co/kendrickfff/waste-classification-yolov8-ken
   - Đăng nhập (nếu cần)

2. **Download model file:**
   - Tìm file `.pt` (thường là `best.pt` hoặc trong thư mục `weights/`)
   - Click "Download" để tải file

3. **Đặt file vào project:**
   - Tạo thư mục `backend/models/` (nếu chưa có)
   - Đặt file model vào `backend/models/best.pt`

4. **Restart backend:**
```bash
cd backend
python api.py
```

### Cách 3: Sử dụng Git LFS (nếu repository hỗ trợ)

```bash
cd backend
git lfs install
git clone https://huggingface.co/kendrickfff/waste-classification-yolov8-ken models/waste-model
# Sau đó update api.py để load từ models/waste-model/best.pt
```

## Kiểm tra Model

### 1. Kiểm tra model đã được load:

Restart backend và xem log:
```
Trying to load model: models/best.pt
✅ Model loaded successfully: models/best.pt

📋 Model classes: ['organic', 'plastic', 'metal', 'paper', 'other']
📋 Total classes: 5
```

Nếu thấy classes như trên → ✅ Model đúng!

Nếu thấy:
```
📋 Model classes: ['person', 'bicycle', 'car', ...]
📋 Total classes: 80
```
→ ❌ Vẫn là COCO model, cần download lại.

### 2. Kiểm tra qua API:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "class_names": ["organic", "plastic", "metal", "paper", "other"],
  "total_classes": 5,
  "is_waste_model": true
}
```

Nếu `is_waste_model: true` → ✅ Model đúng!

## Troubleshooting

### Model không download được

**Lỗi: "huggingface_hub is not installed"**
```bash
pip install huggingface-hub
```

**Lỗi: "Repository not found"**
- Kiểm tra repository ID: `kendrickfff/waste-classification-yolov8-ken`
- Kiểm tra kết nối internet
- Thử download thủ công

**Lỗi: "File not found"**
- Kiểm tra tên file trong repository
- Thử các tên file khác: `best.pt`, `weights/best.pt`, `runs/detect/train/weights/best.pt`
- Download thủ công từ Hugging Face website

### Model không load được

**Lỗi: "Model file not found"**
- Kiểm tra file có trong `backend/models/` không
- Kiểm tra tên file đúng không (`best.pt`)
- Kiểm tra đường dẫn trong `api.py`

**Lỗi: "Model load failed"**
- Kiểm tra file có bị corrupt không
- Thử download lại
- Kiểm tra phiên bản ultralytics: `pip install ultralytics --upgrade`

### Model load nhưng vẫn trả về "other"

- Kiểm tra class names trong model có đúng không
- Kiểm tra confidence threshold (có thể quá cao)
- Kiểm tra class mapping trong `api.py`
- Test với ảnh rác thải rõ ràng

## Model Alternatives

Nếu model `kendrickfff/waste-classification-yolov8-ken` không hoạt động, thử các model khác:

1. **Tìm model khác trên Hugging Face:**
   - https://huggingface.co/models?search=waste+classification
   - https://huggingface.co/models?search=trash+detection+yolo

2. **Fine-tune model của riêng bạn:**
   - Xem `SETUP_MODEL.md` để biết cách fine-tune
   - Sử dụng dataset waste classification
   - Train với YOLOv8

## Sau khi download thành công

1. ✅ Model đã được download vào `backend/models/best.pt`
2. ✅ Backend tự động load model khi start
3. ✅ API sẽ trả về classes đúng: `organic`, `plastic`, `metal`, `paper`, `other`
4. ✅ App sẽ phân loại rác thải chính xác

## Test

Sau khi download và restart backend:

1. **Test với ảnh rác thải:**
```bash
curl -X POST http://localhost:8000/detect-base64 \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_string", "format": "base64"}'
```

2. **Kiểm tra kết quả:**
- Classes phải là: `organic`, `plastic`, `metal`, `paper`, `other`
- Không phải: `person`, `laptop`, `keyboard`, etc.
- Confidence phải cao hơn (> 0.5)

3. **Test trên app:**
- Mở camera
- Hướng vào rác thải
- Kiểm tra classification có đúng không

