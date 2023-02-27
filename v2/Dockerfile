FROM python:3.9

COPY ./server /server

WORKDIR /server

RUN apt update && apt-get update && apt-get install -y sudo && sudo apt-get install git

RUN pip install --upgrade pip && \
    pip install peewee && \
    pip install psycopg2 && \
    pip install psycopg2-binary && \
    pip install python-multipart && \
    pip install fastapi && \
    pip install uvicorn && \
    pip install GitPython

CMD ["python", "main.py"]
