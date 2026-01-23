from .repository import BaseSqlAsyncRepositoryID
from app.models import ServicesAccess
from sqlalchemy.ext.asyncio import AsyncSession

class ServicesAccessRepository(BaseSqlAsyncRepositoryID[ServicesAccess]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    

    

