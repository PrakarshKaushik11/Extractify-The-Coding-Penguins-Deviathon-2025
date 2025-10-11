import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "localhost",   // ✅ Force localhost instead of "::" (IPv6)
    port: 8080,          // ✅ Matches your CORS setup in FastAPI
  },
  plugins: [
    react(),
    mode === "development" && componentTagger()
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // ✅ Optional: automatically open in browser on start
  preview: {
    port: 8080,
    open: true,
  },
}));
