# Quick Start - Web App

## Bước 1: Cấu hình API URL

Mở `src/config/api.ts` và thay đổi IP address:

```typescript
export const API_URL = 'http://192.168.1.6:8000'; // Thay bằng IP máy tính của bạn
```

## Bước 2: Chạy Backend

Trong thư mục `backend/`:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Bước 3: Chạy Web App

Trong thư mục `web/`:
```bash
npm run dev
```

## Bước 4: Truy cập từ điện thoại

1. Tìm IP address của máy tính:
   - Windows: `ipconfig` → xem IPv4 Address
   - Ví dụ: `192.168.1.6`

2. Mở trình duyệt trên điện thoại (cùng WiFi):
   ```
   http://192.168.1.6:5173
   ```

3. Cho phép truy cập camera khi được hỏi

4. Nhấn "Bật Camera" và bắt đầu quét!

## Troubleshooting

- **Không kết nối được WebSocket**: Kiểm tra IP address trong `api.ts` và đảm bảo backend đang chạy
- **Camera không hoạt động**: Kiểm tra quyền truy cập camera trong trình duyệt
- **Không thấy detection**: Kiểm tra console log để xem lỗi

