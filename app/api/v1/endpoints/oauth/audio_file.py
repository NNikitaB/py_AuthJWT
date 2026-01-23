from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.database.db import get_async_session
from sqlalchemy.future import select
from uuid import UUID,uuid4
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Statistics import AudioFiles
from app.schema.AudioFile import AudioFileResponse
from typing import List
from app.services.TokenJWT import get_current_user
from app.models.Users import Users
audio_files_router = APIRouter(prefix="/api/v1/audio_files", tags=["AudioFiles"])

AUDIO_STORAGE_PATH = "audio_storage/"


# get random str for filename 
def get_random_str():
    return str(uuid4())


@audio_files_router.post("/upload/", response_model=AudioFileResponse)
async def upload_audio(file: UploadFile = File(...),filename:str = get_random_str(),current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    file_location = f"{AUDIO_STORAGE_PATH}{file.filename}"

    audio_file = AudioFiles(
        user_uuid=current_user.uuid,
        file_name=file.filename,
        file_path=file_location
    )
    db.add(audio_file)
    await db.commit()
    await db.refresh(audio_file)
    return audio_file

@audio_files_router.get("/get_files", response_model=List[AudioFileResponse])
async def list_audio_files(current_user: Users = Depends(get_current_user),db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(AudioFiles).where(AudioFiles.user_uuid == current_user.uuid))
    return result.scalars().all()

@audio_files_router.get("/get_file/{audio_id}", response_model=AudioFileResponse)
async def get_audio(audio_id: int, current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):

    res = await db.execute(select(AudioFiles).where(AudioFiles.id == audio_id,AudioFiles.user_uuid == current_user.uuid).limit(1))
    audio_file = res.scalar_one_or_none()
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return audio_file