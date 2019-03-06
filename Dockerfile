FROM python:3.7.2-slim

ENV PYTHONPATH=/home/app

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && \
    apt-get install -y git-core

RUN pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

COPY . /home/app
WORKDIR /home/app
