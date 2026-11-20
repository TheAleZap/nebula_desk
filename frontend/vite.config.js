import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { watch: { usePolling: true } }, // file changes are seen inside Docker on Windows/Mac
});
