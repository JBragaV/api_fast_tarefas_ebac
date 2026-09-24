from .base_schema import Base


class MensagemResposta(Base):
    message: str


class ErroResposta(Base):
    detail: str
