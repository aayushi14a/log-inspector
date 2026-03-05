// In production, VITE_API_URL should point to the Railway backend URL
// e.g. https://log-inspector-backend-production.up.railway.app
// In dev, Vite proxy handles /api → localhost:8000, so we use empty string
const API_BASE = import.meta.env.VITE_API_URL || ''

export default API_BASE
