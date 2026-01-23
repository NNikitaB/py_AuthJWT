from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime,Enum
from .Base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID,uuid4
from datetime import datetime,UTC
from app.core.UserRole import UserRole


class Users(Base):
    """
    SQLAlchemy ORM model representing user accounts in the system.
    
    Defines the database schema for user information with fields for authentication,
    account status, and relationships to other entities like service access and roles.
    
    Attributes:
        uuid: Unique identifier for the user
        username: Unique username for login
        email: Unique email address for the user
        email_verified: Flag indicating email verification status
        phone: Optional user phone number
        hashed_password: Securely hashed user password
        is_active: Account active status
        is_superuser: Administrative privilege flag
        created_at: Timestamp of user account creation
        notes: Optional additional user notes
        services_access: Relationship to user's service access entries
        role (UserRole): Relationship to user's assigned roles
    """

    __tablename__ = 'users'
    #basic fields
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)  
    username: Mapped[str] = mapped_column(nullable=False)
    psevdonim: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(default=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(nullable=False,default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(nullable=False,default=datetime.now(UTC))
    notes: Mapped[str] = mapped_column(nullable=True)
    access_user = relationship("ServicesAccess", uselist=False,cascade="all, delete-orphan",backref="users")
    #additional fields
    #services_access = relationship("ServicesAccess",back_populates="user",cascade="all, delete",passive_deletes=True, lazy="selectin")

