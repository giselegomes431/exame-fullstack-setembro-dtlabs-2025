import styled from 'styled-components';
import Sidebar from './Sidebar';

const PageWrapper = styled.div`
  display: flex;
  height: 100vh; /* A altura total da página é 100% da viewport */
  background-color: #1a1b26;
  color: #c0c0c0;
  font-family: 'Poppins', sans-serif;
`;

const MainContent = styled.main`
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* O contêiner principal esconde o overflow vertical */
`;

const ContentArea = styled.div`
  flex-grow: 1; /* Ocupa todo o espaço vertical restante */
  padding: 40px;
  overflow-y: auto; /* Apenas esta área terá a barra de rolagem vertical */

  @media (max-width: 768px) {
    padding: 20px;
  }
`;

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <PageWrapper>
      <Sidebar />
      <MainContent>
        <ContentArea>
          {children}
        </ContentArea>
      </MainContent>
    </PageWrapper>
  );
}

export default Layout;