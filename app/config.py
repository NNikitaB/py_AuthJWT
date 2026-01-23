import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.ENV'))


class Settings:
    MODE: str = os.environ.get('MODE', 'TEST')  # Значение по умолчанию
    DB = os.environ.get('DB','sqlite+aiosqlite')  # Значение по умолчанию
    DB_HOST: str = os.environ.get('DB_HOST', '127.0.0.1')  # Значение по умолчанию
    DB_PORT: int = int(os.environ.get('DB_PORT', 5432))  # Значение по умолчанию
    DB_USER: str = os.environ.get('DB_USER', 'user')  # Значение по умолчанию
    DB_PASS: str = os.environ.get('DB_PASS', 'password')  # Значение по умолчанию
    DB_NAME: str = os.environ.get('DB_NAME', 'dbname')  # Значение по умолчанию

    DB_URL: str = f'{DB}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    BD_URL_TEST: str = f'sqlite+aiosqlite:///:./testdb.sqlite'
    BD_NAME_TEST:str = "testdb.sqlite"
    #YANDEX settings
    YANDEX_CLIENT_ID: str = os.environ.get("YANDEX_CLIENT_ID","c24b56cb912b47378db420335797ed5c")
    YANDEX_CLIENT_SECRET: str = os.environ.get("YANDEX_CLIENT_SECRET","3c36968eb74c4aeca32016be5cc44c26")
    #YANDEX_REDIRECT_URI: str = "http://localhost:8000/oauth/yandex/callback"
    YANDEX_REDIRECT_URI: str = os.environ.get("YANDEX_REDIRECT_URI","https://oauth.yandex.ru/verification_code")
    #JWT settings
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'secret')
    JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 120))
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRE_MINUTES', 60 * 24 * 7))



settings = Settings()

