from django.urls import path
from django.views.generic import TemplateView
from myapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/classes/', views.teacher_classes, name='teacher_classes'),
    path('teacher/class/<int:class_id>/roster/', views.teacher_roster, name='teacher_roster'),
    path('student/major/', views.student_major, name='student_major'),
    path('student/courses/', views.student_dashboard, name='student_dashboard'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('teacher/class/<int:class_id>/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/class/<int:class_id>/assignment/<int:assessment_id>/scores/', views.teacher_assignment_scores, name='teacher_assignment_scores'),
    path('teacher/class/<int:class_id>/assignment/<int:assessment_id>/export/', views.export_scores_excel, name='export_scores_excel'),
    path('teacher/class/<int:class_id>/assignment/<int:assessment_id>/import/', views.import_scores_excel, name='import_scores_excel'),
    path('teacher/class/<int:class_id>/assignment/<int:assessment_id>/delete/', views.delete_assessment, name='delete_assessment'),
    path('logout-confirm/', TemplateView.as_view(template_name='registration/logout_confirm.html'), name='logout-confirm'),
    path('frontdesk/dashboard/', views.frontdesk_dashboard, name='frontdesk_dashboard'),
    path('frontdesk/register/', views.frontdesk_register_student, name='frontdesk_register_student'),
    path('frontdesk/enroll/', views.frontdesk_enroll_student, name='frontdesk_enroll_student'),
    path('frontdesk/students/', views.frontdesk_manage_students, name='frontdesk_manage_students'),
    path('frontdesk/api/classes/', views.frontdesk_api_classes, name='frontdesk_api_classes'),
]