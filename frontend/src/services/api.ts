// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptador para injetar o token de autenticação em todas as requisições privadas
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

// --- Rotas de Autenticação (Públicas) ---
// Rota: POST /api/v1/login
export const login = (credentials: any) => api.post('/api/v1/login', credentials);

// Rota: POST /api/v1/register
export const register = (credentials: any) => api.post('/api/v1/register', credentials);

// --- Rotas de Dispositivos (Privadas) ---
// Rota: GET /api/v1/devices
export const getDevices = () => api.get('/api/v1/devices');

// Rota: POST /api/v1/devices
export const createDevice = (deviceData: any) => api.post('/api/v1/devices', deviceData);

// Rota: PUT /api/v1/devices/{device_uuid}
export const updateDevice = (uuid: string, deviceData: any) => api.put(`/api/v1/devices/${uuid}`, deviceData);

// Rota: DELETE /api/v1/devices/{device_uuid}
export const deleteDevice = (uuid: string) => api.delete(`/api/v1/devices/${uuid}`);

// --- Rotas de Notificações (Privadas) ---
// Rota: GET /api/v1/notifications
export const getNotifications = () => api.get('/api/v1/notifications');

// Rota: POST /api/v1/notifications
export const createNotification = (notificationData: any) => api.post('/api/v1/notifications', notificationData);

// --- Rota de Telemetria (Pública) ---
// Rota: POST /telemetry (Esta rota será usada pelo dispositivo, não pelo frontend)
// Portanto, não há necessidade de uma função de frontend para ela, a menos que você
// queira simular o envio de dados a partir de uma interface de testes.