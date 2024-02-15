import os

from django.core.files.uploadedfile import InMemoryUploadedFile

from .utils import save_picture_to_claud
from django.http import HttpResponseServerError
from django.apps import apps
from django.shortcuts import render, redirect
from .forms import ImageForm
from .models import ImageModel
from .utils import preprocess_image

from wand.image import Image as WandImage
from wand.color import Color
from PIL import Image as PillowImage
import io
import numpy as np
import matplotlib.pyplot as plt


class ModelInference:
    def __init__(self, model):
        self.model = model

    def predict_class(self, img):
        сlass_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
        prediction = self.model.predict(img)
        predicted_class = prediction.argmax()

        return сlass_names[predicted_class]


def home(request):
    form = ImageForm(instance=ImageModel())
    predicted_class = ''

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            uploaded_image = request.FILES['original_file_name']  # отримаємо завантажену картинку (тимчасовий файл)

            # ---------------------------------------SVG-зображення
            file_extension = os.path.splitext(uploaded_image.name)[1]
            print(f'РАСШИРЕНИЕ ФАЙЛА--------{file_extension}')
            if file_extension == '.svg':

                # Створюємо тимчасовий файл для збереження PNG-зображення
                with WandImage(blob=uploaded_image.read(), format='svg', width=32, height=32,
                           background=Color('#00000000')) as img:
                    # Конвертуємо SVG у PNG
                    with img.convert('png') as converted_img:
                        # Замінюємо вміст uploaded_image на вміст конвертованого PNG-файлу
                        uploaded_image1 = converted_img.make_blob()

                # Создаем объект изображения Pillow из байтовой строки
                image = PillowImage.open(io.BytesIO(uploaded_image1))

                # отримаємо масив із зображення з необхідною розмірністю (32, 32, 3)
                img_32x32 = image.resize((32, 32))
                image_array = np.array(img_32x32)
                print(f'Розмірність початкового масиву растра з SVG файлу: {image_array.shape}')  # (32, 32, 4) - кольорове, (32, 32, 2) - чорно-біле

                if image_array.shape == (32, 32, 4):  # кольорове
                    image_array = image_array[:, :, :3]  # змінюємо розмірність на (32, 32, 3)
                    print(f'Розмірність масиву після злиття каналів: {image_array.shape}')
                elif image_array.shape == (32, 32, 2):  # чорно-біле
                    # print(image_array)
                    # копіюємо другий канал і додаємо його до image_array
                    third_channel = image_array[:, :, 1]  # копіюємо 2й канал
                    image_array_with_third_channel = np.dstack((image_array, third_channel))  # додаємо його до image_array
                    image_array = image_array_with_third_channel
                    # print(image_array)
                    # # відображаємо зображення
                    # plt.imshow(image_array)
                    # plt.show()  # зображення виводиться коректно

                    print(f'Розмірність масиву додавання додаткового виміру: {image_array.shape}')
                else:
                    print(f'Розмірність масиву дорівнює {image_array.shape}, підходяча розмірність - (32, 32, 2) або (32, 32, 4)')

                image_array = image_array / 255.0
                img_32x32_array = np.expand_dims(image_array, axis=0)  # перетворення (32, 32, 3) в (1, 32, 32, 3)
                print(f'Розмірність кінцевого масиву: {img_32x32_array.shape}')

                # отримання конфігурації додатка 'app_image'
                AppConfig = apps.get_app_config('app_image')
                # з отриманої конфігурації отримується модель
                model = AppConfig.model

                # передбачення класу зображення за допомогою переданої моделі
                model_inference = ModelInference(model)
                predicted_class = model_inference.predict_class(img_32x32_array)

                # конвертуємо зображення в формат RGB для збереження без альфа-каналу (JPEG його не підтримує)
                img_32x32_rgb = img_32x32.convert('RGB')

                # Отображаем изображение-----------------------
                img_32x32_rgb.save('temp_filename.jpeg', format='JPEG')

                # задаємо ім'я тимчасового файлу
                temp_filename = 'temp_image.jpg'

                # зберігаємо перетворене зображення у файл формату JPEG
                img_32x32_rgb.save(temp_filename, format='JPEG')

                # Отображаем изображение-----------------------


                # завантажуємо зображення з файлу
                saved_image = PillowImage.open(temp_filename)

                # завантажуємо зображення в хмару та отримуємо його URL
                cloudinary_url = save_picture_to_claud(saved_image)

                # видаляємо тимчасовий файл
                os.remove(temp_filename)

                # Збереження URL зображення з Cloudinary у базу даних
                try:
                    image_instance = form.save(commit=False)
                    image_instance.cloudinary_image = cloudinary_url
                    image_instance.save()  # при цьому іде запис в БД і запис оригінального файлу на диск
                except Exception as e:
                    return HttpResponseServerError(f"Помилка при збереженні в БД: {str(e)}")

                # видаляємо тимчасовий файл з диска
                os.remove(uploaded_image.name)


            else:
                # ---------------------------------------Растрові зображення (чорно-білі та кольорові)

                # отримаємо зображення розміром 32х32 пікселі з оригінального зображення та відповідного масиву
                img_32x32, img_32x32_array = preprocess_image(uploaded_image)

                # отримання конфігурації додатка 'app_image'
                AppConfig = apps.get_app_config('app_image')
                # з отриманої конфігурації отримується модель
                model = AppConfig.model

                # передбачення класу зображення за допомогою переданої моделі
                model_inference = ModelInference(model)
                predicted_class = model_inference.predict_class(img_32x32_array)

                # збереження зображення в хмару, отримання його url
                cloudinary_url = save_picture_to_claud(img_32x32)

                # Збереження URL зображення з Cloudinary у базу даних
                try:
                    image_instance = form.save(commit=False)
                    image_instance.cloudinary_image = cloudinary_url
                    image_instance.save()  # при цьому іде запис в БД і запис оригінального файлу на диск
                except Exception as e:
                    return HttpResponseServerError(f"Помилка при збереженні в БД: {str(e)}")

                # видаляємо тимчасовий файл з диска
                os.remove(uploaded_image.name)

    return render(request,
                  template_name='app_image/index.html',
                  context={"form": form, "output_text": predicted_class})


def action(request):
    r = request
    if r:
        print("action")
    return redirect('app_image:home')
