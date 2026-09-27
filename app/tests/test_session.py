from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session


@pytest.mark.asyncio
async def test_get_session_sucesso():
    sessao = AsyncMock(spec=AsyncSession)

    with patch("app.database.session.SessionLocal") as fabrica:
        contexto = fabrica.return_value
        contexto.__aenter__.return_value = sessao
        contexto.__aexit__.return_value = False
        gerador = get_session()

        recebida = await anext(gerador)

        assert recebida is sessao
        fabrica.assert_called_once_with()

        with pytest.raises(StopAsyncIteration):
            await anext(gerador)

        sessao.rollback.assert_not_awaited()
        contexto.__aexit__.assert_awaited_once_with(None, None, None)


@pytest.mark.asyncio
async def test_get_session_rollback_em_caso_de_erro():
    sessao = AsyncMock(spec=AsyncSession)

    with patch("app.database.session.SessionLocal") as fabrica:
        contexto = fabrica.return_value
        contexto.__aenter__.return_value = sessao
        contexto.__aexit__.return_value = False

        gerador = get_session()

        recebida = await anext(gerador)

        assert recebida is sessao

        erro_original = ValueError("Falha durante a operação")

        with pytest.raises(ValueError, match="Falha durante a operação") as erro:
            await gerador.athrow(erro_original)

        assert erro.value is erro_original
        sessao.rollback.assert_awaited_once_with()
        contexto.__aexit__.assert_awaited_once()
