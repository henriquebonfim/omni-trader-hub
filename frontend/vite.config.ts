import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:8000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("proxyReq", (proxyReq) => {
            if (proxyReq.socket && !proxyReq.socket.destroySoon) {
              proxyReq.socket.destroySoon = proxyReq.socket.destroy;
            }
          });
          proxy.on("proxyRes", (proxyRes) => {
            if (proxyRes.socket && !proxyRes.socket.destroySoon) {
              proxyRes.socket.destroySoon = proxyRes.socket.destroy;
            }
          });
        },
      },
      "/ws": {
        target: (process.env.VITE_API_TARGET || "http://localhost:8000").replace(
          /^http/,
          "ws"
        ),
        ws: true,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("open", (socket) => {
            if (socket && !socket.destroySoon) {
              socket.destroySoon = socket.destroy;
            }
          });
          proxy.on("proxyReqWs", (proxyReq, req, socket) => {
            if (socket && !socket.destroySoon) {
              socket.destroySoon = socket.destroy;
            }
          });
        },
      },
    },
  },
  plugins: [tailwindcss(), react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/tests/setup.ts",
  },
}));
