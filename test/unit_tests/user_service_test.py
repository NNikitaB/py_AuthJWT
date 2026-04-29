import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from app.schema import ServiceAccessGet,ServiceAccessCreate, UserUpdate
from app.models import Users, ServiceAccess
from app.services.UserService import UserService



@pytest.mark.asyncio
async def test_update_access_self_user():
    """Тест, когда Admin обновляет свои доступы."""
    uow = AsyncMock()
    service = UserService(uow)

    user_uuid = uuid4()

    # Текущий пользователь (ORM)
    current_user = Users(uuid=user_uuid, username="selfuser",is_superuser=True)

    # Доступы (ORM)
    access_orm = ServiceAccess(
        id=1,
        user_uuid=user_uuid,
        email=True,
        phone=True
    )
    

    # Настройка моков
    uow.users.get_by_identifier.return_value = current_user
    uow.services_access.get_by_user_uuid.return_value = access_orm

    # Схемы
    access_update = ServiceAccessCreate(user_uuid=user_uuid, email=False, phone=False)
    user_update = UserUpdate(uuid=user_uuid)
    cur_user = UserUpdate(uuid=user_uuid,is_superuser=True)

    # Запуск
    result = await service.update_access(cur_user, user_update,access_update)

    # Проверка
    assert isinstance(result, ServiceAccess)
    assert result.email is False
    assert result.phone is False
    uow.services_access.update.assert_awaited_once_with(access_orm)
    uow.commit.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_update_access_other_user():
#     """Тест, когда админ обновляет доступы другого пользователя."""
#     uow = AsyncMock()
#     service = UserService(uow)

#     admin_uuid = uuid4()
#     other_uuid = uuid4()

#     # Текущий пользователь — админ
#     admin_user = Users(uuid=admin_uuid, username="admin", role="admin",is_superuser=True)

#     # Целевой пользователь
#     other_user = Users(uuid=other_uuid, username="otheruser")

#     # Доступы (ORM)
#     access_orm = ServiceAccess(
#         id=2,
#         user_uuid=other_uuid,
#         email=True,
#         phone=True
#     )

#     # Настройка моков
#     uow.users.get_by_identifier.return_value = other_user
#     uow.services_access.get_by_user_uuid.return_value = access_orm

#     # Схемы
#     access_update = ServiceAccessCreate(user_uuid=other_uuid, email=False, phone=True)
#     user_update = UserUpdate(uuid=other_uuid)

#     # Запуск
#     result = await service.update_access(admin_user, user_update, access_update)

#     # Проверка
#     assert isinstance(result, ServiceAccess)
#     assert result.email is False
#     assert result.phone is True
#     uow.services_access.update.assert_awaited_once_with(access_orm)
#     uow.commit.assert_awaited_once()
