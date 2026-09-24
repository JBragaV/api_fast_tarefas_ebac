from __future__ import annotations

from typing import Annotated

from core.redis import invalidar_cache, redis_client
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_usuarios import autenticar_usuario
from app.database.models.tarefa import Tarefa as TarefaORM
from app.database.schemas.respostas_schema import ErroResposta, MensagemResposta
from app.database.schemas.tarefa_schema import (
    ListaTarefasResposta,
    TarefaAtualizar,
    TarefaCriar,
    TarefaResposta,
)
from app.database.session import get_session
from app.utils.utils import pagina_e_limite_sao_validos

type SessaoBanco = Annotated[AsyncSession, Depends(get_session)]
type UsuarioAutenticacao = Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)]


router = APIRouter(
    prefix="/tarefa",
    tags=["Tarefa"],
)


@router.post(
    "/add/",
    response_model=TarefaResposta,
    summary="Cria uma tarefa nos registros",
    status_code=status.HTTP_201_CREATED,
    response_description="Tarefa criada com suecesso",
    tags=["Tarefa"],
)
async def add_tarefa(
    tarefa_nova: TarefaCriar,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> TarefaResposta:
    tarefa = TarefaORM(**tarefa_nova.model_dump())
    session.add(tarefa)
    await session.commit()
    await session.refresh(tarefa)
    await invalidar_cache("tarefa")
    return TarefaResposta.model_validate(tarefa)


@router.get(
    "/",
    summary="Listar todas as tarefas",
    response_model=ListaTarefasResposta,
    response_description="Lista das tarefas cadastradas",
    responses={
        404: {"model": ErroResposta, "description": "Nenhuma tarefa foi cadastrada"}
    },
    tags=["Tarefa"],
)
async def list_tarefas(
    session: SessaoBanco,
    _: UsuarioAutenticacao,
    page: int = 1,
    limit: int = 10,
    ordenacao: str | None = None,
) -> ListaTarefasResposta:
    if not pagina_e_limite_sao_validos(page=page, limit=limit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page ou limit com valores inválidos",
        )

    cache_key = f"tarefa:page={page}:limit={limit}:ordenacao={ordenacao}"
    cache = await redis_client.get(cache_key)
    if cache:
        return ListaTarefasResposta.model_validate_json(cache)

    qtd_tarefas = await session.scalar(select(func.count()).select_from(TarefaORM)) or 0

    if qtd_tarefas == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma tarefa foi cadastrada ainda!!!",
        )
    query = select(TarefaORM)
    if ordenacao:
        if ordenacao.lower() == "nome":
            print("NOME")
            query = query.order_by(TarefaORM.nome)
        elif ordenacao.lower() == "descricao":
            query = query.order_by(TarefaORM.descricao)
    start = (page - 1) * limit
    query = query.offset(start).limit(limit)
    resultado = await session.scalars(query)
    tarfas_lista = [TarefaResposta.model_validate(t) for t in list(resultado.all())]
    return ListaTarefasResposta(
        page=page, limit=limit, tamanho=qtd_tarefas, tarefas=tarfas_lista
    )


@router.put(
    "/atualizar/concluida/{id_tarefa}/",
    summary="Altera o estado de conclusão",
    response_model=TarefaResposta,
    response_description="Tarefa Atualizada",
    responses={
        404: {
            "model": ErroResposta,
            "description": "A tarefa informada não foi encontrada.",
        }
    },
    tags=["Tarefa"],
)
async def put_tarefa_concluida(
    id_tarefa: int,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> TarefaResposta:
    tarefa = await session.get(TarefaORM, id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar a tarefa com o id {id_tarefa}",
        )

    tarefa.concluida = not tarefa.concluida
    await session.commit()
    await session.refresh(tarefa)
    await invalidar_cache("tarefa")
    return TarefaResposta.model_validate(tarefa)


@router.put(
    "/atualizar/dados/{id_tarefa}/",
    summary="Altera as informações da tarefa",
    response_model=TarefaResposta,
    response_description="Dados da tarefa atualizados.",
    responses={
        404: {
            "model": ErroResposta,
            "description": "A tarefa informada não foi encontrada.",
        }
    },
    tags=["Tarefa"],
)
async def put_tarefa_dados(
    id_tarefa: int,
    tarefa_dados: TarefaAtualizar,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> TarefaResposta:
    tarefa = await session.get(TarefaORM, id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar a tarefa com o id {id_tarefa}",
        )

    tarefa.nome = tarefa_dados.nome
    tarefa.descricao = tarefa_dados.descricao
    await session.commit()
    await session.refresh(tarefa)
    await invalidar_cache("tarefa")
    return TarefaResposta.model_validate(tarefa)


@router.delete(
    "/delete/{id_tarefa}/",
    summary="Apaga uma tarefa pelo ID",
    response_model=MensagemResposta,
    response_description="Confirmação da exclusão",
    responses={
        404: {
            "model": ErroResposta,
            "description": "A tarefa informada não foi encontrada.",
        }
    },
    tags=["Tarefa"],
)
async def delete_tarefa(
    id_tarefa: int,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> MensagemResposta:
    tarefa = await session.get(TarefaORM, id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com o id {id_tarefa} não foi encontrada!!!",
        )
    nome = tarefa.nome
    await session.commit()
    await session.delete(tarefa)
    await invalidar_cache("tarefa")
    return MensagemResposta(message=f"{nome} apagada com sucesso!!!")
