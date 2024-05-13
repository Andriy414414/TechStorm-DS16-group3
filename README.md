# Документація для застосунку "SOWA(SMART OCULAR WATCH ASSISTANT)"

## 1. Підстава для розроблення

Застосунок розроблено відповідно до технічного завдання компанії GoIT "Python Data Science". 

## 2. Розробники

Застосунок розроблено:
- Андрій Батіг (Team Lead);
- Ольга Сіренко (Scrum Master);
- Володимир Великий (Python Developer);
- Андрій Котенко (Python Developer);
- Соня Дудій (Python Developer).


## 4. Програмна основа

Мова програмування - Python. Застосунок реалізований на фреймворку Django. В якості бази даних використано PostgreSQL.

## 5. Використані програмні пакети
- boto3 django-environ
- django-storages
- absl-py
- astunparse
- cachetools
- cloudinary
- certifi
- charset-normalizer
- dm-tree
- django
- flatbuffers
- gast
- google-auth
- google-auth-oauthlib
- google-pasta
- grpcio
- h5py
- idna
- keras
- libclang
- markdown
- markdown-it-py
- markupsafe
- matplotlib
- mdurl
- ml-dtypes
- namex
- numpy
- oauthlib
- opt-einsum
- packaging
- pillow
- protobuf
- psycopg2-binary
- pyasn1
- pyasn1-modules
- pygments
- python-dotenv
- requests
- requests-oauthlib
- rich
- rsa
- six
- tensorboard
- tensorboard-data-server
- tensorflow
- tensorflow-estimator
- tensorflow-io-gcs-filesystem
- tensorflow
- termcolor
- typing-extensions
- tzdata
- urllib3
- werkzeug
- wrapt
- wand

## 6. Розгортання застосунку (інструкція відтестована на linux)

Для здійснення розгортання застосунку необхідно виконати наступні кроки:

6.1. Завантажити проект з GitHub, та перейти в його кореневу директорію.
git clone https://github.com/Andriy414414/TechStorm-DS16-group3.git

6.2. Створити файл .env в кореневій директорії з наступним вмістом:

###AWS connection data
AWS_ACCESS_KEY_ID = <aws_access_key_id>
AWS_SECRET_ACCESS_KEY = <aws_secret_access_key> 
AWS_STORAGE_BUCKET_NAME = <aws_storage_bucket_name> 
AWS_S3_REGION_NAME = <aws_s3_region_name> 

###postgres connection data
DB_PASSWORD = <postgres_password>
DB_USER = <postgres_user>
DB_HOST = <address_or_host>
DB_PORT = <default_5432>

###cloudinary connection data
CLOUDINARY_NAME = <cloudinary_login>
CLOUDINARY_API_KEY = <secret_key> 
CLOUDINARY_API_SECRET = <api_secret>

6.3. Виконати команду для збірки всіх необхідних контейнерів:
docker-compose - up

## 7. Опис нейронної мережі, використаної для класифікації зображень

Використана нейромережа - це мініатюрна версія моделі VGG (Visual Geometry Group), яка є однією з перших та впливових глибоких згорткових нейронних мереж для класифікації зображень. Модель використовує набір шарів згортки, пакування та повнозв'язних шарів для розпізнавання образів у зображеннях. Ось докладний опис:

Точність моделі досягає 92 %.

## 8. Функціонал застосунку

- Реєстрація (sign up), аутентифікація (login) та вихід із застосунку (logaut).
- Класифікація зображень за 10 класами: 'літак', 'автомобіль', 'птах', 'кіт', 'олень', 'собака', 'жаба', 'кінь', 'корабель', 'вантажівка'.
- Формат зображень для обробки нейромережею: .jpg, .jpeg та .svg.
- Виведення зображення із визначеним класом на головну сторінку.
- Збереження в Cloudinary підготовленого зображення розширенням 32х32 пікселя для можливості наповнення додаткового датасету.
- Збереження в базі даних інформації про користувача із прив'язкою до його зображень.
- Збереження в базі даних url на зображення в Cloudinary.
- Додатково фото зберігаються в бакеті AWS3.