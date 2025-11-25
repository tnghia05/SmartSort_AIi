# Hướng dẫn Setup Backend API

## Yêu cầu

- Python 3.8+
- pip

## Bước 1: Cài đặt Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Bước 2: Chạy API Local

```bash
python api.py
```

Hoặc sử dụng uvicorn:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: `http://localhost:8000`

## Bước 3: Test API

### Test với curl:

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

### Test với Python:

```python
import requests

url = "http://localhost:8000/detect"
files = {"file": open("test_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Bước 4: Deploy Backend

### Option 1: Deploy lên Render (Khuyến nghị - Free tier)

1. Truy cập https://render.com
2. Tạo account mới
3. Tạo new Web Service
4. Connect GitHub repository
5. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
6. Deploy

### Option 2: Deploy lên Heroku

1. Cài đặt Heroku CLI
2. Login: `heroku login`
3. Tạo app: `heroku create smartsort-api`
4. Deploy: `git push heroku main`

### Option 3: Deploy lên Railway

1. Truy cập https://railway.app
2. Connect GitHub repository
3. Railway sẽ tự detect và deploy

### Option 4: Deploy lên Google Cloud Run

1. Tạo Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. Build và deploy:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/smartsort-api
gcloud run deploy --image gcr.io/PROJECT_ID/smartsort-api
```

## Bước 5: Cập nhật API URL trong App

Sau khi deploy, cập nhật URL trong `mobile/src/config/api.ts`:

```typescript
export const API_URL = 'https://your-backend-url.onrender.com';
```

Hoặc sử dụng environment variable trong `.env`:

```
EXPO_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

## Lưu ý

1. **Model Download**: Model YOLOv8 sẽ được download tự động lần đầu tiên chạy API (có thể mất vài phút)

2. **Memory**: YOLOv8 model cần ~500MB RAM. Đảm bảo server có đủ memory.

3. **Cold Start**: Nếu dùng serverless (Render free tier), có thể có cold start delay lần đầu tiên.

4. **CORS**: API đã được cấu hình CORS để cho phép React Native app gọi API.

5. **Rate Limiting**: Có thể thêm rate limiting nếu cần:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/detect")
@limiter.limit("10/minute")
async def detect_trash(...):
    ...
```

## Troubleshooting

### Model không load được
- Kiểm tra internet connection
- Kiểm tra logs để xem lỗi cụ thể
- Model có thể mất vài phút để download lần đầu

### API chậm
- Sử dụng GPU nếu có (cần cấu hình thêm)
- Tối ưu image size trước khi gửi
- Sử dụng quantization model (nhỏ hơn nhưng chậm hơn)

### CORS error
- Kiểm tra CORS middleware đã được cấu hình
- Kiểm tra API URL trong app có đúng không

## Next Steps

Sau khi deploy thành công:
1. Test API với Postman hoặc curl
2. Cập nhật API URL trong React Native app
3. Test app với API thật
4. Monitor logs để kiểm tra performance

