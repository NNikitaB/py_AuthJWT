from pydantic import BaseModel, EmailStr
from datetime import datetime, UTC
from uuid import UUID


class BaseUserRoleAccessDTO(BaseModel):
    notes: bool  = False
    phone: bool  = False
    email: bool  = False
    psevdonim: bool  = False
    username: bool  = False


class BaseUserRoleAccessCreate(BaseUserRoleAccessDTO):
    user_uuid: UUID


class BaseUserRoleAccessGet(BaseUserRoleAccessCreate):
    id: int


class BaseUserRoleAccessUpdate(BaseUserRoleAccessGet):
    pass

class BaseUserRoleAccessResponse(BaseUserRoleAccessGet):
    pass