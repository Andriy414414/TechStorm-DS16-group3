import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import numpy as np
import io
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import ImageForm
from .models import ImageModel
from .utils import preprocess_image, remove_img_from_cloud, PUBLIC_ID
from wand.image import Image as WandImage
from wand.color import Color
from PIL import Image as PillowImage

from .utils import (model_plots_for_model_1,
                    model_plots_for_model_2,
                    svg_reshape_to_32x32x3,
                    svg_classification,
                    save_jpeg_and_url_from_svg,
                    jpg_classification,
                    save_jpeg_and_url_from_jpg_and_jpeg)



img_public_id = None
predicted_classes = []


class MyModel:
    def __init__(self, model):
        self.model = model


    def predict_class(self, img):
        """
        The predict_class function takes an image and returns predictions of the class that the image belongs to.
        The function uses a pre-trained model to make these predictions.

        :param self: Represent the instance of the class
        :param img: Pass the image to be classified
        :param format_types: Specifies the list of format types for predictions
        :return: A dictionary with predictions for each format type
        """
        class_names = ['літак', 'автомобіль', 'птах', 'кіт', 'олень', 'собака', 'жаба', 'кінь', 'корабель',
                       'вантажівка']
        format_types = ['custom', 'normal']
        predictions = {}
        for format_type in format_types:
            prediction = self.model.predict(img)
            formatted_prediction = self.format_predictions(prediction, class_names, format_type)
            predictions[format_type] = formatted_prediction
        return predictions


    def format_predictions(self, predictions, class_names, format_type='default'):
        """
        The format_predictions function takes in a list of predictions and class names,
        and returns a formatted string with the top two classes and their probabilities.

        :param predictions: Get the main and second classes
        :param class_names: Get the class name from the index
        :param format_type: Specifies the format type for predictions
        :return: A string with the name of the main class
        """
        main_classes = np.argmax(predictions, axis=1)
        sum_all = np.sum(predictions)
        percentage_main = predictions[0][main_classes[0]] / sum_all
        if format_type == 'custom':
            formatted_prediction = f"{class_names[main_classes[0]].upper()}:  {percentage_main * 100:.2f}%\n"
        else:
            formatted_prediction= ''
            for class_name, probability in zip(class_names, predictions[0]):
                formatted_prediction += f"{class_name}\t{probability * 100:.2f}%\n"
        return formatted_prediction


def home_page(request):
    """
    The home_page function is the view function for the home page of our app.
    It renders a template called 'home_page.html' and returns it to the user.

    :param request: Get the request object from django
    :return: An httpresponse object, which is a web page
    """
    return render(request,
                  template_name='app_image_categorize/home_page.html')


def upload_image(request):
    """
    The upload_image function is called when the user uploads an image.
        It takes in a request object, which contains information about the HTTP request that was made to this view function.
        The form variable is set to an instance of ImageForm, which allows us to create a new ImageModel object and save it
        into our database if we want (which we do).

    :param request: Get the uploaded image
    :return: The image, form, predicted class and url
    """
    form = ImageForm(instance=ImageModel())
    img_url = None
    predicted_class = ''
    img_32x32 = None

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            uploaded_image = request.FILES['original_file_name']
            file_extension = os.path.splitext(uploaded_image.name)[1]

            if file_extension == '.svg':
                img_32x32, img_url, predicted_class = process_svg_image(uploaded_image, request
                                                                        )
                save_jpeg_and_url_from_svg(form, img_32x32, request.user)
            else:

                img_32x32, img_url, predicted_class = process_jpg_image(uploaded_image, request
                                                                            )
                save_jpeg_and_url_from_jpg_and_jpeg(form, img_32x32, request.user)
                predicted_classes.append(predicted_class)
                print('predicted_classes', predicted_classes)

            print("img_url:", img_url)
            request.session['img_url'] = img_url
            request.session['predicted_class'] = predicted_class
            with open("output.json", "w", encoding="utf-8") as file:
                json.dump(predicted_classes, file, ensure_ascii=False)
                file.write("\n")

    return img_32x32, form, predicted_class, img_url, request.user


