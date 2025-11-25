# Quick Start Guide - SmartSort AI

## Tổng quan

Ứng dụng phân loại rác với 2 chế độ:
1. **Object Detection** (YOLOv8) - Phát hiện nhiều vật thể với bounding boxes
2. **Classification** (Mock) - Phân loại 1 vật thể (fallback)

## Bước 1: Setup Backend API

### Local Development

```bash
cd backend
pip install -r requirements.txt
python api.py
```

API sẽ chạy tại: `http://localhost:8000`

### Deploy Production

Xem hướng dẫn trong `SETUP_BACKEND.md`

## Bước 2: Cấu hình API URL

Mở `mobile/src/config/api.ts` và cập nhật:

```typescript
export const API_URL = 'http://localhost:8000'; // Local
// hoặc
export const API_URL = 'https://your-backend-url.onrender.com'; // Production
```

## Bước 3: Chạy Mobile App

```bash
cd mobile
npm install
npm start
```

## Bước 4: Test

1. Mở Expo Go app trên điện thoại
2. Quét QR code
3. Chọn chế độ "Detection" hoặc "Classify"
4. Nhấn 🔍 để phát hiện/phân loại
5. Nhấn nút capture để lưu kết quả

## Troubleshooting

### API không kết nối được

1. Kiểm tra backend đang chạy: `http://localhost:8000/health`
2. Kiểm tra API URL trong `mobile/src/config/api.ts`
3. Kiểm tra firewall/network
4. Thử dùng IP address thay vì localhost trên mobile:
   - Windows: `ipconfig` để xem IP
   - Mac/Linux: `ifconfig` để xem IP
   - Cập nhật: `http://YOUR_IP:8000`

### Model không load

- Model sẽ được download tự động lần đầu (có thể mất vài phút)
- Kiểm tra logs trong backend để xem progress

### App fallback sang Classification

- Nếu API không available, app sẽ tự động dùng Classification mode
- Kiểm tra console logs để xem lỗi cụ thể

## Next Steps

1. Deploy backend lên cloud (Render/Heroku)
2. Test với ảnh thực tế
3. Fine-tune model nếu cần (xem `COLAB_TRAINING_GUIDE.md`)
4. Tối ưu performance

