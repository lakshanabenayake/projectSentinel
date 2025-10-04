import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'dist',
    // Ignore TypeScript errors during build
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress TypeScript warnings during build
        if (warning.code === 'PLUGIN_WARNING') return
        warn(warning)
      }
    }
  },
  esbuild: {
    // Don't fail build on TypeScript errors
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  }
})