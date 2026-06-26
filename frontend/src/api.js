import axios from 'axios';

const rawBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
// Remove any trailing slashes to prevent double slashes in URLs
const cleanBase = rawBase.replace(/\/+$/, '');
const apiBase = cleanBase.endsWith('/api') ? cleanBase : `${cleanBase}/api`;

const api = axios.create({
  baseURL: apiBase,
});

export { apiBase };

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getWebSocketUrl = (path) => {
  const wsBaseUrl = import.meta.env.VITE_WS_URL;
  if (wsBaseUrl) {
    const base = wsBaseUrl.endsWith('/') ? wsBaseUrl.slice(0, -1) : wsBaseUrl;
    return `${base}${path}`;
  }
  
  const httpUrl = api.defaults.baseURL;
  const rootHttpUrl = httpUrl.endsWith('/api') ? httpUrl.slice(0, -4) : httpUrl;
  const wsProtocol = rootHttpUrl.startsWith('https') ? 'wss://' : 'ws://';
  const cleanHost = rootHttpUrl.replace(/^https?:\/\//i, '');
  
  if (cleanHost.includes('localhost:8000') || cleanHost.includes('127.0.0.1:8000')) {
    return `ws://localhost:8001${path}`;
  }
  
  return `${wsProtocol}${cleanHost}${path}`;
};

export default api;
