from abc import ABC, abstractmethod


class BaseOAuth(ABC):
    @abstractmethod
    def get_auth_url(self) -> str:
        """Генерация URL для авторизации через сервис"""
        pass
   

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> str:
        """Обмен код авторизации на токен доступа"""
        pass


    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict:
        """Получение информации о пользователе с помощью токена доступа"""
        pass