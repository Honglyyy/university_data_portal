import random
from datetime import datetime

f = open('seed_data.sql', 'w')
def write(sql): f.write(sql + "\n")

write("-- Seed data for university_data_portal")
write("-- Completely relies on auto-increment and subqueries to prevent ANY conflicts!\n")
write("BEGIN TRANSACTION;\n")

password_hash = "pbkdf2_sha256$1500000$PfD8Ri2KEtlwcdipVIS24N$FZlKLGENSKMm8w9KVEfK8dM0Wn+WO7mNfR0EwnU7Imc="

NUM_TEACHERS = 10
NUM_STUDENTS = 800
NUM_DEPARTMENTS = 5
NUM_ROOMS = 10

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
START_YEAR = 2020

first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]

department_subjects = {
    "Computer Science": ["Web Design", "Data Structures", "Algorithms", "Database Systems", "Operating Systems", "Artificial Intelligence", "Software Engineering", "Computer Networks"],
    "Mathematics": ["Calculus I", "Linear Algebra", "Discrete Math", "Differential Equations", "Statistics", "Number Theory"],
    "Physics": ["Classical Mechanics", "Electromagnetism", "Quantum Physics", "Thermodynamics", "Optics"],
    "Business": ["Financial Accounting", "Marketing Principles", "Microeconomics", "Business Ethics", "Corporate Finance"],
    "English": ["Creative Writing", "American Literature", "Poetry", "Linguistics", "Shakespeare"]
}

departments = list(department_subjects.keys())

# 1. Users
write("-- Users")
teacher_usernames = []
for i in range(1, NUM_TEACHERS + 1):
    username = f"T-{i:04d}"
    teacher_usernames.append(username)
    email = f"teacher{i}@example.com"
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    write(f"INSERT INTO myapp_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES ('{password_hash}', 0, '{username}', '{fname}', '{lname}', '{email}', 1, 1, '{current_time}');")

student_usernames = []
for i in range(1, NUM_STUDENTS + 1):
    username = f"S-{i:04d}"
    student_usernames.append(username)
    email = f"student{i}@example.com"
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    write(f"INSERT INTO myapp_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES ('{password_hash}', 0, '{username}', '{fname}', '{lname}', '{email}', 0, 1, '{current_time}');")

# 2. Departments
write("\n-- Departments")
for dep in departments:
    write(f"INSERT INTO myapp_department (name) VALUES ('{dep}');")

