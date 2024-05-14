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
import matplotlib.pyplot as plt
from django.conf import settings

def generate_plot(classes, probabilities, plot_path):
    """
    The generate_plot function takes in three arguments:
        1. classes - a list of strings representing the class names
        2. probabilities - a list of floats representing the predicted probabilities for each class
        3. plot_path - a string representing the path to save the generated plot to

    :param classes: Set the x-axis labels
    :param probabilities: Plot the predicted probabilities of each class
    :param plot_path: Save the plot to a file
    :return: The path to the plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(classes, probabilities, color='limegreen')
    ax.set_ylabel('Probability (%)', color='white', fontsize=14)
    ax.set_xlabel('Class', color='white', fontsize=14)
    ax.set_title('Predicted Class Probabilities', color='white', fontsize=14)
    ax.set_facecolor('black')
    ax.tick_params(axis='x', colors='white', labelsize=12)
    ax.tick_params(axis='y', colors='white', labelsize=12)
    ax.grid(linestyle='--', color='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    plt.tight_layout()
    plt.savefig(plot_path, facecolor='black')
    return plot_path


def model_plots_for_model_1(predicted_data):
    """
    The model_plots_for_model_1 function takes in the predicted_data dictionary and returns a plot of the probabilities
    of each class. The function first extracts the last element from predicted_data, which is a dictionary containing
    the 'normal' key with its value being a string of text that contains all of the classes and their corresponding
    probabilities. The function then splits this string into lines, where each line contains one class name followed by
    its probability (in percentage form). Each line is split into two parts: 1) class name; 2) probability. These are then appended to lists called classes and probabilities respectively. Finally, these lists

    :param predicted_data: Pass the predicted data to the function
    :return: The plot path
    """
    last_predicted_class = predicted_data[-1]
    output_text = last_predicted_class['normal']

    probabilities = []
    classes = []
    for line in output_text.split('\n'):
        parts = line.split('\t')
        if len(parts) == 2:
            class_name = parts[0]
            probability = float(parts[1].replace('%', ''))
            classes.append(class_name)
            probabilities.append(probability)
    plot_path = os.path.join(settings.BASE_DIR, 'app_image_categorize', 'static', 'app_image','predicted_class_plot1.png')
    # plot_path = os.path.join('techstorm_sowa_app', 'app_image_categorize', 'static', 'app_image', 'predicted_class_plot1.png')
    return generate_plot(classes, probabilities, plot_path)


def model_plots_for_model_2(predicted_data):
    """
    The model_plots_for_model_2 function takes in a list of dictionaries, each dictionary containing the predicted class and probability for an image.
    The function then creates two lists: one with the names of all classes that were predicted, and another with their corresponding probabilities.
    It then generates a bar plot using these lists as inputs.

    :param predicted_data: Get the data from the model
    :return: A plot of the predicted classes and their probabilities
    :doc-author: Trelent
    """
    class_names = []
    probabilities = []
    class_counts = {}

    for predicted_class in predicted_data:
        custom_data = predicted_class.get("custom", "")
        parts = custom_data.split(":")
        if len(parts) == 2:
            class_name, percent = parts[0].strip(), float(parts[1].replace('%', '').strip())
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            if class_name in class_names:
                index = class_names.index(class_name)
                probabilities[index] += percent
            else:
                class_names.append(class_name)
                probabilities.append(percent)

    for i, class_name in enumerate(class_names):
        probabilities[i] /= class_counts[class_name]

    # plot_path = os.path.join('techstorm_sowa_app', 'app_image_categorize', 'static', 'app_image', 'predicted_class_plot2.png')
    plot_path = os.path.join(settings.BASE_DIR, 'app_image_categorize', 'static', 'app_image', 'predicted_class_plot2.png')

    print('path', plot_path)
    exist = os.path.exists(plot_path)
    print('exist', exist)
    return generate_plot(class_names, probabilities, plot_path)


def save_picture_to_claud(img_32x32: PIL.Image.Image):
    """
    The save_picture_to_claud function takes a PIL.Image.Image object as an argument and returns a tuple of two strings:
    the URL of the uploaded image on Cloudinary, and its Public ID on Cloudinary.
    
    :param img_32x32: PIL.Image.Image: Specify the type of data that will be passed to this function
    :return: A tuple with two elements:
    """
    random_filename = str(uuid.uuid4())[:10]
    temp_filename = random_filename + '.jpg'
    img_32x32.save(temp_filename)
    with open(temp_filename, 'rb') as f:
        img_data = f.read()

    img_temp = SimpleUploadedFile(temp_filename, img_data, content_type='image/jpeg')
    os.remove(temp_filename)
    uploaded_result = cloudinary.uploader.upload(img_temp, public_id=random_filename)
    try:
        cloudinary_url = uploaded_result['url']
        cloudinary_public_id = uploaded_result['public_id']
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

    if image_array.shape == (32, 32, 4):
        image_array = image_array[:, :, :3]
    elif image_array.shape == (32, 32, 2):
        third_channel = image_array[:, :, 1]
        image_array_with_third_channel = np.dstack((image_array, third_channel))
        image_array = image_array_with_third_channel
        img_32x32 = PillowImage.fromarray(image_array.astype('uint8'), 'RGB')
    else:
        print(f'Розмірність масиву дорівнює {image_array.shape}, підходяча розмірність - (32, 32, 2) або (32, 32, 4)')

    return image_array, img_32x32


def svg_classification(image_array, class_name_modelinference):
    """
    The svg_classification function takes an image array and a class name model inference as input.
    The image array is normalized, converted to a 32x32x3 shape, and then the app_image_categorize configuration is retrieved.
    The model from the app_image_categorize configuration is used to predict the class of the image.
    
    :param image_array: Pass the image data to the function
    :param class_name_modelinference: Pass the model to be used for prediction
    :return: The predicted class of the image
    """
    image_array = image_array / 255.0
    img_32x32_array = np.expand_dims(image_array, axis=0)
    AppConfig = apps.get_app_config('app_image_categorize')
    model = AppConfig.model
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
    img_32x32_rgb = img_32x32.convert('RGB')
    temp_filename = 'temp_image.jpg'
    img_32x32_rgb.save(temp_filename, format='JPEG')
    saved_image = PillowImage.open(temp_filename)
    cloudinary_url = save_picture_to_claud(saved_image)[0]
    os.remove(temp_filename)
    try:
        image_instance = form.save(commit=False)
        image_instance.cloudinary_image = cloudinary_url
        image_instance.user = request_user
        image_instance.save()
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
    AppConfig = apps.get_app_config('app_image_categorize')
    model = AppConfig.model
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
