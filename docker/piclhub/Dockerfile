Dockerfile                                                                                                                                438/438               100%
#piclhub.pp.ua
FROM python:3.11.2
LABEL maintainer="Digital future"

RUN pip install poetry==1.3.2
ENV HOME_DIR = /usr/piclhub
WORKDIR $HOME_DIR
ENTRYPOINT [ "poetry", "run", "python", "./app_picture_classify/manage.py", "runserver", "0.0.0.0:80"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#COPY .env .
COPY . .
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --without dev,test