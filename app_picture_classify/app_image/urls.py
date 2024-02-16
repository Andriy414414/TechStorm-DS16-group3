from django.contrib import admin
from django.urls import path
from . import views


app_name = 'app_image'

urlpatterns = [
    path('', views.run_home_page, name='home'), # app_image:home
]



