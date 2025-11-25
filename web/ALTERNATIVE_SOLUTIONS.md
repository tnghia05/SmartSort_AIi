# Giải pháp thay thế cho Ngrok

## Vấn đề
- Ngrok free plan chỉ cho phép 1 tunnel
- getUserMedia cần HTTPS hoặc localhost
- Mixed Content: HTTPS page không thể gọi HTTP backend

## Giải pháp

### 1. Vite với HTTPS local (Đã cấu hình) ✅

**Cách hoạt động:**
- Vite tự động tạo self-signed certificate
- Web chạy HTTPS local: `https://192.168.1.6:5173`
- getUserMedia hoạt động (HTTPS)
- Web có thể gọi backend qua ngrok (HTTPS) → OK

**Cách dùng:**
```bash
cd web
npm run dev
# Web sẽ chạy tại https://localhost:5173
# Truy cập từ máy khác: https://192.168.1.6:5173
```

**Lưu ý:**
- Browser sẽ cảnh báo "Not Secure" (self-signed certificate)
- Click "Advanced" → "Proceed to site" để tiếp tục
- Cần chấp nhận certificate trên mỗi máy khác

### 2. Cloudflare Tunnel (Free, nhiều tunnels)

**Cài đặt:**
```bash
# Download cloudflared từ: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
# Hoặc dùng package manager
```

**Cách dùng:**
```bash
# Terminal 1: Backend tunnel
cloudflared tunnel --url http://localhost:8000

# Terminal 2: Web tunnel  
cloudflared tunnel --url http://localhost:5173
```

**Ưu điểm:**
- ✅ Free
- ✅ Nhiều tunnels cùng lúc
- ✅ HTTPS tự động
- ✅ Không cần đăng ký

**Nhược điểm:**
- ⚠️ URL thay đổi mỗi lần (có thể fix với domain)

### 3. localtunnel (Free alternative)

**Cài đặt:**
```bash
npm install -g localtunnel
```

**Cách dùng:**
```bash
# Terminal 1: Backend
lt --port 8000

# Terminal 2: Web
lt --port 5173
```

**Ưu điểm:**
- ✅ Free
- ✅ Nhiều tunnels
- ✅ Đơn giản

**Nhược điểm:**
- ⚠️ URL thay đổi mỗi lần
- ⚠️ Có thể chậm hơn ngrok

### 4. serveo (SSH tunnel - Free)

**Cách dùng:**
```bash
# Terminal 1: Backend
ssh -R 80:localhost:8000 serveo.net

# Terminal 2: Web
ssh -R 80:localhost:5173 serveo.net
```

**Ưu điểm:**
- ✅ Free
- ✅ Không cần cài đặt (chỉ cần SSH)
- ✅ HTTPS tự động

**Nhược điểm:**
- ⚠️ Cần SSH client
- ⚠️ URL thay đổi

### 5. mkcert (Local certificate - Không cần tunnel)

**Cài đặt:**
```bash
# Windows: choco install mkcert
# Hoặc download từ: https://github.com/FiloSottile/mkcert
```

**Cách dùng:**
```bash
# Tạo local CA
mkcert -install

# Tạo certificate cho IP
mkcert 192.168.1.6 localhost 127.0.0.1

# Cấu hình Vite để dùng certificate này
```

**Ưu điểm:**
- ✅ Certificate được trust (không có warning)
- ✅ Không cần tunnel
- ✅ Nhanh (local)

**Nhược điểm:**
- ⚠️ Chỉ hoạt động trong mạng LAN
- ⚠️ Cần cài đặt mkcert trên mỗi máy

## Khuyến nghị

**Cho development:**
- ✅ **Vite HTTPS** (đã cấu hình) - Đơn giản nhất
- ✅ **Cloudflare Tunnel** - Nếu cần truy cập từ internet

**Cho production:**
- Deploy web lên Vercel/Netlify (HTTPS tự động)
- Backend deploy lên Railway/Render (HTTPS tự động)



