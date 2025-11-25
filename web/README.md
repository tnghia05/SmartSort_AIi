# SmartSort AI - Web App

Web application để phát hiện và phân loại rác thải real-time qua camera.

## Cài đặt

1. **Cài đặt dependencies:**
```bash
cd web
npm install
```

2. **Cấu hình API URL:**
   - Mở file `src/config/api.ts`
   - Thay đổi `API_URL` thành IP address của máy tính chạy backend
   - Ví dụ: `http://192.168.1.6:8000`

   Hoặc tạo file `.env`:
```env
VITE_API_URL=http://192.168.1.6:8000
```

3. **Chạy development server:**
```bash
npm run dev
```

Server sẽ chạy tại `http://localhost:5173`

## Truy cập từ điện thoại

1. Đảm bảo máy tính và điện thoại cùng mạng WiFi
2. Tìm IP address của máy tính:
   - Windows: `ipconfig` (xem IPv4 Address)
   - Mac/Linux: `ifconfig` hoặc `ip addr`
3. Mở trình duyệt trên điện thoại và truy cập:
   ```
   http://<IP_ADDRESS>:5173
   ```
   Ví dụ: `http://192.168.1.6:5173`

## Tính năng

- ✅ Camera streaming real-time
- ✅ WebSocket connection với backend
- ✅ Detection overlay với bounding boxes
- ✅ Detection summary với phân loại
- ✅ Responsive design cho mobile
- ✅ Auto-reconnect khi mất kết nối

## Build cho production

```bash
npm run build
```

Files sẽ được build vào thư mục `dist/`. Có thể deploy lên bất kỳ static hosting nào (Vercel, Netlify, etc.)

## Lưu ý

- Trình duyệt cần hỗ trợ WebRTC (MediaDevices API)
- Cần cho phép truy cập camera trong trình duyệt
- Backend phải chạy và accessible từ mạng LAN
