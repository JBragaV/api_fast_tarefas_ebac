import json
from unittest.mock import ANY, AsyncMock, patch

import pytest

TAREFA_URL = "/tarefa/"


@pytest.fixture
def dados_tarefa():
    return {
        "nome": "Estudar FastApi",
        "descricao": "Estudo do fastapi para praticar teste",
    }


@pytest.mark.asyncio
async def test_criar_tarefa(dados_tarefa, client):
    with patch("app.router.tarefas.invalidar_cache") as redis:
        resposta = await client.post(TAREFA_URL, json=dados_tarefa)
        assert resposta.status_code == 201
        dado = resposta.json()
        assert dado["nome"] == "Estudar FastApi"
        assert dado["concluida"] is False
        redis.assert_called_once()


@pytest.mark.asyncio
async def test_criar_tarefa_sem_nome(dados_tarefa, client):
    dados_tarefa.pop("descricao")
    with patch("app.router.tarefas.invalidar_cache") as redis:
        resposta = await client.post(TAREFA_URL, json=dados_tarefa)
        assert resposta.status_code == 422
        redis.assert_not_awaited()


@pytest.mark.asyncio
async def test_criar_tarefa_sem_descricao(dados_tarefa, client):
    dados_tarefa.pop("nome")
    with patch("app.router.tarefas.invalidar_cache") as redis:
        resposta = await client.post(TAREFA_URL, json=dados_tarefa)
        assert resposta.status_code == 422
        redis.assert_not_awaited()


# List All
@pytest.mark.asyncio
async def test_listar_tarefas_sem_cache(client, dados_tarefa):
    with patch("app.router.tarefas.invalidar_cache"):
        await client.post(TAREFA_URL, json=dados_tarefa)

    with (
        patch(
            "app.router.tarefas.redis_client.get",
            new_callable=AsyncMock,
            return_value=None,
        ) as redis_get,
        patch(
            "app.router.tarefas.redis_client.set", new_callable=AsyncMock
        ) as redis_set,
    ):
        resposta = await client.get(TAREFA_URL)
        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados["tamanho"] == 1
        assert dados["tarefas"][0]["nome"] == dados_tarefa["nome"]
        cache_key = "tarefa:page=1:limit=10:ordenacao=None"
        redis_set.assert_called_once_with(cache_key, ANY, ex=30)
        redis_get.assert_called_once_with(cache_key)


@pytest.mark.asyncio
async def test_listar_tarefas_com_cache(client, dados_tarefa):
    with patch(
        "app.router.tarefas.invalidar_cache",
        new_callable=AsyncMock,
    ):
        criada = await client.post(TAREFA_URL, json=dados_tarefa)

    assert criada.status_code == 201

    tarefa_cache = {
        **criada.json(),
    }

    conteudo_cache = {
        "page": 1,
        "limit": 10,
        "tamanho": 1,
        "tarefas": [tarefa_cache],
    }

    with (
        patch(
            "app.router.tarefas.redis_client.get",
            new_callable=AsyncMock,
            return_value=json.dumps(conteudo_cache),
        ) as redis_get,
        patch(
            "app.router.tarefas.redis_client.set",
            new_callable=AsyncMock,
        ) as redis_set,
    ):
        resposta = await client.get(TAREFA_URL)

        assert resposta.status_code == 200
        assert resposta.json() == conteudo_cache

        cache_key = "tarefa:page=1:limit=10:ordenacao=None"
        redis_get.assert_awaited_once_with(cache_key)
        redis_set.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("ordenacao", "nomes_esperados"),
    [
        ("nome", ["Alfa", "Beta", "Gama"]),
        ("descricao", ["Beta", "Gama", "Alfa"]),
        ("NOME", ["Alfa", "Beta", "Gama"]),
        ("DESCRICAO", ["Beta", "Gama", "Alfa"]),
    ],
)
async def test_listar_tarefas_ordenadas(client, ordenacao, nomes_esperados):
    tarefas = [
        {"nome": "Gama", "descricao": "Segunda descricao"},
        {"nome": "Alfa", "descricao": "Terceira descricao"},
        {"nome": "Beta", "descricao": "Primeira descricao"},
    ]
    with (
        patch(
            "app.router.tarefas.invalidar_cache",
            new_callable=AsyncMock,
        ),
        patch(
            "app.router.tarefas.redis_client.get",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.router.tarefas.redis_client.set",
            new_callable=AsyncMock,
        ),
    ):
        for tarefa in tarefas:
            await client.post(TAREFA_URL, json=tarefa)

        resposta = await client.get(
            TAREFA_URL,
            params={"ordenacao": ordenacao},
        )

        assert resposta.status_code == 200

        nomes_recebidos = [tarefa["nome"] for tarefa in resposta.json()["tarefas"]]

        assert nomes_recebidos == nomes_esperados


