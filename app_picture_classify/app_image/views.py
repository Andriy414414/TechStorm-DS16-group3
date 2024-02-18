import os

from django.core.files.uploadedfile import InMemoryUploadedFile

from .utils import save_picture_to_claud, svg_reshape_to_32x32x3, svg_classification, save_jpeg_and_url_from_svg, \
    jpg_classification, save_jpeg_and_url_from_jpg_and_jpeg
from django.http import HttpResponseServerError
from django.apps import apps
from django.shortcuts import render, redirect
from .forms import ImageForm
from .models import ImageModel
from .utils import preprocess_image, remove_img_from_cloud, PUBLIC_ID

from wand.image import Image as WandImage
from wand.color import Color
from PIL import Image as PillowImage
import io
import numpy as np
import matplotlib.pyplot as plt

img_public_id = None

import cloudinary
import cloudinary.uploader
import cloudinary.api


def destroy_original_image_from_cloud(func):
    """
    Функція destroy_original_image_from_cloud — це декоратор,
    який видалить оригінальне зображення з cloudinary після виконнання основної функції
    """

    def inner(request, *args):
        # Получаем PUBLIC_ID из сессии
        if request.session.get('PUBLIC_ID'):
            remove_img_from_cloud(request.session.get('PUBLIC_ID'))
        result = func(request, *args)

        return result

    return inner


class ModelInference:
    def __init__(self, model):
        self.model = model

    def predict_class(self, img):
        сlass_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
        prediction = self.model.predict(img)
        predicted_class = prediction.argmax()

        return сlass_names[predicted_class]


def home_page(request):
    return render(request,
                  template_name='app_image/home_page.html')


@destroy_original_image_from_cloud
def home(request):
    form = ImageForm(instance=ImageModel())
    predicted_class = ''
    img_url = None

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            # global img_public_id
            uploaded_image = request.FILES['original_file_name']  # отримуємо завантажену картинку (тимчасовий файл)
            # img_url, img_public_id = save_picture_to_claud(PillowImage.open(uploaded_image))
            # PUBLIC_ID['public_id'] = img_public_id
            file_extension = os.path.splitext(uploaded_image.name)[1]  # отримуємо розширення тимчасового файла

            if file_extension == '.svg':
                # Створюємо тимчасовий файл для збереження PNG-зображення
                with WandImage(blob=uploaded_image.read(), format='svg', width=32, height=32,
                               background=Color('#00000000')) as img:
                    # Конвертуємо SVG у PNG
                    img.compression_quality = 100  # якіст стискання (від 0 до 100)
                    with img.convert('png') as converted_img:
                        # Замінюємо вміст uploaded_image на вміст конвертованого PNG-файлу
                        uploaded_image1 = converted_img.make_blob()
                print("Замінили вміст uploaded_image на вміст конвертованого PNG-файлу")

                # Сохраняем файл в Cloudinary
                cloudinary_response = cloudinary.uploader.upload(uploaded_image1)
                print("Зберегли СВГ в Клауд")
                # Получаем URL загруженного изображения из ответа Cloudinary
                img_url = cloudinary_response['secure_url']
                print("=========++++++++++++SVG==============++++++++++++++++")  # working--------------

                PUBLIC_ID = cloudinary_response['public_id']
                # Сохраняем PUBLIC_ID в сессии
                request.session['PUBLIC_ID'] = PUBLIC_ID

                # створюємо об'єкт зображення Pillow з байтового рядка
                image = PillowImage.open(io.BytesIO(uploaded_image1))

                # отримуємо масив із зображення з необхідною розмірністю (32, 32, 3)
                image_array, img_32x32 = svg_reshape_to_32x32x3(image)

                # Класифікація
                predicted_class = svg_classification(image_array, ModelInference)

                # збереження зображення в хмару, його url в базу даних
                save_jpeg_and_url_from_svg(form, img_32x32, request.user)

            else:
                # ---------------------------------------Растрові зображення (чорно-білі та кольорові)
                # img_url, img_public_id = save_picture_to_claud(PillowImage.open(uploaded_image))
                # PUBLIC_ID['public_id'] = img_public_id

                # Сохраняем файл в Cloudinary
                cloudinary_response = cloudinary.uploader.upload(uploaded_image)
                print("Зберегли СВГ в Клауд")
                # Получаем URL загруженного изображения из ответа Cloudinary
                img_url = cloudinary_response['secure_url']
                print("=========++++++++++++SVG==============++++++++++++++++")  # working--------------

                PUBLIC_ID = cloudinary_response['public_id']
                # Сохраняем PUBLIC_ID в сессии
                request.session['PUBLIC_ID'] = PUBLIC_ID

                # отримуємо зображення розміром 32х32 пікселі з оригінального зображення та відповідного масиву
                img_32x32, img_32x32_array = preprocess_image(uploaded_image)

                # Класифікація
                predicted_class = jpg_classification(img_32x32_array, ModelInference)

                # збереження зображення в хмару, його url в базу даних
                save_jpeg_and_url_from_jpg_and_jpeg(form, img_32x32, request.user)

            # видаляємо тимчасовий файл з диска
            os.remove(uploaded_image.name)


    return render(request,
                  template_name='app_image/index.html',
                  context={"form": form, "output_text": predicted_class, "uploaded_image_url": img_url})
