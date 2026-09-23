import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


usuario = "jocimar"
senha = "jocimar"


def autenticar_usuario(credencial: Annotated[HTTPBasicCredentials, Depends(security)]):
    is_username_correct = secrets.compare_digest(credencial.username, usuario)
    is_password_correct = secrets.compare_digest(credencial.password, senha)
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )
