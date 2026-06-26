import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base './' so the built bundle works when served from a nested gallery path
export default defineConfig({
  base: './',
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 8080,
    strictPort: true,
  },
})
