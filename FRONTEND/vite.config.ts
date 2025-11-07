import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Tu backend local, si lo usas
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      // Proxy al IP externo SIN CORS
      '/api/risk': {
        target: 'http://98.95.87.20',
        changeOrigin: true
      }
    }
  }
})
