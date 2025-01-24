# we have to use python 3.8 since Lemmagen does not support 3.9
FROM python:3.12

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    libmemcached-dev \
    libsasl2-modules \
    gettext

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

RUN python3 manage.py compilemessages

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=parladata_project.settings.k8s

CMD exec python manage.py runserver 0.0.0.0:8000


# FROM python:3.8
# RUN apt-get update && apt-get install --yes postgresql-client
# RUN mkdir /app
# WORKDIR /app
# COPY . /app
# RUN pip install -r requirements.txt
# EXPOSE 8000
