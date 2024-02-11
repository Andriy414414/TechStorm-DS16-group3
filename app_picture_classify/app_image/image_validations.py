import os
from django.core.exceptions import ValidationError



def validate_image_size(value):
    filesize = value.size
    if filesize > 1_000_000:
        raise ValidationError("максимальний розмір файлу 10мб")
    return value

def validate_image_format(value):
    ext = os.path.splitext(value.name)[1] 
    valid_extensions = ['.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError("Допускаються лише файли з розширенням .jpg або .jpeg")
    return value

