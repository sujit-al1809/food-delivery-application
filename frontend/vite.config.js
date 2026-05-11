import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: 'localhost',
    cors: true
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
    sourcemap: false
  }
})
