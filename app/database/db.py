from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase,declarative_base
from sqlalchemy_utils import database_exists, create_database # type: ignore
from sqlalchemy import MetaData
import logging
from ..core.config import settings
from ..models.Base import Base


url = ""

if settings.MODE == "TEST":
    url = settings.BD_URL_TEST
    logging.debug("TEST MODE")
else:
    url = settings.DB_URL
    logging.info("PROD MODE")

#logging.basicConfig(level=logging.DEBUG)
#url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
#url = "sqlite+aiosqlite://"

engine = create_async_engine(url=url,pool_size=100,max_overflow=200,)

if settings.MODE == "TEST":
    engine = create_async_engine(url=url)


#if not database_exists(engine.url):
#    create_database(engine.url)

async_session_maker = async_sessionmaker(engine,class_=AsyncSession,expire_on_commit=False,autoflush=False,autocommit=False,)



#class Base(DeclarativeBase):
#    abstract = True
#    pass

#Base = declarative_base()

async def get_async_session():
    #await create_tables()
    async with async_session_maker() as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

