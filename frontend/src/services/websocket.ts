import { io, Socket } from "socket.io-client";

const URL = import.meta.env.VITE_WEBSOCKET_URL || "http://localhost:8000";

export const setupSocketConnection = (userId: string | null): Socket | null => {
  if (!userId) {
    console.warn("[SOCKET SETUP] userId é nulo. Conexão abortada.");
    return null;
  }

  console.log(
    `[SOCKET SETUP] Tentando conectar a: ${URL} com UserId: ${userId}`
  );

  const socket = io(URL, {
    auth: {
      token: localStorage.getItem("token"),
      userId: userId,
    },
    transports: ["websocket", "polling"],
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
  });

  return socket;
};
