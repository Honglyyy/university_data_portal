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
            'student',
            'class_instance__subject',
            'class_instance__term',
            'class_instance__room',
            'class_instance__teacher',
        ).order_by('-class_instance__term__start_date', '-class_instance__term__name', 'class_instance__subject__name')
        
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

@login_required(login_url='/login')
def student_major(request):
    try:
        student = request.user.student
    except AttributeError:
        student = None
    
    context = {
        'student': student
    }
    return render(request, 'myapp/student_major.html', context)

@login_required(login_url='/login')
def student_grades(request):
    try:
        enrollments = request.user.student.enrollment_set.select_related(
            'class_instance__subject',
            'class_instance__term'
        ).order_by('-class_instance__term__start_date', '-class_instance__term__name', 'class_instance__subject__name')
        
        overall_total_credits = 0
        overall_credits_earned = 0
        overall_total_points = 0
        overall_graded_credits = 0
        
        # We will use an ordered dictionary to keep the sorting order
        terms_data_dict = {}
        
        for e in enrollments:
            term = e.class_instance.term
            if term not in terms_data_dict:
                terms_data_dict[term] = {
                    'term': term,
                    'enrollments': [],
                    'total_credits': 0,
                    'credits_earned': 0,
                    'total_points': 0,
                    'graded_credits': 0,
                }
            
            terms_data_dict[term]['enrollments'].append(e)
            
            subject_credits = e.class_instance.subject.credits
            terms_data_dict[term]['total_credits'] += subject_credits
            overall_total_credits += subject_credits
            
            if e.final_grade:
                e.point = e.gpa
                e.total_point = e.gpa * subject_credits
                
                terms_data_dict[term]['total_points'] += e.total_point
                overall_total_points += e.total_point
                
                terms_data_dict[term]['graded_credits'] += subject_credits
                overall_graded_credits += subject_credits
                
                terms_data_dict[term]['credits_earned'] += e.credits
                overall_credits_earned += e.credits
            else:
                e.point = None
                e.total_point = None
                
        terms_data_list = []
        for term, data in terms_data_dict.items():
            g_credits = data['graded_credits']
            data['gpa'] = data['total_points'] / g_credits if g_credits > 0 else 0.0
            terms_data_list.append(data)
            
        overall_gpa = overall_total_points / overall_graded_credits if overall_graded_credits > 0 else 0.0
        
    except AttributeError:
        terms_data_list = []
        overall_total_credits = 0
        overall_credits_earned = 0
        overall_gpa = 0.0
        
    context = {
        'terms_data': terms_data_list,
        'overall_total_credits': overall_total_credits,
        'overall_credits_earned': overall_credits_earned,
        'overall_gpa': round(overall_gpa, 2)
    }
    return render(request, 'myapp/student_grades.html', context)
