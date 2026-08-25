from django.urls import path
from django.views.generic import TemplateView
from myapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/major/', views.student_major, name='student_major'),
    path('student/courses/', views.student_dashboard, name='student_dashboard'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('logout-confirm/', TemplateView.as_view(template_name='registration/logout_confirm.html'), name='logout-confirm'),
]