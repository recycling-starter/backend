FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get upgrade -y

COPY . /srv/html/bugbounty
WORKDIR /srv/html/bugbounty
RUN pip install -r /srv/html/bugbounty/env/requirements.txt
