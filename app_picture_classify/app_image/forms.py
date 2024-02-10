from django.forms import ModelForm, ImageField, FileInput
from .models import ImageModel

class ImageForm(ModelForm):
    path = ImageField(widget=FileInput(attrs={
        "class": "form-control-lg form-control mx-auto", 
        "name": "image", 
        "id": "image",
        "accept": "image/*",
        }))

    class Meta:
        model = ImageModel
        fields = ['path']