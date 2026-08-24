from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count, Model

from myapp.models import Teacher, Class, Student


@login_required(login_url='/login')
def index(request):
    user = request.user
    if hasattr(user, 'teacher'):
        return redirect('teacher_dashboard')
    elif hasattr(user, 'student'):
        return redirect('student_dashboard')
    elif user.is_staff or user.is_superuser:
        return redirect('/admin/')
    else:
        # Fallback if the user has no role assigned
        return render(request, 'myapp/base.html')

@login_required(login_url='/login')
def teacher_dashboard(request):
    try:
        # Get the classes assigned to the logged-in teacher and count enrollments
        classes = request.user.teacher.class_set.select_related('subject', 'term', 'room').annotate(
            student_count=Count('enrollment')
        ).all()
    except AttributeError:
        # Failsafe in case a non-teacher ends up here (though index routing prevents this)
        classes = []

    context = {
        'classes': classes,
    }

    return render(request, 'myapp/teacher_dashboard.html', context)

@login_required(login_url='/login')
def student_dashboard(request):
    try:
        # Get the enrollments for the logged-in student
        enrollments = request.user.student.enrollment_set.select_related(
            'class_instance__subject',
            'class_instance__term',
            'class_instance__room',
            'class_instance__teacher'
        ).all()
        
        # Calculate total credits
        total_credits = sum(e.class_instance.subject.credits for e in enrollments)
        
        # Get current term from the first enrollment if available
        first_enrollment = enrollments.first()
        current_term = first_enrollment.class_instance.term if first_enrollment else None
    except AttributeError:
        enrollments = []
        total_credits = 0
        current_term = None

    context = {
        'enrollments': enrollments,
        'total_credits': total_credits,
        'current_term': current_term,
    }
    return render(request, 'myapp/student_dashboard.html', context)
