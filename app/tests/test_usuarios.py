from unittest.mock import patch

import pytest

USUARIOS_URL = "/users/"


# TEST Rota POST
@pytest.mark.asyncio
@patch("app.router.usuarios.task_envio_email_boas_vindas.delay")  # Celery
@patch("app.router.usuarios.publicar_evento")  # Kafka
async def test_criar_usuario(mock_publicar, mock_task, client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    response = await client.post(USUARIOS_URL, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "NUNUELA CAIADO"
    assert "password1" not in data
    mock_task.assert_called_once()
    mock_publicar.assert_called_once()


@pytest.mark.asyncio
async def test_criar_usuario_senha_diferentes(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha456",
    }

    response = await client.post(USUARIOS_URL, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_usuario_email_duplicado(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }

    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        await client.post(USUARIOS_URL, json=payload)
        payload2 = payload.copy()
        payload2["username"] = "outronomequalquer"[:15]
        print(payload2)
        response = await client.post("/users/", json=payload2)
    assert response.status_code == 409


# TEST Rota GET List
@pytest.mark.asyncio
async def test_listar_usuarios_vazio(client):
    response = await client.get(USUARIOS_URL)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_usuarios_sucesso(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        await client.post(USUARIOS_URL, json=payload)

    response = await client.get(USUARIOS_URL)
    assert response.status_code == 200
    data = response.json()
    assert data["tamanho"] == 1
    assert data["usuarios"][0]["nome"] == "NUNUELA CAIADO"


@pytest.mark.asyncio
async def test_buscar_usuario_por_id_sucesso(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        user_criado = await client.post(USUARIOS_URL, json=payload)

    print(user_criado.json())
    id_usuario = user_criado.json()["id"]
    response = await client.get(f"{USUARIOS_URL}{id_usuario}/")

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "NUNUELA CAIADO"
    assert data["email"] == "nunulinda@email.com.br"


@pytest.mark.asyncio
async def test_buscar_usuario_id_nao_encontrado(client):
    response = await client.get(f"{USUARIOS_URL}999/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_usuario_sucesso(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }

    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        usuario_criado = await client.post(USUARIOS_URL, json=payload)
    print(usuario_criado.json())
    id_user = usuario_criado.json()["id"]
    response = await client.put(
        f"{USUARIOS_URL}{id_user}/", json={"nome": "Manuela Caiado"}
    )

    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Manuela Caiado"
    assert data["email"] == "nunulinda@email.com.br"


@pytest.mark.asyncio
async def test_atualizar_usuario_não_encontrado(client):
    response = await client.put(
        f"{USUARIOS_URL}999/", json={"nome": "TANTO FAZ tanto faz"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_usuario_senha(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        criado = await client.post(USUARIOS_URL, json=payload)

    id_user = criado.json()["id"]

    response = await client.put(
        f"{USUARIOS_URL}{id_user}/",
        json={"password1": "NovaSenha123", "password2": "NovaSenha123"},
    )

    assert response.status_code == 200
    assert "password1" not in response.json()


@pytest.mark.asyncio
async def test_atualizar_usuario_senhas_diferentes(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        criado = await client.post(USUARIOS_URL, json=payload)

    id_user = criado.json()["id"]

    response = await client.put(
        f"{USUARIOS_URL}{id_user}/",
        json={"password1": "Senha123", "password2": "SenhaDiferente456"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_atualizar_usuario_email_existente(client):
    payload1 = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    payload2 = {
        "nome": "OUTRA PESSOA AQUI",
        "email": "outra@email.com.br",
        "username": "outrapessoa",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        await client.post(USUARIOS_URL, json=payload1)
        criado2 = await client.post(USUARIOS_URL, json=payload2)

    id_user2 = criado2.json()["id"]
    response = await client.put(
        f"{USUARIOS_URL}{id_user2}/",
        json={"email": "nunulinda@email.com.br"},  # já pertence ao usuário 1
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_deletar_usuario_sucesso(client):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        criado = await client.post(USUARIOS_URL, json=payload)

    id_user = criado.json()["id"]

    response = await client.delete(f"{USUARIOS_URL}{id_user}/")
    assert response.status_code == 200

    # confirma que realmente sumiu
    busca = await client.get(f"{USUARIOS_URL}{id_user}/")
    assert busca.status_code == 404


@pytest.mark.asyncio
async def test_deletar_usuario_nao_encontrado(client):
    response = await client.delete(f"{USUARIOS_URL}9999/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_usuarios_paginacao_invalida(client):
    response = await client.get(f"{USUARIOS_URL}?page=0&limit=10")
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("campo", ["nome", "username", "email"])
async def test_listar_usuarios_ordenacao(client, campo):
    payload = {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }
    with (
        patch("app.router.usuarios.task_envio_email_boas_vindas.delay"),
        patch("app.router.usuarios.publicar_evento"),
    ):
        await client.post(USUARIOS_URL, json=payload)

    response = await client.get(f"{USUARIOS_URL}?ordenacao={campo}")
    assert response.status_code == 200
