import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Enable HTTPS với self-signed certificate
    basicSsl(),
  ],
  server: {
    host: '0.0.0.0', // Cho phép truy cập từ mạng LAN
    port: 5173,
    allowedHosts: [
      'glaucomatous-preactively-louetta.ngrok-free.dev',
    ],
  },
  optimizeDeps: {
    exclude: [],
  },
})
