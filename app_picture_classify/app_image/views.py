from django.shortcuts import render

from .forms import ImageForm
from .models import ImageModel
from .image_handler import preprocess_image


# Create your views here.


def home(request):
    form = ImageForm(instance=ImageModel())
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            image_instance = form.save(commit=False)  # Отримуємо екземпляр моделі без збереження в базу даних
            uploaded_image = request.FILES['path']  # Отримуємо завантажений файл зображення
            img_32x32 = preprocess_image(uploaded_image) # Обрізаємо зображення і зменшуємо до 32х32
            img_32x32.save('test.jpg')

    return render(request, 
                  template_name='app_image/index.html', 
                  context={"form": form})


