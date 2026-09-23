from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session

router = APIRouter(prefix="/users", tags=["Usuarios"])


type SessaoBanco = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", summary="Listar Usuarios do sistema")
async def list_users(session: SessaoBanco):
    pass
