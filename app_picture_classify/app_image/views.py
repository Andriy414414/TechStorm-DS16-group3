import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import numpy as np
import io

from .utils import (svg_reshape_to_32x32x3, 
                    svg_classification, 
                    save_jpeg_and_url_from_svg,
                    jpg_classification, 
                    save_jpeg_and_url_from_jpg_and_jpeg)

from django.shortcuts import render, redirect
from .forms import ImageForm
from .models import ImageModel
from .utils import preprocess_image, remove_img_from_cloud, PUBLIC_ID

from wand.image import Image as WandImage
from wand.color import Color
from PIL import Image as PillowImage

img_public_id = None


def destroy_original_image_from_cloud(func):
    """
    The destroy_original_image_from_cloud function is a decorator that removes the original image from Cloudinary
    after it has been uploaded. This function is used to prevent users from uploading multiple images with the same PUBLIC_ID,
    which would result in an error.
    
    :param func: Pass the function that will be decorated
    :return: A function that takes the request as a parameter
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
        """
        The predict_class function takes an image and returns a prediction of the class that the image belongs to.
        The function uses a pre-trained model to make this prediction.
        
        :param self: Represent the instance of the class
        :param img: Pass the image to be classified
        :return: The name of the class with the highest probability
        """
        class_names = ['літак', 'автомобіль', 'птах', 'кіт', 'олень', 'собака', 'жаба', 'кінь', 'корабель', 'вантажівка']
        prediction = self.model.predict(img)
        result = self.format_predictions(prediction, class_names)
        return result 

    def format_predictions(self, predictions, class_names):
        """
        The format_predictions function takes in a list of predictions and class names,
        and returns a formatted string with the top two classes and their probabilities.
        
        
        :param self: Represent the instance of the class
        :param predictions: Get the main and second classes
        :param class_names: Get the class name from the index
        :return: A string with the name of the main class,
        """
        main_classes = np.argmax(predictions, axis=1)
        second_classes = np.argsort(-predictions, axis=1)[:, 1]

        sum_all = np.sum(predictions)
        percentage_main = predictions[0][main_classes[0]] / sum_all
        percentage_second = predictions[0][second_classes[0]] / sum_all
        percentage_others = 1 - percentage_main - percentage_second

        formatted_prediction = f"{class_names[main_classes[0]]} - {percentage_main*100:.2f}%\n"
        formatted_prediction += f"{class_names[second_classes[0]]} - {percentage_second*100:.2f}%\n"
        formatted_prediction += f"Інші класи - {percentage_others*100:.2f}%"

        return formatted_prediction


def home_page(request):
    """
    The home_page function is the view function for the home page of our app.
    It renders a template called 'home_page.html' and returns it to the user.
    
    :param request: Get the request object from django
    :return: An httpresponse object, which is a web page
    """
    return render(request,
                  template_name='app_image/home_page.html')


@destroy_original_image_from_cloud
def home(request):
    """
    The home function is the main function of the app.
    It handles all requests to the root URL, and renders a template with a form for uploading images.
    If an image is uploaded, it will be preprocessed and classified by our model, then rendered in another template.
    
    :param request: Get the request object
    :return: A rendered template
    """
    form = ImageForm(instance=ImageModel())
    predicted_class = ''
    img_url = None

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            uploaded_image = request.FILES['original_file_name']  # отримуємо завантажену картинку (тимчасовий файл)
            file_extension = os.path.splitext(uploaded_image.name)[1]  # отримуємо розширення тимчасового файла

            if file_extension == '.svg':
                # Створюємо тимчасовий файл для збереження PNG-зображення
                with WandImage(blob=uploaded_image.read(), format='svg', width=300, height=300,
                               background=Color('#00000000')) as img:
                    # Конвертуємо SVG у PNG
                    img.compression_quality = 100  # якіст стискання (від 0 до 100)
                    with img.convert('png') as converted_img:
                        # Замінюємо вміст uploaded_image на вміст конвертованого PNG-файлу
                        uploaded_image1 = converted_img.make_blob()

                # зберігаємо файл в Cloudinary
                cloudinary_response = cloudinary.uploader.upload(uploaded_image1)
                # отримаємо URL завантаженого зображення з відповіді Cloudinary
                img_url = cloudinary_response['secure_url']

                PUBLIC_ID = cloudinary_response['public_id']
                # зберігаємо PUBLIC_ID в сесії
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
                # Зберігаємо файл в Cloudinary
                cloudinary_response = cloudinary.uploader.upload(uploaded_image)
                # Отримаємо URL завантаженого зображення з відповіді Cloudinary
                img_url = cloudinary_response['secure_url']

                PUBLIC_ID = cloudinary_response['public_id']
                # зберігаємо PUBLIC_ID в сесії
                request.session['PUBLIC_ID'] = PUBLIC_ID

                # отримуємо зображення розміром 32х32 пікселі з оригінального зображення та відповідного масиву
                img_32x32, img_32x32_array = preprocess_image(uploaded_image)

                # Класифікація
                predicted_class = jpg_classification(img_32x32_array, ModelInference)

                # збереження зображення в хмару, його url в базу даних
                save_jpeg_and_url_from_jpg_and_jpeg(form, img_32x32, request.user)

                # видаляємо тимчасовий файл з диска
                # os.remove(uploaded_image.name)



    return render(request,
                  template_name='app_image/index.html',
                  context={"form": form, "output_text": predicted_class, "uploaded_image_url": img_url})
