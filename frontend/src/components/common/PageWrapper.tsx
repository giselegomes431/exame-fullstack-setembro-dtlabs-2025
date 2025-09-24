// src/components/common/PageWrapper.tsx
import styled from 'styled-components';

export const PageWrapper = styled.div`
  padding: 40px;
  background-color: #1a1b26;
  min-height: 100vh;
  width: 100%; /* Corrigido para 100% para evitar overflow horizontal */
  color: #c0c0c0;
  font-family: 'Poppins', sans-serif;
  box-sizing: border-box;
  overflow-x: hidden;

  @media (max-width: 768px) {
    padding: 20px;
  }
`;