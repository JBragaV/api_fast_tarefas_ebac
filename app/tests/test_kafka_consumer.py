from unittest.mock import ANY, AsyncMock, patch

import pytest
from aiokafka import AIOKafkaConsumer

import app.messaging.kafka_consumer as kafka
from app.core.configs import SysConfig


@pytest.fixture
def consumer_mock():
    return AsyncMock(spec=AIOKafkaConsumer)


@pytest.mark.asyncio
async def test_consumir_mensagem(consumer_mock, capsys):
    mensagem = {"id": 1, "nome": "NUNUELA CAIADO"}

    consumer_mock.__aiter__.return_value = [mensagem]

    with patch(
        "app.messaging.kafka_consumer.AIOKafkaConsumer", return_value=consumer_mock
    ) as classe_mock:
        await kafka.consumir()

        classe_mock.assert_called_once_with(
            "usuario.criado",
            bootstrap_servers=SysConfig.BOOTSTRAP_SERVER_KAFKA,
            value_deserializer=ANY,
            group_id="grupo-usuario-criado",
        )

        consumer_mock.start.assert_awaited_once_with()
        consumer_mock.stop.assert_awaited_once_with()
        saida = capsys.readouterr()

        assert saida.out == f"Evento Recebido {mensagem}\n"

        desserializador = classe_mock.call_args.kwargs["value_deserializer"]

        dados = '{"id": 1, "nome": "João"}'.encode()

        assert desserializador(dados) == {
            "id": 1,
            "nome": "João",
        }


@pytest.mark.asyncio
async def test_consumir_iteracao_vazia(consumer_mock, capsys):
    consumer_mock.__aiter__.return_value = []

    with patch(
        "app.messaging.kafka_consumer.AIOKafkaConsumer",
        return_value=consumer_mock,
    ):
        await kafka.consumir()

    consumer_mock.start.assert_awaited_once_with()
    consumer_mock.stop.assert_awaited_once_with()
    assert capsys.readouterr().out == ""


@pytest.mark.asyncio
async def test_encerra_consumer_quando_iteracao_falha(consumer_mock):
    erro_original = RuntimeError("Falha ao consumir mensagens")

    consumer_mock.__aiter__.side_effect = erro_original

    with (
        patch(
            "app.messaging.kafka_consumer.AIOKafkaConsumer", return_value=consumer_mock
        ),
        pytest.raises(RuntimeError, match="Falha ao consumir mensagens") as erro,
    ):
        await kafka.consumir()
    assert erro.value is erro_original
    consumer_mock.start.assert_awaited_once_with()
    consumer_mock.stop.assert_awaited_once_with()
