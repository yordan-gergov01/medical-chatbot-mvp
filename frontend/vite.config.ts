import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // All /api calls forwarded to FastAPI during local development
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
})