from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_usuarios import autenticar_usuario
from app.database.models.usuario import Usuario as UsuarioORM
from app.database.schemas.respostas_schema import ErroResposta, MensagemResposta
from app.database.schemas.usuario_schema import (
    ListaUsuarioResposta,
    UsuarioInput,
    UsuarioResposta,
    UsuarioUpdate,
)
from app.database.session import get_session
from app.messaging.kafka_producer import publicar_evento
from app.tasks.email_tasks import task_envio_email_boas_vindas
from app.utils.security import hash_senha
from app.utils.utils import pagina_e_limite_sao_validos

router = APIRouter(prefix="/users", tags=["Usuarios"])


type SessaoBanco = Annotated[AsyncSession, Depends(get_session)]
type UsuarioAutenticacao = Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)]


@router.post(
    "/",
    summary="Criar usuario no sistema",
    response_model=UsuarioResposta,
    responses={
        409: {"model": ErroResposta, "description": "E-mail ou username já cadastrados"}
    },
    status_code=status.HTTP_201_CREATED,
)
async def criar_usuario(usuario_input: UsuarioInput, session: SessaoBanco):
    usuario = usuario_input.model_dump(exclude={"password1", "password2"})
    novo_usuario = UsuarioORM(
        **usuario,
        hashed_password=hash_senha(usuario_input.password1.get_secret_value()),
    )
    session.add(novo_usuario)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail ou username já cadastrados",
        )
    await session.refresh(novo_usuario)
    task_envio_email_boas_vindas.delay(novo_usuario.nome, novo_usuario.email)
    await publicar_evento(
        "usuario.criado",
        {
            "id": novo_usuario.id,
            "nome": novo_usuario.nome,
            "username": novo_usuario.username,
            "email": novo_usuario.email,
        },
    )
    return UsuarioResposta.model_validate(novo_usuario)


@router.get(
    "/",
    summary="Listar Usuarios do sistema",
    response_model=ListaUsuarioResposta,
    response_description="Lista de usuários cadastrados",
    responses={
        404: {"model": ErroResposta, "description": "Nenhum usuário foi cadastrado"}
    },
)
async def list_users(
    session: SessaoBanco,
    _: UsuarioAutenticacao,
    page: int = 1,
    limit: int = 10,
    ordenacao: str | None = None,
):
    if not pagina_e_limite_sao_validos(page=page, limit=limit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page ou limit com valores inválidos",
        )
    qtd_usuario = (
        await session.scalar(select(func.count()).select_from(UsuarioORM)) or 0
    )
    if qtd_usuario == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum usuário achado"
        )

    query = select(UsuarioORM)
    if ordenacao:
        if ordenacao.lower() == "nome":
            query = query.order_by(UsuarioORM.nome)
        elif ordenacao.lower() == "username":
            query = query.order_by(UsuarioORM.username)
        elif ordenacao.lower() == "email":
            query = query.order_by(UsuarioORM.email)
    start = (page - 1) * limit
    query = query.offset(start).limit(limit)
    resultado = await session.scalars(query)
    usuarios_lista = [UsuarioResposta.model_validate(t) for t in list(resultado.all())]
    return ListaUsuarioResposta(
        page=page, limit=limit, tamanho=qtd_usuario, usuarios=usuarios_lista
    )


@router.get(
    "/{id_user}/",
    summary="Listar dados de usuário",
    response_model=UsuarioResposta,
    responses={
        404: {"model": ErroResposta, "description": "Usuário não foi encontrado"}
    },
)
async def list_user(id_user: int, session: SessaoBanco, _: UsuarioAutenticacao):
    usuario = await session.get(UsuarioORM, id_user)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar o usuario de id {id_user}.",
        )
    return UsuarioResposta.model_validate(usuario)


@router.put(
    "/{id_user}/",
    summary="Atualiza os dados do usuário",
    response_model=UsuarioResposta,
    responses={
        404: {"model": ErroResposta, "description": "Usuário não encontrado"},
        409: {
            "model": ErroResposta,
            "description": "E-mail ou username já cadastrados",
        },
    },
)
async def put_dados_usuario(
    id_usuario: int,
    usuario_dados: UsuarioUpdate,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
):
    usuario = await session.get(UsuarioORM, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {id_usuario} não foi encontrado",
        )
    # Inpede que o usuario envie uma string vazia para algum dos dados
    # dados_usuario_atualizado = usuario_dados.model_dump(exclude_unset=True, exclude={"password1", "password2"})
    # for campo, valor in dados_usuario_atualizado.items():
    #     setattr(usuario, campo, valor)

    usuario.nome = usuario_dados.nome if usuario_dados.nome else usuario.nome
    usuario.username = (
        usuario_dados.username if usuario_dados.username else usuario.username
    )
    usuario.email = usuario_dados.email if usuario_dados.email else usuario.email
    if usuario_dados.password1 is not None:
        usuario.hashed_password = hash_senha(usuario_dados.password1.get_secret_value())
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail ou username já cadastrados",
        )
    await session.refresh(usuario)
    return UsuarioResposta(
        id=usuario.id, nome=usuario.nome, email=usuario.email, username=usuario.username
    )


@router.delete(
    "/{id_user}/",
    summary="Deletar usuário do sistema",
    response_model=MensagemResposta,
    responses={
        404: {"model": ErroResposta, "description": "Usuário não foi encontrado"}
    },
)
async def delete_user(id_user: int, session: SessaoBanco, _: UsuarioAutenticacao):
    usuario = await session.get(UsuarioORM, id_user)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário de id {id_user} não foi localizado",
        )
    usernome = usuario.username
    await session.delete(usuario)
    await session.commit()
    return MensagemResposta(message=f"Usuário {usernome} apagado com sucesso")
