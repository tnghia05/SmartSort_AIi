# Quick Start - Backend API

## Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

## Khởi động Server

```bash
# Windows
python api.py
# hoặc
start.bat

# Linux/Mac  
python api.py
```

Server sẽ chạy tại: `http://localhost:8000`

## Test API

### 1. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Hoặc mở trình duyệt: http://localhost:8000/health

### 2. Test Detect Endpoint

```bash
# Sử dụng curl
curl -X POST http://localhost:8000/detect \
  -F "file=@path/to/your/image.jpg"

# Hoặc sử dụng Python script
python test_api.py
```

### 3. Xem API Documentation

Mở trình duyệt: http://localhost:8000/docs

FastAPI tự động tạo interactive API documentation (Swagger UI)

## Kết nối với React Native App

### 1. Tìm IP Address của máy tính

**Windows:**
```bash
ipconfig
# Tìm IPv4 Address (ví dụ: 192.168.1.100)
```

**Linux/Mac:**
```bash
ifconfig
# hoặc
ip addr show
```

### 2. Cập nhật API URL trong React Native App

Mở file `mobile/src/config/api.ts` và thay đổi:

```typescript
// Thay localhost bằng IP address của máy tính
export const API_URL = 'http://192.168.1.100:8000';
```

**Lưu ý:** 
- Đảm bảo mobile device và máy tính cùng một mạng Wi-Fi
- Đảm bảo firewall cho phép kết nối đến port 8000
- Trên Android, có thể cần thêm quyền `INTERNET` trong `AndroidManifest.xml`

### 3. Test từ React Native App

1. Khởi động backend API
2. Khởi động React Native app
3. Mở camera screen và chụp ảnh
4. App sẽ gửi ảnh đến API và nhận kết quả detection

## Troubleshooting

### Port 8000 đã được sử dụng

Thay đổi port trong `api.py`:
```python
port = int(os.getenv("PORT", 8001))  # Đổi sang port khác
```

Hoặc set environment variable:
```bash
# Windows
set PORT=8001
python api.py

# Linux/Mac
export PORT=8001
python api.py
```

### Model không load được

Xem file `SETUP_MODEL.md` để biết cách setup model.

### CORS Error

API đã được cấu hình CORS để cho phép tất cả origins. Nếu vẫn gặp lỗi, kiểm tra:
- Backend đang chạy đúng port
- URL trong React Native app đúng
- Mobile device và máy tính cùng mạng

### Connection Refused

- Kiểm tra backend đang chạy: `curl http://localhost:8000/health`
- Kiểm tra firewall không block port 8000
- Kiểm tra IP address đúng
- Đảm bảo mobile device và máy tính cùng mạng Wi-Fi

## Next Steps

1. Setup model từ Hugging Face (xem `SETUP_MODEL.md`)
2. Fine-tune model với dataset của bạn
3. Deploy backend lên cloud (Render, Railway, AWS, etc.)
4. Cập nhật API URL trong React Native app

