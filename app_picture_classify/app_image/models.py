from django.db import models

# Create your models here.


class ImageModel(models.Model):
    path = models.ImageField(upload_to='pictures')