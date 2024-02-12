from django.shortcuts import render, redirect

from .forms import ImageForm
from .models import ImageModel

from .utils import cutting_image, save_picture_to_claud, save_image_url_to_db


def home(request):
    form = ImageForm()
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=ImageModel())
        if form.is_valid():
            uploaded_image = request.FILES['path']  # отримаємо завантажену картинку

            # обробляємо картинку в 32х32 пікселя
            img_32x32 = cutting_image(uploaded_image)

            # збереження зображення в хмару, отримання його url
            cloudinary_url = save_picture_to_claud(img_32x32)

            # зберігаємо URL в базі даних
            save_image_url_to_db(form, cloudinary_url)


    return render(request, 'app_image/index.html', {'form': form})



def action(request):
    r = request
    if r:
        print("action")
    return redirect('app_image:home')
