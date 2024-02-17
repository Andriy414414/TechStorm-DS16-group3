from django.forms import ModelForm, ImageField, FileInput, FileField
from .models import ImageModel
from django import forms


class ImageForm(ModelForm):
    original_file_name = FileField(widget=FileInput(attrs={
        "class": "form-control-lg form-control mx-auto",
        "name": "image",
        "id": "image",
        "accept": "image/*",
        }))

    class Meta:
        model = ImageModel
        fields = ['original_file_name']
