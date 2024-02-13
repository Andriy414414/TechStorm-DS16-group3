import os
from django.core.exceptions import ValidationError



def validate_image_size(value):
    """Валідація розміру файла зображення"""

    filesize = value.size
    if filesize > 6_000_000:  # 6 Мб
        raise ValidationError("Максимальний розмір файлу 6 Мб!")
    return value


def validate_image_format(value):
    """Валідація типу файла зображення"""

    ext = os.path.splitext(value.name)[1] 
    valid_extensions = ['.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError("Допускаються лише файли з розширенням .jpg або .jpeg")
    return value

