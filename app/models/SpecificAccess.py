from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from .Base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID,uuid4
from datetime import datetime, UTC
from app.core.AccessLevel import AccessLevel
from app.core.ServiceName import ServiceName


class SpecificAccess(Base):
    """
    Represents a service access record in the database, tracking user permissions for specific access.
    
    This model defines the relationship between users and their specific access,
    ,.
    Attributes:
        id (int): Primary key for the service access record.
        service_name (ServiceName): The specific service being accessed.
        name_access(str): Specific name Access.
        is_active (bool): Indicates whether the service access is currently active.
        access_level (AccessLevel): The user's permission level for the service.
        user_uuid (UUID): Foreign key linking to the associated user.
    """
        
    __tablename__ = "specific_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(nullable=False,default=ServiceName.Default)
    name_access: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    granted_at = mapped_column(DateTime, default=datetime.now(UTC))
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid",ondelete="CASCADE"), nullable=False)

    user = relationship("Users", back_populates="specific_access")
