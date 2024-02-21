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
    The save_picture_to_claud function takes a PIL.Image.Image object as an argument and returns a tuple of two strings:
    the URL of the uploaded image on Cloudinary, and its Public ID on Cloudinary.
    
    :param img_32x32: PIL.Image.Image: Specify the type of data that will be passed to this function
    :return: A tuple with two elements:
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


def preprocess_image(img):
    """
    The preprocess_image function takes an image file and returns a resized version of the image as well as an array representation of the image.
    The function first opens the uploaded file using PIL's Image module, then uses that to resize it to 32x32 pixels.
    It then converts this into a numpy array and divides each element by 255 (to normalize it). It also adds another dimension at index 0 for Keras' benefit.
    
    :param img: Open the image
    :return: The image as a numpy array
    """
    img = Image.open(img)
    image_resized = img.resize((32, 32))
    image_array = np.array(image_resized)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    return image_resized, image_array


def svg_reshape_to_32x32x3(image: PillowImage):
    """
    The svg_reshape_to_32x32x3 function takes an image and resizes it to 32x32 pixels.
    It then converts the image into a numpy array, which is used by Keras for training.
    The function also checks if the image has 2 or 4 channels (grayscale or RGB) and adds a third channel if necessary.
    
    :param image: PillowImage: Resize the image to 32x32
    :return: A tuple of two elements:
    """
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
    """
    The svg_classification function takes an image array and a class name model inference as input.
    The image array is normalized, converted to a 32x32x3 shape, and then the app_image configuration is retrieved.
    The model from the app_image configuration is used to predict the class of the image.
    
    :param image_array: Pass the image data to the function
    :param class_name_modelinference: Pass the model to be used for prediction
    :return: The predicted class of the image
    """
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
    """
    The save_jpeg_and_url_from_svg function takes a form and an image as input,
        converts the image to RGB format (JPEG does not support alpha channels), saves it to disk,
        uploads it to Cloudinary, and then saves the URL of that uploaded image in our database.
    
    :param form: Pass the form instance to the function
    :param img_32x32: Pass the image object to the function
    :param request_user: Associate the image with the current user
    :return: The url of the image saved in cloudinary
    """

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
    """
    The jpg_classification function takes an image and a model as input,
        and returns the predicted class of the image.
    
    :param img_32x32_array: Pass the image to be classified
    :param class_name_modelinference: Pass the model to be used for inference
    :return: A class name
    """
    AppConfig = apps.get_app_config('app_image')
    # з отриманої конфігурації отримується модель
    model = AppConfig.model
    # передбачення класу зображення за допомогою переданої моделі
    model_inference = class_name_modelinference(model)
    predicted_class = model_inference.predict_class(img_32x32_array)

    return predicted_class


def save_jpeg_and_url_from_jpg_and_jpeg(form, img_32x32, request_user):
    """
    The save_jpeg_and_url_from_jpg_and_jpeg function takes a form and an image, saves the image to cloudinary,
    and then saves the url of that image to the database. It also returns a HttpResponseServerError if there is an error.
    
    :param form: Save the form data to the database
    :param img_32x32: Pass the image to the save_picture_to_claud function
    :param request_user: Save the user who uploaded the image
    :return: The image_instance if it was successfully saved to the database
    """
    cloudinary_url = save_picture_to_claud(img_32x32)[0]
    
    try:
        image_instance = form.save(commit=False)
        image_instance.cloudinary_image = cloudinary_url
        image_instance.user = request_user  
        image_instance.save() 
    except Exception as e:
        return HttpResponseServerError(f"Помилка при збереженні в БД: {str(e)}")


def remove_img_from_cloud(public_id: str) -> None:
    """
    The remove_img_from_cloud function takes a public_id as an argument and removes the image from cloudinary.
        
    
    :param public_id: str: Specify the public id of the image to be removed from cloudinary
    :return: None
    """
    cloudinary.uploader.destroy(public_id)

PUBLIC_ID = {"public_id": None}
