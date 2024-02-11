from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.postgres.fields import ArrayField


class LabelsModel(models.Model):
    label_of_class = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    names_of_class = models.CharField(max_length=100, choices=[
        ('airplane', 'airplane'),
        ('car', 'car'),
        ('bird', 'bird'),
        ('cat', 'cat'),
        ('deer', 'deer'),
        ('dog', 'dog'),
        ('frog', 'frog'),
        ('horse', 'horse'),
        ('ship', 'ship'),
        ('truck', 'truck'),
    ])


class ImageModel(models.Model):
    cloudinary_image = CloudinaryField('image')  # збереження зображення в хмарі, а його url в БД
    array = ArrayField(models.IntegerField(), blank=True, null=True, default=list)  # поле для збереження масиву пікселів
    # blank=True та null=True вказують, що поле може бути порожнім, і default=list встановлює порожній список як значення за замовчуванням
    label_of_class = models.ForeignKey(LabelsModel, on_delete=models.CASCADE, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


