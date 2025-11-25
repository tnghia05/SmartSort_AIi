# Hướng dẫn Setup với Ngrok

## Vấn đề
Khi truy cập web app qua ngrok, backend và WebSocket có thể không kết nối được vì:
1. URL backend không khớp với ngrok URL
2. Ngrok cần header đặc biệt để bypass warning page

## Giải pháp

### 1. Khởi động Backend và Web với Ngrok

**Option A: Chạy 2 ngrok riêng biệt (Khuyến nghị - Hoạt động với free plan)**

```bash
# Terminal 1: Chạy backend
cd backend
python api.py
# Backend sẽ chạy tại http://localhost:8000

# Terminal 2: Chạy ngrok cho backend
ngrok http 8000
# Ngrok sẽ tạo URL như: https://backend-xxxxx.ngrok-free.app

# Terminal 3: Chạy web dev server
cd web
npm run dev
# Web sẽ chạy tại http://localhost:5173

# Terminal 4: Chạy ngrok cho web
ngrok http 5173
# Ngrok sẽ tạo URL như: https://web-xxxxx.ngrok-free.app
```

**Option B: Dùng ngrok config file (1 ngrok, nhiều tunnels) - Cần paid plan**

⚠️ **Lưu ý:** Ngrok free plan chỉ cho phép 1 tunnel. Option B cần ngrok paid plan.

**Nếu bạn dùng free plan, hãy dùng Option A (2 ngrok riêng biệt) thay vì Option B.**

1. **Setup authtoken (chỉ cần làm 1 lần):**
```bash
# Lấy token từ: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

2. **File `ngrok.yml` đã được tạo sẵn ở root project:**
```yaml
version: "2"
tunnels:
  backend:
    addr: 8000
    proto: http
  web:
    addr: 5173
    proto: http
```

3. **Chạy ngrok với config:**
```bash
# Từ root directory của project (nơi có file ngrok.yml)
ngrok start --all --config ngrok.yml
# Hoặc chỉ định tunnels cụ thể
ngrok start backend web --config ngrok.yml
# Hoặc nếu ngrok.yml ở vị trí khác
ngrok start --all --config=./ngrok.yml
```

**Lưu ý:** 
- Nếu gặp lỗi "no configuration file", đảm bảo file `ngrok.yml` ở cùng thư mục với lệnh
- Nếu gặp lỗi "authtoken", chạy: `ngrok config add-authtoken YOUR_TOKEN`
- Có thể cần chỉ định đường dẫn đầy đủ: `ngrok start --all --config E:\Code\rac\ngrok.yml`

4. **Ngrok sẽ tạo 2 URLs:**
- Backend: `https://xxxxx.ngrok-free.app` → trỏ đến `localhost:8000`
- Web: `https://yyyyy.ngrok-free.app` → trỏ đến `localhost:5173`

5. **Xem URLs:**
- Mở browser: http://localhost:4040 (ngrok web interface)
- Hoặc xem trong terminal output

6. **Cấu hình web app:**
- Truy cập web qua ngrok URL của web (ví dụ: `https://yyyyy.ngrok-free.app`)
- Web app sẽ tự động detect ngrok URL và dùng cho API
- **Hoặc** set environment variable trong `web/.env`:
  ```bash
  VITE_API_URL=https://xxxxx.ngrok-free.app
  ```
  (Thay `xxxxx` bằng URL thực tế của backend tunnel)

**Option C: Chỉ ngrok backend, web chạy localhost (Khuyến nghị cho free plan)**

✅ **Giải pháp tốt nhất cho ngrok free plan:**
- Chỉ ngrok backend (1 tunnel)
- Web chạy localhost:5173 (HTTP)
- Web app gọi backend qua ngrok URL (HTTPS) → **OK** (HTTP page có thể gọi HTTPS API)

```bash
# Terminal 1: Chạy backend
cd backend
python api.py

# Terminal 2: Chỉ ngrok cho backend
ngrok http 8000
# Lấy URL: https://xxxxx.ngrok-free.app

# Terminal 3: Chạy web dev server
cd web
npm run dev
# Web chạy tại http://localhost:5173
```

**Cấu hình:**

1. **Lấy backend ngrok URL** từ terminal hoặc http://localhost:4040

2. **Tạo file `web/.env`:**
   ```bash
   VITE_BACKEND_NGROK_URL=https://xxxxx.ngrok-free.app
   ```
   (Thay `xxxxx` bằng URL thực tế của backend tunnel)

3. **Restart web dev server:**
   ```bash
   cd web
   npm run dev
   ```

4. **Truy cập:**
   - Trên máy tính: http://localhost:5173
   - Từ máy khác trong mạng LAN: http://192.168.1.6:5173 (IP laptop)
   - Web app sẽ gọi backend qua ngrok URL (HTTPS)

**Lưu ý:**
- ✅ Hoạt động với ngrok free plan (chỉ cần 1 tunnel)
- ✅ Không có Mixed Content (HTTP page gọi HTTPS API - OK)
- ⚠️ Máy khác cần cùng mạng LAN để truy cập web qua IP laptop
- ⚠️ Nếu máy khác ở ngoài mạng, cần ngrok cho cả web (nhưng free plan không cho phép 2 tunnels)

