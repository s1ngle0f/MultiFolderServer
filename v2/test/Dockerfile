FROM python:3.9

COPY . /server

WORKDIR /server

RUN apt update && apt-get update && apt-get install -y sudo

#RUN pip install --upgrade pip && \
#    pip install peewee && \
#    pip install psycopg2 && \
#    pip install psycopg2-binary && \
#    pip install python-multipart && \
#    pip install fastapi && \
#    pip install uvicorn

CMD ["python", "main_test.py"]
