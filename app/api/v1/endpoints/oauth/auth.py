from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_async_session
from app.models.Users import Users
from app.schema.User import UserResponse
from app.services.oauth import OAuthYandex
from app.services.TokenJWT import TokenJWT, get_current_user
from app.core.logger import logger
from uuid import UUID

jwt_router = APIRouter(prefix="/api/v1/jwt", tags=["JWTAuth"])



@jwt_router.get("/get_authorization_url")
async def get_authorization_url():
    """Получение URL для авторизации через Яндекс"""
    oauth_yandex = OAuthYandex()
    return {"authorization_url": oauth_yandex.get_auth_url()}

@jwt_router.get("/yandex")
async def login_with_yandex(token: str, db: AsyncSession = Depends(get_async_session)):
    """Авторизация через Яндекс"""
    logger.info(f"Авторизация через Яндекс с кодом: {token}")
    oauth_yandex = OAuthYandex()
    jwt_token = TokenJWT()
    #access_token = await oauth_yandex.exchange_code_for_token(code)
    user_data = await oauth_yandex.get_user_info(token)
    print(user_data)
    email = user_data.get("default_email")
    username=user_data.get("login")
    existing_user = await db.execute(select(Users).where(Users.email == email))
    user = existing_user.scalar()

    if not user:
        user = Users(username=username, email=email, hashed_password=token)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Создан новый пользователь: {user.username}")

    access_token = jwt_token.create_access_token({"sub": str(user.uuid)})
    refresh_token = jwt_token.create_refresh_token({"sub": str(user.uuid)})

    logger.info(f"Выданы токены для пользователя {user.username}")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@jwt_router.post("/refresh")
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_async_session)):
    """Обновление access_token с помощью refresh_token"""
    jwt_token = TokenJWT()
    user_uuid = jwt_token.verify_refresh_token(refresh_token)
    if not user_uuid:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await db.get(Users, UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = jwt_token.create_access_token({"sub": str(user.uuid)})

    return {"access_token": access_token, "token_type": "bearer"}