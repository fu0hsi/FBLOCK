FROM python:3.8-slim-buster

WORKDIR /app

COPY ./main.py .

RUN pip install kafka-python redis
CMD ["python3", "main.py"]