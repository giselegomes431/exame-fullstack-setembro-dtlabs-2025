// src/services/api.ts (código corrigido)

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor para injetar o token de autenticação
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

export interface AuthResponse {
  access_token: string;
  user_id: string; // O ID único do usuário, crucial para o SocketIO
  username: string; // Nome do usuário
  // Se houverem outros campos (ex: token_type), adicione-os aqui
}

// --- Export the api constant itself for use in AuthContext ---
export { api };

// --- Public Authentication Routes ---
export const login = (credentials: any) => api.post<AuthResponse>('/api/v1/login', credentials);
export const register = (credentials: any) => api.post('/api/v1/register', credentials);

// --- Private Device Routes ---
export const getDevices = () => api.get('/api/v1/devices');
export const createDevice = (deviceData: any) => api.post('/api/v1/devices', deviceData);
export const updateDevice = (uuid: string, deviceData: any) => api.put(`/api/v1/devices/${uuid}`, deviceData);
export const deleteDevice = (uuid: string) => api.delete(`/api/v1/devices/${uuid}`);

// --- Private Notification Routes ---
export const getNotifications = () => api.get('/api/v1/notifications');
export const createNotification = (notificationData: any) => api.post('/api/v1/notifications', notificationData);

// --- Adicionada: Rota de Telemetria Mais Recente ---
export const getLatestTelemetry = () => api.get('/api/v1/devices/latest-telemetry');
export const getHistoricalData = (uuid: string, period: string) => api.get(`/api/v1/devices/${uuid}/historical`, {
  params: { period }
});