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
    SpecificAccessGet,
    SpecificAccessCreate,
    SpecificAccessUpdate,
    SpecificAccessResponse,
    BaseUserRoleAccessGet,
    BaseUserRoleAccessCreate,
    BaseUserRoleAccessUpdate,
    BaseUserRoleAccessResponse,
)
from app.core import ServiceName, AccessLevel, UserRole
from  uuid import uuid4
from datetime import datetime


# Test for ServiceAccess schemas
@pytest.fixture
def service_access_data():
    return {
        "service_name": ServiceName.Default,
        "is_active": True,
        "access_level": AccessLevel.Admin,
        "granted_at": datetime.now(),
        "user_uuid": uuid4(),
        # id
    }



# Test for SpecificAccess schemas
@pytest.fixture
def service_specific_data():
    return {
        "service_name": ServiceName.Default,
        "name_access": "TestAccess",
        "is_active": True,
        "granted_at": datetime.now(),
        "user_uuid": uuid4(),
        # id
    }


# Test for BaseUserRoleAccess schemas
@pytest.fixture
def service_BaseUserRoleAccess_data():
    return {
        "notes": True,
        "phone": True,
        "email": True,
        "psevdonim": True,
        "username": True,
        "user_uuid": uuid4(),
        "id": 1,
    }


# Test for User schemas
@pytest.fixture
def user_data():
    return {
    "uuid": uuid4(),
    "username": "user",
    "email": "user@mail.test",
    "psevdonim": "test",
    "is_active": True,
    "is_superuser": False,
    "role": UserRole.USER,
    "notes": "About a",
    "phone": "77777777777",
    "email_verified": False,
    "hashed_password": "hashed_password_value",

    "access_user": None,
    "services_access": None, 
    "specific_access": None,
    }


# Begin BaseUserRoleAccess Tests
# Test BaseUserRoleAccessCreate schema validation
def test_BaseUserRoleAccessCreate(service_BaseUserRoleAccess_data):
    base_user_role_access = BaseUserRoleAccessCreate(**service_BaseUserRoleAccess_data)
    assert base_user_role_access.user_uuid is not None
    assert base_user_role_access.notes is True
    assert base_user_role_access.phone is True
    assert base_user_role_access.email is True
    assert base_user_role_access.psevdonim is True
    assert base_user_role_access.username is True


# Test BaseUserRoleAccessUpdate schema validation
def test_BaseUserRoleAccessUpdate():
    base_user_role_access_update = BaseUserRoleAccessUpdate(id=1, username=False,user_uuid=uuid4())
    assert base_user_role_access_update.id == 1
    assert base_user_role_access_update.username == False

#     service_access_data['granted_at'] = datetime.now()
#     service_access = ServiceAccessCreate(**service_access_data)
#     assert service_access.user_uuid is not None
#     assert service_access.service_name == ServiceName.Default
#     assert service_access.is_active is True
#     assert service_access.access_level == AccessLevel.Admin
#     assert isinstance(service_access.granted_at, datetime)


# Test BaseUserRoleAccessGet schema validation
def test_BaseUserRoleAccessGet(service_BaseUserRoleAccess_data):
    base_user_role_access_get = BaseUserRoleAccessGet(**service_BaseUserRoleAccess_data)
    assert base_user_role_access_get.user_uuid == service_BaseUserRoleAccess_data["user_uuid"]
    assert base_user_role_access_get.notes == service_BaseUserRoleAccess_data["notes"]
    assert base_user_role_access_get.id == service_BaseUserRoleAccess_data["id"]

    # assert isinstance(service_access.granted_at, datetime)
    # assert service_access.user_uuid is not None


# Begin ServiceAccess Tests
# Test ServiceAccessCreate schema validation
def test_service_access_create(service_access_data):
    service_access = ServiceAccessCreate(**service_access_data)
    assert service_access.user_uuid is not None
    assert service_access.service_name == ServiceName.Default
    assert service_access.is_active is True
    assert service_access.access_level  == AccessLevel.Admin
    assert service_access.granted_at is not None
    assert isinstance(service_access.granted_at, datetime)


# Test ServiceAccessUpdate schema validation
def test_service_access_update():
    service_access_update = ServiceAccessUpdate(id=1, service_name=ServiceName.ServicesRegistry)
    assert service_access_update.id == 1
    assert service_access_update.service_name == ServiceName.ServicesRegistry
    

# Test ServiceAccessGet schema validation
def test_service_access_get(service_access_data):
    service_access = ServiceAccessGet(**service_access_data,id=1)
    assert service_access.user_uuid == service_access_data["user_uuid"]
    assert service_access.granted_at == service_access_data["granted_at"]
    assert service_access.id == 1


# Begin User Tests
# Test UserCreate schema validation (including hashed_password and created_at)
def test_user_create(user_data):
    user_data['hashed_password'] = "hashed_password_value"
    user_data['created_at'] = datetime.now()
    user_create = UserCreate(**user_data)
    assert user_create.username == user_data["username"]
    assert user_create.email == user_data["email"]
    assert user_create.is_active == user_data["is_active"]
    assert user_create.role == user_data["role"]
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
    user_data['services_access'] = [ServiceAccessUpdate(id=2,user_uuid=user_data["uuid"])]
    user_get = UserGet(**user_data)
    assert user_get.username == user_data["username"]
    assert isinstance(user_get.services_access[0], ServiceAccessUpdate)


# Test UserResponse schema validation (for response containing user details and access_user)
def test_user_response(user_data):
    user_data['email_verified'] = True
    user_data["created_at"] = datetime.now()
    user_data['access_user'] = BaseUserRoleAccessGet(id=2, user_uuid=user_data["uuid"])
    user_response = UserResponse(**user_data)
    assert user_response.username == user_data["username"]
    assert user_response.email_verified is True
    assert isinstance(user_response.access_user, BaseUserRoleAccessGet)


# Begin SpecificAccess Tests
# Test SpecificAccessCreate schema validation 
def test_specific_access_create(service_specific_data):
    user_create = SpecificAccessCreate(**service_specific_data)
    assert user_create.service_name == service_specific_data["service_name"]
    assert user_create.name_access == service_specific_data["name_access"]
    assert user_create.is_active == service_specific_data["is_active"]
    assert user_create.user_uuid == service_specific_data["user_uuid"]


# # Test UserGet schema validation (including services_access as a list of ServiceAccessGet)
# def test_user_get(user_data):
#     user_data['email_verified'] = True
#     user_data['services_access'] = [ServiceAccessGet(id=1, user_uuid=uuid4(), service_name=ServiceName.Default,granted_at=datetime.now())]
#     user_get = UserGet(**user_data)
#     assert user_get.username == "john_doe"
#     assert isinstance(user_get.services_access, list)
#     assert isinstance(user_get.services_access[0], ServiceAccessGet)

# # Test UserResponse schema validation (for response containing user details and services_access)
# def test_user_response(user_data):
#     user_data['email_verified'] = True
#     user_data["created_at"] = datetime.now()
#     user_data['services_access'] = [
#         ServiceAccessGet(id=1, user_uuid=uuid4(), service_name=ServiceName.Default,granted_at=datetime.now()),
#         ServiceAccessGet(id=2, user_uuid=uuid4(), service_name=ServiceName.Donate,granted_at=datetime.now())
#         ]
#     user_response = UserResponse(**user_data)
#     assert user_response.username == "john_doe"
#     assert user_response.email_verified is True
#     assert isinstance(user_response.services_access, list)
#     assert isinstance(user_response.services_access[0], ServiceAccessGet)

