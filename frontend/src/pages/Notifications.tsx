import React, { useEffect, useState } from "react";
import styled from "styled-components";
import {
  getDevices,
  getNotifications,
  createNotification,
} from "../services/api";
import { socket } from "../services/websocket"; // Importa a instância do socket

// --- Interfaces de Dados ---
interface Device {
  uuid: string;
  name: string;
}

interface NotificationRule {
  id: number;
  device_uuid: string | null;
  parameter: string;
  operator: string;
  threshold: number;
  message: string;
  created_at: string;
}

// --- Estilos dos Componentes ---
const NotificationsContainer = styled.div`
  padding: 40px;
  h1 {
    color: #007bff;
    margin-bottom: 10px;
  }
  p {
    color: #a0a0a0;
    margin-bottom: 20px;
  }
`;

const FormSection = styled.div`
  background-color: #21222c;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 40px;
  h2 {
    color: #e0e0e0;
    margin-bottom: 20px;
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
  label {
    font-size: 0.9rem;
    color: #a0a0a0;
  }
  input,
  select {
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #444;
    background-color: #1a1b26;
    color: #fff;
  }
`;

const Button = styled.button`
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 10px;

  &:hover {
    background-color: #0056b3;
  }
`;

const NotificationsListSection = styled.div`
  h2 {
    color: #e0e0e0;
    margin-bottom: 20px;
  }
`;

const NotificationCard = styled.div`
  background-color: #21222c;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 10px;
  border-left: 5px solid #007bff;
  color: #e0e0e0;
  p {
    margin: 5px 0;
    color: #c0c0c0;
  }
  span {
    font-weight: 600;
    color: #fff;
  }
`;

const RealTimeNotificationCard = styled.div`
  background-color: #21222c;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 10px;
  border-left: 5px solid #28a745; /* Cor para notificações em tempo real */
  animation: fadeIn 0.5s ease-in-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const Title = styled.h1`
  font-size: 3rem;
  font-weight: 700;
  color: #007bff;
  letter-spacing: -1px;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: #a0a0a0;
  margin-top: 5px;
`;

// --- Componente Principal ---
function Notifications() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [configuredNotifications, setConfiguredNotifications] = useState<
    NotificationRule[]
  >([]);
  const [realTimeAlerts, setRealTimeAlerts] = useState<any[]>([]); // Estado para alertas em tempo real
  const [formData, setFormData] = useState({
    device_uuid: "",
    parameter: "cpu_usage",
    operator: ">",
    threshold: 70,
    message: "",
  });

  // useEffect para buscar dados e configurar o WebSocket
  useEffect(() => {
    fetchDevices();
    fetchConfiguredNotifications();

    // Listener para o evento de notificação em tempo real
    socket.on("notification_event", (data) => {
      console.log("Alerta de notificação em tempo real recebido:", data);
      setRealTimeAlerts((prev) => [data, ...prev]);
    });

    // Limpeza dos listeners ao desmontar o componente
    return () => {
      socket.off("notification_event");
    };
  }, []); // Dependência vazia para rodar apenas uma vez na montagem do componente

  const fetchDevices = async () => {
    try {
      const response = await getDevices();
      setDevices(response.data);
    } catch (error) {
      console.error("Erro ao buscar dispositivos:", error);
    }
  };

  const fetchConfiguredNotifications = async () => {
    try {
      const response = await getNotifications();
      setConfiguredNotifications(response.data);
    } catch (error) {
      console.error("Erro ao buscar notificações:", error);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newNotification = await createNotification(formData);
      setConfiguredNotifications((prev) => [...prev, newNotification.data]);
      setFormData({
        device_uuid: "",
        parameter: "cpu_usage",
        operator: ">",
        threshold: 70,
        message: "",
      });
    } catch (error) {
      console.error("Erro ao criar notificação:", error);
    }
  };

  const getDeviceNameByUuid = (uuid: string | null) => {
    if (!uuid) return "Todos os dispositivos";
    const device = devices.find((d) => d.uuid === uuid);
    return device ? device.name : "Dispositivo desconhecido";
  };

  return (
    <NotificationsContainer>
      <Title>Notificações</Title>
      <Subtitle>Crie e gerencie suas regras de notificação.</Subtitle>

      <FormSection>
        <h2>Criar nova notificação</h2>
        <Form onSubmit={handleSubmit}>
          <InputGroup>
            <label htmlFor="device_uuid">Dispositivo</label>
            <select
              name="device_uuid"
              value={formData.device_uuid}
              onChange={handleInputChange}
            >
              <option value="">Todos os dispositivos</option>
              {devices.map((device) => (
                <option key={device.uuid} value={device.uuid}>
                  {device.name}
                </option>
              ))}
            </select>
          </InputGroup>

          <InputGroup>
            <label htmlFor="parameter">Parâmetro</label>
            <select
              name="parameter"
              value={formData.parameter}
              onChange={handleInputChange}
            >
              <option value="cpu_usage">Uso de CPU</option>
              <option value="ram_usage">Uso de RAM</option>
              <option value="temperature">Temperatura</option>
            </select>
          </InputGroup>

          <InputGroup>
            <label htmlFor="operator">Operador e Limite</label>
            <div style={{ display: "flex", gap: "10px" }}>
              <select
                name="operator"
                value={formData.operator}
                onChange={handleInputChange}
              >
                <option value=">">Maior que (&gt;)</option>
                <option value="<">Menor que (&lt;)</option>
                <option value=">=">Maior ou igual (&ge;)</option>
                <option value="<=">Menor ou igual (&le;)</option>
                <option value="==">Igual a (==)</option>
                <option value="!=">Diferente de (!=)</option>
              </select>
              <input
                type="number"
                name="threshold"
                value={formData.threshold}
                onChange={handleInputChange}
                required
              />
            </div>
          </InputGroup>

          <InputGroup>
            <label htmlFor="message">Mensagem da Notificação</label>
            <input
              type="text"
              name="message"
              value={formData.message}
              onChange={handleInputChange}
              required
            />
          </InputGroup>

          <Button type="submit">Salvar Regra</Button>
        </Form>
      </FormSection>

      <NotificationsListSection>
        <h2>Alertas em Tempo Real</h2>
        {realTimeAlerts.length > 0 ? (
          realTimeAlerts.map((alert, index) => (
            <RealTimeNotificationCard key={index}>
              <p>
                <span>ALERTA!</span> {alert.message} - Dispositivo: **
                {getDeviceNameByUuid(alert.device_uuid)}**
              </p>
            </RealTimeNotificationCard>
          ))
        ) : (
          <p>Nenhum alerta em tempo real.</p>
        )}
      </NotificationsListSection>

      <NotificationsListSection>
        <h2>Regras configuradas</h2>
        {configuredNotifications.length > 0 ? (
          configuredNotifications.map((rule) => (
            <NotificationCard key={rule.id}>
              <p>
                <span>Regra:</span> Se **{rule.parameter}** {rule.operator}{" "}
                {rule.threshold} em **{getDeviceNameByUuid(rule.device_uuid)}**,
                notificar: <br />
                <span>"{rule.message}"</span>
              </p>
            </NotificationCard>
          ))
        ) : (
          <p>Nenhuma regra de notificação configurada.</p>
        )}
      </NotificationsListSection>
    </NotificationsContainer>
  );
}

export default Notifications;
