#piclhub.pp.ua
FROM ubuntu:latest
LABEL maintainer="Digital future"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME_DIR /usr/piclhub

WORKDIR $HOME_DIR
COPY . .
COPY .env .

RUN apt-get update \
    && apt-get -y install imagemagick \
    && apt-get -y install python3.11

RUN python3.11 get-pip.py \
    && python3.11 -m pip install -r requirements.txt \
    && pip install keras==3.0.4

WORKDIR $HOME_DIR/app_picture_classify
COPY .env .
ENTRYPOINT ["python3.11", "manage.py", "runserver", "0.0.0.0:80"]
