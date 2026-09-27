import pytest
from pydantic import ValidationError

from app.database.schemas.tarefa_schema import (
    ListaTarefasResposta,
    TarefaAtualizar,
    TarefaCriar,
    TarefaResposta,
)


@pytest.fixture
def dados_tarefa():
    return {
        "nome": "Estudar FastAPI",
        "descricao": "Praticar testes com pytest.",
    }


@pytest.mark.parametrize("schema", [TarefaCriar, TarefaAtualizar])
def test_remove_espacos_nome_e_descricao(schema):
    tarefa = schema(
        nome="  Estudar FastAPI  ",
        descricao="  Praticar testes com pytest.  ",
    )

    assert tarefa.nome == "Estudar FastAPI"
    assert tarefa.descricao == "Praticar testes com pytest."


@pytest.mark.parametrize("schema", [TarefaCriar, TarefaAtualizar])
@pytest.mark.parametrize(
    ("campo", "mensagem"),
    [
        ("nome", "A tarefa deve ter um título."),
        ("descricao", "A tarefa deve ter uma descrição."),
    ],
)
def test_rejeita_campos_apenas_com_espacos(schema, campo, mensagem):
    dados = {
        "nome": "Estudar FastAPI",
        "descricao": "Praticar testes com pytest.",
    }
    dados[campo] = "   "

    with pytest.raises(ValidationError, match=mensagem):
        schema.model_validate(dados)


@pytest.mark.parametrize("schema", [TarefaCriar, TarefaAtualizar])
@pytest.mark.parametrize("campo", ["nome", "descricao"])
def test_rejeita_string_vazia(schema, campo):
    dados = {
        "nome": "Estudar FastAPI",
        "descricao": "Praticar testes com pytest.",
    }
    dados[campo] = ""

    with pytest.raises(ValidationError) as err:
        schema.model_validate(dados)

    assert any(
        item["loc"] == (campo,) and item["type"] == "string_too_short"
        for item in err.value.errors()
    )


@pytest.mark.parametrize("schema", [TarefaCriar, TarefaAtualizar])
@pytest.mark.parametrize("campo", ["nome", "descricao"])
def test_exige_nome_e_descricao(schema, campo, dados_tarefa):
    dados_tarefa.pop(campo)

    with pytest.raises(ValidationError) as erro:
        schema.model_validate(dados_tarefa)
    assert any(
        item["loc"] == (campo,) and item["type"] == "missing"
        for item in erro.value.errors()
    )


def test_tarefa_criada_nao_concluida_por_padrao(dados_tarefa):
    tarefa = TarefaCriar(**dados_tarefa)
    assert tarefa.concluida is False


def test_permite_criar_tarefa_concluida(dados_tarefa):
    tarefa = TarefaCriar(**dados_tarefa, concluida=True)
    assert tarefa.concluida is True


def test_resposta_criada_a_partir_de_atributos(dados_tarefa):
    dados_tarefa["id"] = 1
    dados_tarefa["concluida"] = False

    resposta = TarefaResposta.model_validate(dados_tarefa)

    assert resposta.model_dump() == {
        "id": 1,
        "nome": "Estudar FastAPI",
        "descricao": "Praticar testes com pytest.",
        "concluida": False,
    }


def test_lista_de_tarefas(dados_tarefa):
    resposta = ListaTarefasResposta(
        page=1,
        limit=10,
        tamanho=1,
        tarefas=[TarefaResposta(**dados_tarefa, id=1, concluida=False)],
    )
    assert resposta.page == 1
    assert resposta.limit == 10
    assert resposta.tamanho == 1
    assert len(resposta.tarefas) == 1
    assert isinstance(resposta.tarefas[0], TarefaResposta)
    assert resposta.tarefas[0].id == 1
