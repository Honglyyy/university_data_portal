import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_data_portal.settings')
django.setup()

from myapp.models import Enrollment, StudentScore

print("Updating grades for all enrollments...")
enrollments = Enrollment.objects.all()
for e in enrollments:
    # This will trigger the calculation and update the final_score, final_grade, gpa, and credits
    scores = StudentScore.objects.filter(enrollment=e)
    total_achieved = sum(s.score for s in scores)
    total_max_attempted = sum(s.assessment.max_score for s in scores)
    
    if total_max_attempted > 0:
        e.final_score = (total_achieved / total_max_attempted) * 100
    else:
        e.final_score = 0
        
    e.save() # This triggers the grading scale logic in Enrollment.save()
print("Done!")
