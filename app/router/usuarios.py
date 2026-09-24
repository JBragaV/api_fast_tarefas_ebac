from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_usuarios import autenticar_usuario
from app.database.models.usuario import Usuario as UsuarioORM
from app.database.schemas.respostas_schema import ErroResposta
from app.database.schemas.usuario_schema import (
    ListaUsuarioResposta,
    UsuarioInput,
    UsuarioResposta,
)
from app.database.session import get_session
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
    return UsuarioResposta.model_validate(novo_usuario)


@router.get(
    "/",
    summary="Listar Usuarios do sistema",
    response_model=ListaUsuarioResposta,
    response_description="Lista das tarefas cadastradas",
    responses={
        404: {"model": ErroResposta, "description": "Nenhum usuário foi cadastrado"}
    },
    tags=["Tarefa"],
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
