// src/App.tsx
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useState } from 'react';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
// import Devices from './pages/Devices';
// import Notifications from './pages/Notifications';
// import DeviceRegistration from './pages/DeviceRegistration';

// Componente de Rota Privada
const PrivateRoute = () => {
  const [isAuthenticated] = useState(false); // Simule a autenticação aqui
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Signup />} />
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Home />} />
        {/* <Route path="/devices" element={<Devices />} />
        <Route path="/devices/register" element={<DeviceRegistration />} />
        <Route path="/notifications" element={<Notifications />} /> */}
      </Route>
    </Routes>
  );
}

export default App;