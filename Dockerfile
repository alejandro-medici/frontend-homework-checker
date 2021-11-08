FROM python:bullseye

COPY requirements.txt ./

RUN pip install -r requirements.txt