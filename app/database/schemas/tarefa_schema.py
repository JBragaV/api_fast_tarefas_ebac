from pydantic import ConfigDict, Field, field_validator

from .base_schema import Base


class TarefaBase(Base):
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


class ListaTarefasResposta(Base):
    page: int
    limit: int
    tamanho: int
    tarefas: list[TarefaResposta]
