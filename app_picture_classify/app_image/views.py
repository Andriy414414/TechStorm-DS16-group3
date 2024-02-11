import os
import uuid

from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.core.files.uploadedfile import SimpleUploadedFile

from .forms import ImageForm
from .models import ImageModel
from .image_handler import preprocess_image

import cloudinary
import cloudinary.uploader
import cloudinary.api


def home(request):
    form = ImageForm()
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            uploaded_image = request.FILES['path']  # отримаємо завантажену картинку
            img_32x32 = preprocess_image(uploaded_image)  # обробляємо картинку в 32х32 пікселя

            random_filename = str(uuid.uuid4())[:10]  # генеруємо випадкове ім'я файлу
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
            except Exception as e:
                return HttpResponseServerError(f"URL зображення не отримано, помилка: {str(e)}")

            # зберігаємо URL в базі даних
            try:
                image_instance = form.save(commit=False)
                image_instance.cloudinary_image = cloudinary_url
                image_instance.save()
            except Exception as e:
                return HttpResponseServerError(f"Помилка при збереженні в БД: {str(e)}")

    return render(request, 'app_image/index.html', {'form': form})


def action(request):
    r = request
    if r:
        print("action")
    return redirect('app_image:home')




