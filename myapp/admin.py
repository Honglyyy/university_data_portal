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
admin.site.register(Enrollment)
admin.site.register(Assessment)
admin.site.register(StudentScore)
admin.site.register(Room)