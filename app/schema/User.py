from pydantic import BaseModel, EmailStr,Field
from typing import Optional, List
from app.schema import (
    ServiceAccessGet, 
    ServiceAccessCreate,
    ServiceAccessUpdate,
    ServiceAccessUpdate,
    SpecificAccessGet,
    SpecificAccessCreate,
    SpecificAccessUpdate,
    BaseUserRoleAccessGet,
    BaseUserRoleAccessCreate,
    BaseUserRoleAccessUpdate,
)
from uuid import UUID
from app.core import UserRole
from datetime import datetime,UTC
from bcrypt import gensalt, hashpw, checkpw 

class UserBase(BaseModel):
    uuid: UUID
    username: Optional[str] = None
    email: Optional[str] = None 
    psevdonim: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = UserRole.USER
    notes: Optional[str] = None
    phone: Optional[str] = None

class UserGet(UserBase):
    email_verified: bool = False
    hashed_password: str
    access_user: Optional[BaseUserRoleAccessGet]
    services_access: Optional[List[ServiceAccessUpdate]] 
    specific_access: Optional[List[SpecificAccessUpdate]] 


class UserCreate(UserBase):
    email_verified: bool = False
    access_user: Optional[BaseUserRoleAccessCreate]
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))
    

class UserUpdate(BaseModel):
    uuid: UUID
    role: Optional[UserRole] = None
    notes: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None 
    psevdonim: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    hashed_password: Optional[str] = None
    created_at: Optional[datetime] = None
    email_verified: Optional[bool] = None
    access_user: Optional[BaseUserRoleAccessUpdate]
    services_access: Optional[List[ServiceAccessUpdate]] 
    specific_access: Optional[List[SpecificAccessUpdate]] 

class UserResponse(UserGet):
    pass

