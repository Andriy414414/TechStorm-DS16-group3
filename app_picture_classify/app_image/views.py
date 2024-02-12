from django.apps import apps
from django.shortcuts import render, redirect

from .forms import ImageForm
from .models import ImageModel
from .image_handler import preprocess_image


class ModelInference:
    def __init__(self, model):
        self.model = model

    def predict_class(self, img):
        сlass_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
        prediction = self.model.predict(img)
        predicted_class = prediction.argmax()

        return сlass_names[predicted_class]


def home(request):
    form = ImageForm(instance=ImageModel())
    predicted_class = ''

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            image_instance = form.save(commit=False)  # Отримуємо екземпляр моделі без збереження в базу даних
            uploaded_image = request.FILES['path']  # Отримуємо завантажений файл зображення
            img_32x32_array = preprocess_image(uploaded_image) # Обрізаємо зображення і зменшуємо до 32х32

            AppConfig = apps.get_app_config('app_image')
            model = AppConfig.model
            
            model_inference = ModelInference(model)
            predicted_class = model_inference.predict_class(img_32x32_array)

    return render(request, 
                  template_name='app_image/index.html', 
                  context={"form": form, "output_text": predicted_class})


def action(request):
    r = request
    if r: 
        print("action")
    return redirect('app_image:home')








