FROM python:3.12.0-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt


RUN pip install -r requirements.txt