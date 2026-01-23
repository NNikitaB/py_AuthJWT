import pytest
from sqlalchemy import create_mock_engine,create_engine,delete,update
from sqlalchemy.orm import Session
from app.models import Base,Users,UserRole,ServicesAccess
from app.core import AccessLevel,ServiceName
from datetime import  datetime, UTC
from sqlalchemy import event
import uuid

def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')



def test_create_db():
    """
    Creates a new SQLite database and initializes the database schema.
    """
    url = "sqlite://"
    engine = create_engine(url, echo=True)
    Base.metadata.create_all(engine)


@pytest.fixture(scope="module")
def db_session():
    url="sqlite://"
    engine = create_engine(url,echo=True)
    event.listen(engine, 'connect', _fk_pragma_on_connect)
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    #session.("PRAGMA foreign_keys = ON") 
    yield session
    session.rollback()
    session.close()


def test_add_user(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",
        )
    s = db_session
    s.add(user)
    s.commit()


def test_get_user(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",
        )
    s = db_session
    s.add(user)
    s.commit()
    user_from_db = s.query(Users).filter(Users.uuid == user.uuid).first()
    assert user_from_db.uuid == user.uuid

def test_delete_user(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",
        )
    s = db_session
    s.add(user)
    s.commit()
    s.execute(delete(Users).where(Users.uuid == user.uuid))


def test_update_user(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",
        )
    s = db_session
    s.add(user)
    s.commit()
    user.role = UserRole.ADMIN
    user.is_superuser = True
    user.notes = "Updated user"
    s.execute(update(Users).where(Users.uuid == user.uuid).values(role=user.role, is_superuser=user.is_superuser, notes=user.notes))
    user_from_db = s.query(Users).filter(Users.uuid == user.uuid).first()
    assert user_from_db.uuid == user.uuid

def test_add_user_service(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",       
        )
    serv = ServicesAccess(user_uuid=user.uuid)
    user.services_access = serv


    # serv1 = ServicesAccess(service_name=ServiceName.PreprocessingTable, access_level=AccessLevel.User, user_uuid=user.uuid)
    # serv2 = ServicesAccess(service_name=ServiceName.TimeSeries, access_level=AccessLevel.Pro, user_uuid=user.uuid)
    # user.services_access.append(serv1)
    # user.services_access.append(serv2)

    s = db_session
    s.add(user)
    s.commit()


def test_get_user_services(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",
        )
    serv = ServicesAccess(user_uuid=user.uuid)
    user.access_user = serv

    # serv1 = ServicesAccess(service_name=ServiceName.PreprocessingTable, access_level=AccessLevel.User, user_uuid=user.uuid)
    # serv2 = ServicesAccess(service_name=ServiceName.TimeSeries, access_level=AccessLevel.Pro, user_uuid=user.uuid)
    # user.services_access.append(serv1)
    # user.services_access.append(serv2)

    s = db_session
    s.add(user)
    s.commit()
    services_from_db = s.query(ServicesAccess).filter(ServicesAccess.user_uuid == user.uuid).all()
    assert len(services_from_db) == 1

def test_delete_user_services(db_session):
    id = uuid.uuid4()
    user = Users(
        uuid=id,
        username="test_user",
        psevdonim=f"test_user{id}",
        email=f"test{id}@example.com",
        email_verified=True,
        phone=None,
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
        notes="Test user",
        )
    serv = ServicesAccess(user_uuid=user.uuid)
    user.access_user = serv

    # serv1 = ServicesAccess(service_name=ServiceName.PreprocessingTable, access_level=AccessLevel.User, user_uuid=user.uuid)
    # serv2 = ServicesAccess(service_name=ServiceName.TimeSeries, access_level=AccessLevel.Pro, user_uuid=user.uuid)
    # user.services_access.append(serv1)
    # user.services_access.append(serv2)

    s = db_session
    s.add(user)
    s.commit()
    s.delete(user)
    s.commit()
    services_from_db = s.query(ServicesAccess).filter(ServicesAccess.user_uuid == user.uuid).all()
    assert len(services_from_db) == 0

