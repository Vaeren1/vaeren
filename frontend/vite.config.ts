import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: "localhost",
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        // Im Dev sprechen wir Backend mit Tenant-Subdomain "acme.app.localhost"
        // an, damit django-tenants routen kann. /etc/hosts braucht den Eintrag.
        headers: { Host: "acme.app.localhost" },
      },
      "/accounts": {
        target: "http://localhost:8000",
        changeOrigin: true,
        headers: { Host: "acme.app.localhost" },
      },
    },
  },
});
