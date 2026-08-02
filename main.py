from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models.base import Base
from app.database.models.tarefa import Tarefa as TarefaORM
from app.database.session import engine, get_session

Base.metadata.create_all(bind=engine)


# Segurança e autenticação API
# Básica
security = HTTPBasic()


def autenticar_usuario(credencial: Annotated[HTTPBasicCredentials, Depends(security)]):
    is_username_correct = secrets.compare_digest(credencial.username, usuario)
    is_password_correct = secrets.compare_digest(credencial.password, senha)
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )


# Variaveis globais
# Depêndencias
SessaoBanco = Annotated[Session, Depends(get_session)]
UsuarioAutenticacao = Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)]

# Inicialização da API
app = FastAPI(
    title="API de Tarefas",
    description="API para gerenciamento de tarefas em memória.",
    version="0.1.0",
    contact={"nome": "Jocimar Braga", "email": "jocimarcaiadobraga@gmail.com"},
)

usuario = "jocimar"
senha = "jocimar"


# Classes de validações
class Usuario(BaseModel):
    usuario: str
    senha: str


class TarefaBase(BaseModel):
    nome: str = Field(
        min_length=1,
        examples=["Estudar FastAPI"],
        description="Nome da tarefa.",
    )

    descricao: str = Field(
        min_length=1,
        examples=["Estudar modelos de resposta e tratamento de erros."],
        description="Descrição detalhada da tarefa.",
    )

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("A tarefa deve ter um título.")

        return valor

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("A tarefa deve ter uma descrição.")

        return valor


class TarefaCriar(TarefaBase):
    concluida: bool = Field(
        default=False,
        description="Indica se a tarefa foi concluída.",
    )


class TarefaAtualizar(TarefaBase):
    """
    Modelo utilizado para atualizar somente nome e descrição.

    O estado 'concluida' não é recebido nesse endpoint.
    """


class TarefaResposta(TarefaCriar):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        description="Identificador único da tarefa.",
    )


class ListaTarefasResposta(BaseModel):
    page: int
    limit: int
    tamanho: int
    tarefas: list[TarefaResposta]


class MensagemResposta(BaseModel):
    message: str


class ErroResposta(BaseModel):
    detail: str


# valiadações
def pagina_e_limite_sao_validos(page: int, limit: int) -> bool:
    return page >= 1 and limit >= 1


# Rotas
@app.get(
    "/",
    response_model=MensagemResposta,
    summary="Verifica o funcionamento da API",
    tags=["Sistema"],
)
def boas_vindas() -> MensagemResposta:
    return MensagemResposta(message="Hello Ebac")


@app.post(
    "/tarefa/",
    response_model=TarefaResposta,
    summary="Cria uma tarefa nos registros",
    status_code=status.HTTP_201_CREATED,
    response_description="Tarefa criada com suecesso",
    tags=["Tarefa"],
)
def add_tarefa(
    tarefa_nova: TarefaCriar,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> TarefaResposta:
    tarefa = TarefaORM(**tarefa_nova.model_dump())
    session.add(tarefa)
    session.flush()
    session.refresh(tarefa)

    return TarefaResposta.model_validate(tarefa)


@app.get(
    "/tarefas/",
    summary="Listar todas as tarefas",
    response_model=ListaTarefasResposta,
    response_description="Lista das tarefas cadastradas",
    responses={
        404: {"model": ErroResposta, "description": "Nenhuma tarefa foi cadastrada"}
    },
    tags=["Tarefa"],
)
def list_tarefas(
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

    # qtd_tarefas = session.scalar(select(func.count(TarefaORM.id))) or 0
    qtd_tarefas = (
        session.query(func.count(TarefaORM.id)) or 0
    )  # Documentação https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.count

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

    tarfas_lista = [
        TarefaResposta.model_validate(t) for t in list(session.scalars(query).all())
    ]
    return ListaTarefasResposta(
        page=page, limit=limit, tamanho=qtd_tarefas, tarefas=tarfas_lista
    )


@app.put(
    "/tarefa/concluida/{id_tarefa}/",
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
def put_tarefa_concluida(
    id_tarefa: int,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> TarefaResposta:
    tarefa = session.get(TarefaORM, id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar a tarefa com o id {id_tarefa}",
        )

    tarefa.concluida = not tarefa.concluida
    session.flush()
    session.refresh(tarefa)
    return TarefaResposta.model_validate(tarefa)


@app.put(
    "/tarefa/dados/{id_tarefa}/",
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
def put_tarefa_dados(
    id_tarefa: int,
    tarefa_dados: TarefaAtualizar,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> TarefaResposta:
    tarefa = session.get(TarefaORM, id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar a tarefa com o id {id_tarefa}",
        )

    tarefa.nome = tarefa_dados.nome
    tarefa.descricao = tarefa_dados.descricao

    session.flush()
    session.refresh(tarefa)

    return TarefaResposta.model_validate(tarefa)


@app.delete(
    "/tarefa/{id_tarefa}/",
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
def delete_tarefa(
    id_tarefa: int,
    session: SessaoBanco,
    _: UsuarioAutenticacao,
) -> MensagemResposta:
    tarefa = session.get(TarefaORM, id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com o id {id_tarefa} não foi encontrada!!!",
        )
    nome = tarefa.nome
    session.delete(tarefa)
    return MensagemResposta(message=f"{nome} apagada com sucesso!!!")
