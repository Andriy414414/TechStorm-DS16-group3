import PIL
from PIL import Image
import os
import uuid

from django.http import HttpResponseServerError
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.core.exceptions import ValidationError

from .forms import ImageForm

import cloudinary
import cloudinary.uploader
import cloudinary.api

import numpy as np


def cutting_image(uploaded_image: InMemoryUploadedFile):
    """
    Ця функція призначена для попередньої обробки зображень.
    Вона вирізає центральну частину зображення та змінює його розмір на 32x32 пікселі.
    """

    img = Image.open(uploaded_image)
    width, height = img.size
    if width > height:
        new_width = height
        left = (width - new_width) // 2
        right = (width + new_width) // 2
        top = 0
        bottom = height
    else:
        new_height = width
        top = (height - new_height) // 2
        bottom = (height + new_height) // 2
        left = 0
        right = width
    img = img.crop((left, top, right, bottom))
    img = img.resize((32, 32))

    return img


def save_picture_to_claud(img_32x32: PIL.Image.Image):
    """
    Збереження зображення зі згенерованим випадковим ім'ям у Cloudinary.
    Отримання URL зображення з Cloudinary.
    """

    # генеруємо випадкове ім'я файлу
    random_filename = str(uuid.uuid4())[:10]

    # зберігаємо оброблену картинку у тимчасовий файл
    temp_filename = random_filename + '.jpg'
    img_32x32.save(temp_filename)

    # відкриваємо тимчасовий файл і читаємо його вміст
    with open(temp_filename, 'rb') as f:
        img_data = f.read()

    # створюємо об'єкт SimpleUploadedFile
    img_temp = SimpleUploadedFile(temp_filename, img_data, content_type='image/jpeg')

    # видаляємо тимчасовий файл
    os.remove(temp_filename)

    # завантажуємо оброблену картинку в Cloudinary
    uploaded_result = cloudinary.uploader.upload(img_temp, public_id=random_filename)

    try:
        cloudinary_url = uploaded_result['url']  # отримаємо URL картинки на Cloudinary
        return cloudinary_url
    except Exception as e:
        return HttpResponseServerError(f"URL зображення не отримано, помилка: {str(e)}")


def preprocess_image(img):
    """
    Підготовка зображення до роботи (повертається зображення розширенням 32х32)
    """
    img = Image.open(img)
    image_resized = img.resize((32, 32))
    image_array = np.array(image_resized)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    return image_array
