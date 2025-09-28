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
import { register } from "../services/api";

interface SignupPageProps {
  onLoginSuccess: (data: any) => void;
}

function Signup({ onLoginSuccess }: SignupPageProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("As senhas não coincidem.");
      return;
    }
    try {
      await register({ username, password });
      onLoginSuccess({});
    } catch (err) {
      setError("Erro ao cadastrar. Tente outro nome de usuário.");
      console.error(err);
    }
  };

  return (
    <FormContainer>
      <AuthCard>
        <Title>Crie sua conta</Title>
        <Subtitle>Junte-se a nós e monitore seus dispositivos.</Subtitle>
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
          <Input
            type="password"
            placeholder="Confirme a senha"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <Button type="submit">Cadastrar</Button>
        </form>
        <LinkText to="/login">Já tem uma conta? Faça login</LinkText>
      </AuthCard>
    </FormContainer>
  );
}

export default Signup;
