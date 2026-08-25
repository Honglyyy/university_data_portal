import random
from datetime import datetime

f = open('seed_data.sql', 'w')
def write(sql): f.write(sql + "\n")

write("-- Seed data for university_data_portal")
write("-- Completely relies on auto-increment and subqueries to prevent ANY conflicts!\n")

password_hash = "pbkdf2_sha256$1500000$PfD8Ri2KEtlwcdipVIS24N$FZlKLGENSKMm8w9KVEfK8dM0Wn+WO7mNfR0EwnU7Imc="

NUM_TEACHERS = 10
NUM_STUDENTS = 100
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
# 11 terms: Fall 2020 to Fall 2025
write("\n-- Terms")
term_names = []
term_years = {}
for i in range(11):
    year = START_YEAR + (i // 2)
    sem = "Fall" if i % 2 == 0 else "Spring"
    term_name = f"{sem} {year}"
    term_names.append(term_name)
    term_years[term_name] = year
    write(f"INSERT INTO myapp_term (name, start_date, end_date) VALUES ('{term_name}', '{year}-01-01', '{year}-06-01');")

# 4. Subjects
write("\n-- Subjects")
subject_names = []
for dep_name, subjects in department_subjects.items():
    for sub_name in subjects:
        subject_names.append(sub_name)
        write(f"INSERT INTO myapp_subject (name, credits, department_id) VALUES ('{sub_name}', {random.choice([3,4])}, (SELECT id FROM myapp_department WHERE name = '{dep_name}'));")

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
for username in student_usernames:
    dep_name = random.choice(departments)
    stid = f"STID-{username}"
    
    # Assign a batch 1 to 6
    batch_num = random.randint(1, 6)
    
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
# Each teacher teaches 3-4 classes TOTAL.
# We distribute these classes evenly across the 11 terms.
write("\n-- Classes")
all_classes = []
cid_counter = 1

for tid in teacher_ids:
    num_classes = random.randint(3, 4)
    tid_dep = teacher_departments[tid]
    possible_subjects = department_subjects[tid_dep]
    
    for _ in range(num_classes):
        cid = f"C{cid_counter}"
        room_name = random.choice(room_names)
        sub_name = random.choice(possible_subjects)
        
        all_classes.append({
            'cid': cid,
            'tid': tid,
            'room_name': room_name,
            'sub_name': sub_name
        })
        cid_counter += 1

# Shuffle and assign terms round-robin to ensure every term gets ~3 classes
random.shuffle(all_classes)
for i, cls in enumerate(all_classes):
    term_idx = i % 11
    term_name = term_names[term_idx]
    cls['term_idx'] = term_idx
    cls['term_name'] = term_name
    
    class_year = term_years[term_name]
    batch_num = class_year - START_YEAR + 1
    
    write(f"INSERT INTO myapp_class (class_id, batch, room_id, subject_id, teacher_id, term_id) VALUES ('{cls['cid']}', 'Batch {batch_num}', (SELECT id FROM myapp_room WHERE name = '{cls['room_name']}'), (SELECT id FROM myapp_subject WHERE name = '{cls['sub_name']}'), (SELECT id FROM myapp_teacher WHERE teacher_id = '{cls['tid']}'), (SELECT id FROM myapp_term WHERE name = '{term_name}'));")

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

for student in student_data:
    stid = student['stid']
    batch = student['batch']
    
    # Batch 1 starts at term 0. Batch 2 at term 2.
    start_term = (batch - 1) * 2
    # 4 years = 8 terms contiguous. Cap at term 10 (current term)
    end_term = min(start_term + 7, 10)
    
    # For every active term
    for term_idx in range(start_term, end_term + 1):
        classes_in_term = [c for c in all_classes if c['term_idx'] == term_idx]
        
        # Take at least 3 courses (or all available if < 3)
        num_to_take = min(len(classes_in_term), random.randint(3, 4))
        if num_to_take == 0: continue
        
        enrolled_classes = random.sample(classes_in_term, num_to_take)
        
        for cls in enrolled_classes:
            cid = cls['cid']
            write(f"INSERT INTO myapp_enrollment (final_score, final_grade, credits, gpa, class_instance_id, student_id) VALUES (NULL, NULL, 0, 0.0, (SELECT id FROM myapp_class WHERE class_id = '{cid}'), (SELECT id FROM myapp_student WHERE student_id = '{stid}'));")
            
            for aname in assessments_by_class[cid]:
                score = random.uniform(40.0, 100.0)
                enr_subquery = f"(SELECT id FROM myapp_enrollment WHERE student_id = (SELECT id FROM myapp_student WHERE student_id = '{stid}') AND class_instance_id = (SELECT id FROM myapp_class WHERE class_id = '{cid}'))"
                ass_subquery = f"(SELECT id FROM myapp_assessment WHERE name = '{aname}')"
                scores_sql.append(f"INSERT INTO myapp_studentscore (score, assessment_id, enrollment_id) VALUES ({score:.2f}, {ass_subquery}, {enr_subquery});")

for line in scores_sql:
    write(line)

f.close()
