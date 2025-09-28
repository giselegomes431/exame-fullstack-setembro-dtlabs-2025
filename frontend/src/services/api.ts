import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor para injetar o token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
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
  user_id: string;
  username: string;
}

export interface TelemetryData {
  id: number;
  cpu_usage: number;
  ram_usage: number;
  temperature: number;
  latency: number;
  connectivity: number;
  boot_date: string;
  device_uuid: string;
}

export { api };

// --- Public Authentication Routes ---
export const login = (credentials: any) =>
  api.post<AuthResponse>("/api/v1/login", credentials);
export const register = (credentials: any) =>
  api.post("/api/v1/register", credentials);

// --- Private Device Routes ---
export const getDevices = () => api.get("/api/v1/devices");
export const createDevice = (deviceData: any) =>
  api.post("/api/v1/devices", deviceData);
export const updateDevice = (uuid: string, deviceData: any) =>
  api.put(`/api/v1/devices/${uuid}`, deviceData);
export const deleteDevice = (uuid: string) =>
  api.delete(`/api/v1/devices/${uuid}`);

// --- Private Notification Routes ---
export const getNotifications = () => api.get("/api/v1/notifications");
export const createNotification = (notificationData: any) =>
  api.post("/api/v1/notifications", notificationData);

// --- Telemetry Routes ---
export const getLatestTelemetry = () =>
  api.get("/api/v1/devices/latest-telemetry");
export const getHistoricalData = (uuid: string, period: string) =>
  api.get(`/api/v1/devices/${uuid}/historical`, {
    params: { period },
  });
  export const getLatestTelemetries = (deviceUuid: string, limit: number = 20) =>
  api.get<TelemetryData[]>(`/api/v1/devices/${deviceUuid}/latest-telemetry-list`, {
    params: { limit },
  });
