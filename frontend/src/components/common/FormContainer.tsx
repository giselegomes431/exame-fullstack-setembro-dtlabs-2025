// src/components/common/FormContainer.tsx

import styled from 'styled-components';

export const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100vw;
  background-color: #121212;
  color: #e0e0e0;
  font-family: 'Poppins', sans-serif;
  padding: 20px;
  box-sizing: border-box;

  @media (max-width: 768px) {
    padding: 10px;
  }
`;

export const AuthCard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 40px;
  background-color: #1e1e1e;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 450px;

  /* Removido o align-items: center; e text-align: center; daqui */
  
  @media (max-width: 768px) {
    padding: 25px;
    max-width: 90%;
  }
`;

export const Title = styled.h2`
  font-size: 2.5rem;
  font-weight: 600;
  color: #007bff;
  text-align: center; /* Mantém a centralização do título */
  margin-bottom: 10px;
`;

export const Subtitle = styled.p`
  font-size: 1rem;
  color: #a0a0a0;
  text-align: center; /* Mantém a centralização do subtítulo */
  margin-bottom: 20px;

  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
`;