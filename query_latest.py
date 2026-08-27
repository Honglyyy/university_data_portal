import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_data_portal.settings')
django.setup()

from myapp.models import Student

latest_student = Student.objects.order_by('-id').first()
print(f"Latest username: {latest_student.user.username}")
print(f"Latest student_id: {latest_student.student_id}")
print(f"Latest batch: {latest_student.batch}")
