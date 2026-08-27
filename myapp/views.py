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
        teacher = request.user.teacher
        classes = teacher.class_set.select_related('subject', 'term', 'room').annotate(
            student_count=Count('enrollment')
        ).order_by('-term__start_date', 'subject__name')
        salary = teacher.salary
    except AttributeError:
        classes = []
        salary = None

    context = {
        'classes': classes,
        'salary': salary,
    }

    return render(request, 'myapp/teacher_dashboard.html', context)

@login_required(login_url='/login')
def teacher_classes(request):
    try:
        teacher = request.user.teacher
        classes = teacher.class_set.select_related('subject', 'term', 'room').annotate(
            student_count=Count('enrollment')
        ).order_by('-term__start_date', 'subject__name')
        
        grouped_classes = {}
        for c in classes:
            if c.term not in grouped_classes:
                grouped_classes[c.term] = []
            grouped_classes[c.term].append(c)
    except AttributeError:
        classes = []
        grouped_classes = {}

    context = {
        'classes': classes,
        'grouped_classes': grouped_classes,
    }

    return render(request, 'myapp/teacher_classes.html', context)

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


@login_required(login_url='/login')
def teacher_roster(request, class_id):
    try:
        teacher = request.user.teacher
        # Ensure the class belongs to this teacher
        class_instance = Class.objects.get(id=class_id, teacher=teacher)
    except (AttributeError, Class.DoesNotExist):
        return redirect('teacher_dashboard')

    expected_batch = class_instance.computed_batch
    enrollments = class_instance.enrollment_set.filter(
        student__batch=expected_batch
    ).select_related('student', 'student__user').all()

    grade_distribution = {'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'N/A': 0}
    for e in enrollments:
        if e.final_grade in grade_distribution:
            grade_distribution[e.final_grade] += 1
        else:
            grade_distribution['N/A'] += 1
            
    import json
    
    context = {
        'class_instance': class_instance,
        'enrollments': enrollments,
        'grades_labels_json': json.dumps(list(grade_distribution.keys())),
        'grades_counts_json': json.dumps(list(grade_distribution.values())),
    }
    return render(request, 'myapp/teacher_roster.html', context)

from django.views.decorators.http import require_POST
from myapp.models import Assessment, StudentScore

@login_required(login_url='/login')
def teacher_assignments(request, class_id):
    try:
        teacher = request.user.teacher
        class_instance = Class.objects.get(id=class_id, teacher=teacher)
    except (AttributeError, Class.DoesNotExist):
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        max_score = request.POST.get('max_score')
        if name and max_score:
            try:
                max_score_float = float(max_score)
                if max_score_float > 0 and max_score_float <= 99999.99:
                    Assessment.objects.create(
                        class_instance=class_instance,
                        name=name,
                        max_score=max_score_float
                    )
                else:
                    messages.error(request, 'Max score must be between 0.01 and 99999.99.')
            except ValueError:
                messages.error(request, 'Invalid max score value.')
            return redirect('teacher_assignments', class_id=class_id)
            
    assignments = Assessment.objects.filter(class_instance=class_instance).order_by('id')
    
    context = {
        'class_instance': class_instance,
        'assignments': assignments,
    }
    return render(request, 'myapp/teacher_assignments.html', context)

@login_required(login_url='/login')
def teacher_assignment_scores(request, class_id, assessment_id):
    try:
        teacher = request.user.teacher
        class_instance = Class.objects.get(id=class_id, teacher=teacher)
        assessment = Assessment.objects.get(id=assessment_id, class_instance=class_instance)
    except (AttributeError, Class.DoesNotExist, Assessment.DoesNotExist):
        return redirect('teacher_dashboard')
        
    expected_batch = class_instance.computed_batch
    enrollments = class_instance.enrollment_set.filter(
        student__batch=expected_batch
    ).select_related('student', 'student__user').all()

    if request.method == 'POST':
        for enrollment in enrollments:
            score_val = request.POST.get(f'score_{enrollment.id}')
            if score_val:
                # Update or create
                StudentScore.objects.update_or_create(
                    enrollment=enrollment,
                    assessment=assessment,
                    defaults={'score': score_val}
                )
            elif score_val == "":
                # If explicitly cleared, delete the score manually to trigger delete() method
                for score in StudentScore.objects.filter(
                    enrollment=enrollment,
                    assessment=assessment
                ):
                    score.delete()
        return redirect('teacher_assignment_scores', class_id=class_id, assessment_id=assessment_id)

    # Pre-fetch scores for this assessment
    student_scores = StudentScore.objects.filter(
        assessment=assessment, 
        enrollment__in=enrollments
    )
    score_map = {s.enrollment_id: s.score for s in student_scores}
    
    # attach score to enrollment for the template
    for e in enrollments:
        e.current_score = score_map.get(e.id, '')

    context = {
        'class_instance': class_instance,
        'assessment': assessment,
        'enrollments': enrollments,
    }
    return render(request, 'myapp/teacher_assignment_scores.html', context)


@login_required(login_url='/login')
@require_POST
def delete_assessment(request, class_id, assessment_id):
    try:
        teacher = request.user.teacher
        class_instance = Class.objects.get(id=class_id, teacher=teacher)
        assessment = Assessment.objects.get(id=assessment_id, class_instance=class_instance)
        # Manually delete scores to trigger the custom delete() method
        for score in StudentScore.objects.filter(assessment=assessment):
            score.delete()
        assessment.delete()
    except (AttributeError, Class.DoesNotExist, Assessment.DoesNotExist):
        pass
    
    return redirect('teacher_assignments', class_id=class_id)


import openpyxl
from django.http import HttpResponse
from django.contrib import messages

@login_required(login_url='/login')
def export_scores_excel(request, class_id, assessment_id):
    try:
        teacher = request.user.teacher
        class_instance = Class.objects.get(id=class_id, teacher=teacher)
        assessment = Assessment.objects.get(id=assessment_id, class_instance=class_instance)
    except (AttributeError, Class.DoesNotExist, Assessment.DoesNotExist):
        return redirect('teacher_dashboard')

    expected_batch = class_instance.computed_batch
    enrollments = class_instance.enrollment_set.filter(
        student__batch=expected_batch
    ).select_related('student', 'student__user').all()

    student_scores = StudentScore.objects.filter(
        assessment=assessment, 
        enrollment__in=enrollments
    )
    score_map = {s.enrollment_id: s.score for s in student_scores}

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Scores"

    # Header
    ws.append(['Student ID', 'Student Name', 'Score'])

    for e in enrollments:
        student_id = e.student.student_id
        student_name = e.student.user.get_full_name() or e.student.user.username
        score = score_map.get(e.id, 0)
        ws.append([student_id, student_name, score])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"{class_instance.subject.name}_{assessment.name}_Scores.xlsx".replace(' ', '_')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required(login_url='/login')
@require_POST
def import_scores_excel(request, class_id, assessment_id):
    try:
        teacher = request.user.teacher
        class_instance = Class.objects.get(id=class_id, teacher=teacher)
        assessment = Assessment.objects.get(id=assessment_id, class_instance=class_instance)
    except (AttributeError, Class.DoesNotExist, Assessment.DoesNotExist):
        return redirect('teacher_dashboard')

    if 'excel_file' not in request.FILES:
        messages.error(request, 'Please upload a valid Excel file.')
        return redirect('teacher_assignment_scores', class_id=class_id, assessment_id=assessment_id)

    excel_file = request.FILES['excel_file']
    if not excel_file.name.endswith('.xlsx'):
        messages.error(request, 'Invalid file format. Please upload an .xlsx file.')
        return redirect('teacher_assignment_scores', class_id=class_id, assessment_id=assessment_id)

    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb.active

        # Find indexes of columns by reading header
        headers = [str(cell.value).strip().lower() for cell in ws[1] if cell.value is not None]
        try:
            id_idx = headers.index('student id')
            score_idx = headers.index('score')
        except ValueError:
            messages.error(request, 'Invalid Excel format. Must contain "Student ID" and "Score" columns.')
            return redirect('teacher_assignment_scores', class_id=class_id, assessment_id=assessment_id)

        expected_batch = class_instance.computed_batch
        enrollments = class_instance.enrollment_set.filter(
            student__batch=expected_batch
        ).select_related('student')
        
        # Mapping student ID to enrollment object
        enrollment_map = {str(e.student.student_id): e for e in enrollments}
        
        updated_count = 0
        skipped_count = 0

        # Skip header
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[id_idx] is None:
                continue
                
            student_id = str(row[id_idx]).strip()
            score_val = row[score_idx]
            
            if not student_id or score_val is None:
                continue

            try:
                score_val = float(score_val)
            except ValueError:
                skipped_count += 1
                continue
            
            if score_val < 0 or score_val > float(assessment.max_score):
                skipped_count += 1
                continue

            if student_id in enrollment_map:
                enrollment = enrollment_map[student_id]
                obj, created = StudentScore.objects.update_or_create(
                    enrollment=enrollment,
                    assessment=assessment,
                    defaults={'score': score_val}
                )
                updated_count += 1
            else:
                skipped_count += 1
        
        if skipped_count > 0:
            messages.success(request, f'Successfully imported scores for {updated_count} students. (Skipped/Invalid: {skipped_count})')
        else:
            messages.success(request, f'Successfully imported scores for {updated_count} students.')
    
    except Exception as e:
        messages.error(request, f'Error reading Excel file: {str(e)}')
    
    return redirect('teacher_assignment_scores', class_id=class_id, assessment_id=assessment_id)

