from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_usuarios import autenticar_usuario
from app.database.schemas.respostas_schema import ErroResposta, MensagemResposta
from app.database.session import get_session

router = APIRouter(prefix="/users", tags=["Usuarios"])


type SessaoBanco = Annotated[AsyncSession, Depends(get_session)]
type UsuarioAutenticacao = Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)]


@router.get(
    "/",
    summary="Listar Usuarios do sistema",
    # response_model=ListaTarefasResposta,
    response_description="Lista das tarefas cadastradas",
    responses={
        404: {"model": ErroResposta, "description": "Nenhuma tarefa foi cadastrada"}
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

    return MensagemResposta(message="TOMA OS USUÁRIOS NO MEIO DA SUA TEMPORA!")
