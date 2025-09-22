// src/pages/Home.tsx
import React from 'react';
import styled from 'styled-components';

const HomeContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #121212;
  color: #e0e0e0;
  font-family: 'Poppins', sans-serif;
  font-size: 2rem;
  text-align: center;
`;

function Home() {
  return (
    <HomeContainer>
      <h1>Página Home em construção...</h1>
    </HomeContainer>
  );
}

export default Home;