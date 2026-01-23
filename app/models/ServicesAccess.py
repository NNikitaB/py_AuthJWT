from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from .Base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID,uuid4
from datetime import datetime, UTC
from app.core.AccessLevel import AccessLevel
from app.core.ServiceName import ServiceName


class ServicesAccess(Base):
    """
    Represents a service access record in the database, tracking user permissions for specific access.
    
    This model defines the relationship between users and their access to different parameters,
    , activation status, access level, and timestamp of access grant.
    
    Attributes:
        id (int): Primary key for the  access record.
        notes (bool): Indicates whether the service access is currently active.
        phone (bool): user can change
        email (bool): user can change
        psevdonim (bool): user can change
        username (bool): user can change 
-------------- todo
    Represents a service access record in the database, tracking user permissions for specific services.
    
    This model defines the relationship between users and their access to different services,
    including the service name, activation status, access level, and timestamp of access grant.
    
    Attributes:
        id (int): Primary key for the service access record.
        service_name (ServiceName): The specific service being accessed.
        is_active (bool): Indicates whether the service access is currently active.
        access_level (AccessLevel): The user's permission level for the service.
-------------------- todo
        user_uuid (UUID): Foreign key linking to the associated user.
    """
        
    __tablename__ = "service_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    notes: Mapped[bool]  = mapped_column(default=False)
    phone: Mapped[bool]  = mapped_column(default=False)
    email: Mapped[bool]  = mapped_column(default=False)
    psevdonim: Mapped[bool]  = mapped_column(default=False)
    username: Mapped[bool]  = mapped_column(default=False)

    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid",ondelete="CASCADE"), nullable=False)

# todo
    service_name: Mapped[str] = mapped_column(nullable=False,default=ServiceName.Default)
    is_active: Mapped[bool] = mapped_column(default=False)
    access_level: Mapped[str] = mapped_column(nullable=False,default=AccessLevel.User)
    granted_at = mapped_column(DateTime, default=datetime.now(UTC))
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid",ondelete="CASCADE"), nullable=False)

    user = relationship("Users", back_populates="services_access")

 # todo
