#piclhub webhook
FROM python:3.11.2
LABEL maintainer="Digital future"

ARG ROOT_DIR=../..
ENV HOME_DIR /usr/piclhub
WORKDIR $HOME_DIR
ENTRYPOINT [ "python", "./ansible_hook.py"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./webhook/* .
RUN pip install flask