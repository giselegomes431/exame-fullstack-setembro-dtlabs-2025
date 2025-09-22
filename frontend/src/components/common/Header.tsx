// src/components/common/Header.tsx
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const HeaderContainer = styled.header`
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 20px 40px;
  background-color: #1e1e1e;
  border-bottom: 1px solid #333;
  color: #e0e0e0;
  height: 80px;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const UserName = styled.span`
  font-weight: 500;
`;

const LogoutButton = styled.button`
  background-color: transparent;
  border: 1px solid #007bff;
  color: #007bff;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: #007bff;
    color: #fff;
  }
`;

function Header() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <HeaderContainer>
      <UserInfo>
        <UserName>Usuário</UserName> {/* Deixa um texto estático ou vazio */}
        <LogoutButton onClick={handleLogout}>
          Logout
        </LogoutButton>
      </UserInfo>
    </HeaderContainer>
  );
}

export default Header;