@pytest.mark.asyncio
async def test_listar_pagina_invalida(client):
    response = await client.get(f"{TAREFA_URL}?page=0")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_listar_limite_invalido(client):
    response = await client.get(f"{TAREFA_URL}?limit=0")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_listar_tarefas_vazias(client):
    resposta = await client.get(TAREFA_URL)
    assert resposta.status_code == 404


# List 1

# Put


@pytest.mark.asyncio
async def test_put_tarefa_concluida(client, dados_tarefa):
    with patch("app.router.tarefas.invalidar_cache"):
        tarefa_criada = await client.post(TAREFA_URL, json=dados_tarefa)
        tarefa = tarefa_criada.json()
        id_tarefa = tarefa["id"]
        print(tarefa)
        tarefa["concluida"] = not tarefa["concluida"]
        resposta = await client.put(
            f"{TAREFA_URL}atualizar/concluida/{id_tarefa}/", json=tarefa
        )
        assert resposta.status_code == 200
        dado = resposta.json()
        print(dado)
        assert dado["concluida"] is True


@pytest.mark.asyncio
async def test_put_tarefa_dados(client, dados_tarefa):
    with patch("app.router.tarefas.invalidar_cache"):
        tarefa_criada = await client.post(TAREFA_URL, json=dados_tarefa)
        tarefa_criada = tarefa_criada.json()
        id_tarefa = tarefa_criada["id"]
        tarefa_criada["nome"] = "Nova Tarefa Criada"
        print(tarefa_criada)
        response = await client.put(
            f"{TAREFA_URL}atualizar/dados/{id_tarefa}/", json=tarefa_criada
        )

        assert response.status_code == 200
        dado = response.json()
        assert dado["nome"] == "Nova Tarefa Criada"


@pytest.mark.asyncio
async def test_put_tarefa_concluida_id_errado(client, dados_tarefa):
    resposta = await client.put(
        f"{TAREFA_URL}atualizar/concluida/999/", json=dados_tarefa
    )
    assert resposta.status_code == 404


@pytest.mark.asyncio
async def test_put_tarefa_dado_id_errado(client, dados_tarefa):
    resposta = await client.put(f"{TAREFA_URL}atualizar/dados/999/", json=dados_tarefa)
    assert resposta.status_code == 404


@pytest.mark.asyncio
async def test_delete_tarefa_id_correto(client, dados_tarefa):
    with patch("app.router.tarefas.invalidar_cache"):
        tarefa_criada = await client.post(TAREFA_URL, json=dados_tarefa)
        tarefa_criada = tarefa_criada.json()
        id_tarefa = tarefa_criada["id"]
        response = await client.delete(f"{TAREFA_URL}delete/{id_tarefa}/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_tarefa_id_incorreto(client):
    with patch("app.router.tarefas.invalidar_cache"):
        response = await client.delete(f"{TAREFA_URL}delete/999/")
        assert response.status_code == 404
