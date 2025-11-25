// API Configuration
// Thay đổi URL này thành IP address của máy tính chạy backend
// Ví dụ: http://192.168.1.6:8000
// Hoặc nếu dùng ngrok: https://your-backend-ngrok-url.ngrok-free.app

// Giải pháp: Chỉ ngrok backend, web chạy localhost
// - Web chạy localhost:5173 (HTTP) → có thể gọi ngrok backend (HTTPS) - OK
// - Hoặc web chạy IP laptop (HTTP) → có thể gọi ngrok backend (HTTPS) - OK
const getApiUrl = () => {
  // Priority 1: Environment variable (highest priority)
  if (import.meta.env.VITE_API_URL) {
    console.log('Using VITE_API_URL:', import.meta.env.VITE_API_URL);
    return import.meta.env.VITE_API_URL;
  }
  
  // Priority 2: Nếu có backend ngrok URL trong env, dùng nó
  // (Web chạy localhost hoặc IP laptop, backend qua ngrok)
  if (import.meta.env.VITE_BACKEND_NGROK_URL) {
    console.log('Using VITE_BACKEND_NGROK_URL:', import.meta.env.VITE_BACKEND_NGROK_URL);
    return import.meta.env.VITE_BACKEND_NGROK_URL;
  }
  
  // Priority 3: Chạy localhost hoặc IP laptop, backend cũng local
  const backendIP = import.meta.env.VITE_BACKEND_IP || '192.168.1.6';
  const apiUrl = `http://${backendIP}:8000`;
  console.log('Using default backend IP:', apiUrl);
  return apiUrl;
};

export const API_URL = getApiUrl();
console.log('🔧 Final API_URL:', API_URL);

export const WS_URL = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
console.log('🔧 Final WS_URL:', WS_URL);

export const API_ENDPOINTS = {
  DETECT: '/detect',
  DETECT_BASE64: '/detect-base64',
  DETECT_BATCH: '/detect-batch',
  HEALTH: '/health',
  WS_DETECT: '/ws/detect',
} as const;

