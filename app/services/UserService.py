from app.schema import (
    UserCreate, 
    UserGet, 
    UserUpdate,
    UserResponse,
    UserBase,   
    ServiceAccessCreate,
    ServiceAccessUpdate,
    ServiceAccessGet,
    ServiceAccessCreate,
    ServiceAccessResponse,
)
from app.models import Users, ServicesAccess
from app.utils.patterns import IUnitOfWork, UnitOfWork
from uuid import UUID
from app.services.TokenJWT import get_user
from fastapi import Depends,HTTPException,status
from functools import wraps
from functools import wraps
from fastapi import HTTPException, status


credentials_exception_403_not_admin = HTTPException(
    status_code=403,
    detail="Forbidden: the user is not an administrator and can only change their own settings",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception_404_not_found_update = HTTPException(
    status_code=404,
    detail="User  not found",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception_409_not_update = HTTPException(
    status_code=409,
    detail="Already exists",
    headers={"WWW-Authenticate": "Bearer"},
)

def admin_or_self_or_permission_required(permission: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, current_user: UserGet, user_update: UserUpdate, *args, **kwargs):
            # Проверка, является ли пользователь администратором
            if current_user.is_superuser:
                # Администратор — доступ разрешён
                return await func(self, current_user, user_update, *args, **kwargs)
            # Проверяем наличие разрешения только если permission не None
            elif permission is not None:
                # Проверяем, меняет ли пользователь свои данные и проверяем наличие запрета доступа
                if current_user.uuid == user_update.uuid:
                    if current_user.access_user is not None:
                        has_permission = getattr(current_user.access_user, permission, True)
                        # Проверяем, разрешение  
                        if has_permission:
                            return await func(self, current_user, user_update, *args, **kwargs)
                    else:
                         return await func(self, current_user, user_update, *args, **kwargs)
                else:
                    raise credentials_exception_403_not_admin
            else:
                return await func(self, current_user, user_update, *args, **kwargs)        
            # Если ни одно из условий не выполнено, выбрасываем исключение
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: privileges, own data update, or specific permission required"
            )
        return wrapper
    return decorator


# Декоратор для проверки прав администратора
def admin_required(func):
    @wraps(func)
    async def wrapper(self, current_user: UserGet, *args, **kwargs):
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return await func(self, current_user, *args, **kwargs)
    return wrapper


# Декоратор для проверки прав администратора и что данные этого пользователя
def admin_or_own_date_required(func):
    @wraps(func)
    async def wrapper(self, current_user: UserGet, user_update: UserUpdate, *args, **kwargs):
        if not (current_user.is_superuser or current_user.uuid == user_update.uuid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return await func(self, current_user, *args, **kwargs)
    return wrapper

class UserService:
    """Service for working with data of users"""
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        

    async def create_user(self, user_data: UserCreate) -> UserGet:
            """Create new user"""
            async with self.uow:
                new_user = Users(
                    uuid=user_data.uuid,
                    username=user_data.username,
                    psevdonim=user_data.psevdonim,
                    email=user_data.email,
                    email_verified=user_data.email_verified,
                    phone=user_data.phone,
                    hashed_password=user_data.hashed_password,
                    is_active=user_data.is_active,
                    is_superuser=user_data.is_superuser,
                    role=user_data.role,
                    notes=user_data.notes,
                    created_at=user_data.created_at
                )
                await self.uow.users.add(new_user)
                await self.uow.commit()
                return UserGet.model_validate(new_user)
            
    @admin_required
    async def update_user(self,current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Update existing user"""
        async with self.uow:    
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)

            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(current_user, field, value)
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)


    async def _get_cur_user_or_changed_user(self,current_user: UserUpdate, change_user: UserUpdate)->UserUpdate:
        if current_user.uuid != change_user.uuid:
            user = await self.uow.users.get_by_identifier(change_user.uuid)
            if user is None:
                raise credentials_exception_404_not_found_update
            return UserUpdate.model_validate(**user)  
        return current_user    

    @admin_or_own_date_required
    async def get_user(self,current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Get user by UUID"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            return UserGet.model_validate(current_user)
     
    @admin_or_self_or_permission_required()    
    async def set_new_password(self,current_user: UserUpdate,user_data: UserUpdate) -> UserGet:
        """Set new password for user"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            current_user.hashed_password = user_data.hashed_password
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)

    @admin_required    
    async def set_email_verified(self,current_user: UserUpdate, user_data: UserUpdate,verified = True) -> UserGet:
        """Set email verified for user"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            current_user.email_verified = verified
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)

    @admin_required    
    async def update_user_role(self, current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Update user role"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            current_user.role = user_data.role
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)

    @admin_or_self_or_permission_required("notes")     
    async def update_user_notes(self,  current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Update user notes"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            current_user.notes = user_data.notes
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)
    
    @admin_or_self_or_permission_required("email") 
    async def update_email(self,  current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Update user email"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            users_email = await self.uow.users.list(filters={"email":user_data.email})
            if users_email:
                raise credentials_exception_409_not_update
            current_user.email = user_data.email
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)
        
    @admin_or_self_or_permission_required("username")     
    async def update_username(self,  current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Update user username"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            current_user.username = user_data.username
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)

    @admin_or_self_or_permission_required("psevdonim")     
    async def update_psevdonim(self,  current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Update user psevdonim"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            user_psevdonim = await self.uow.users.get_by_psevdonim(user_data.psevdonim)
            if user_psevdonim:
                raise credentials_exception_409_not_update
            current_user.psevdonim = user_data.psevdonim
            orm_user = Users(**current_user.model_dump(exclude_unset=True))
            await self.uow.users.update(orm_user)
            await self.uow.commit()
            return UserGet.model_validate(current_user)

    @admin_required
    async def delete_user(self,  current_user: UserUpdate, user_data: UserUpdate) -> None:
        """Delete user by UUID"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            await self.uow.users.delete(current_user.uuid)
            await self.uow.commit()

    @admin_or_self_or_permission_required()  
    async def activate_user(self,  current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Activate user"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            user = await self.uow.users.activate_user(current_user.uuid)
            await self.uow.commit()
            return UserGet.model_validate(user)

    @admin_or_self_or_permission_required()  
    async def deactivate_user(self, current_user: UserUpdate, user_data: UserUpdate) -> UserGet:
        """Deactivate user"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            user = await self.uow.users.deactivate_user(current_user.uuid)
            await self.uow.commit()
            return UserGet.model_validate(user)
    
    @admin_required    
    async def update_access(self, current_user: UserUpdate, user_data: UserUpdate,access_data: ServiceAccessCreate) -> UserGet:
        """Add set access to user"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            access =  current_user.access_user
            if access:
                for field, value in access_data.model_dump(exclude_unset=True).items():
                    setattr(current_user, field, value)
            orm_access = ServicesAccess(**access.model_dump(exclude_unset=True))
            await self.uow.services_access.update(orm_access)
            await self.uow.commit()
            user = await self.uow.users.get_by_identifier(current_user.uuid)
            return UserGet.model_validate(user)
    
    @admin_required    
    async def delete_access(self,  current_user: UserUpdate, user_data: UserUpdate,access_data: ServiceAccessGet) -> UserGet:
        """Delete access user"""
        async with self.uow:
            current_user = await self._get_cur_user_or_changed_user(current_user,user_data)
            if current_user.access_user:
                await self.uow.services_access.delete(current_user.access_user.id)
                await self.uow.commit()
            user = await self.uow.users.get_by_identifier(user_data.uuid)
            return UserGet.model_validate(user)
    
 

    # async def update_user(self,user_data: UserUpdate) -> UserGet:
    #     """Update existing user"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
            
    #         for field, value in user_data.model_dump(exclude_unset=True).items():
    #             setattr(user, field, value)
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def get_user(self, user_data: UserUpdate) -> UserGet:
    #     """Get user by UUID"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         return UserGet.model_validate(user)
        
    # async def set_new_password(self,user_data: UserUpdate) -> UserGet:
    #     """Set new password for user"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         user.hashed_password = user_data.hashed_password
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def set_email_verified(self, user_uuid: UUID) -> UserGet:
    #     """Set email verified for user"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         user.email_verified = True
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def set_email_unverified(self, user_uuid: UUID) -> UserGet:
    #     """Set email unverified for user"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         user.email_verified = False
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def update_user_role(self, user_data: UserUpdate) -> UserGet:
    #     """Update user role"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         user.role = user_data.role
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def update_user_notes(self, user_data: UserUpdate) -> UserGet:
    #     """Update user notes"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         if user_data.notes is None:
    #             raise ValueError("User notes is None")
    #         user.notes = user_data.notes
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
    
    # async def update_email(self, user_data: UserUpdate) -> UserGet:
    #     """Update user email"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         users_email = await self.uow.users.list(filters={"email":user_data.email})
    #         if users_email:
    #             raise ValueError("Email already exists other user")
    #         if user is None:
    #             raise ValueError("User not found")
    #         user.email = user_data.email
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def update_username(self, user_data: UserUpdate) -> UserGet:
    #     """Update user username"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         user.username = user_data.username
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def update_psevdonim(self, user_data: UserUpdate) -> UserGet:
    #     """Update user psevdonim"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         user_psevdonim = await self.uow.users.get_by_psevdonim(user_data.psevdonim)
    #         if user_psevdonim:
    #             raise ValueError("Psevdonim already exists other user")
    #         user.psevdonim = user_data.psevdonim
    #         await self.uow.users.update(user)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)

    # async def delete_user(self, user_uuid: UUID) -> None:
    #     """Delete user by UUID"""
    #     async with self.uow:
    #         await self.uow.users.delete(user_uuid)
    #         await self.uow.commit()

    # async def activate_user(self, user_uuid: UUID) -> UserGet:
    #     """Activate user"""
    #     async with self.uow:
    #         user = await self.uow.users.activate_user(user_uuid)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)

    # async def deactivate_user(self, user_uuid: UUID) -> UserGet:
    #     """Deactivate user"""
    #     async with self.uow:
    #         user = await self.uow.users.deactivate_user(user_uuid)
    #         await self.uow.commit()
    #         return UserGet.model_validate(user)
        
    # async def add_service(self,user_data: UserBase,servise_data: ServiceAccessCreate) -> UserGet:
    #     """Add service to user"""
    #     async with self.uow:
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         if user is None:
    #             raise ValueError("User not found")
    #         sers =  user.services_access
    #         if servise_data.service_name in sers:
    #             raise ValueError("Service already exists")
    #         servise = ServicesAccess(
    #             service_name=servise_data.service_name,
    #             user_uuid=servise_data.user_uuid,
    #             is_active=servise_data.is_active,
    #             access_level=servise_data.access_level
    #             )
    #         await self.uow.services_access.add(servise)
    #         await self.uow.commit()
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         return UserGet.model_validate(user)
        
    # async def delete_service(self,user_data: UserBase,servise_id: int) -> UserGet:
    #     """Delete service from user"""
    #     async with self.uow:
    #         ser = await self.uow.services_access.get_by_identifier(servise_id)
    #         if ser is None:
    #             raise ValueError("Service not found")
    #         if ser.user_uuid == user_data.uuid:
    #             raise ValueError("User not have this service")
    #         await self.uow.services_access.delete(servise_id)
    #         await self.uow.commit()
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         return UserGet.model_validate(user)
    # async def update_service(self,user_data: UserBase,servise_data: ServiceAccessUpdate) -> UserGet:
    #     """Update service"""
    #     async with self.uow:
    #         ser = await self.uow.services_access.get_by_identifier(servise_data.id)
    #         if ser is None:
    #             raise ValueError("Service not found")
    #         if ser.user_uuid == user_data.uuid:
    #             raise ValueError("User not have this service")
    #         ser.access_level = servise_data.access_level
    #         ser.is_active = servise_data.is_active
    #         await self.uow.services_access.update(ser)
    #         await self.uow.commit()
    #         user = await self.uow.users.get_by_identifier(user_data.uuid)
    #         return UserGet.model_validate(user)

        

        



