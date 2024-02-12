import numpy as np
from PIL import Image

def preprocess_image(img):
    """
    Підготовка зображення до роботи (повертається зображення розширенням 32х32)
    """
    img = Image.open(img)
    image_resized = img.resize((32, 32))
    image_array = np.array(image_resized)
    image_array = image_array[:, :, ::-1]
    image_array = image_array.astype('float32') / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    return image_array