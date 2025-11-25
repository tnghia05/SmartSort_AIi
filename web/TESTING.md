# Hướng dẫn Test Web App

## Bước 1: Kiểm tra Backend

1. **Chạy backend:**
   ```bash
   cd backend
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Kiểm tra backend hoạt động:**
   - Mở trình duyệt: `http://localhost:8000/health`
   - Hoặc: `http://localhost:8000/`
   - Phải thấy JSON response với `"status": "ok"`

## Bước 2: Cấu hình API URL

1. **Mở file:** `web/src/config/api.ts`
2. **Thay đổi IP address:**
   ```typescript
   export const API_URL = 'http://192.168.1.6:8000'; // Thay bằng IP máy tính của bạn
   ```
3. **Tìm IP máy tính:**
   - Windows: `ipconfig` → xem IPv4 Address
   - Ví dụ: `192.168.1.6`

## Bước 3: Test trên máy tính

1. **Mở web app:** `http://localhost:5173`
2. **Nhấn "Bật Camera"**
3. **Cho phép truy cập camera**
4. **Đưa vật thể vào camera:**
   - Quần áo (clothes)
   - Nhựa (plastic)
   - Giấy (paper)
   - Kim loại (metal)
   - v.v.
5. **Kiểm tra:**
   - Status phải hiển thị "Đã kết nối" (màu xanh)
   - Detection summary phải hiển thị số lượng vật thể
   - Bounding boxes phải xuất hiện trên video

## Bước 4: Test từ điện thoại

1. **Đảm bảo điện thoại và máy tính cùng WiFi**
2. **Tìm IP máy tính:** `ipconfig` (Windows)
3. **Mở trình duyệt trên điện thoại:**
   ```
   http://<IP_MÁY_TÍNH>:5173
   ```
   Ví dụ: `http://192.168.1.6:5173`
4. **Cho phép truy cập camera**
5. **Nhấn "Bật Camera"**
6. **Test detection như trên**

## Troubleshooting

### WebSocket không kết nối được
- Kiểm tra backend đang chạy: `http://localhost:8000/health`
- Kiểm tra IP trong `web/src/config/api.ts` đúng chưa
- Kiểm tra Windows Firewall cho phép port 8000

### Camera không hoạt động
- Cho phép truy cập camera trong trình duyệt
- Kiểm tra camera đang được dùng bởi app khác không
- Thử refresh trang

### Không thấy detection
- Kiểm tra backend có model loaded không
- Kiểm tra Console (F12) xem có lỗi không
- Đảm bảo vật thể rõ ràng, đủ ánh sáng

