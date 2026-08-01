from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ConfigDict, Field, field_validator
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


# Variaveis globais
tarefas: dict[int, TarefaCriar] = {}
# "nome", "descrição" e "concluída" (inicialmente como False).


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
        404: {"model": ErroResposta, "desciption": "Nenhuma tarefa foi cadastrada"}
    },
    tags=["Tarefa"],
)
def list_tarefas(
    _: Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)],
    page: int = 1,
    limit: int = 10,
    ordenacao: str | None = None,
) -> ListaTarefasResposta:
    if not pagina_e_limite_sao_validos(page=page, limit=limit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page ou limit com valores inválidos",
        )
    if not tarefas:
        # if not len(tarefas):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma tarefa foi cadastrada ainda!!!",
        )
    tarefas_ordenadas = {}
    if ordenacao:
        if ordenacao.lower() == "nome":
            tarefas_ordenadas = dict(sorted(tarefas.items(), key=lambda x: x[1].nome))  # type: ignore
        elif ordenacao.lower() == "descricao":
            tarefas_ordenadas = dict(
                sorted(tarefas.items(), key=lambda x: x[1].descricao)  # type: ignore
            )
    else:
        tarefas_ordenadas = tarefas
    start_page = (page - 1) * limit
    end_page = start_page + limit
    tarfas_lista = [
        TarefaResposta(id=i, **v.model_dump())
        for i, v in list(tarefas_ordenadas.items())
    ][start_page:end_page]
    return ListaTarefasResposta(
        page=page, limit=limit, tamanho=len(tarefas_ordenadas), tarefas=tarfas_lista
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
    credencial: Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)],
) -> TarefaResposta:
    tarefa = tarefas.get(id_tarefa, None)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar a tarefa com o id {id_tarefa}",
        )
    tarefa_concluida = tarefa.model_copy(update={"concluida": not tarefa.concluida})
    tarefas[id_tarefa] = tarefa_concluida
    return TarefaResposta(id=id_tarefa, **tarefa_concluida.model_dump())


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
    credencial: Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)],
) -> TarefaResposta:
    tarefa = tarefas.get(id_tarefa)
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível achar a tarefa com o id {id_tarefa}",
        )

    tarefa_atualizada = TarefaCriar(
        nome=tarefa_dados.nome,
        descricao=tarefa_dados.descricao,
        concluida=tarefa.concluida,
    )
    tarefas[id_tarefa] = tarefa_atualizada
    return TarefaResposta(id=id_tarefa, **tarefa_atualizada.model_dump())


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
    credencial: Annotated[HTTPBasicCredentials, Depends(autenticar_usuario)],
) -> MensagemResposta:
    tarefa = tarefas.get(id_tarefa, None)
    if not tarefa:
        raise HTTPException(
            status_code=404, detail=f"Tarefa com o id {id_tarefa} não foi encontrado!!!"
        )
    del tarefas[id_tarefa]
    return MensagemResposta(message=f"{tarefa.nome} apagada com suecesso!!!")
