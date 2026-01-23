import pytest
import pytest_asyncio
import asyncio
from uuid import uuid4
from app.models.Users import Users
from app.schema import UserCreate
from app.utils.patterns.uow import UnitOfWork
from sqlalchemy import event
from  uuid import uuid4
from datetime import datetime
from app.models.Base import Base
from app.core import UserRole,AccessLevel,ServiceName
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine,AsyncSession


@pytest.fixture
def user_data():
    return {
        "uuid": uuid4(),
        "username": "john_doe",
        "email": "john.doe@example.com",
        "psevdonim": "johnny",
        "is_active": True,
        "is_superuser": False,
        "role": UserRole.USER,
        "notes": "Test user",
        "phone": "123456789",
        "created_at":datetime.now(),
        "hashed_password":"dsfdfdefw",
    }
 

def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


@pytest_asyncio.fixture(scope="function")
async def db_session():
    url="sqlite+aiosqlite://"
    engine = create_async_engine(url=url,echo=True)
    #event.listen(engine, 'connect', _fk_pragma_on_connect)
    event.listen(engine.sync_engine, 'connect', _fk_pragma_on_connect)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        await session.begin()
        yield session
        await session.rollback()
 
@pytest.mark.asyncio
async def test_uow_add_and_commit(db_session):
    # Создаем UnitOfWork с сессией
    async with UnitOfWork(db_session) as uow:
        # Создаем тестового пользователя
        user_uuid = uuid4()
        user = Users(
            uuid=user_uuid,
            username="testuser",
            psevdonim="tester",
            email="testuser@example.com",
            email_verified=False,
            phone="1234567890",
            hashed_password="hashedpassword",
            is_active=False,
            is_superuser=False,
            role="user",
        )
        # Добавляем пользователя через репозиторий
        await uow.users.add(user)

        # Проверяем, что пользователь еще не в базе (транзакция не зафиксирована)
        user_in_db = await uow.users.get_by_identifier(user_uuid)
        assert user_in_db is not None  # В рамках сессии пользователь доступен

    # После выхода из контекста транзакция коммитится

    # Создаем новую сессию (или используем ту же, но с commit)
    async with UnitOfWork(db_session) as uow:
        user_in_db = await uow.users.get_by_identifier(user_uuid)
        assert user_in_db is not None
        assert user_in_db.email == "testuser@example.com"

@pytest.mark.asyncio
async def test_uow_rollback_on_error(db_session):
    user_uuid = uuid4()
    try:
        async with UnitOfWork(db_session) as uow:
            user = Users(
                uuid=user_uuid,
                username="testuser2",
                psevdonim="tester2",
                email="testuser2@example.com",
                email_verified=False,
                phone="0987654321",
                hashed_password="hashedpassword",
                is_active=False,
                is_superuser=False,
                role="user",
            )
            await uow.users.add(user)
            # Искусственно вызываем ошибку
            raise Exception("Force rollback")
    except Exception:
        pass

    # После rollback пользователь не должен быть в базе
    async with UnitOfWork(db_session) as uow:
        user_in_db = await uow.users.get_by_identifier(user_uuid)
        assert user_in_db is None
