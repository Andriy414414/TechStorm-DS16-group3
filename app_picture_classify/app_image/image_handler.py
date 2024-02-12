from PIL import Image

def preprocess_image(img):
    """
    Підготовка зображення до роботи (повертається зображення розширенням 32х32)
    """
    img = Image.open(img)
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