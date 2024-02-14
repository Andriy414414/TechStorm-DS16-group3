#piclhub.pp.ua
FROM python:3.11.2
LABEL maintainer="Digital future"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME_DIR /usr/piclhub

WORKDIR $HOME_DIR
COPY . .
COPY .env .


RUN pip install -r requirements.txt \
    && pip install keras==3.0.4

WORKDIR $HOME_DIR/app_picture_classify
COPY .env .
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:80"]