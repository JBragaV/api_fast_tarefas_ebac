from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from app.core.redis import invalidar_cache


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("origem", "chaves"),
    [
        ("tarefa", []),
        ("tarefa", ["tarefa:page=1"]),
        ("tarefa", ["tarefa:page=1", "tarefa:page=2"]),
        ("usuario", ["usuario:page=1"]),
    ],
)
async def test_invalidar_cache(origem, chaves):
    iterador = MagicMock()
    iterador.__aiter__.return_value = chaves

    with (
        patch(
            "app.core.redis.redis_client.scan_iter",
            new_callable=MagicMock,
            return_value=iterador,
        ) as scan_mock,
        patch(
            "app.core.redis.redis_client.delete",
            new_callable=AsyncMock,
            return_value=1,
        ) as delete_mock,
    ):
        await invalidar_cache(origem)

        scan_mock.assert_called_once_with(f"{origem}:*")

        assert delete_mock.await_args_list == [call(chave) for chave in chaves]
