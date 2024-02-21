from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'app_image'

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('home/', views.home, name='home'),
]
