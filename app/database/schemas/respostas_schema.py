from .base_shcema import Base


class MensagemResposta(Base):
    message: str


class ErroResposta(Base):
    detail: str
