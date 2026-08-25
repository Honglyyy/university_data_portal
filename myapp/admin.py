from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Term, Subject, Teacher, Student, Class, Enrollment, Assessment, StudentScore, Room

# Register your Custom User
admin.site.register(User, UserAdmin)

# Register the rest of your models
admin.site.register(Department)
admin.site.register(Term)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Class)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_instance', 'final_score', 'final_grade', 'gpa', 'credits')
    list_filter = ('class_instance',)
    search_fields = ('student__user__username', 'class_instance__subject__name')

admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Assessment)
admin.site.register(StudentScore)
admin.site.register(Room)