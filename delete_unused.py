import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_data_portal.settings')
django.setup()

from myapp.models import Student

unused_students = Student.objects.filter(enrollment__isnull=True)
count = unused_students.count()

# Because Student has a OneToOne to User, we should delete the User objects which will cascade delete the Students
for student in unused_students:
    student.user.delete()

print(f"Deleted {count} unused students and their users.")
