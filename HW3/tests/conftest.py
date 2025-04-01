import pytest
from src.auth.db import Base, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from main import app


#Создаем тестовую базу данных SQLite
TEST_DATABASE_URL="sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
test_session_maker = async_sessionmaker(autocommit=False, bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
async def create_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function", name="session")
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as test_session:
        app.dependency_overrides[get_async_session] = test_session
    yield test_session
    async with test_session_maker() as test_session:
        await test_session.close()


@pytest.fixture(scope="function", name="client")
async def client_fixture(session: AsyncSession):
    def get_session_override():
        return session

    app.dependency_overrides[get_async_session] = get_session_override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="module", name="registred_user")
def registred_user():
    return {"email": "test12@mail.ru",
          "password": "testpass12",
          "is_active": True,
          "is_superuser": False,
          "is_verified": False,
          "id": "3fa85f64-5717-4562-b3fc-2c963f66afa2",
          "name": "Test12"
          }


@pytest.fixture(scope="module", name="authorized_user")
def authorized_user():
    return {"username": "test12@mail.ru", "password": "testpass12"}


@pytest.fixture(scope="module", name="fake_user")
def fake_user():
    return {"username": "fake@mail.ru", "password": "fakepass"}