import pytest
import pytest_asyncio
from app.models import Users
from app.schema import UserBase,UserGet,ServiceAccessBase
from jose import JWTError, jwt
from app.services.TokenJWT import TokenJWT
from app.core.config import settings
from app.core import UserRole


@pytest.fixture
def user_get():
    """Создаем фиктивный объект UserGet для тестирования."""
    user = UserGet(
        uuid="123e4567-e89b-12d3-a456-426614174000",
        username="testuser",
        psevdonim="testnick",
        is_active=True,
        is_superuser=False,
        role="user",
        access_user=ServiceAccessBase()
    )
    user.access_user.email = False
    return user

@pytest.fixture
def token_service():
    """Создаем экземпляр класса, который будет тестироваться."""
    service = TokenJWT()
    return service

def test_create_user_access_service_tokens(token_service, user_get):
    access_token, refresh_token = token_service.create_user_access_service_tokens(user_get)
    
    # Проверяем, что токены созданы
    assert access_token is not None
    assert refresh_token is not None
    
    # Проверяем, что токены декодируются корректно
    access_payload = jwt.decode(access_token, token_service.secret_key, algorithms=[token_service.algorithm])
    assert access_payload["sub"] == str(user_get.uuid)
    assert access_payload["username"] == user_get.username
    assert access_payload["access_user"] == user_get.access_user.model_dump()

    refresh_payload = jwt.decode(refresh_token, token_service.secret_key, algorithms=[token_service.algorithm])
    assert refresh_payload["sub"] == str(user_get.uuid)

def test_verify_user_refresh_token(token_service, user_get):
    _, refresh_token = token_service.create_user_access_service_tokens(user_get)
    user_uuid = token_service.verify_user_refresh_token(refresh_token)
    
    assert user_uuid == str(user_get.uuid)

def test_verify_user_refresh_token_invalid(token_service):
    invalid_token = "invalidtoken"
    user_uuid = token_service.verify_user_refresh_token(invalid_token)
    
    assert user_uuid is None

def test_verify_user_access_token_get_access(token_service, user_get):
    access_token, _ = token_service.create_user_access_service_tokens(user_get)
    access = token_service.verify_user_access_token_get_access(access_token)
    
    assert access.email == user_get.access_user.email

def test_verify_user_access_token_get_access_invalid(token_service):
    invalid_token = "invalidtoken"
    access_user = token_service.verify_user_access_token_get_access(invalid_token)
    
    assert access_user is None

def test_verify_user_access_token_get_info(token_service, user_get):
    access_token, _ = token_service.create_user_access_service_tokens(user_get)
    user_info = token_service.verify_user_access_token_get_info(access_token)
    
    assert user_info is not None
    assert user_info["uuid"] == str(user_get.uuid)
    assert user_info["username"] == user_get.username
    assert user_info["is_active"] == user_get.is_active
    assert user_info["role"] == UserRole(user_get.role)

def test_verify_user_access_token_get_info_invalid(token_service):
    invalid_token = "invalidtoken"
    user_info = token_service.verify_user_access_token_get_info(invalid_token)
    
    assert user_info is None