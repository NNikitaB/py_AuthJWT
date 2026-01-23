# Это проект личного сайта с сервисами и авторизацией
# Для запуска:
## Локально с docker-compose
### Запустите compose
```
docker-compose up --build
```
OpenAPI [http://localhost:8080/docs]
или
OpenAPI [http://127.0.0.1:8080/docs]


#Авторизация
Использование API
1. получить ссылку для авторизации Яндекс
/api/v1/oauth/get_authorization_url - получить ссылку для авторизации Яндекс
2. перейти и получить токен Яндекс
3. отправить токен яндекса и получить токен для сайта
/api/v1/oauth/yandex - регистрация через Яндекс получение и JWT токена для сайта
4. Ддя загрузки файлов отправить токен сайта,имя файла и файл.
http://localhost:8080/api/v1/audio_files/upload/ - загрузить файл
http://localhost:8080/api/v1/audio_files/get_file/ - получить файл по id
http://localhost:8080/api/v1/audio_files/get_files - получить список аудиофайлов


## Локально без docker-compose
### 1. Установите venv 
```python
python -m venv .venv
```
### 2. Установите зависимости
```python
python -m pip install -r app\requirements.txt
```
### 3. Запустите проект
Выполните комманду в корне проекта
```python
python -m uvicorn  app.main.app:app --host localhost  --port 8080 --reload
```
