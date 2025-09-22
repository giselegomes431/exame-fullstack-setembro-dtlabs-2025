import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { getDevices } from '../services/api';
import { MiniChart } from '../components/common/MiniChart';
import { useNavigate } from 'react-router-dom';

// Tipagens para os dados
interface Telemetry {
  cpu_usage: number;
  ram_usage: number;
  temperature: number;
}

interface Device {
  uuid: string;
  name: string;
  sn: string;
  description: string;
  telemetry: Telemetry;
  history?: {
    cpu_usage: number[];
    ram_usage: number[];
    temperature: number[];
  }
}

// Estilos com Styled-components
const PageContainer = styled.div`
  padding: 40px;
  background-color: #121212;
  min-height: 100vh;
  width: 100vw;
  color: #e0e0e0;
  font-family: 'Poppins', sans-serif;
  box-sizing: border-box;
  overflow-x: hidden;

  @media (max-width: 768px) {
    padding: 20px;
  }
`;

const PageHeader = styled.header`
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 3rem; /* Aumenta o tamanho da fonte */
  font-weight: 700;
  color: #007bff; /* Cor primária */
  letter-spacing: -1px; /* Espaçamento entre letras */
`;

const Subtitle = styled.p`
  font-size: 1.2rem; /* Aumenta o tamanho da fonte */
  color: #a0a0a0;
  margin-top: 5px;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  border: 1px dashed #333; /* Adiciona uma borda tracejada */
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: #a0a0a0;
  font-size: 1.1rem;
`;

const Header = styled.header`
  margin-bottom: 40px;
  border-bottom: 1px solid #333;
  padding-bottom: 20px;
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
  background-color: #1e1e1e;
  border-radius: 12px;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
  }
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

function Home() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await getDevices();
        // Simulação de dados históricos para os mini-gráficos
        const devicesWithHistory = response.data.map((device: any) => ({
          ...device,
          history: {
            cpu_usage: Array.from({ length: 10 }, () => Math.floor(Math.random() * 100)),
            ram_usage: Array.from({ length: 10 }, () => Math.floor(Math.random() * 100)),
            temperature: Array.from({ length: 10 }, () => Math.floor(Math.random() * 60) + 20),
          },
        }));
        setDevices(devicesWithHistory);
      } catch (err) {
        setError('Não foi possível carregar os dispositivos.');
      } finally {
        setLoading(false);
      }
    };

    fetchDevices();
  }, []);

  if (loading) return <PageContainer>Carregando dispositivos...</PageContainer>;
  if (error) return <PageContainer style={{ textAlign: 'center' }}>{error}</PageContainer>;

  return (
    <PageContainer>
      <Header>
        <PageHeader>
        <Title>Dashboard</Title>
        <Subtitle>Resumo rápido dos seus dispositivos.</Subtitle>
      </PageHeader>
      </Header>
      <DevicesGrid>
        {devices.length > 0 ? (
          devices.map((device) => (
            <DeviceCard key={device.uuid} onClick={() => navigate(`/devices/${device.uuid}`)}>
              <CardTitle>{device.name}</CardTitle>
              <CardSubtitle>{device.description}</CardSubtitle>
              
              <StatItem>
                <StatLabel>Uso de CPU</StatLabel>
                <StatValue>{device.history?.cpu_usage.slice(-1)[0]}%</StatValue>
              </StatItem>
              <MiniChart 
                label="Uso de CPU" 
                data={device.history?.cpu_usage || []} 
                color="#007bff" 
              />
              
              <StatItem>
                <StatLabel>Uso de RAM</StatLabel>
                <StatValue>{device.history?.ram_usage.slice(-1)[0]}%</StatValue>
              </StatItem>
              <MiniChart 
                label="Uso de RAM" 
                data={device.history?.ram_usage || []} 
                color="#28a745" 
              />

              <StatItem>
                <StatLabel>Temperatura</StatLabel>
                <StatValue>{device.history?.temperature.slice(-1)[0]}°C</StatValue>
              </StatItem>
              <MiniChart 
                label="Temperatura" 
                data={device.history?.temperature || []} 
                color="#dc3545" 
              />
              
            </DeviceCard>
          ))
        ) : (
          <EmptyState>
          Nenhum dispositivo cadastrado.
          <br />Adicione um na página de registro.
        </EmptyState>
        )}
      </DevicesGrid>
    </PageContainer>
  );
}

export default Home;