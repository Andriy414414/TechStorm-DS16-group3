from django.forms import ModelForm, ImageField, FileInput
from .models import ImageModel


class ImageForm(ModelForm):
    original_file_name = ImageField(widget=FileInput(attrs={
        "class": "form-control-lg form-control mx-auto",
        "name": "image",
        "id": "image",
        "accept": "image/*",
        }))

    class Meta:
        model = ImageModel
        fields = ['original_file_name']

