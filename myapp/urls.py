from django.urls import path
import myapp
from myapp import views

urlpatterns = [
    path('home', views.index),
]