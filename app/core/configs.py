from __future__ import annotations


class SysConfig:
    """
    Classe responsável por centralizar as varíaveis do sistema.
    No futuro será intalado o dotenv e será criado o arquivo .env (Não feito)
    """

    DATABASE_URL = "sqlite+aiosqlite:///./livraria_ebac.db"
    DEBUG = True
