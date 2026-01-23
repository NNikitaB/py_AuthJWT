from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.models.Users import Users
from app.schema.User import UserCreate, UserResponse, UserUpdate
from app.database.db import get_async_session
from sqlalchemy.future import select
from uuid import UUID
from app.services.TokenJWT import get_current_user

user_crud_router = APIRouter(prefix="/api/v1/user", tags=["CRUDUser"])


@user_crud_router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing_user = await db.execute(select(Users).where(Users.email == user_data.email))
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = Users(
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@user_crud_router.get("/{user_uuid}", response_model=UserResponse)
async def get_user(user_uuid: UUID, db: AsyncSession = Depends(get_async_session)):
    user = await db.get(Users, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_crud_router.patch("/{user_uuid}", response_model=UserResponse)
async def update_user(user_uuid: UUID, user_data: UserUpdate, db: AsyncSession = Depends(get_async_session)):
    user = await db.get(Users, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

@user_crud_router.delete("/{user_uuid}")
async def delete_user(user_uuid: UUID, db: AsyncSession = Depends(get_async_session)):
    user = await db.get(Users, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}
