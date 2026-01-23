from enum import StrEnum


class UserRole(StrEnum):
    """
    Enumeration representing user roles in the application.
    
    Defines two distinct roles:
    - User: Standard user role with basic permissions
    - Admin: Administrative role with elevated privileges
    """
        
    USER = "user"
    ADMIN = "admin"
    #BOT = "bot"
    #AGENT = "agent"

