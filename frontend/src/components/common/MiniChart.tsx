import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
} from 'chart.js';
import styled from 'styled-components';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip
);

const ChartContainer = styled.div`
  width: 100%;
  height: 80px;
  background-color: #2a2a2a;
  padding: 10px;
  border-radius: 8px;
`;

interface MiniChartProps {
  label: string;
  data: number[];
  color: string;
}

export const MiniChart = ({ label, data, color }: MiniChartProps) => {
  const chartData = {
    labels: data.map((_, i) => i + 1),
    datasets: [
      {
        label,
        data,
        borderColor: color,
        backgroundColor: 'transparent', // Fundo transparente
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { display: false },
      y: { display: false },
    },
    plugins: {
      tooltip: { enabled: true },
      legend: { display: false },
    },
    elements: {
      line: {
        tension: 0.4,
      },
    },
  };

  return (
    <ChartContainer>
      <Line data={chartData} options={options as any} />
    </ChartContainer>
  );
};