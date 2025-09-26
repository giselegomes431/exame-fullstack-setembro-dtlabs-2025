import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate, Outlet, useNavigate } from "react-router-dom";
import LoginPage from "./pages/Login";
import HomePage from "./pages/Home";
import DevicesPage from "./pages/Devices";
import NotificationsPage from "./pages/Notifications";
import Layout from "./components/common/Layout";
import { register } from "./services/api";
import DeviceRegistration from "./pages/DeviceRegistration";
import { setupSocketConnection } from "./services/websocket";
import { api } from "./services/api";
import { Socket } from "socket.io-client"; // Importa a tipagem do socket

// --- Tipagens ---
interface AuthData {
  access_token: string;
  user_id: string; // CRUCIAL
  username: string;
}

// PrivateRoute component to protect routes (Mantido da sua lógica)
const PrivateRoute = () => {
  const isAuthenticated = localStorage.getItem("token") !== null;
  return isAuthenticated ? (
    <Layout>
            <Outlet />   {" "}
    </Layout>
  ) : (
    <Navigate to="/login" replace />
  );
};

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState<string | null>(null); // Usamos o tipo Socket ou null para consistência
  const [socketInstance, setSocketInstance] = useState<Socket | null>(null);
  const navigate = useNavigate(); // --- Handlers de Autenticação ---

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id"); // Desconecta e limpa o estado do socket
    if (socketInstance) {
      socketInstance.disconnect();
    }
    setSocketInstance(null);
    setIsAuthenticated(false);
    setUserId(null);
    navigate("/login");
  };

  const handleAuthSuccess = (data: AuthData) => {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    setUserId(data.user_id);
    setIsAuthenticated(true);
    navigate("/");
  };

  const handleRegister = async (registerForm: {
    username: string;
    password: string;
    confirmPassword: string;
  }) => {
    try {
      await register({
        username: registerForm.username,
        password: registerForm.password,
      });
      console.log("Registro bem-sucedido! Faça login.");
      navigate("/login");
    } catch (err: any) {
      console.error(
        "Registration failed:",
        err.response?.data?.detail || "Registration failed."
      );
    }
  }; // 1. Checagem e Restauração de Sessão

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUserId = localStorage.getItem("user_id");

    if (storedToken && storedUserId) {
      setIsAuthenticated(true);
      setUserId(storedUserId);
      api.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
    }
  }, []); // 2. Lógica de Conexão do Socket (Executa SOMENTE quando o userId muda para um valor não-nulo)

  useEffect(() => {
    // Se o userId for nulo (não logado), apenas retorna.
    if (!userId) return;

    console.log(`[SOCKET INIT] Tentando conectar com userId: ${userId}`); // Limpa qualquer socket anterior para evitar duplicação
    if (socketInstance) {
      socketInstance.disconnect();
    }

    const newSocket = setupSocketConnection(userId);
    if (newSocket) {
      setSocketInstance(newSocket); // 🚨 LISTENERS ESSENCIAIS DE DEBUG NO CLIENTE

      newSocket.on("connect", () => {
        console.log(
          "🎉 [SOCKET SUCESSO] Conectado e autenticado com o backend!"
        );
      });
      newSocket.on("disconnect", (reason) => {
        console.warn(`[SOCKET AVISO] Desconectado. Razão: ${reason}`);
      });
      newSocket.on("connect_error", (err) => {
        console.error(
          "[SOCKET ERRO] Falha de conexão. Verifique a VITE_WEBSOCKET_URL e CORS.",
          err
        );
      });
    } // Cleanup: Desconecta o socket ao desmontar ou se o userId mudar

    return () => {
      if (newSocket) {
        console.log("[SOCKET CLEANUP] Desconectando o socket...");
        newSocket.off();
        newSocket.disconnect();
      }
    };
  }, [userId]); // Depende apenas do userId

  return (
    <Routes>
            {/* Rotas de Autenticação */}     {" "}
      <Route
        path="/login"
        element={
          <LoginPage
            onLoginSuccess={handleAuthSuccess}
            onRegister={handleRegister}
          />
        }
      />
           {" "}
      <Route
        path="/register"
        element={
          <LoginPage
            onLoginSuccess={handleAuthSuccess}
            onRegister={handleRegister}
            isRegisterView={true}
          />
        }
      />
            {/* Rotas Protegidas */}     {" "}
      <Route element={<PrivateRoute />}>
                {/* Rotas Privadas (Injetando props) */}       {" "}
        <Route
          path="/"
          element={<HomePage onLogout={handleLogout} userId={userId} />}
        />
               {" "}
        <Route path="/devices" element={<DevicesPage userId={userId} />} />     
         {" "}
        <Route
          path="/devices/register"
          element={<DeviceRegistration />}
        />
               {" "}
        <Route
          path="/notifications"
          element={
            <NotificationsPage
              userId={userId}
              socketInstance={socketInstance}
            />
          }
        />{" "}
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />   {" "}
    </Routes>
  );
}
