import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FormContainer, AuthCard, Title, Subtitle } from '../components/common/FormContainer';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { LinkText } from '../components/common/LinkText';
import { login } from '../services/api';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await login({ username, password });
      localStorage.setItem('token', response.data.access_token);
      navigate('/');
    } catch (err) {
      setError('Credenciais inválidas. Tente novamente.');
      console.error(err);
    }
  };

  return (
    <FormContainer>
      <AuthCard>
        <Title>Bem-vindo(a) de volta!</Title>
        <Subtitle>Faça login para continuar.</Subtitle>
        {error && <p style={{ color: '#ff4d4d', textAlign: 'center' }}>{error}</p>}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <Input
            type="text"
            placeholder="Nome de usuário"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <Input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit">Entrar</Button>
        </form>
        <LinkText to="/register">Não tem uma conta? Cadastre-se</LinkText>
      </AuthCard>
    </FormContainer>
  );
}

export default Login;