// src/App.tsx

// Remove the BrowserRouter import
import { Routes, Route, Navigate, Outlet } from 'react-router-dom'; 
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Layout from './components/common/Layout'; 
import Devices from './pages/Devices';
import DeviceRegistration from './pages/DeviceRegistration';
import Notifications from './pages/Notifications';

// PrivateRoute component to protect routes
const PrivateRoute = () => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  return isAuthenticated ? (
    <Layout>
      <Outlet />
    </Layout>
  ) : (
    <Navigate to="/login" />
  );
};

function App() {
  return (
    // Remove the BrowserRouter tag here
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Signup />} />
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/devices" element={<Devices />} />
        <Route path="/devices/register" element={<DeviceRegistration />} />
        <Route path="/notifications" element={<Notifications />} />
      </Route>
    </Routes>
  );
}

export default App;