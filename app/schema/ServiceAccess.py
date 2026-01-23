from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from app.core import ServiceName, AccessLevel
from datetime import datetime, UTC


class ServiceAccessBase(BaseModel):
    notes: bool = True
    phone: bool = True
    email: bool = True
    psevdonim: bool = True
    username: bool = True


class ServiceAccessGet(ServiceAccessBase):
    id: int
    user_uuid: UUID


class ServiceAccessCreate(ServiceAccessBase):
    user_uuid: UUID


class ServiceAccessUpdate(ServiceAccessBase):
    id: int
    


class ServiceAccessResponse(ServiceAccessGet):
    pass