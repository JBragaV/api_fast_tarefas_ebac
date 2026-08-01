from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


# Tabela do banco de dados (SQLite) com suas colunas
class Tarefa(Base):
    __tablename__ = "tarefass"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    concluida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"id: {self.id} -- Titulo: {self.nome} -- Concluida: {self.concluida}"
