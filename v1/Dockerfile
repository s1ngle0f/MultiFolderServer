FROM python:3.10.7

COPY .. /server

WORKDIR /server

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
