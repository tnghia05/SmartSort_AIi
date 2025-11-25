# Hướng dẫn Tích hợp YOLOv8 Object Detection

## Tổng quan

Ứng dụng đã được tích hợp với **YOLOv8 Object Detection** từ Hugging Face (`kendrickfff/waste-classification-yolov8-ken`) để phát hiện nhiều vật thể trong 1 ảnh.

## Kiến trúc

```
Mobile App (React Native) 
    ↓
Backend API (Python FastAPI)
    ↓
YOLOv8 Model (Hugging Face)
    ↓
Detections với Bounding Boxes
```

## Các file đã tạo

### Backend
- `backend/api.py` - FastAPI server với YOLOv8
- `backend/requirements.txt` - Python dependencies
- `backend/Procfile` - Heroku deployment config
- `backend/test_api.py` - Test script
- `backend/README.md` - Backend documentation

### Mobile App
- `mobile/src/services/DetectionService.ts` - Service để gọi API
- `mobile/src/components/BoundingBoxOverlay.tsx` - Component hiển thị bounding boxes
- `mobile/src/config/api.ts` - API configuration
- `mobile/src/types/index.ts` - Updated types cho detection

### Documentation
- `SETUP_BACKEND.md` - Hướng dẫn setup backend
- `ARCHITECTURE.md` - Kiến trúc tổng quan
- `QUICK_START.md` - Quick start guide

## Setup

### 1. Setup Backend

```bash
cd backend
pip install -r requirements.txt
python api.py
```

API sẽ chạy tại: `http://localhost:8000`

### 2. Cấu hình API URL

Mở `mobile/src/config/api.ts` và cập nhật:

```typescript
export const API_URL = 'http://YOUR_IP:8000'; // Thay YOUR_IP bằng IP máy tính
```

**Lưu ý quan trọng**: 
- Trên mobile device, `localhost` sẽ không hoạt động
- Cần sử dụng IP address của máy tính
- Ví dụ: `http://192.168.1.100:8000`

### 3. Test API

```bash
cd backend
python test_api.py path/to/image.jpg
```

### 4. Chạy Mobile App

```bash
cd mobile
npm start
```

## Sử dụng

### Detection Mode (Mặc định)

1. Mở app, chọn tab "Camera"
2. Chọn chế độ "Detection" (mặc định)
3. Nhấn 🔍 để phát hiện vật thể
4. Xem bounding boxes trên camera
5. Nhấn nút capture để lưu kết quả

### Classification Mode (Fallback)

1. Chọn chế độ "Classify"
2. Nhấn 🔍 để phân loại
3. Xem kết quả classification
4. Nhấn capture để lưu

## API Endpoints

### GET `/health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### POST `/detect`
Detect objects in image

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "detections": [
    {
      "bbox": [0.1, 0.2, 0.5, 0.6],
      "bbox_pixels": [100, 200, 500, 600],
      "class": "plastic",
      "class_original": "plastic_bottle",
      "confidence": 0.95
    }
  ],
  "count": 1
}
```

## Deploy Backend

### Render (Khuyến nghị - Free tier)

1. Truy cập https://render.com
2. Tạo new Web Service
3. Connect GitHub repository
4. Cấu hình:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Heroku

```bash
heroku create smartsort-api
git push heroku main
```

### Railway

1. Connect GitHub repository
2. Railway sẽ tự detect và deploy

## Troubleshooting

### API không kết nối được

1. **Kiểm tra backend đang chạy**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Kiểm tra IP address**:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`
   - Sử dụng IP address thay vì localhost

3. **Kiểm tra firewall**:
   - Đảm bảo port 8000 không bị chặn
   - Cho phép connection từ mobile device

4. **Kiểm tra network**:
   - Mobile device và computer phải cùng WiFi
   - Hoặc sử dụng tunnel (ngrok) nếu khác network

### Model không load

- Model sẽ được download tự động lần đầu (có thể mất vài phút)
- Kiểm tra logs trong backend để xem progress
- Kiểm tra internet connection

### App fallback sang Classification

- Nếu API không available, app sẽ tự động dùng Classification mode
- Kiểm tra console logs để xem lỗi cụ thể
- Kiểm tra API URL trong config

## Performance

### Backend
- **Model Size**: ~500MB RAM
- **Inference Time**: ~1-2 giây/ảnh (tùy vào hardware)
- **Memory**: Cần ít nhất 1GB RAM

### Mobile App
- **Network Latency**: ~1-3 giây (tùy vào network)
- **Image Size**: Compress ảnh trước khi gửi (quality: 0.8)

## Next Steps

1. **Deploy backend** lên cloud (Render/Heroku)
2. **Test với ảnh thực tế**
3. **Fine-tune model** nếu cần (xem `COLAB_TRAINING_GUIDE.md`)
4. **Optimize performance** (caching, batch processing)
5. **Add real-time detection** (stream camera frames)

## Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Model](https://huggingface.co/kendrickfff/waste-classification-yolov8-ken)
- [Render Deployment](https://render.com/docs)
- [Heroku Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)

