import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.auth_usuarios import autenticar_usuario
from app.database.models.base import Base
from app.database.session import get_session
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_teste = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionTest = async_sessionmaker(
    bind=engine_teste, class_=AsyncSession, autoflush=False
)


async def get_session_teste():
    async with SessionTest() as session:
        yield session


app.dependency_overrides[get_session] = get_session_teste
app.dependency_overrides[autenticar_usuario] = lambda: None


@pytest_asyncio.fixture(autouse=True)
async def criar_tabelas():
    async with engine_teste.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_teste.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def sessao_teste(criar_tabelas):
    async with SessionTest() as session:
        yield session
