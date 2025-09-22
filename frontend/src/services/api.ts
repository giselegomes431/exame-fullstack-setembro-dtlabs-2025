// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor to inject the auth token into all private requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Export the api constant itself for use in AuthContext ---
export { api };

// --- Public Authentication Routes ---
export const login = (credentials: any) => api.post('/api/v1/login', credentials);
export const register = (credentials: any) => api.post('/api/v1/register', credentials);

// --- Private Device Routes ---
export const getDevices = () => api.get('/api/v1/devices');
export const createDevice = (deviceData: any) => api.post('/api/v1/devices', deviceData);
export const updateDevice = (uuid: string, deviceData: any) => api.put(`/api/v1/devices/${uuid}`, deviceData);
export const deleteDevice = (uuid: string) => api.delete(`/api/v1/devices/${uuid}`);

// --- Private Notification Routes ---
export const getNotifications = () => api.get('/api/v1/notifications');
export const createNotification = (notificationData: any) => api.post('/api/v1/notifications', notificationData);