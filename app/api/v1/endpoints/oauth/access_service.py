from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.database.db import get_async_session
from sqlalchemy.future import select
from uuid import UUID,uuid4
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.ServiceAccess import ServiceAccessBase,ServiceAccessCreate,ServiceAccessGet,ServiceAccessResponse,ServiceAccessUpdate
from typing import List
from app.services.TokenJWT import get_current_user
from app.models import Users,ServiceAccess



access_user_router = APIRouter(prefix="/api/v1/access_user", tags=["CRUDAccessUser"])




# get random str uuid4 
def get_random_str():
    return str(uuid4())


@access_user_router.get("/get_access", response_model=List[ServiceAccessResponse])
async def list_access(current_user: Users = Depends(get_current_user),db: AsyncSession = Depends(get_async_session)):

    result = await db.execute(select(ServiceAccess).where(ServiceAccess.user_uuid == current_user.uuid))
    return result.scalars().all()

@access_user_router.get("/get_access/{id}", response_model=ServiceAccessResponse)
async def get_audio(id: int, current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):

    res = await db.execute(select(ServiceAccess).where(ServiceAccess.id == id,ServiceAccess.user_uuid == current_user.uuid).limit(1))
    audio_file = res.scalar_one_or_none()
    if not audio_file:
        raise HTTPException(status_code=404, detail="User access not found")
    return audio_file