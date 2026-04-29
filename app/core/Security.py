from bcrypt import hashpw, gensalt, checkpw
import asyncio

class Security:
    @staticmethod
    def create_password_hash(password: str) -> str:
        """Create hash"""
        password_bytes = password.encode('utf-8')
        salt = gensalt()
        hashed = hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """ Check hash"""
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return checkpw(plain_bytes, hashed_bytes)
    
    @staticmethod
    async def hash_password_async(password: str) -> str:
        return await asyncio.to_thread(Security.create_password_hash, password)
    
    @staticmethod
    async def check_password_async(plain_password: str, hashed_password: str) -> bool:
        return await asyncio.to_thread(Security.check_password, plain_password, hashed_password)
