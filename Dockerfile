FROM ubuntu:latest
MAINTAINER Aleksandr Shaldaev 'Shaldaev03@mail.ru'

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

COPY . /app
COPY . /templates
COPY . run.sh
COPY . main.py

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ['sh', 'run.sh']