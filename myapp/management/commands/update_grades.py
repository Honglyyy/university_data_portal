from django.core.management.base import BaseCommand
from myapp.models import Enrollment, StudentScore

class Command(BaseCommand):
    help = 'Recalculates and updates final scores, credits, and GPA for all enrollments'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting grade update process..."))
        
        # Use prefetch_related to load all scores in memory to avoid N+1 queries
        enrollments = Enrollment.objects.prefetch_related(
            'studentscore_set', 
            'studentscore_set__assessment', 
            'class_instance__subject'
        ).all()
        
        updated_count = 0
        
        for enrollment in enrollments:
            student_scores = enrollment.studentscore_set.all()
            
            if student_scores:
                total_achieved = sum(s.score for s in student_scores)
                total_max_attempted = sum(s.assessment.max_score for s in student_scores)
                
                if total_max_attempted > 0:
                    percentage = (total_achieved / total_max_attempted) * 100
                    enrollment.final_score = percentage
                else:
                    enrollment.final_score = 0
                    
            # Calling save will trigger the final_grade, gpa, and credits calculation in Enrollment.save()
            enrollment.save()
            updated_count += 1
            
            if updated_count % 100 == 0:
                self.stdout.write(f"Updated {updated_count} enrollments...")
                
        self.stdout.write(self.style.SUCCESS(f"Finished! Successfully updated {updated_count} enrollments."))
