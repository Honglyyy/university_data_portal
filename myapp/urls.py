from django.urls import path
from django.views.generic import TemplateView
from myapp import views

urlpatterns = [
    path('', views.index),
    path('logout-confirm/', TemplateView.as_view(template_name='registration/logout_confirm.html'), name='logout-confirm'),
]