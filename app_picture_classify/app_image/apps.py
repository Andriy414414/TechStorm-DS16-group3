from django.apps import AppConfig
from keras.models import load_model

class AppImageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_image'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None

    def ready(self):
        self.model = load_model('app_image/ml_models/model_cifar10_90_vgg16.h5')