from django.apps import AppConfig
from keras.models import load_model  # noqa
import os
from django.conf import settings


class AppImageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_image_categorize'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None

    def ready(self):
        # self.model = load_model('app_image_categorize/ml_models/model_cifar10_90_vgg16.h5')
        model_path = os.path.join(settings.BASE_DIR, 'app_image_categorize/ml_models/model_cifar10_90_vgg16.h5')

        # Завантажуємо модель за абсолютним шляхом
        self.model = load_model(model_path)