def process_svg_image(uploaded_image, request):
    """
    The process_svg_image function takes in an uploaded image, and returns a 32x32x3 numpy array of the image,
    the url of the uploaded image on Cloudinary, and the predicted class. The function first converts any SVG images to PNGs
    using WandImage (a Python ImageMagick binding). It then uploads this converted PNG to Cloudinary using cloudinary's
    Python API. The function then uses PillowImage to open this converted PNG as an object that can be manipulated by Pillow.
    The svg_reshape_to_32x32x3 function is called on this opened object which resh

    :param uploaded_image: Store the uploaded image
    :param request: Access the session variables
    :return: The image in 32x32x3 format, the url of the uploaded image and
    """
    with WandImage(blob=uploaded_image.read(), format='svg', width=300, height=300,
                   background=Color('#00000000')) as img:
        img.compression_quality = 100
        with img.convert('png') as converted_img:
            uploaded_image1 = converted_img.make_blob()

    cloudinary_response = cloudinary.uploader.upload(uploaded_image1)
    img_url = cloudinary_response['secure_url']
    public_id = cloudinary_response['public_id']
    request.session['PUBLIC_ID'] = public_id
    image = PillowImage.open(io.BytesIO(uploaded_image1))
    image_array, img_32x32 = svg_reshape_to_32x32x3(image)
    predicted_class = svg_classification(image_array, MyModel)
    return img_32x32, img_url, predicted_class

def process_jpg_image(uploaded_image, request):
    """
    The process_jpg_image function takes in a user-uploaded image and returns the following:
        1. A 32x32 pixel version of the uploaded image, which is used to display on the results page.
        2. The URL of the uploaded image, which is stored in a session variable for later use by other functions.
        3. The predicted class (i.e., 'dog' or 'cat') based on an ML model trained using Keras.

    :param uploaded_image: Store the image uploaded by the user
    :param request: Access the session variable public_id
    :return: A 32x32 image, the url of the uploaded image, and a predicted class
    """
    cloudinary_response = cloudinary.uploader.upload(uploaded_image)
    img_url = cloudinary_response['secure_url']
    public_id = cloudinary_response['public_id']
    request.session['PUBLIC_ID'] = public_id
    img_32x32, img_32x32_array = preprocess_image(uploaded_image)
    predicted_class = jpg_classification(img_32x32_array, MyModel)
    return img_32x32, img_url, predicted_class


def home(request):
    """
    The home function is the main view for the app. It handles all of the logic
    for uploading an image, predicting its class, and displaying it to a user.
    :param request: Get the request object
    :return: The index
    """
    user_images_count = ImageModel.objects.filter(user=request.user).count()
    img_32x32, form, predicted_class, img_url, user = upload_image(request)

    img_url = request.session.get('img_url')
    predicted_class = request.session.get('predicted_class')
    if predicted_class is not None:
        output_text = predicted_class.get('custom', '')
    else:
        output_text = ''
    return render(request,
                  template_name='app_image_categorize/index.html',
                  context={"form": form, "output_text": output_text, "uploaded_image_url": img_url, "user_images_count": user_images_count})


def images(request, page=1):
    """
    The images function is used to display all of the images that a user has uploaded.
    It takes in a request object and an optional page number, which defaults to 1 if not specified.
    The function then filters the ImageModel objects by the current user, and sets up pagination for 8 images per page.
    It then renders the template with context containing all of the pictures on that particular page.

    :param request: Access the request object
    :param page: Specify the page number
    :return: A page of images
    """
    user_images = ImageModel.objects.filter(user=request.user)
    per_page = 8
    paginator = Paginator(user_images, per_page)
    page_obj = paginator.page(page)
    context = {'pictures': page_obj}
    return render(request, 'app_image_categorize/images.html', context=context)


def model_plots(request):
    """
    The model_plots function is a view that renders the model_plots.html template, which displays plots of the
        performance of our image categorization model.

    :param request: Get the image from the html page
    :return: The model_plots
    """
    return render(request, 'app_image_categorize/model_plots.html')


def model_plots_for_model(request):
    """
    The model_plots_for_model function is used to create plots for the model.
        The function first checks if the output file exists, and if it does, it loads its contents into a variable.
        Then, two different plots are created using this data: one with default settings and one with custom settings.
        Finally, both of these paths are passed to the template as context variables.

    :param request: Get the data from the form
    :return: The model_plots_for_model
    :doc-author: Trelent
    """
    output_exists = os.path.exists("output.json")
    normal_plot_path = None
    custom_plot_path = None
    if output_exists:
        with open("output.json", "r", encoding="utf-8") as file:
            predicted_data = json.load(file)

        normal_plot_path = model_plots_for_model_1(predicted_data)
        custom_plot_path = model_plots_for_model_2(predicted_data)

    return render(request, template_name='app_image_categorize/model_plots_for_model.html',
                  context={"output_text": "", "normal_plot": normal_plot_path, "custom_plot": custom_plot_path})


