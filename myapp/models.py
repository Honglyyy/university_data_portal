from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    pass

class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Term(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    credits = models.IntegerField(default=3)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    level = models.CharField(max_length=50)
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Class(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.subject.name} - {self.term.name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    final_grade = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'class_instance')

    def __str__(self):
        return f"{self.student} enrolled in {self.class_instance}"

class Assessment(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.class_instance})"

class StudentScore(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.enrollment.student} - {self.assessment.name}: {self.score}"