# SmartSort AI - Backend API

Backend API sử dụng YOLOv8 model từ Hugging Face để phát hiện và phân loại rác thải trong ảnh.

## Cài đặt

1. **Cài đặt Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Khởi động server:**
```bash
# Windows
python api.py
# hoặc
start.bat

# Linux/Mac
python api.py
```

Server sẽ chạy tại `http://localhost:8000`

## API Endpoints

### GET `/`
Kiểm tra trạng thái API
```json
{
  "message": "SmartSort AI - Trash Detection API",
  "status": "running",
  "model_loaded": true
}
```

### GET `/health`
Health check endpoint
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### POST `/detect`
Phát hiện rác thải trong ảnh (FormData)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File image (form field: `file`)

**Response:**
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
        "x1": 100,
        "y1": 200,
        "x2": 500,
        "y2": 600
      },
      "class": "plastic",
      "class_original": "plastic_bottle",
      "confidence": 0.95
    }
  ],
  "count": 1
}
```

### POST `/detect-base64`
Phát hiện rác thải trong ảnh (Base64) - **Khuyến nghị cho React Native**

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "image": "base64_encoded_image_string",
  "format": "base64"
}
```

**Response:**
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
        "x1": 100,
        "y1": 200,
        "x2": 500,
        "y2": 600
      },
      "class": "plastic",
      "class_original": "plastic_bottle",
      "confidence": 0.95
    }
  ],
  "count": 1
}
```

**Lưu ý:** Endpoint `/detect-base64` được khuyến nghị cho React Native vì FormData với file URI có thể gây vấn đề trong React Native.

### POST `/detect-batch`
Phát hiện rác thải trong nhiều ảnh cùng lúc

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Multiple image files (form field: `files`)

**Response:**
```json
{
  "results": [
    {
      "filename": "image1.jpg",
      "detections": [...],
      "count": 2
    },
    {
      "filename": "image2.jpg",
      "detections": [...],
      "count": 1
    }
  ]
}
```

## Model

API sử dụng YOLOv8 model từ Hugging Face:
- Model: `kendrickfff/waste-classification-yolov8-ken`
- Model sẽ được tự động download lần đầu tiên khi chạy API
- Model được load vào memory khi server khởi động

## Class Mapping

Model có thể trả về các class names khác nhau. API sẽ map chúng về các class chuẩn:
- `organic` - Rác hữu cơ
- `plastic` - Nhựa
- `metal` - Kim loại
- `paper` - Giấy
- `other` - Khác

## CORS

API đã được cấu hình CORS để cho phép React Native app gọi từ bất kỳ origin nào. Trong production, nên giới hạn các origin được phép.

## Testing

Sử dụng curl để test API:

```bash
# Health check
curl http://localhost:8000/health

# Detect trash in image
curl -X POST http://localhost:8000/detect \
  -F "file=@path/to/image.jpg"
```

## Lưu ý

- Lần đầu tiên chạy API, model sẽ được download từ Hugging Face (có thể mất vài phút)
- Model được load vào memory, cần đủ RAM để chạy
- API mặc định chạy trên port 8000, có thể thay đổi qua environment variable `PORT`
- Để test trên mobile device, cần thay `localhost` bằng IP address của máy tính chạy backend

## Troubleshooting

### Model không load được
- Kiểm tra kết nối internet (cần để download model lần đầu)
- Kiểm tra RAM (model cần ~2-4GB RAM)
- Kiểm tra log để xem lỗi cụ thể

### API không chạy được
- Kiểm tra Python version (yêu cầu Python 3.8+)
- Kiểm tra dependencies đã được cài đặt đầy đủ
- Kiểm tra port 8000 đã được sử dụng chưa
