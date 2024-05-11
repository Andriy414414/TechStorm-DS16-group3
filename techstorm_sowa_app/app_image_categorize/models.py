from django.db import models
from cloudinary.models import CloudinaryField
from .image_validations import validate_image_format, validate_image_size
from django.contrib.auth.models import User
from pathlib import Path
from uuid import uuid4

def upload_image(instance, filename):
    ext = Path(filename).suffix
    new_filename = f"{uuid4().hex}{ext}"
    return f"data-science-project/{new_filename}"


class ImageModel(models.Model):
    original_file_name = models.FileField(upload_to=upload_image, validators=[validate_image_size, validate_image_format])
    cloudinary_image = CloudinaryField('image')  # збереження зображення в хмарі, а його url в БД
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
