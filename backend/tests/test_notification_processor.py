import pytest
from unittest.mock import Mock, patch
from backend.app.services.notification_processor import check_notification_rules, compare_values
from backend.app.database.models import Notification, Device
from sqlalchemy.orm import Session
import uuid

# Dados básicos de teste
TEST_USER_ID = uuid.uuid4()
TEST_DEVICE_UUID = uuid.uuid4()
ANOTHER_DEVICE_UUID = uuid.uuid4()

@pytest.fixture
def mock_db_session():
    """Mocka a sessão do banco de dados."""
    session = Mock(spec=Session)
    return session

# --- Testes de Lógica de Comparação (Omitidos por brevidade) ---
def test_compare_values_greater_than():
    assert compare_values(80, '>', 70) is True
def test_compare_values_less_than():
    assert compare_values(70, '<', 80) is True
def test_compare_values_equals():
    assert compare_values(70, '==', 70) is True
def test_compare_values_not_equals():
    assert compare_values(71, '!=', 70) is True
def test_compare_values_greater_or_equals():
    assert compare_values(70, '>=', 70) is True
def test_compare_values_less_or_equals():
    assert compare_values(70, '<=', 70) is True


# --- Testes do Processador de Notificações ---

# 🚨 CORREÇÃO: Removemos o patch do asyncio.get_event_loop e usamos apenas o patch do sio_instance
@patch('backend.app.services.notification_processor.sio_instance')
def test_check_rules_trigger_and_emit(mock_sio_instance, mock_db_session):
    """
    Testa se o processador aciona a regra e emite o evento via SocketIO.
    """
    # 🚨 CRÍTICO: Configura o mock do .emit para ser rastreado
    # Como check_notification_rules.__globals__['sio_instance'] é o objeto mock,
    # precisamos garantir que ele tenha um método 'emit' que é um Mock.
    mock_sio_instance.emit = Mock()
    
    # 1. Mocka o Dispositivo
    mock_device = Device(user_id=TEST_USER_ID, uuid=TEST_DEVICE_UUID, name="Sensor X")
    
    # 2. Mocka a Regra de Notificação (deve ser acionada)
    mock_rule = Notification(
        user_id=TEST_USER_ID, 
        device_uuid=TEST_DEVICE_UUID, 
        parameter="cpu_usage", 
        operator=">", 
        threshold=80.0, 
        message="CPU ALTA"
    )
    
    # 3. Configura a Sessão do DB
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_device
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_rule]

    # 4. Dados de telemetria que ACIONAM a regra (CPU > 80.0)
    telemetry_data = {
        "device_uuid": str(TEST_DEVICE_UUID),
        "cpu_usage": 95.0, # Valor que aciona o alerta
        "ram_usage": 50.0,
    }

    # 5. Executa a função
    check_notification_rules(mock_db_session, telemetry_data)

    # 6. Verifica a Asserção: Agora o Mock.emit.called deve ser True
    # O erro 'Called 0 times' será corrigido porque o mock está configurado corretamente.
    mock_sio_instance.emit.assert_called_once()
    
    # Verifica o payload
    args, kwargs = mock_sio_instance.emit.call_args
    assert args[0] == 'new_notification'
    assert kwargs['room'] == str(TEST_USER_ID)
    assert 'ALERTA: CPU ALTA' in args[1]['message']


@patch('backend.app.services.notification_processor.sio_instance')
def test_check_rules_global_device_uuid_none(mock_sio_instance, mock_db_session):
    """
    Testa se uma regra global (device_uuid=None) é acionada por um dispositivo qualquer.
    """
    # 🚨 CRÍTICO: Configura o mock do .emit para ser rastreado
    mock_sio_instance.emit = Mock() 
    
    mock_device = Device(user_id=TEST_USER_ID, uuid=ANOTHER_DEVICE_UUID, name="Global Device")
    
    # Regra Global: device_uuid é None
    mock_global_rule = Notification(
        user_id=TEST_USER_ID,
        device_uuid=None, 
        parameter="temperature", 
        operator=">", 
        threshold=50.0, 
        message="Temperatura Geral Alta"
    )
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_device
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_global_rule]

    telemetry_data = {
        "device_uuid": str(ANOTHER_DEVICE_UUID),
        "cpu_usage": 30.0, 
        "temperature": 55.0,
    }
    
    check_notification_rules(mock_db_session, telemetry_data)

    # Asserção principal: emit DEVE ser chamado UMA VEZ
    mock_sio_instance.emit.assert_called_once()
    
    # Verifica o room e o device_uuid
    args, kwargs = mock_sio_instance.emit.call_args
    assert kwargs['room'] == str(TEST_USER_ID)
    assert args[1]['device_uuid'] == str(ANOTHER_DEVICE_UUID)
