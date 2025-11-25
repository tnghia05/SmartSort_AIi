# Kiến trúc Ứng dụng - SmartSort AI

## Tổng quan

Ứng dụng sử dụng **Backend API** để xử lý Object Detection với YOLOv8, cho phép phát hiện nhiều vật thể trong 1 ảnh.

## Kiến trúc

```
┌─────────────────┐
│  React Native   │
│     Mobile      │
│     App         │
└────────┬────────┘
         │
         │ HTTP POST (Image)
         │
         ▼
┌─────────────────┐
│  Python Backend │
│   FastAPI +     │
│   YOLOv8        │
└────────┬────────┘
         │
         │ Inference
         │
         ▼
┌─────────────────┐
│  YOLOv8 Model   │
│  (Hugging Face) │
└─────────────────┘
```

## Components

### Mobile App (React Native)

#### Services
- **DetectionService**: Gọi API backend để detect objects
- **ClassificationService**: Fallback classification (mock)
- **StorageService**: Lưu trữ lịch sử local

#### Screens
- **CameraScreen**: Camera với object detection
- **HistoryScreen**: Lịch sử phân loại
- **RewardsScreen**: Điểm thưởng và statistics

#### Components
- **BoundingBoxOverlay**: Hiển thị bounding boxes trên camera
- **ClassificationOverlay**: Hiển thị kết quả classification

### Backend API (Python)

#### FastAPI Endpoints
- `GET /health`: Health check
- `POST /detect`: Detect objects in 1 image
- `POST /detect-batch`: Detect objects in multiple images

#### Model
- **YOLOv8**: `kendrickfff/waste-classification-yolov8-ken`
- Load từ Hugging Face
- Auto-download lần đầu tiên

## Data Flow

### Object Detection Flow

1. User chụp ảnh từ camera
2. App gửi ảnh đến backend API (`/detect`)
3. Backend xử lý ảnh với YOLOv8
4. Backend trả về detections với bounding boxes
5. App hiển thị bounding boxes trên camera
6. User nhấn capture để lưu kết quả
7. App lưu tất cả detections vào local storage

### Classification Flow (Fallback)

1. User chụp ảnh
2. App dùng ClassificationService (mock)
3. App hiển thị kết quả classification
4. User nhấn capture để lưu

## API Response Format

### Detection Response

```json
{
  "detections": [
    {
      "bbox": [0.1, 0.2, 0.5, 0.6],  // Normalized [x1, y1, x2, y2]
      "bbox_pixels": [100, 200, 500, 600],  // Pixel coordinates
      "class": "plastic",
      "class_original": "plastic_bottle",
      "confidence": 0.95
    }
  ],
  "count": 1
}
```

## Storage

### Local Storage (AsyncStorage)

- **Classifications**: Lịch sử phân loại
- **Stats**: User statistics (points, streak, etc.)

### Data Format

```typescript
{
  id: string;
  type: TrashType;
  label: string;
  confidence: number;
  timestamp: number;
  detections?: Detection[];  // For object detection
}
```

## Performance

### Optimizations

1. **Image Quality**: Compress ảnh trước khi gửi (quality: 0.8)
2. **API Caching**: Có thể cache kết quả nếu cần
3. **Batch Processing**: Hỗ trợ detect nhiều ảnh cùng lúc
4. **Fallback**: Tự động fallback sang classification nếu API lỗi

### Limitations

1. **Network Required**: Cần internet để gọi API
2. **Latency**: Có độ trễ do network + inference
3. **Model Size**: YOLOv8 model lớn (~500MB RAM)

## Security

1. **CORS**: Đã cấu hình CORS cho React Native
2. **Input Validation**: Validate image format
3. **Error Handling**: Xử lý lỗi gracefully

## Deployment

### Backend

- Deploy lên Render/Heroku/Railway
- Model tự động download khi deploy
- Cần ~1GB RAM để chạy model

### Mobile App

- Build với Expo
- Publish lên App Store/Google Play
- Hoặc dùng Expo Go để test

## Future Improvements

1. **Offline Mode**: Convert YOLOv8 sang ONNX để chạy offline
2. **Caching**: Cache model predictions
3. **Batch Processing**: Process nhiều ảnh cùng lúc
4. **Real-time**: Stream camera frames đến API
5. **Model Optimization**: Quantize model để giảm size

