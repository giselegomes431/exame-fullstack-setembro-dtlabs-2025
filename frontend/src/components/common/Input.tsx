import styled from 'styled-components';

export const Input = styled.input`
  width: 93%;
  padding: 12px 16px;
  border: 1px solid #333;
  border-radius: 8px;
  background-color: #2a2a2a;
  color: #e0e0e0;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;

  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.3);
  }

  &::placeholder {
    color: #888;
  }
`;