import styled from "styled-components";
import { NavLink, useNavigate } from "react-router-dom";
import {
  FaHome,
  FaMicrochip,
  FaBell,
  FaSignOutAlt,
  FaPlusSquare,
} from "react-icons/fa";

const SidebarContainer = styled.aside`
  width: 250px;
  background-color: #21222c;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-right: 1px solid #333;
  justify-content: space-between;
`;

const NavItems = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  border-radius: 8px;
  color: #a0a0a0;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;

  &:hover {
    background-color: #2a2c38;
    color: #e0e0e0;
  }

  &.active {
    background-color: #007bff;
    color: #fff;
    &:hover {
      background-color: #0056b3;
    }
  }
`;

const LogoutContainer = styled.div`
  margin-top: auto;
`;

const LogoutButton = styled.button`
  display: flex;
  align-items: center;
  width: 100%;
  gap: 15px;
  padding: 12px 15px;
  border-radius: 8px;
  background-color: transparent;
  color: #a0a0a0;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
  border: none;
  cursor: pointer;

  &:hover {
    background-color: #dc3545;
    color: #fff;
  }
`;

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <SidebarContainer>
      <NavItems>
        <NavItem to="/">
          <FaHome />
          Dashboard
        </NavItem>
        <NavItem to="/devices" end>
          <FaMicrochip />
          Devices (Gráficos)
        </NavItem>
        <NavItem to="/devices/register">
          <FaPlusSquare />
          Registro de Dispositivos
        </NavItem>
        <NavItem to="/notifications">
          <FaBell />
          Notifications
        </NavItem>
      </NavItems>
      <LogoutContainer>
        <LogoutButton onClick={handleLogout}>
          <FaSignOutAlt />
          Logout
        </LogoutButton>
      </LogoutContainer>
    </SidebarContainer>
  );
}

export default Sidebar;
