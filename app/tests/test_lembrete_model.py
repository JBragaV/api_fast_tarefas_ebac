from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.database.models.lembretes import Lembretes


@pytest.mark.asyncio
async def test_criar_lembrete_com_valores_padrao(sessao_teste):
    lembrete = Lembretes(nome="Estudar FastAPI")

    sessao_teste.add(lembrete)
    await sessao_teste.commit()
    await sessao_teste.refresh(lembrete)

    assert isinstance(lembrete.id, int)
    assert lembrete.id > 0
    assert lembrete.nome == "Estudar FastAPI"
    assert lembrete.descricao is None
    assert lembrete.concluida is False
    assert isinstance(lembrete.create_at, datetime)
    assert isinstance(lembrete.updated_at, datetime)


@pytest.mark.asyncio
async def test_salvar_descricao_e_conclusao(sessao_teste):
    lembrete = Lembretes(
        nome="Estudar FastAPI",
        descricao="Praticar testes com pytest.",
        concluida=True,
    )

    sessao_teste.add(lembrete)
    await sessao_teste.commit()
    await sessao_teste.refresh(lembrete)

    id_lembrete = lembrete.id

    sessao_teste.expunge_all()

    salvo = await sessao_teste.get(Lembretes, id_lembrete)

    assert salvo is not None
    assert salvo.nome == "Estudar FastAPI"
    assert salvo.descricao == "Praticar testes com pytest."
    assert salvo.concluida is True


@pytest.mark.asyncio
async def test_rejeitar_lembrete_sem_nome(sessao_teste):
    lembrete = Lembretes(descricao="Lembrete sem título")

    sessao_teste.add(lembrete)

    with pytest.raises(IntegrityError):
        await sessao_teste.commit()
    await sessao_teste.rollback()


@pytest.mark.asyncio
async def test_atualizar_data_de_modificacao(sessao_teste):
    lembrete = Lembretes(
        nome="Estudar FastAPI",
        updated_at=datetime(2000, 1, 1, tzinfo=UTC),
    )

    sessao_teste.add(lembrete)
    await sessao_teste.commit()
    await sessao_teste.refresh(lembrete)

    criacao_original = lembrete.create_at
    atualizacao_original = lembrete.updated_at

    lembrete.nome = "Estudar SQLAlchemy"

    await sessao_teste.commit()
    await sessao_teste.refresh(lembrete)

    assert lembrete.nome == "Estudar SQLAlchemy"
    assert lembrete.updated_at != atualizacao_original
    assert lembrete.create_at == criacao_original


def test_representacao_do_lembrete():
    lembrete = Lembretes(
        id=1,
        nome="Estudar FastAPI",
        concluida=False,
    )

    assert repr(lembrete) == ("id: 1 -- Titulo: Estudar FastAPI -- Concluida: False")
