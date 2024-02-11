from django.db import models
from .image_validations import validate_image_format, validate_image_size




class ImageModel(models.Model):
    path = models.ImageField(upload_to='pictures', validators=[validate_image_size, validate_image_format])