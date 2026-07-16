import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const devBackend = env.DEV_BACKEND

  // Optional dev-only proxy: when DEV_BACKEND is set (e.g. in .env.local),
  // the dev server forwards /api, /media and /ws to that backend server-side,
  // so the browser talks same-origin and there are no CORS issues in local dev.
  // Has no effect on production builds.
  const proxy = devBackend
    ? {
        '/api': { target: devBackend, changeOrigin: true, secure: true },
        '/media': { target: devBackend, changeOrigin: true, secure: true },
        '/ws': { target: devBackend, changeOrigin: true, secure: true, ws: true },
      }
    : undefined

  return {
    plugins: [react()],
    server: { proxy },
  }
})
