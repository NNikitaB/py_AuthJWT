from enum import StrEnum

class AccessLevel(StrEnum):
    """
    Enumeration representing different access levels for service permissions.
    
    Defines the hierarchy of user access levels in the application:
    - User: Standard access level with basic permissions
    - Pro: Enhanced access level with additional privileges
    - Admin: Highest access level with full system permissions
    """
        
    User = "user"
    Pro = "pro"
    Moderator = "moderator"
    Admin = "admin"

