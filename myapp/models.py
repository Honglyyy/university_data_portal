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
    teacher_id = models.TextField()
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Student(models.Model):
    student_id = models.TextField()
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    level = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    batch = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} {str(self.student_id)}"

class Room(models.Model):
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=255)
    campus = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.building} ({self.campus})"

class Class(models.Model):
    class_id = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.CharField(max_length=100, null=True, blank=True)
    schedule = models.CharField(max_length=255, null=True, blank=True)

    @property
    def computed_batch(self):
        parts = self.term.name.split()
        if len(parts) == 2:
            sem, year = parts[0], int(parts[1])
            term_num = (year - 2020) * 2 + (1 if sem == "Fall" else 2)
            batch_num = (term_num + 1) // 2
            return f"Batch {batch_num}"
        return self.batch

    def __str__(self):
        return f"{self.subject.name} - {self.term.name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_grade = models.CharField(max_length=10, blank=True, null=True)
    credits = models.IntegerField(default=0)
    gpa = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('student', 'class_instance')

    def save(self, *args, **kwargs):
        if self.final_score is not None:
            # Grading scale (can be adjusted to your exact university requirements)
            score = float(self.final_score)
            if score >= 95:
                self.final_grade = 'A+'
                self.gpa = 4.0
            elif score >= 90:
                self.final_grade = 'A'
                self.gpa = 3.75
            elif score >= 85:
                self.final_grade = 'B'
                self.gpa = 3.0
            elif score >= 70:
                self.final_grade = 'C'
                self.gpa = 2.0
            elif score >= 65:
                self.final_grade = 'D'
                self.gpa = 1.0
            elif score >= 60:
                self.final_grade = 'E'
                self.gpa = 0.5
            else:
                self.final_grade = 'F'
                self.gpa = 0.0

            # Assign class credits if they pass (e.g. score >= 60, avoiding F)
            if score >= 60:
                self.credits = self.class_instance.subject.credits
            else:
                self.credits = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} enrolled in {self.class_instance}"

class Assessment(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    max_score = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.class_instance})"

class StudentScore(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=7, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_enrollment_grade()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_enrollment_grade()

    def update_enrollment_grade(self):
        # Get all the scores the student has actually received
        student_scores = StudentScore.objects.filter(enrollment=self.enrollment)
        
        # Calculate the total points the student achieved
        total_achieved = sum(s.score for s in student_scores)
        
        # Calculate the total possible points ONLY from the assessments they were scored on
        total_max_attempted = sum(s.assessment.max_score for s in student_scores)
        
        if total_max_attempted > 0:
            percentage = (total_achieved / total_max_attempted) * 100
            self.enrollment.final_score = percentage
        else:
            self.enrollment.final_score = 0

        self.enrollment.save()

    def __str__(self):
        return f"{self.enrollment.student} - {self.assessment.name}: {self.score}"