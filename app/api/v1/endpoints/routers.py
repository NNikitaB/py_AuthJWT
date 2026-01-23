from fastapi import APIRouter
from .oauth.auth import jwt_router
from .oauth.user import user_crud_router
from .oauth.access_service import access_user_router


routers = APIRouter()


routers.include_router(jwt_router)
routers.include_router(user_crud_router)
routers.include_router(access_user_router)

