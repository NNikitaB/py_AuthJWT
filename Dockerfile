FROM python:3.12.4
WORKDIR /code
RUN mkdir -p ./test/
RUN mkdir -p ./app/
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app ./app/
COPY ./test /test/
EXPOSE 8080
CMD ["uvicorn", "app.main.app:app","--host", "0.0.0.0", "--port", "8080"]

