# Testing Guide

## Test Backend API

### 1. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Hoặc mở trình duyệt: http://localhost:8000/health

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### 2. Test Detect Endpoint (FormData)

```bash
curl -X POST http://localhost:8000/detect \
  -F "file=@path/to/your/image.jpg"
```

### 3. Test Detect-Base64 Endpoint

```bash
python test_base64_endpoint.py
```

Hoặc sử dụng Python script:

```python
import requests
import base64

# Read image file and encode to base64
with open('test_image.jpg', 'rb') as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Send request
response = requests.post(
    'http://localhost:8000/detect-base64',
    json={
        'image': image_b64,
        'format': 'base64'
    }
)

print(response.json())
```

### 4. Test từ React Native App

1. Đảm bảo backend đang chạy
2. Cập nhật `mobile/src/config/api.ts` với IP address đúng
3. Khởi động React Native app
4. Mở camera screen và chụp ảnh
5. Kiểm tra log trong Expo để xem kết quả

## Expected Behavior

### With YOLOv8n (Default Model)
- Model sẽ load thành công
- API sẽ trả về detections (có thể không chính xác vì model chưa được train cho waste classification)
- Response format:
```json
{
  "detections": [
    {
      "bbox": {
        "x1": 0.1,
        "y1": 0.2,
        "x2": 0.5,
        "y2": 0.6
      },
      "bbox_pixels": {
        "x1": 64.0,
        "y1": 128.0,
        "x2": 320.0,
        "y2": 384.0
      },
      "class": "other",
      "class_original": "person",
      "confidence": 0.85
    }
  ],
  "count": 1
}
```

### With Waste Classification Model
- Cần download model từ Hugging Face
- Model sẽ detect các loại rác: organic, plastic, metal, paper, other
- Detections sẽ chính xác hơn

## Troubleshooting

### Backend không start được
- Kiểm tra Python version (>= 3.8)
- Kiểm tra dependencies đã được cài đặt: `pip install -r requirements.txt`
- Kiểm tra port 8000 đã được sử dụng chưa

### Model không load được
- Kiểm tra kết nối internet (cần để download YOLOv8n lần đầu)
- Kiểm tra RAM (model cần ~2-4GB RAM)
- Xem log để biết lỗi cụ thể

### API trả về lỗi 500
- Kiểm tra log trong backend terminal
- Kiểm tra model đã được load chưa
- Kiểm tra image format (phải là JPEG/PNG)

### React Native không kết nối được
- Kiểm tra backend đang chạy
- Kiểm tra IP address trong `mobile/src/config/api.ts`
- Kiểm tra mobile device và máy tính cùng mạng Wi-Fi
- Kiểm tra firewall không block port 8000

### No detections returned
- YOLOv8n mặc định không được train cho waste classification
- Cần fine-tune model hoặc sử dụng model đã được train sẵn
- Thử với ảnh có vật thể rõ ràng (người, xe, v.v.) để test model hoạt động

## Next Steps

1. **Setup Waste Classification Model:**
   - Xem `SETUP_MODEL.md` để biết cách download và setup model từ Hugging Face
   - Hoặc fine-tune YOLOv8 với dataset của bạn

2. **Improve Detection Accuracy:**
   - Fine-tune model với dataset waste classification
   - Tăng confidence threshold nếu cần
   - Thêm post-processing để filter detections

3. **Deploy Backend:**
   - Deploy lên cloud (Render, Railway, AWS, etc.)
   - Cập nhật API URL trong React Native app
   - Setup monitoring và logging

