from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core import SysConfig

DATABASE_URL = SysConfig.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_session():
    with SessionLocal() as session:
        try:
            yield session
            print("O commit vai rolar agora aqui")
            session.commit()
        except Exception:
            session.rollback()
