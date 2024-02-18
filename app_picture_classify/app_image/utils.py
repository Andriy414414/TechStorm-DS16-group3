import PIL
from PIL import Image
import os
import uuid

from django.http import HttpResponseServerError
from django.core.files.uploadedfile import SimpleUploadedFile

import cloudinary
import cloudinary.uploader
import cloudinary.api

import numpy as np
from PIL import Image as PillowImage
from django.apps import apps


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
        cloudinary_public_id = uploaded_result['public_id']  # отримаємо Public ID картинки на Cloudinary
        return cloudinary_url, cloudinary_public_id
    except Exception as e:
        return HttpResponseServerError(f"URL зображення не отримано, помилка: {str(e)}")


import imghdr


def preprocess_image(img):
    """
    Підготовка зображення до роботи (повертається зображення розширенням 32х32)
    """

    img = Image.open(img)
    image_resized = img.resize((32, 32))
    image_array = np.array(image_resized)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    return image_resized, image_array


def svg_reshape_to_32x32x3(image: PillowImage):
    """Отримання масиву із зображення з необхідною розмірністю (32, 32, 3)"""

    img_32x32 = image.resize((32, 32))
    image_array = np.array(img_32x32)

    if image_array.shape == (32, 32, 4):  # кольорове зображення
        image_array = image_array[:, :, :3]  # змінюємо розмірність на (32, 32, 3)
    elif image_array.shape == (32, 32, 2):  # чорно-біле зображення
        # копіюємо другий канал і додаємо його до image_array
        third_channel = image_array[:, :, 1]  # копіюємо 2-й канал
        image_array_with_third_channel = np.dstack((image_array, third_channel))  # додаємо його до image_array
        image_array = image_array_with_third_channel
        # створюємо об'єкт зображення Pillow із масиву image_array
        img_32x32 = PillowImage.fromarray(image_array.astype('uint8'), 'RGB')
    else:
        print(f'Розмірність масиву дорівнює {image_array.shape}, підходяча розмірність - (32, 32, 2) або (32, 32, 4)')

    return image_array, img_32x32


def svg_classification(image_array, class_name_modelinference):
    """Класифікація зображення з файлу формату .svg"""

    image_array = image_array / 255.0  # нормалізація даних
    img_32x32_array = np.expand_dims(image_array, axis=0)  # перетворення (32, 32, 3) в (1, 32, 32, 3)
    # отримання конфігурації додатка 'app_image'
    AppConfig = apps.get_app_config('app_image')
    # з отриманої конфігурації отримується модель
    model = AppConfig.model
    # передбачення класу зображення за допомогою переданої моделі
    model_inference = class_name_modelinference(model)
    predicted_class = model_inference.predict_class(img_32x32_array)

    return predicted_class


def save_jpeg_and_url_from_svg(form, img_32x32, request_user):
    """Збереження картинки в Coudinary та її URL в базі даних"""

    # конвертуємо зображення в формат RGB для збереження без альфа-каналу (JPEG його не підтримує)
    img_32x32_rgb = img_32x32.convert('RGB')

    # задаємо ім'я тимчасового файлу
    temp_filename = 'temp_image.jpg'

    # зберігаємо перетворене зображення у файл формату JPEG
    img_32x32_rgb.save(temp_filename, format='JPEG')

    # завантажуємо зображення з файлу
    saved_image = PillowImage.open(temp_filename)

    # завантажуємо зображення в хмару та отримуємо його URL
    cloudinary_url = save_picture_to_claud(saved_image)[0]

    # видаляємо тимчасовий файл
    os.remove(temp_filename)

    # Збереження URL зображення з Cloudinary у базу даних
    try:
        image_instance = form.save(commit=False)
        image_instance.cloudinary_image = cloudinary_url
        image_instance.user = request_user  # прив'язування картинки до поточного користувача
        image_instance.save()  # при цьому іде запис в БД і запис оригінального файлу на диск
    except Exception as e:
        return HttpResponseServerError(f"Помилка при збереженні в БД: {str(e)}")


def jpg_classification(img_32x32_array, class_name_modelinference):
    """Класифікація зображення з файлу формату .jpg та .jpeg"""

    # отримання конфігурації додатка 'app_image'
    AppConfig = apps.get_app_config('app_image')
    # з отриманої конфігурації отримується модель
    model = AppConfig.model
    # передбачення класу зображення за допомогою переданої моделі
    model_inference = class_name_modelinference(model)
    predicted_class = model_inference.predict_class(img_32x32_array)

    return predicted_class


def save_jpeg_and_url_from_jpg_and_jpeg(form, img_32x32, request_user):
    cloudinary_url = save_picture_to_claud(img_32x32)[0]
    # Збереження URL зображення з Cloudinary у базу даних
    try:
        image_instance = form.save(commit=False)
        image_instance.cloudinary_image = cloudinary_url
        image_instance.user = request_user  # прив'язування картинки до поточного користувача
        image_instance.save()  # при цьому іде запис в БД і запис оригінального файлу на диск
    except Exception as e:
        return HttpResponseServerError(f"Помилка при збереженні в БД: {str(e)}")


def remove_img_from_cloud(public_id: str) -> None:
    '''
    Видаляє фотографію з cloudinary по її public_id
    Повертає None
    '''
    cloudinary.uploader.destroy(public_id)
    print("the image saccessfully deleted")


PUBLIC_ID = {"public_id": None}  # зберігає public id попередньго фото
