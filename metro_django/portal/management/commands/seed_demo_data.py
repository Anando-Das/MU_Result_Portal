from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
# pyrefly: ignore [missing-import]
from portal.models import Student, Teacher, TeacherBatch, ResultSheet, StudentResult
from datetime import date

class Command(BaseCommand):
    help = 'Seeds demo data for students and results'

    def handle(self, *args, **kwargs):
        hashed_password = make_password('123456')
        
        student, _ = Student.objects.get_or_create(
            student_id='STU-2025-101',
            defaults={
                'student_name': 'Demo Student',
                'email': 'demo@student.com',
                'password': hashed_password,
                'batch': 'Summer 25',
                'dept': 'CSE',
                'section': 'A'
            }
        )
        
        teacher, _ = Teacher.objects.get_or_create(
            email='teacher@demo.com',
            defaults={
                'teacher_name': 'Demo Teacher',
                'password': hashed_password,
                'dept': 'CSE'
            }
        )

        tbatch, _ = TeacherBatch.objects.get_or_create(
            teacher=teacher,
            batch='Summer 25',
            section='A'
        )

        # Past courses (Completed)
        rs1, _ = ResultSheet.objects.get_or_create(
            teacher_batch=tbatch,
            course_title='Introduction to Computer Science',
            semester='Summer 25',
            defaults={
                'start_date': date(2025, 5, 1),
                'end_date': date(2025, 8, 30),
                'course_credit': 3.0
            }
        )
        sr1, _ = StudentResult.objects.get_or_create(result_sheet=rs1, student=student)
        sr1.total = 85
        sr1.cgpa = 4.00
        sr1.save()

        rs2, _ = ResultSheet.objects.get_or_create(
            teacher_batch=tbatch,
            course_title='Calculus I',
            semester='Summer 25',
            defaults={
                'start_date': date(2025, 5, 1),
                'end_date': date(2025, 8, 30),
                'course_credit': 3.0
            }
        )
        sr2, _ = StudentResult.objects.get_or_create(result_sheet=rs2, student=student)
        sr2.total = 78
        sr2.cgpa = 3.75
        sr2.save()
        
        rs3, _ = ResultSheet.objects.get_or_create(
            teacher_batch=tbatch,
            course_title='Physics I',
            semester='Fall 25',
            defaults={
                'start_date': date(2025, 9, 1),
                'end_date': date(2025, 12, 30),
                'course_credit': 3.0
            }
        )
        sr3, _ = StudentResult.objects.get_or_create(result_sheet=rs3, student=student)
        sr3.total = 70
        sr3.cgpa = 3.50
        sr3.save()
        
        rs4, _ = ResultSheet.objects.get_or_create(
            teacher_batch=tbatch,
            course_title='English Composition',
            semester='Spring 26',
            defaults={
                'start_date': date(2026, 1, 1),
                'end_date': date(2026, 4, 30),
                'course_credit': 2.0
            }
        )
        sr4, _ = StudentResult.objects.get_or_create(result_sheet=rs4, student=student)
        sr4.total = 81
        sr4.cgpa = 4.00
        sr4.save()

        # Current courses (Not yet graded)
        rs5, _ = ResultSheet.objects.get_or_create(
            teacher_batch=tbatch,
            course_title='Data Structures',
            semester='Summer 26',
            defaults={
                'start_date': date(2026, 5, 1),
                'end_date': date(2026, 8, 30),
                'course_credit': 3.0
            }
        )
        sr5, _ = StudentResult.objects.get_or_create(result_sheet=rs5, student=student)
        sr5.total = None
        sr5.cgpa = None
        sr5.save()
        
        rs6, _ = ResultSheet.objects.get_or_create(
            teacher_batch=tbatch,
            course_title='Linear Algebra',
            semester='Summer 26',
            defaults={
                'start_date': date(2026, 5, 1),
                'end_date': date(2026, 8, 30),
                'course_credit': 3.0
            }
        )
        sr6, _ = StudentResult.objects.get_or_create(result_sheet=rs6, student=student)
        sr6.total = None
        sr6.cgpa = None
        sr6.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data'))
