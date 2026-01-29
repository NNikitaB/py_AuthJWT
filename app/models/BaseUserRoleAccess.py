from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from .Base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID,uuid4
from datetime import datetime, UTC
from app.core.AccessLevel import AccessLevel
from app.core.ServiceName import ServiceName


class BaseUserRoleAccess(Base):
    """
    Represents a user setting access record in the database.
    This model defines the relationship between users and their access to account parameters
    Attributes:
        id (int): Primary key for the  access record.
        notes (bool): Indicates whether the service access is currently active.
        phone (bool): user can change
        email (bool): user can change
        psevdonim (bool): user can change
        username (bool): user can change 
        user_uuid (UUID): Foreign key linking to the associated user.
    """
        
    __tablename__ = "base_user_role_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    notes: Mapped[bool]  = mapped_column(default=False)
    phone: Mapped[bool]  = mapped_column(default=False)
    email: Mapped[bool]  = mapped_column(default=False)
    psevdonim: Mapped[bool]  = mapped_column(default=False)
    username: Mapped[bool]  = mapped_column(default=False)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid",ondelete="CASCADE"), nullable=False)
