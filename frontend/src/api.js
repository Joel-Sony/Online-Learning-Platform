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

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Avoid infinite loop if refresh fails, and don't try to refresh on login/register endpoints
    const isAuthEndpoint = originalRequest.url?.endsWith('/users/login/') || originalRequest.url?.endsWith('/users/token/refresh/') || originalRequest.url?.endsWith('/users/register/');
    
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh');

      if (refreshToken) {
        try {
          // Use axios directly to avoid interceptors on the refresh call
          const response = await axios.post(`${apiBase}/users/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access', access);

          // Update the authorization header and retry original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // If refresh fails, log out the user
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, clear and redirect
        localStorage.clear();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

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
