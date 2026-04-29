from pydantic import BaseModel
from app.core import ServiceName
from datetime import datetime, UTC
from uuid import UUID
from typing import Optional


class SpecificAccessDTO(BaseModel):
    service_name: ServiceName = ServiceName.Default
    name_access: str = ""
    is_active: bool = False


class SpecificAccessGet(SpecificAccessDTO):
    id: int
    granted_at: datetime
    user_uuid: UUID


class SpecificAccessUpdate(SpecificAccessGet):
    pass


class SpecificAccessCreate(SpecificAccessDTO):
    user_uuid: UUID
    granted_at: Optional[datetime] = datetime.now(UTC)


class SpecificAccessResponse(SpecificAccessGet):
    pass
