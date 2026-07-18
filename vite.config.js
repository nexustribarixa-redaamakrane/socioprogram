import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/socioprogram/', 
  build: {
    // Ensuring the build is strictly clean
    outDir: 'dist',
    sourcemap: false, 
  }
})
