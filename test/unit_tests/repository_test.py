import pytest
import pytest_asyncio
from sqlalchemy import create_mock_engine,create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine,AsyncSession
from sqlalchemy.orm import Session
from app.models.Base import Base
from app.core import UserRole,AccessLevel,ServiceName
from app.models import Users, ServiceAccess
from app.utils.patterns import UsersRepository, ServiceAccessRepository
from app.schema import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserGet,
    ServiceAccessCreate,
    ServiceAccessUpdate,
    ServiceAccessGet,
    ServiceAccessResponse,
)
from typing import Sequence
import datetime
import uuid
import asyncio
from sqlalchemy import event
from  uuid import uuid4
from datetime import datetime


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
async def test_add_user_repos(db_session,user_data):
    rep = UsersRepository(db_session)
    user_test = UserCreate(**user_data).model_dump()  
    user_uuid = await rep.add(Users(**user_test) )  
    print(f'user uuid: {user_uuid}')
    assert user_uuid is not None


@pytest.mark.asyncio
async def test_get_user_repos(db_session,user_data):
    rep = UsersRepository(db_session)
    user_test = UserCreate(**user_data)
    user_test_dump = user_test.model_dump()  
    user  = await rep.add(Users(**user_test_dump) ) 
    assert user  is not None
    user:Users = await rep.get_by_identifier(user_test.uuid)
    assert user is not None
    print(user)

@pytest.mark.asyncio
async def test_update_user_repos(db_session,user_data):
    rep = UsersRepository(db_session)
    user_test = UserCreate(**user_data)
    user_test_dump = user_test.model_dump()  
    user:Users  = await rep.add(Users(**user_test_dump) ) 
    assert user  is not None
    user_update = UserUpdate(uuid=user.uuid, notes="1000")
    user = await rep.update_user(user_update)
    assert user is not None
    assert user.notes == "1000"
    print(user)

@pytest.mark.asyncio
async def test_delete_user_repos(db_session,user_data):
    rep = UsersRepository(db_session)
    user_test = UserCreate(**user_data)
    user_test_dump = user_test.model_dump()  
    user:Users  = await rep.add(Users(**user_test_dump) ) 
    tuuid  = user.uuid
    assert user  is not None
    await rep.delete(tuuid)
    user = await rep.get_by_identifier(tuuid)
    assert user  is None

@pytest.mark.asyncio    
async def test_get_all_user_repos(db_session,user_data):
    rep = UsersRepository(db_session)
    user_test = UserCreate(**user_data)
    #create 10 users
    for _ in range(10):
        user_test.uuid = uuid4()
        user_test.psevdonim = str(uuid4())
        user_test.email = str(uuid4())
        user_test_dump = user_test.model_dump()  
        await rep.add(Users(**user_test_dump) ) 
    users: list[Users] | None = await rep.list()
    assert users is not None
    assert len(users)== 10
    print([w  for w in users])


