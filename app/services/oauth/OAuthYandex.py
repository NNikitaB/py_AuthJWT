from app.core.config import settings
from urllib.parse import urlencode
from  httpx import AsyncClient
from fastapi import HTTPException
from .base_oauth import BaseOAuth
from app.core.logger import logger
import base64

class OAuthYandex(BaseOAuth):
    client_id = settings.YANDEX_CLIENT_ID
    client_secret = settings.YANDEX_CLIENT_SECRET
    redirect_uri = settings.YANDEX_REDIRECT_URI

    def get_auth_url(self) -> str:
        yandex_auth_url = "https://oauth.yandex.ru/authorize"
        params = {
            "response_type": "token",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }

        return f"{yandex_auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> str:
        token_url = "https://oauth.yandex.ru/"
        data = {
            "grant_type": "token",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        # Кодируем client_id и client_secret в Base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
        }

        async with AsyncClient() as client:
            #logger.info(data)
            response = await client.post(token_url, headers=headers, data=data)
            #logger.info(f"Ответ от Яндекса: {response.status_code} - {response.text}")
            #print("\n\n\n\n\n\n\n")
            #print(response.text)
            #print("\n\n\n\n\n\n\n")
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Ошибка получения токена")
            try:
                tokens = response.json()                
                return tokens.get("access_token")
            except Exception as e:
                logger.error(f"Ошибка парсинга JSON: {e} | Ответ: {response.text}")
                raise HTTPException(status_code=500, detail="Ошибка обработки ответа от Яндекса")
            #tokens = response.json()
            #return tokens.get("access_token")
    
    async def get_user_info(self, access_token: str) -> dict:
        user_info_url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}

        async with AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail="Ошибка получения данных пользователя"
                )
            try:
                return response.json()
            except Exception as e:
                logger.error(f"Ошибка парсинга JSON: {e} | Ответ: {response.text}")
                raise HTTPException(status_code=500, detail="Ошибка обработки ответа от Яндекса")
            #return response.json()
