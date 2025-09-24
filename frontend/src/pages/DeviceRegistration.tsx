import React, { useEffect, useState } from "react";
import styled from "styled-components";
import {
  getDevices,
  createDevice,
  updateDevice,
  deleteDevice,
} from "../services/api";
import { FaPlus, FaEdit, FaTrash } from "react-icons/fa";
import { PageWrapper } from "../components/common/PageWrapper";

// --- Interfaces de Dados ---
interface Device {
  uuid?: string;
  name: string;
  location: string;
  sn: string;
  description: string;
}

// --- Estilos dos Componentes ---
const RegistrationContainer = styled.div`
  flex: 1;
  padding: 30px;
  border-radius: 8px;
  min-height: calc(100vh - 80px - 80px);
`;

const DeviceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const DeviceItem = styled.div`
  background-color: #21222c;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 5px solid #28a745;
  color: #e0e0e0;
`;

const DeviceInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const DeviceName = styled.h3`
  margin: 0;
  color: #fff;
`;

const DeviceDetails = styled.span`
  font-size: 0.9em;
  color: #a0a0a0;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
`;

const IconButton = styled.button`
  background-color: transparent;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 1.2em;
  transition: color 0.2s ease;

  &:hover {
    color: #0056b3;
  }
`;

const CreateButton = styled.button`
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;

  &:hover {
    background-color: #0056b3;
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
`;

const ModalContent = styled.div`
  background: #2b2b3b;
  padding: 30px;
  border-radius: 10px;
  width: 400px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  color: #fff;
`;

const Input = styled.input`
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #444;
  background-color: #333;
  color: #fff;
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
function DeviceRegistration() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentDevice, setCurrentDevice] = useState<Device>({
    name: "",
    location: "",
    sn: "",
    description: "",
  });

  const fetchDevices = async () => {
    try {
      const response = await getDevices();
      setDevices(response.data);
    } catch (error) {
      console.error("Erro ao buscar dispositivos:", error);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCurrentDevice((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateOrUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentDevice) return;

    try {
      if (currentDevice.uuid) {
        const { name, location, sn, description } = currentDevice;
        await updateDevice(currentDevice.uuid, {
          name,
          location,
          sn,
          description,
        });
      } else {
        const { name, location, sn, description } = currentDevice;
        await createDevice({ name, location, sn, description });
      }
      setIsModalOpen(false);
      fetchDevices();
    } catch (error) {
      console.error("Erro ao salvar dispositivo:", error);
    }
  };

  const handleDelete = async (deviceId: string) => {
    if (window.confirm("Tem certeza que deseja excluir este dispositivo?")) {
      try {
        await deleteDevice(deviceId);
        fetchDevices();
      } catch (error) {
        console.error("Erro ao excluir dispositivo:", error);
      }
    }
  };

  const openModalForCreation = () => {
    setCurrentDevice({ name: "", location: "", sn: "", description: "" });
    setIsModalOpen(true);
  };

  const openModalForEdit = (device: Device) => {
    setCurrentDevice(device);
    setIsModalOpen(true);
  };

  return (
    <PageWrapper>
      <Title>Registro de Dispositivos</Title>
      <Subtitle>Gerencie seus dispositivos IoT aqui.</Subtitle>
      <RegistrationContainer>
        <CreateButton onClick={openModalForCreation}>
          <FaPlus /> Cadastrar Novo
        </CreateButton>
        <DeviceList>
          {devices.map((device) => (
            <DeviceItem key={device.uuid}>
              <DeviceInfo>
                <DeviceName>{device.name}</DeviceName>
                <DeviceDetails>
                  SN: {device.sn} | Local: {device.location}
                </DeviceDetails>
                <DeviceDetails>{device.description}</DeviceDetails>
              </DeviceInfo>
              <ActionButtons>
                <IconButton onClick={() => openModalForEdit(device)}>
                  <FaEdit />
                </IconButton>
                <IconButton
                  onClick={() => device.uuid && handleDelete(device.uuid)}
                >
                  <FaTrash />
                </IconButton>
              </ActionButtons>
            </DeviceItem>
          ))}
        </DeviceList>

        {isModalOpen && (
          <Modal>
            <ModalContent>
              <h2>
                {currentDevice.uuid
                  ? "Editar Dispositivo"
                  : "Cadastrar Dispositivo"}
              </h2>
              <form
                onSubmit={handleCreateOrUpdate}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "15px",
                }}
              >
                <Input
                  type="text"
                  name="name"
                  placeholder="Nome do dispositivo"
                  value={currentDevice.name}
                  onChange={handleInputChange}
                  required
                />
                <Input
                  type="text"
                  name="location"
                  placeholder="Localização"
                  value={currentDevice.location}
                  onChange={handleInputChange}
                  required
                />
                <Input
                  type="text"
                  name="sn"
                  placeholder="Número de Série (SN)"
                  value={currentDevice.sn}
                  onChange={handleInputChange}
                  required
                />
                <Input
                  type="text"
                  name="description"
                  placeholder="Descrição"
                  value={currentDevice.description}
                  onChange={handleInputChange}
                  required
                />
                <button
                  type="submit"
                  style={{
                    padding: "10px",
                    backgroundColor: "#007bff",
                    color: "#fff",
                    border: "none",
                    borderRadius: "5px",
                  }}
                >
                  {currentDevice.uuid ? "Salvar" : "Cadastrar"}
                </button>
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  style={{
                    padding: "10px",
                    backgroundColor: "#555",
                    color: "#fff",
                    border: "none",
                    borderRadius: "5px",
                  }}
                >
                  Cancelar
                </button>
              </form>
            </ModalContent>
          </Modal>
        )}
      </RegistrationContainer>
    </PageWrapper>
  );
}

export default DeviceRegistration;
