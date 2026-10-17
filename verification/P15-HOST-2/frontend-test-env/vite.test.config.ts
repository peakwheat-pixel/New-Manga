import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";
const modules = process.env.P15_TEST_NODE_MODULES;
export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: { port: 5188, strictPort: true },
  build: { outDir: "dist", target: "es2021" },
  cacheDir: process.env.VITE_CACHE_DIR,
  resolve: { alias: [
    { find: /^jsdom$/, replacement: resolve(modules, "jsdom/lib/api.js") },
    { find: "react/jsx-dev-runtime", replacement: resolve(modules, "react/jsx-dev-runtime.js") },
    { find: "react/jsx-runtime", replacement: resolve(modules, "react/jsx-runtime.js") },
    { find: "react-dom/client", replacement: resolve(modules, "react-dom/client.js") },
    { find: "react-dom/server", replacement: resolve(modules, "react-dom/server.js") },
    { find: "react", replacement: resolve(modules, "react/index.js") },
    { find: "react-dom", replacement: resolve(modules, "react-dom/index.js") },
    { find: "@tauri-apps/api/event", replacement: resolve(modules, "@tauri-apps/api/event.js") },
    { find: "@tauri-apps/api", replacement: resolve(modules, "@tauri-apps/api/index.js") },
  ] },
});
