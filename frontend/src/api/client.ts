import axios from "axios";

/**
 * In dev, Vite proxies /api to the Django dev server (see vite.config.ts),
 * so this stays a relative path and the browser sees everything as
 * same-origin — no CORS, cookies/CSRF work without extra config.
 */
export const apiClient = axios.create({
  baseURL: "/api/v1",
});
