from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.models.base import Base
from app.database.schemas.respostas_schema import MensagemResposta
from app.database.session import engine
from app.router import tarefas, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Variaveis globais
# Depêndencias

# Inicialização da API
app = FastAPI(
    title="API de Tarefas",
    description="API para gerenciamento de tarefas em memória.",
    version="0.1.0",
    contact={"nome": "Jocimar Braga", "email": "jocimarcaiadobraga@gmail.com"},
    lifespan=lifespan,
)
app.include_router(tarefas.router)
app.include_router(usuarios.router)


# Rotas
@app.get(
    "/",
    response_model=MensagemResposta,
    summary="Verifica o funcionamento da API",
    tags=["Sistema"],
)
def boas_vindas() -> MensagemResposta:
    print("Chegguei")
    time.sleep(15)
    return MensagemResposta(message="Hello Ebac")


@app.get(
    "/async",
    response_model=MensagemResposta,
    summary="Verifica o funcionamento da API (assíncrono)",
    tags=["Sistema"],
)
async def boas_vindas_async() -> MensagemResposta:
    await asyncio.sleep(15)
    return MensagemResposta(message="Hello Ebac Async")
