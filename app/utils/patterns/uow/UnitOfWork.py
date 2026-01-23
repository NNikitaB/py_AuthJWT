from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable
from abc import ABC, abstractmethod
from typing import Protocol
from app.utils.patterns.rep import UsersRepository,ServicesAccessRepository


class IUnitOfWork(ABC):
    """Интерфейс Unit of Work для управления транзакциями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def __aenter__(self):
        """Начало контекста Unit of Work"""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Завершение контекста Unit of Work"""
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        """Фиксация транзакции"""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        """Откат транзакции"""
        raise NotImplementedError
    

class UnitOfWork(IUnitOfWork):
    """Unit of Work для управления транзакциями """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.users = UsersRepository(session)  # Подключаем репозиторий пользователей
        self.services_access = ServicesAccessRepository(session)  # Подключаем репозиторий доступа

    async def __aenter__(self):
        """Начинаем транзакцию"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Коммитим или откатываем транзакцию в зависимости от наличия ошибок"""
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        """Фиксация транзакции"""
        await self.session.commit()

    async def rollback(self):
        """Откат транзакции"""
        await self.session.rollback()
        