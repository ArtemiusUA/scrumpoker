FROM python:3.8
LABEL maintainer="Artem Merkulov <artem.merkulov@gmail.com>"

WORKDIR /srv/app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /srv/app

RUN adduser --disabled-password --gecos '' app && \
    adduser app sudo && \
    chown -R app /srv/app
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER app
