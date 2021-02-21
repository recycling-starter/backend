FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y gdal-bin libgdal-dev python3-gdal binutils libproj-dev lsb-release
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list && apt-get update && apt-get install -y postgresql-client-12

COPY . /srv/html/restarter
WORKDIR /srv/html/restarter
RUN pip3 install -r /srv/html/restarter/env/requirements.txt

