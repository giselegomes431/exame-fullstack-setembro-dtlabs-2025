import { useEffect, useState } from "react";
import styled from "styled-components";
import { getDevices, getLatestTelemetry } from "../services/api";
import { PageWrapper } from "../components/common/PageWrapper";

interface Device {
  uuid: string;
  name: string;
  description: string;
  history?: {
    cpu_usage: number[];
    ram_usage: number[];
    temperature: number[];
  };
}

interface HomePageProps {
  onLogout: () => void;
  userId: string | null;
}

const PageHeader = styled.header`
  margin-bottom: 40px;
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

const DevicesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const DeviceCard = styled.div`
  background-color: #21222c;
  border-radius: 12px;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  /* Removido o transition e o cursor, já que não é clicável */
`;

const CardTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: #e0e0e0;
`;

const CardSubtitle = styled.p`
  font-size: 0.9rem;
  color: #888;
  margin-top: -10px;
`;

const StatItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const StatLabel = styled.span`
  font-weight: 500;
  color: #a0a0a0;
`;

const StatValue = styled.span`
  font-weight: 600;
  color: #00e676;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  border: 1px dashed #333;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: #a0a0a0;
  font-size: 1.1rem;
`;

function Home(props: HomePageProps) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [latestTelemetry, setLatestTelemetry] = useState<any>({});

  useEffect(() => {
    const fetchDevicesAndTelemetry = async () => {
      try {
        // Busca os dispositivos do usuário
        const devicesResponse = await getDevices();
        setDevices(devicesResponse.data);

        // Busca a telemetria mais recente para esses dispositivos
        if (devicesResponse.data.length > 0) {
          const telemetryResponse = await getLatestTelemetry();
          setLatestTelemetry(telemetryResponse.data);
        }
      } catch (err) {
        setError("Não foi possível carregar os dispositivos e a telemetria.");
      } finally {
        setLoading(false);
      }
    };

    fetchDevicesAndTelemetry();
  }, []);

  if (loading) {
    return (
      <PageWrapper>
        <EmptyState>Carregando dispositivos...</EmptyState>
      </PageWrapper>
    );
  }

  if (error) {
    return (
      <PageWrapper>
        <EmptyState style={{ border: "1px dashed red", color: "red" }}>
          {error}
        </EmptyState>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <PageHeader>
        <Title>Dashboard</Title>
        <Subtitle>Resumo rápido dos seus dispositivos.</Subtitle>
      </PageHeader>

      <DevicesGrid>
        {devices.length > 0 ? (
          devices.map((device) => (
            <DeviceCard key={device.uuid}>
              <CardTitle>{device.name}</CardTitle>
              <CardSubtitle>{device.description}</CardSubtitle>

              <StatItem>
                <StatLabel>Uso de CPU</StatLabel>
                <StatValue>
                  {latestTelemetry[device.uuid]?.cpu_usage || "N/A"}%
                </StatValue>
              </StatItem>

              <StatItem>
                <StatLabel>Uso de RAM</StatLabel>
                <StatValue>
                  {latestTelemetry[device.uuid]?.ram_usage || "N/A"}%
                </StatValue>
              </StatItem>

              <StatItem>
                <StatLabel>Temperatura</StatLabel>
                <StatValue>
                  {latestTelemetry[device.uuid]?.temperature || "N/A"}°C
                </StatValue>
              </StatItem>
            </DeviceCard>
          ))
        ) : (
          <EmptyState>
            Nenhum dispositivo cadastrado.
            <br />
            Adicione um na página de registro.
          </EmptyState>
        )}
      </DevicesGrid>
    </PageWrapper>
  );
}

export default Home;
