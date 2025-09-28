import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FormContainer,
  AuthCard,
  Title,
  Subtitle,
} from "../components/common/FormContainer";
import { Input } from "../components/common/Input";
import { Button } from "../components/common/Button";
import { LinkText } from "../components/common/LinkText";
import { login } from "../services/api";
import type { AuthResponse } from "../services/api";

interface LoginPageProps {
  onLoginSuccess: (data: AuthResponse) => void;
  isRegisterView?: boolean;
  onRegister?: (data: any) => Promise<void>;
}
function Login(props: LoginPageProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await login({ username, password });
      props.onLoginSuccess(response.data);
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("userId", response.data.user_id);
      navigate("/");
    } catch (err) {
      setError("Credenciais inválidas. Tente novamente.");
      console.error(err);
    }
  };

  return (
    <FormContainer>
      <AuthCard>
        <Title>Bem-vindo(a) de volta!</Title>
        <Subtitle>Faça login para continuar.</Subtitle>
        {error && (
          <p style={{ color: "#ff4d4d", textAlign: "center" }}>{error}</p>
        )}
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "20px" }}
        >
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