# 3. Terms
# 12 terms: Fall 2020 to Spring 2026
write("\n-- Terms")
term_names = []
term_years = {}
for i in range(12):
    if i % 2 == 0:
        sem = "Fall"
        year = START_YEAR + (i // 2)
        start_date = f"{year}-09-01"
        end_date = f"{year}-12-31"
    else:
        sem = "Spring"
        year = START_YEAR + (i // 2) + 1
        start_date = f"{year}-01-01"
        end_date = f"{year}-05-31"
    term_name = f"{sem} {year}"
    term_names.append(term_name)
    term_years[term_name] = year
    write(f"INSERT INTO myapp_term (name, start_date, end_date) VALUES ('{term_name}', '{start_date}', '{end_date}');")

# 4. Subjects
write("\n-- Subjects")
subject_names = []
subject_credits_dict = {}
for dep_name, subjects in department_subjects.items():
    for sub_name in subjects:
        subject_names.append(sub_name)
        c = random.choice([3,4])
        subject_credits_dict[sub_name] = c
        write(f"INSERT INTO myapp_subject (name, credits, department_id) VALUES ('{sub_name}', {c}, (SELECT id FROM myapp_department WHERE name = '{dep_name}'));")

# 5. Teachers
write("\n-- Teachers")
teacher_ids = []
teacher_departments = {}
for username in teacher_usernames:
    dep_name = random.choice(departments)
    tid = f"TID-{username}"
    teacher_ids.append(tid)
    teacher_departments[tid] = dep_name
    write(f"INSERT INTO myapp_teacher (teacher_id, salary, department_id, user_id) VALUES ('{tid}', {random.randint(50000, 100000)}, (SELECT id FROM myapp_department WHERE name = '{dep_name}'), (SELECT id FROM myapp_user WHERE username = '{username}'));")

# 6. Students
write("\n-- Students")
student_data = [] # stores dict of student info
for idx, username in enumerate(student_usernames):
    dep_name = random.choice(departments)
    stid = f"STID-{username}"
    
    student_number = idx + 1
    if student_number <= 133:
        batch_num = 1
    elif student_number <= 266:
        batch_num = 2
    elif student_number <= 399:
        batch_num = 3
    elif student_number <= 533:
        batch_num = 4
    elif student_number <= 666:
        batch_num = 5
    else:
        batch_num = 6
    
    student_data.append({
        'stid': stid,
        'batch': batch_num
    })
    
    write(f"INSERT INTO myapp_student (student_id, level, batch, created_at, department_id, user_id) VALUES ('{stid}', 'Undergraduate', 'Batch {batch_num}', '{current_time}', (SELECT id FROM myapp_department WHERE name = '{dep_name}'), (SELECT id FROM myapp_user WHERE username = '{username}'));")

# 7. Rooms
write("\n-- Rooms")
room_names = []
for i in range(1, NUM_ROOMS + 1):
    rname = f"Room {i}"
    room_names.append(rname)
    write(f"INSERT INTO myapp_room (name, building, campus) VALUES ('{rname}', 'Building {chr(65 + i%5)}', 'Main Campus');")

# 8. Classes
# Each teacher teaches 1 class per term.
write("\n-- Classes")
all_classes = []
cid_counter = 1

for tid in teacher_ids:
    tid_dep = teacher_departments[tid]
    possible_subjects = department_subjects[tid_dep]
    
    for term_idx, term_name in enumerate(term_names):
        num_classes_in_term = random.randint(2, 3)
        
        if num_classes_in_term == 3:
            schedules = ["Saturday 10:00 - 13:00", "Saturday 13:30 - 16:30", "Sunday 10:00 - 13:00"]
        else:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            times = ["08:00 - 11:00", "12:00 - 15:00", "17:00 - 21:00"]
            all_weekday_slots = [f"{d} {t}" for d in days for t in times]
            schedules = random.sample(all_weekday_slots, num_classes_in_term)
            
        for i in range(num_classes_in_term):
            cid = f"C{cid_counter}"
            room_name = random.choice(room_names)
            sub_name = random.choice(possible_subjects)
            schedule = schedules[i]
            
            # Determine active batches for this term
            active_batches = [b for b in range(1, 7) if (b - 1) * 2 <= term_idx < (b - 1) * 2 + 8]
            batch_num = random.choice(active_batches) if active_batches else 1
            
            all_classes.append({
                'cid': cid,
                'tid': tid,
                'room_name': room_name,
                'sub_name': sub_name,
                'term_idx': term_idx,
                'term_name': term_name,
                'schedule': schedule,
                'batch': batch_num
            })
            cid_counter += 1

for cls in all_classes:
    term_name = cls['term_name']
    batch_num = cls['batch']
    write(f"INSERT INTO myapp_class (class_id, batch, schedule, room_id, subject_id, teacher_id, term_id) VALUES ('{cls['cid']}', 'Batch {batch_num}', '{cls['schedule']}', (SELECT id FROM myapp_room WHERE name = '{cls['room_name']}'), (SELECT id FROM myapp_subject WHERE name = '{cls['sub_name']}'), (SELECT id FROM myapp_teacher WHERE teacher_id = '{cls['tid']}'), (SELECT id FROM myapp_term WHERE name = '{term_name}'));")

# 9. Assessments
write("\n-- Assessments")
assessments_by_class = {}
for cls in all_classes:
    cid = cls['cid']
    assessments_by_class[cid] = []
    num_assessments = random.randint(3, 5)
    
    assessment_types = ["Midterm", "Final Exam", "Assignment 1", "Assignment 2", "Project", "Quiz 1", "Quiz 2"]
    chosen_types = random.sample(assessment_types, num_assessments)
    
    for atype in chosen_types:
        aname = f"{atype} - {cid}"
        assessments_by_class[cid].append(aname)
        write(f"INSERT INTO myapp_assessment (name, max_score, class_instance_id) VALUES ('{aname}', 100.00, (SELECT id FROM myapp_class WHERE class_id = '{cid}'));")

# 10. Enrollments and 11. StudentScores
write("\n-- Enrollments")
scores_sql = ["\n-- StudentScores"]

for term_idx in range(12):
    classes_in_term = [c for c in all_classes if c['term_idx'] == term_idx]
    
    for cls in classes_in_term:
        cid = cls['cid']
        cls_batch = cls.get('batch')
        
        # Enforce same-batch-only enrollment
        valid_students = [s for s in student_data if s['batch'] == cls_batch]
        
        num_students_for_class = random.randint(10, 20)
        num_students_for_class = min(num_students_for_class, len(valid_students))
        if num_students_for_class == 0: continue
        
        enrolled_students = random.sample(valid_students, num_students_for_class)
        
        for student in enrolled_students:
            stid = student['stid']
            
            assessments = assessments_by_class[cid]
            total_achieved = 0.0
            total_max = len(assessments) * 100.0
            
            my_scores = []
            for aname in assessments:
                score = random.uniform(40.0, 100.0)
                my_scores.append((aname, score))
                total_achieved += score
                
            final_score = (total_achieved / total_max) * 100 if total_max > 0 else 0
            
            if final_score >= 95:
                final_grade, gpa = 'A+', 4.0
            elif final_score >= 90:
                final_grade, gpa = 'A', 3.75
            elif final_score >= 85:
                final_grade, gpa = 'B', 3.0
            elif final_score >= 70:
                final_grade, gpa = 'C', 2.0
            elif final_score >= 65:
                final_grade, gpa = 'D', 1.0
            elif final_score >= 60:
                final_grade, gpa = 'E', 0.5
            else:
                final_grade, gpa = 'F', 0.0
                
            sub_name = cls['sub_name']
            credits_earned = subject_credits_dict[sub_name] if final_score >= 60 else 0 
            
            write(f"INSERT INTO myapp_enrollment (final_score, final_grade, credits, gpa, class_instance_id, student_id) VALUES ({final_score:.2f}, '{final_grade}', {credits_earned}, {gpa:.2f}, (SELECT id FROM myapp_class WHERE class_id = '{cid}'), (SELECT id FROM myapp_student WHERE student_id = '{stid}'));")
            
            for aname, score in my_scores:
                enr_subquery = f"(SELECT id FROM myapp_enrollment WHERE student_id = (SELECT id FROM myapp_student WHERE student_id = '{stid}') AND class_instance_id = (SELECT id FROM myapp_class WHERE class_id = '{cid}'))"
                ass_subquery = f"(SELECT id FROM myapp_assessment WHERE name = '{aname}')"
                scores_sql.append(f"INSERT INTO myapp_studentscore (score, assessment_id, enrollment_id) VALUES ({score:.2f}, {ass_subquery}, {enr_subquery});")

for line in scores_sql:
    write(line)

write("\n-- Cleanup unused students")
write("DELETE FROM myapp_student WHERE id NOT IN (SELECT student_id FROM myapp_enrollment);")
write("DELETE FROM myapp_user WHERE is_staff = 0 AND id NOT IN (SELECT user_id FROM myapp_student);")

write("COMMIT;")
f.close()
