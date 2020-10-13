FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get upgrade -y

COPY . /srv/html/restarter
WORKDIR /srv/html/restarter
RUN pip install -r /srv/html/restarter/env/requirements.txt
