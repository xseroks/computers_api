FROM ubuntu:22.04

MAINTAINER Aleksandr Shaldaev 'Shaldaev03@mail.ru'

RUN apt-get update -y
RUN apt-get install python3-pip python3-dev build-essential -y

COPY . /app

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=main.py