import json
from unittest.mock import ANY, AsyncMock, patch

import pytest
from aiokafka import AIOKafkaProducer

import app.messaging.kafka_producer as kafka
from app.core.configs import SysConfig


@pytest.fixture(autouse=True)
def isolar_producer(monkeypatch):
    monkeypatch.setattr(kafka, "producer", None)


@pytest.fixture
def producer_mock():
    return AsyncMock(spec=AIOKafkaProducer)


@pytest.mark.asyncio
async def test_iniciar_producer(producer_mock):
    with patch(
        "app.messaging.kafka_producer.AIOKafkaProducer", return_value=producer_mock
    ) as classe_mock:
        await kafka.iniciar_producer()

        classe_mock.assert_called_once_with(
            bootstrap_servers=SysConfig.BOOTSTRAP_SERVER_KAFKA,
            value_serializer=ANY,
        )

        assert kafka.producer is producer_mock

        producer_mock.start.assert_awaited_once_with()

        serializador = classe_mock.call_args.kwargs["value_serializer"]

        evento = {"id": 1, "nome": "João", "ativo": True}

        restultado = serializador(evento)

        assert isinstance(restultado, bytes)
        assert json.loads(restultado.decode("utf-8")) == evento


@pytest.mark.asyncio
async def test_parar_producer(producer_mock, monkeypatch):
    monkeypatch.setattr(kafka, "producer", producer_mock)
    await kafka.parar_producer()

    producer_mock.stop.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_parar_sem_producer():
    resultado = await kafka.parar_producer()

    assert resultado is None
    assert kafka.producer is None


@pytest.mark.asyncio
async def test_publicar_evento(monkeypatch, producer_mock):
    monkeypatch.setattr(kafka, "producer", producer_mock)
    evento = {
        "id": 1,
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
    }
    await kafka.publicar_evento("usuario.criado", evento)

    producer_mock.send_and_wait.assert_awaited_once_with("usuario.criado", evento)


@pytest.mark.asyncio
async def test_publicar_sem_producer():
    resultado = await kafka.publicar_evento("usuario.criado", {"id": 1})
    assert resultado is None
    assert kafka.producer is None
