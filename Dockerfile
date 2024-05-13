# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.10
FROM python:3.10

# Встановимо змінну середовища
ENV APP_HOME /data-django-final-project

# Встановимо робочу директорію усередині контейнера
WORKDIR $APP_HOME

# Створіть каталоги static і media
RUN mkdir -p /data-django-final-project/techstorm_sowa_app/static
RUN mkdir -p /data-django-final-project/techstorm_sowa_app/media

# Копіюємо файли pyproject.toml і poetry.lock у контейнер
COPY pyproject.toml poetry.lock $APP_HOME/
RUN pip install tensorflow==2.16.1
# Встановимо залежності усередині контейнера
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main

# Копіюємо всі інші файли проекту у контейнер
COPY techstorm_sowa_app/ $APP_HOME/techstorm_sowa_app/

# Позначимо порт, на якому працює програма всередині контейнера
EXPOSE 9003

# Запускаємо нашу програму всередині контейнера
CMD ["python", "techstorm_sowa_app/manage.py", "runserver", "0.0.0.0:9003"]