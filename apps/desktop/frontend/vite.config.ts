import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// React front-end for the M2-RC1 resource-channel vertical slice.
export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: { port: 5188, strictPort: true },
  build: { outDir: "dist", target: "es2021" },
});
