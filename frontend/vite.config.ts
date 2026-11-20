import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The frontend calls the API through /api, which Vite forwards to FastAPI.
// This keeps the browser on one origin, so cookie sessions work without CORS setup.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
