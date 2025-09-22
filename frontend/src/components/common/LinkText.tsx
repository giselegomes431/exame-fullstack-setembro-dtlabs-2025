import styled from 'styled-components';
import { Link } from 'react-router-dom';

export const LinkText = styled(Link)`
  font-size: 0.9rem;
  color: #007bff;
  text-align: center;
  text-decoration: none;
  transition: color 0.3s;

  &:hover {
    color: #00aaff;
  }
`;