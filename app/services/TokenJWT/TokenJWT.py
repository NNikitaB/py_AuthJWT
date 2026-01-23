from datetime import datetime, timedelta, UTC

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.database.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Users
from app.schema import UserBase,UserGet,ServiceAccessBase,UserResponse,UserUpdate
from jose import JWTError, jwt
from app.core.config import settings
from app.core import UserRole
from app.utils.patterns import UnitOfWork

from app.schema import UserBase,UserGet,ServiceAccessBase
from jose import JWTError, jwt
from app.config import settings

from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenJWT:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, data: dict):
        """Создание access токена"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict):
        """Создание refresh токена"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_refresh_token(self, token: str):
        """Проверка refresh токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_uuid: str|None = payload.get("sub") 
            if user_uuid is None:
                return None
            return user_uuid
        except JWTError:
            return None
        

    def create_user_access_services_tokens(self, user_base: UserGet)-> tuple[str, str]:
        """
            Create access and refresh tokens for a user with service access details.
        
            Args:
                user_base (UserGet): User information containing service access and profile details.
        
            Returns:
                tuple[str, str]: A tuple containing the access token and refresh token.
        
            The method generates two JWT tokens:
            1. An access token with service access levels and user UUID
            2. A refresh token with user profile information
            """
        
        to_encode = {}
        services = user_base.access_user.model_dump() if user_base.access_user is not None else None
        to_encode.update({"access_user": services})
        sub = str(user_base.uuid)
        to_encode.update({"sub": sub})
        to_encode.update({"username": user_base.username})
        to_encode.update({"psevdonim": user_base.psevdonim})
        to_encode.update({"is_active": user_base.is_active})
        to_encode.update({"is_superuser": user_base.is_superuser})
        to_encode.update({"role": user_base.role})
        services = [it.model_dump() for it in user_base.services_access]
        to_encode.update({"services": services})
        sub = {"uuid": str(user_base.uuid)}
        to_encode.update({"sub": sub})

        expire1 = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire1})
        access_token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        user_data = {
            "sub": str(user_base.uuid),
            }
        expire2 = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)
        user_data.update({"exp": expire2})
        refresh_token = jwt.encode(user_data, self.secret_key, algorithm=self.algorithm)
        
        return access_token, refresh_token
    
    def verify_user_refresh_token(self, token: str):
        """Проверка refresh токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_uuid: str|None = payload.get("sub")
            if user_uuid is None:
                return None
            return user_uuid
        except JWTError:
            return None
        

    def verify_user_access_token_get_services(self, token: str)->list[ServiceAccessBase]|None:
        """Проверка access токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_uuid: str|None = payload.get("sub")
            if user_uuid is None:
                return None
            access_user_dict: dict|None = payload.get("access_user")
            if access_user_dict is None:
                return None
            access_user: ServiceAccessBase = ServiceAccessBase(**access_user_dict)
            return access_user
        except JWTError:
            return None
        
    def verify_user_access_token_get_info(self, token: str)->dict|None:
        """Проверка access токена и получение данных
        returns:
        None 
        or 
        dict{
           uuid: UUID
           access_user: ServiceAccessBase
           is_active: bool
           is_superuser: bool
           role: UserRole
           username: str
           psevdonim: str
           }
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_uuid: str|None = payload.get("sub")
            dict_to = {"uuid": user_uuid}
            if user_uuid is None:
                return None
            access_user_dict: dict|None = payload.get("access_user")
            dict_to.update({"access_user": None})
            if access_user_dict is not None:
                access_user: ServiceAccessBase = ServiceAccessBase(**access_user_dict)
                dict_to.update({"access_user": access_user})

            dict_to.update({"is_active": payload.get("is_active")})
            dict_to.update({"is_superuser": payload.get("is_superuser")})
            dict_to.update({"username": payload.get("username")})
            dict_to.update({"psevdonim": payload.get("psevdonim")})
            dict_to.update({"role": UserRole(payload.get("role"))})

            return dict_to
            # TODO
            # servs: list|None = payload.get("services")
            # if servs is None:
            #     return None
            # services: list[ServiceAccessBase] = [ServiceAccessBase(**it) for it in servs]
            # return services
        except JWTError:
            return None
    


    
    def verify_access_token(self, token: str):
        """Проверка access токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_uuid: str|None = payload.get("sub")
            if user_uuid is None:
                return None
            return user_uuid
        except JWTError:
            return None

 # = Depends(oauth2_scheme),       
async def get_current_user(token: str, db: AsyncSession = Depends(get_async_session)):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_uuid: str|None = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(Users, UUID(user_uuid))
    if user is None:
        raise credentials_exception
    return user

credentials_exception_401 = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
credentials_exception_403 = HTTPException(
    status_code=403,
    detail="Forbidden: user is deactivated",
    headers={"WWW-Authenticate": "Bearer"},
)
credentials_exception_404 = HTTPException(
    status_code=404,
    detail="User not found",
    headers={"WWW-Authenticate": "Bearer"},
)

# async def get_user(token: str, uof: UnitOfWork) -> UserUpdate:
#     """Получение пользователя"""
#     try:
#         payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
#         user_uuid: str|None = payload.get("sub")
#         if user_uuid is None:
#             raise credentials_exception_401
#     except JWTError:
#         raise credentials_exception_401
#     user = await uof.users.get_by_identifier(UUID(user_uuid))
#     if user is None:
#         raise credentials_exception_404
#     if not user.is_active:
#         raise credentials_exception_403
#     return UserGet.model_validate(user)


async def get_user(token: str, uof: UnitOfWork) -> UserUpdate:
    """Получение пользователя"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_uuid: str|None = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception_401
    except JWTError:
        raise credentials_exception_401
    user = await uof.users.get_by_identifier(UUID(user_uuid))
    if user is None:
        raise credentials_exception_404
    if not user.is_active:
        raise credentials_exception_403
    return UserUpdate.model_validate(user)


