from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(25), index=True)
    email: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(
        String(15), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"id: {self.id} -- username: {self.username} -- E-mail: {self.email}"
