from django.contrib import admin
from django.urls import path
from . import views


app_name = 'app_image'

urlpatterns = [
    path('', views.home, name='home') # app_image:home
]