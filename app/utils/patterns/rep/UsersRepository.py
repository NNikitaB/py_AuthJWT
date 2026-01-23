from .repository import BaseSqlAsyncRepository
from app.models.Users import Users
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserGet,
)

class UsersRepository(BaseSqlAsyncRepository[Users]):

    def __init__(self, session: AsyncSession):
        super().__init__(session,Users)


    async def activate_user(self, uuid):
        """Activate user"""
        user = await self.get_by_identifier(uuid)
        if user:
            user.is_active = True
            await self.update(user)
            return user
        return None

    async def deactivate_user(self, uuid):
        """Deactivate user(easy clear)"""
        user = await self.get_by_identifier(uuid)
        if user:
            user.is_active = False
            await self.update(user)
            return user
        return None 
    
    async def update_user(self, user_update:UserUpdate):
        """update user"""
        user = await self.get_by_identifier(user_update.uuid)
        if user: 
            # Обновляем поля
            for field in user_update.__class__.model_fields:
                value = getattr(user_update, field)
                if value is not None:
                    setattr(user, field, value)
            user = await self.update(user)
            return user
        return None 
    
    async def get_by_email(self, email):
        """Get user by email"""
        return await self.list(filters={'email': email})
    async def get_by_username(self, username):
        """Get user by username"""
        return await self.list(filters={'username': username})
    async def get_by_phone(self, phone):
        """Get user by phone"""
        return await self.list(filters={'phone': phone})
    async def get_by_psevdonim(self, psevdonim):
        """Get user by psevdonim"""
        return await self.list(filters={'psevdonim': psevdonim})
    async def get_access_user(self, uuid):
        """Get access for user"""
        user = await self.get_by_identifier(uuid)
        if user:
            return user.access_user
        return None