from django.db import models
from cloudinary.models import CloudinaryField
from .image_validations import validate_image_format, validate_image_size


class ImageModel(models.Model):
    original_file_name = models.ImageField(upload_to='', validators=[validate_image_size, validate_image_format])
    cloudinary_image = CloudinaryField('image')  # збереження зображення в хмарі, а його url в БД
    created_at = models.DateTimeField(auto_now_add=True)


class UserModel(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    pictures = models.ForeignKey(ImageModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username  # Для відображення на сторінці username
