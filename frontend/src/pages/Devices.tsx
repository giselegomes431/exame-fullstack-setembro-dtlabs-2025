import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { getDevices } from "../services/api";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title as ChartTitle,
  Tooltip,
  Legend,
} from "chart.js";
import { PageWrapper } from "../components/common/PageWrapper";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ChartTitle,
  Tooltip,
  Legend
);

// --- Interfaces de Dados ---
interface Device {
  uuid: string;
  name: string;
}

interface HistoricalData {
  cpu_usage: number[];
  ram_usage: number[];
  temperature: number[];
}

// --- Estilos dos Componentes ---
const MainContent = styled.main`
  flex: 1;
  background-color: #21222c;
  padding: 30px;
  border-radius: 8px;
  min-height: calc(100vh - 80px - 80px);
`;

const FilterPanel = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;

  select {
    padding: 8px;
    border-radius: 5px;
    background-color: #1a1b26;
    color: #c0c0c0;
    border: 1px solid #333;
  }
`;

const ChartWrapper = styled.div`
  background-color: #1a1b26;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 50px;
  color: #777;
  border: 2px dashed #444;
  border-radius: 8px;
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

// --- Componente da Página ---
function Devices() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>("");
  const [historicalData, setHistoricalData] = useState<HistoricalData>({
    cpu_usage: [],
    ram_usage: [],
    temperature: [],
  });

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await getDevices();
        setDevices(response.data);
        if (response.data.length > 0) {
          setSelectedDevice(response.data[0].uuid);
          fetchHistoricalData(response.data[0].uuid);
        }
      } catch (error) {
        console.error("Erro ao buscar dispositivos:", error);
      }
    };
    fetchDevices();
  }, []);

  const fetchHistoricalData = async (
    uuid: string,
    period: string = "last_24h"
  ) => {
    try {
      // Simulação da chamada da API de telemetria
      console.log(
        `Buscando dados históricos para o dispositivo ${uuid} no período: ${period}`
      );
      const data = {
        cpu_usage: Array.from({ length: 24 }, () =>
          Math.floor(Math.random() * 100)
        ),
        ram_usage: Array.from({ length: 24 }, () =>
          Math.floor(Math.random() * 100)
        ),
        temperature: Array.from(
          { length: 24 },
          () => Math.floor(Math.random() * 60) + 20
        ),
      };
      setHistoricalData(data);
    } catch (error) {
      console.error("Erro ao buscar dados históricos:", error);
    }
  };

  const handleDeviceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const uuid = e.target.value;
    setSelectedDevice(uuid);
    fetchHistoricalData(uuid);
  };

  const handlePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (selectedDevice) {
      fetchHistoricalData(selectedDevice, e.target.value);
    }
  };

  const getChartOptions = (label: string) => ({
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
        labels: {
          color: "#c0c0c0",
        },
      },
      title: {
        display: true,
        text: label,
        color: "#e0e0e0",
      },
    },
    scales: {
      x: {
        grid: { color: "#333" },
        ticks: { color: "#c0c0c0" },
      },
      y: {
        grid: { color: "#333" },
        ticks: { color: "#c0c0c0" },
      },
    },
  });

  const getChartData = (data: number[], label: string, color: string) => ({
    labels: Array.from({ length: data.length }, (_, i) => `${i + 1}h`),
    datasets: [
      {
        label,
        data,
        borderColor: color,
        backgroundColor: `${color}40`,
        fill: true,
      },
    ],
  });

  return (
    <PageWrapper>
      <Title>Gráficos Históricos</Title>
      <Subtitle>
        Visualize a telemetria do seu dispositivo em tempo real.
      </Subtitle>
      <MainContent>
        {devices.length > 0 ? (
          <>
            <FilterPanel>
              <span>Dispositivo:</span>
              <select onChange={handleDeviceChange} value={selectedDevice}>
                {devices.map((device) => (
                  <option key={device.uuid} value={device.uuid}>
                    {device.name}
                  </option>
                ))}
              </select>

              <span>Período de Análise:</span>
              <select onChange={handlePeriodChange}>
                <option value="last_24h">Últimas 24h</option>
                <option value="last_7d">Últimos 7 dias</option>
                <option value="last_30d">Últimos 30 dias</option>
              </select>
            </FilterPanel>

            <ChartWrapper>
              <Line
                options={getChartOptions("Uso de CPU")}
                data={getChartData(
                  historicalData.cpu_usage,
                  "Uso de CPU (%)",
                  "#007bff"
                )}
              />
            </ChartWrapper>
            <ChartWrapper>
              <Line
                options={getChartOptions("Uso de RAM")}
                data={getChartData(
                  historicalData.ram_usage,
                  "Uso de RAM (%)",
                  "#28a745"
                )}
              />
            </ChartWrapper>
            <ChartWrapper>
              <Line
                options={getChartOptions("Temperatura")}
                data={getChartData(
                  historicalData.temperature,
                  "Temperatura (°C)",
                  "#dc3545"
                )}
              />
            </ChartWrapper>
          </>
        ) : (
          <EmptyState>
            <h1>Nenhum dispositivo cadastrado.</h1>
            <p>Por favor, cadastre um dispositivo na página de registro.</p>
          </EmptyState>
        )}
      </MainContent>
    </PageWrapper>
  );
}

export default Devices;
