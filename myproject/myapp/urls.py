from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('camera_feed/', views.camera_feed, name='camera_feed'),
    path('capture/', views.capture, name='capture'),
]