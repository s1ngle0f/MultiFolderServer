FROM python:3.10.7

COPY ./server /server

WORKDIR /server

RUN apt update

RUN pip install --upgrade pip && \
    pip install peewee && \
    pip install psycopg2 && \
    pip install psycopg2-binary && \
    pip install python-multipart && \
    pip install fastapi && \
    pip install uvicorn

CMD ["python", "main.py"]
