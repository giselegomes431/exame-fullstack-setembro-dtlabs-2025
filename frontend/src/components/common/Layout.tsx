import styled from 'styled-components';
import Header from './Header';
import Sidebar from './Sidebar';

const PageWrapper = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: #121212;
  color: #e0e0e0;
  font-family: 'Poppins', sans-serif;
`;

const MainContent = styled.main`
  flex-grow: 1;
  display: flex;
  flex-direction: column;
`;

const ContentArea = styled.div`
  flex-grow: 1;
  padding: 40px;
`;

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <PageWrapper>
      <Sidebar />
      <MainContent>
        <Header />
        <ContentArea>
          {children}
        </ContentArea>
      </MainContent>
    </PageWrapper>
  );
}

export default Layout;