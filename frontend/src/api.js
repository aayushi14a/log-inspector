// In production, VITE_API_URL should point to the Railway backend URL
// In dev, Vite proxy handles /api → localhost:8000, so we use empty string
const raw = import.meta.env.VITE_API_URL ||
  (window.location.hostname !== 'localhost'
    ? 'https://log-inspector-production.up.railway.app'
    : '')

// Strip trailing slash to avoid double-slash in URLs
const API_BASE = raw.replace(/\/+$/, '')

export default API_BASE