**Option D: Chỉ ngrok web, backend dùng IP laptop - KHÔNG HOẠT ĐỘNG**

⚠️ **Lưu ý quan trọng:** Option này KHÔNG hoạt động vì **Mixed Content**:
- Web chạy qua ngrok = HTTPS
- Backend chạy HTTP (IP laptop)
- Browser block: HTTPS page không thể gọi HTTP backend

**Option C (Cũ - Không dùng được): Chỉ ngrok web, backend dùng IP laptop**

Chỉ cần ngrok cho web, backend chạy trên IP laptop trong mạng LAN.

```bash
# Terminal 1: Chạy backend
cd backend
python api.py
# Backend sẽ chạy tại http://localhost:8000

# Terminal 2: Chạy web dev server
cd web
npm run dev
# Web sẽ chạy tại http://localhost:5173

# Terminal 3: Chỉ ngrok cho web
ngrok http 5173
# Hoặc dùng config (đã được cập nhật chỉ có web tunnel)
ngrok start web --config ngrok.yml
# Lấy URL: https://yyyyy.ngrok-free.app
```

**Cấu hình:**

1. **Tìm IP laptop:**
   ```bash
   # Windows
   ipconfig
   # Tìm IPv4 Address (ví dụ: 192.168.1.6)
   ```

2. **Tạo file `web/.env`:**
   ```bash
   # IP của laptop chạy backend
   VITE_BACKEND_IP=192.168.1.6
   # Hoặc set trực tiếp backend URL
   # VITE_API_URL=http://192.168.1.6:8000
   ```

3. **Restart web dev server:**
   ```bash
   cd web
   npm run dev
   ```

4. **Truy cập:**
   - Máy khác: Truy cập web qua ngrok URL `https://yyyyy.ngrok-free.app`
   - Web app sẽ tự động gọi backend qua IP laptop `http://192.168.1.6:8000`

**Lưu ý:**
- ⚠️ Chỉ hoạt động nếu máy khác và laptop **cùng mạng LAN**
- ⚠️ Nếu máy khác ở ngoài mạng (internet), cần ngrok cho cả backend
- ✅ Đơn giản hơn, không cần 2 ngrok tunnels
- ✅ Backend không qua ngrok nên nhanh hơn

**Option D: Chỉ ngrok backend, web dùng localhost (Đơn giản nhất)**

```bash
# Terminal 1: Chạy backend
cd backend
python api.py

# Terminal 2: Chạy ngrok cho backend
ngrok http 8000
# Lấy URL: https://xxxxx.ngrok-free.app

# Terminal 3: Chạy web dev server
cd web
npm run dev

# Truy cập web qua: http://localhost:5173
# Web app sẽ tự động detect ngrok URL từ backend
```

**Lưu ý:** Với Option C, bạn cần truy cập web qua `localhost:5173` trên máy tính, không thể truy cập từ điện thoại qua ngrok. Nếu cần truy cập từ điện thoại, dùng Option A hoặc B.

### 2. Cấu hình Web App

**Nếu dùng Option A hoặc B (2 ngrok URLs):**

Cập nhật `web/src/config/api.ts` hoặc tạo file `.env`:

```bash
# Tạo file .env trong thư mục web/
VITE_API_URL=https://backend-xxxxx.ngrok-free.app
```

**Nếu dùng Option C (chỉ ngrok backend):**

Web app sẽ **tự động phát hiện** ngrok URL từ backend khi bạn truy cập qua `localhost:5173`.

**Hoặc** set environment variable:

```bash
# Tạo file .env trong thư mục web/
VITE_API_URL=https://your-backend-ngrok-url.ngrok-free.app
```

### 3. Kiểm tra Kết nối

1. Mở web app qua ngrok URL
2. Kiểm tra Console (F12) để xem:
   - `API_URL` và `WS_URL` có đúng không
   - Backend health check có thành công không
   - WebSocket có kết nối được không

### 4. Troubleshooting

**Backend không kết nối:**
- Kiểm tra backend đang chạy: `curl http://localhost:8000/health`
- Kiểm tra ngrok đang chạy và URL đúng
- Kiểm tra Console logs để xem lỗi cụ thể

**WebSocket lỗi:**
- Ngrok free plan có thể không hỗ trợ WebSocket tốt
- Thử upgrade lên ngrok paid plan
- Hoặc dùng local network (IP address) thay vì ngrok

**Ngrok Warning Page:**
- Code đã tự động thêm header `ngrok-skip-browser-warning: true`
- Nếu vẫn thấy warning page, click "Visit Site" để tiếp tục

## Alternative: Dùng Local Network

Nếu ngrok không ổn định, dùng local network:

1. Tìm IP của máy tính:
   ```bash
   # Windows
   ipconfig
   # Tìm IPv4 Address (ví dụ: 192.168.1.6)
   ```

2. Cập nhật `web/src/config/api.ts`:
   ```typescript
   export const API_URL = 'http://192.168.1.6:8000';
   ```

3. Đảm bảo mobile/device và máy tính cùng mạng Wi-Fi

