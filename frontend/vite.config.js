import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    },
    fs: {
      // 允许访问 node_modules
      allow: ['..']
    }
  },
  optimizeDeps: {
    exclude: ['@mediapipe/pose', '@mediapipe/drawing_utils', '@mediapipe/camera_utils']
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    },
    dedupe: []
  },
  assetsInclude: ['**/*.wasm', '**/*.tflite', '**/*.binarypb']
})

