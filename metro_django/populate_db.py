import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metro_django.settings')
django.setup()

from portal.models import Student, Teacher, Course, TeacherBatch, ResultSheet, StudentResult, Department
from django.contrib.auth.hashers import make_password

def populate():
    # Clear existing data
    StudentResult.objects.all().delete()
    ResultSheet.objects.all().delete()
    TeacherBatch.objects.all().delete()
    Course.objects.all().delete()
    Department.objects.all().delete()
    Teacher.objects.all().delete()
    Student.objects.all().delete()

    departments_data = {
        'CSE': {
            'name': 'Computer Science and Engineering',
            'courses': [
                ('CSE111', 'Computer Fundamentals', 3.0),
                ('CSE112', 'Programming Language C', 3.0),
                ('CSE113', 'Programming Language C Lab', 1.5),
                ('MAT111', 'Mathematics-I', 3.0),
                ('ENG111', 'English-I', 3.0),
                ('CSE121', 'Object Oriented Programming', 3.0),
                ('CSE122', 'Object Oriented Programming Lab', 1.5),
                ('CSE123', 'Data Structures', 3.0),
                ('CSE124', 'Data Structures Lab', 1.5),
                ('MAT121', 'Mathematics-II', 3.0),
                ('CSE211', 'Algorithms', 3.0),
                ('CSE212', 'Algorithms Lab', 1.5),
                ('CSE213', 'Database Management Systems', 3.0),
                ('CSE214', 'Database Management Systems Lab', 1.5),
                ('CSE311', 'Software Engineering', 3.0),
                ('CSE312', 'Web Engineering', 3.0),
                ('CSE411', 'Artificial Intelligence', 3.0),
                ('CSE412', 'Machine Learning', 3.0),
            ]
        },
        'BBA': {
            'name': 'Business Administration',
            'courses': [
                ('BBA111', 'Introduction to Business', 3.0),
                ('BBA112', 'Principles of Management', 3.0),
                ('BBA121', 'Business Mathematics', 3.0),
                ('BBA122', 'Financial Accounting', 3.0),
                ('BBA211', 'Business Communication', 3.0),
                ('BBA212', 'Marketing Management', 3.0),
                ('BBA311', 'Human Resource Management', 3.0),
                ('BBA312', 'Corporate Finance', 3.0),
            ]
        },
        'English': {
            'name': 'English',
            'courses': [
                ('ENGL111', 'Introduction to Poetry', 3.0),
                ('ENGL112', 'Introduction to Prose', 3.0),
                ('ENGL121', 'History of English Literature', 3.0),
                ('ENGL122', 'Elizabethan Drama', 3.0),
                ('ENGL211', 'Romantic Poetry', 3.0),
                ('ENGL212', 'Victorian Literature', 3.0),
                ('ENGL311', 'Modern Drama', 3.0),
                ('ENGL312', 'American Literature', 3.0),
            ]
        }
    }

    for short_name, data in departments_data.items():
        Department.objects.create(
            name=short_name,
            num_courses=len(data['courses']),
            total_credits=sum(c[2] for c in data['courses']),
            num_semesters=8
        )
        for code, title, credit in data['courses']:
            Course.objects.create(course_code=code, course_title=title, credit=credit, dept=short_name)

    teachers = {}
    for dept in departments_data.keys():
        teachers[dept] = Teacher.objects.create(
            teacher_name=f"{dept} Professor",
            email=f"prof_{dept.lower()}@gmail.com",
            password=make_password("password123"),
            plain_password="password123",
            dept=dept,
            status='approved'
        )

    primary_student = Student.objects.create(
        student_id='232-115-150',
        student_name='Rakib Hasan',
        email='rakib@gmail.com',
        password=make_password("password123"),
        plain_password="password123",
        batch='Spring 23',
        dept='CSE',
        section='A',
        status='approved'
    )

    teacher_batch = TeacherBatch.objects.create(teacher=teachers['CSE'], batch='Spring 23', section='A')

    today = date.today()
    past_courses = departments_data['CSE']['courses'][:4]
    for code, title, credit in past_courses:
        rs = ResultSheet.objects.create(
            teacher_batch=teacher_batch, semester='Spring 2023',
            start_date=today - timedelta(days=200), end_date=today - timedelta(days=100),
            course_title=title, course_credit=credit
        )
        sr = StudentResult.objects.create(
            result_sheet=rs, student=primary_student,
            attendance=9, ct1=12, ct2=14, assignment=8, mid_term=25, final_term=32
        )
        sr.total = sr.attendance + sr.ct1 + sr.ct2 + sr.assignment + sr.mid_term + sr.final_term
        if sr.total >= 80: sr.cgpa = 4.00
        elif sr.total >= 75: sr.cgpa = 3.75
        elif sr.total >= 70: sr.cgpa = 3.50
        elif sr.total >= 65: sr.cgpa = 3.25
        elif sr.total >= 60: sr.cgpa = 3.00
        elif sr.total >= 55: sr.cgpa = 2.75
        elif sr.total >= 50: sr.cgpa = 2.50
        elif sr.total >= 45: sr.cgpa = 2.25
        elif sr.total >= 40: sr.cgpa = 2.00
        else: sr.cgpa = 0.00
        sr.save()

    current_courses = departments_data['CSE']['courses'][4:8]
    for code, title, credit in current_courses:
        rs = ResultSheet.objects.create(
            teacher_batch=teacher_batch, semester='Fall 2023',
            start_date=today - timedelta(days=30), end_date=today + timedelta(days=60),
            course_title=title, course_credit=credit
        )
        StudentResult.objects.create(result_sheet=rs, student=primary_student)
        
    print("Database populated successfully!")

if __name__ == '__main__':
    populate()
