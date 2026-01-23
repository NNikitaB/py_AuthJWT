import pytest
from app.schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserGet,
    ServiceAccessCreate,
    ServiceAccessUpdate,
    ServiceAccessGet,
    ServiceAccessResponse,
)
from app.core import ServiceName, AccessLevel, UserRole
from  uuid import uuid4
from datetime import datetime


# Test for ServiceAccess schemas
@pytest.fixture
def service_access_data():
    return {
        "notes": True,
        "phone": True,
        "email": True,
        "psevdonim": True,
        "username": True,
        "user_uuid": uuid4(),
    }


# Test ServiceAccessCreate schema validation
def test_service_access_create(service_access_data):
    service_access = ServiceAccessCreate(**service_access_data)
    assert service_access.user_uuid is not None
    assert service_access.notes is True
    assert service_access.phone is True
    assert service_access.email is True
    assert service_access.psevdonim is True
    assert service_access.username is True

# Test ServiceAccessUpdate schema validation
def test_service_access_update():
    service_access_update = ServiceAccessUpdate(id=1, username=False)
    assert service_access_update.id == 1
    assert service_access_update.username == False

# Test ServiceAccessGet schema validation
def test_service_access_get(service_access_data):
    service_access_data['id'] = 1
    service_access_data['user_uuid'] = uuid4()
    service_access = ServiceAccessGet(**service_access_data)
    assert service_access.id == 1
    assert service_access.user_uuid is not None
    assert service_access.notes is True


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
    }


# Test UserCreate schema validation (including hashed_password and created_at)
def test_user_create(user_data):
    user_data['hashed_password'] = "hashed_password_value"
    user_data['created_at'] = datetime.now()
    user_create = UserCreate(**user_data)
    assert user_create.username == "john_doe"
    assert user_create.email == "john.doe@example.com"
    assert user_create.is_active is True
    assert user_create.role == UserRole.USER
    assert user_create.hashed_password == "hashed_password_value"
    assert isinstance(user_create.created_at, datetime)

# Test UserUpdate schema validation (optional fields like hashed_password and email_verified)
def test_user_update(user_data):
    user_data['hashed_password'] = "new_hashed_password"
    user_data['email_verified'] = True
    user_update = UserUpdate(**user_data)
    assert user_update.hashed_password == "new_hashed_password"
    assert user_update.email_verified is True

# Test UserGet schema validation (including access_user as a access ServiceAccessGet)
def test_user_get(user_data):
    user_data['email_verified'] = True
    user_data['access_user'] = ServiceAccessGet(id=1, user_uuid=uuid4())
    user_get = UserGet(**user_data)
    assert user_get.username == "john_doe"
    assert isinstance(user_get.access_user, ServiceAccessGet)

# Test UserResponse schema validation (for response containing user details and access_user)
def test_user_response(user_data):
    user_data['email_verified'] = True
    user_data["created_at"] = datetime.now()
    user_data['access_user'] = ServiceAccessGet(id=2, user_uuid=uuid4(), service_name=ServiceName.Donate,granted_at=datetime.now())
    user_response = UserResponse(**user_data)
    assert user_response.username == "john_doe"
    assert user_response.email_verified is True
    assert isinstance(user_response.access_user, ServiceAccessGet)
