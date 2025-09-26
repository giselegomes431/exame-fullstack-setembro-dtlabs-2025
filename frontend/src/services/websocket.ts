import { io, Socket } from "socket.io-client";

// Presumindo que esta variável de ambiente está definida corretamente
const URL = import.meta.env.VITE_WEBSOCKET_URL || "http://localhost:8000";

// Função para criar a conexão e configurar o token e o ID do usuário
export const setupSocketConnection = (userId: string | null): Socket | null => {
  // Se não houver ID de usuário, não conecte
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
      userId: userId, // Envia o ID do usuário no payload de autenticação
    },
    transports: ["websocket", "polling"], // Força a ordem de transporte
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
  }); // Os listeners de connect/error estão no App.tsx. Aqui apenas retornamos a instância.

  return socket;
};
