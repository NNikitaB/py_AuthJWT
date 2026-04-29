from .repository import BaseSqlAsyncRepositoryID
from app.models import ServiceAccess
from sqlalchemy.ext.asyncio import AsyncSession

class ServiceAccessRepository(BaseSqlAsyncRepositoryID[ServiceAccess]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    

    

