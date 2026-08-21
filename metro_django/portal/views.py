# pyrefly: ignore [missing-import, untyped-import]
from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import, untyped-import]
from django.contrib import messages
# pyrefly: ignore [missing-import, untyped-import]
from django.contrib.auth.hashers import make_password, check_password
# pyrefly: ignore [missing-import, untyped-import]
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
# pyrefly: ignore [missing-import, untyped-import]
from django.http import HttpResponse
# pyrefly: ignore [missing-import, untyped-import]
from django.template.loader import get_template
# pyrefly: ignore [missing-import]
import xhtml2pdf.pisa as pisa
from io import BytesIO

# pyrefly: ignore [missing-import]
from .models import Student, Teacher, Course, CourseFaculty, TeacherBatch, ResultSheet, StudentResult, Notice, Department

def welcome(request):
    return render(request, 'portal/welcome.html')

# ---- Navbar Main Pages ----

def academics(request):
    schools = [
        {'name': 'Engineering', 'desc': 'Cutting-edge programs in CS, civil, mechanical, electrical, and more.'},
        {'name': 'Business', 'desc': 'MBA, finance, marketing, and entrepreneurship for the global economy.'},
        {'name': 'Humanities & Sciences', 'desc': 'Philosophy, literature, mathematics, chemistry, and physics.'},
        {'name': 'Medicine', 'desc': 'World-renowned medical school training the next generation of healers.'},
        {'name': 'Law', 'desc': 'A top-ranked law school producing leaders in justice and policy.'},
        {'name': 'Education', 'desc': 'Programs in teaching, curriculum design, and educational leadership.'},
        {'name': 'Architecture', 'desc': 'Creative and sustainable design programs shaping the built environment.'},
        {'name': 'Social Sciences', 'desc': 'Psychology, sociology, economics, and political science programs.'},
    ]
    return render(request, 'portal/pages/academics.html', {'active_nav': 'academics', 'schools': schools})

def research(request):
    return render(request, 'portal/pages/research.html', {'active_nav': 'research'})

def campus_life(request):
    return render(request, 'portal/pages/campus_life.html', {'active_nav': 'campus_life'})

def athletics(request):
    sports = [
        {'name': 'Cricket', 'detail': 'Men\'s & Women\'s varsity teams — 8 national championships.'},
        {'name': 'Football', 'detail': 'Competing at the highest level with a storied 80-year history.'},
        {'name': 'Swimming & Diving', 'detail': '12 Olympic medalists produced in the last two decades.'},
        {'name': 'Track & Field', 'detail': 'All-weather facilities and elite coaching programs.'},
        {'name': 'Basketball', 'detail': 'Men\'s & Women\'s teams competing nationally.'},
        {'name': 'Volleyball', 'detail': 'Award-winning programs for both indoor and beach volleyball.'},
        {'name': 'Tennis', 'detail': 'State-of-the-art courts and nationally ranked squads.'},
        {'name': 'Golf', 'detail': 'Championship-level facilities and a tradition of tour professionals.'},
    ]
    return render(request, 'portal/pages/athletics.html', {'active_nav': 'athletics', 'sports': sports})

def admission(request):
    return render(request, 'portal/pages/admission.html', {'active_nav': 'admission'})

def about(request):
    return render(request, 'portal/pages/about.html', {'active_nav': 'about'})

def news(request):
    return render(request, 'portal/pages/news.html', {'active_nav': 'news'})

def events(request):
    return render(request, 'portal/pages/events.html', {'active_nav': 'events'})

# ---- Top Bar Audience Pages ----

def students(request):
    return render(request, 'portal/pages/students.html')

def staff(request):
    return render(request, 'portal/pages/staff.html')

def visitors(request):
    return render(request, 'portal/pages/visitors.html')

def alumni(request):
    return render(request, 'portal/pages/alumni.html')

def student_signup(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '')
        student_name = request.POST.get('student_name', '')
        email = request.POST.get('email', '')
        batch = request.POST.get('batch', '')
        dept = request.POST.get('dept', '')
        section = request.POST.get('section', '')
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')

        errors = []
        if not student_id or not student_name or not email or not batch or not dept or not section or not password:
            errors.append("All fields are required.")
        if password != password_confirmation:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if Student.objects.filter(student_id=student_id).exists():
            errors.append("Student ID already exists.")
        if Student.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            for error in errors:
                messages.error(request, error)
            # Retain form input via context or just return with errors
            return render(request, 'portal/signup.html', {
                'old_data': request.POST
            })

        hashed_password = make_password(password)
        student = Student.objects.create(
            student_id=student_id,
            student_name=student_name,
            email=email,
            batch=batch,
            dept=dept,
            section=section,
            password=hashed_password,
            plain_password=password
        )

        messages.success(request, "Account created successfully. Please wait for admin approval.")
        return redirect('portal:login')

    return render(request, 'portal/signup.html')

def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        student = Student.objects.filter(email=email).first()
        if student and check_password(password, student.password):
            if student.status == 'pending':
                messages.error(request, "Your account is pending approval.")
                return render(request, 'portal/login.html', {'old_email': email})
            
            request.session['student_id'] = student.id
            request.session['student_name'] = student.student_name
            request.session['email'] = student.email
            return redirect('/')
        else:
            messages.error(request, "These credentials do not match our records.")
            return render(request, 'portal/login.html', {
                'old_email': email
            })

    return render(request, 'portal/login.html')

def student_logout(request):
    request.session.flush()
    return redirect('/')

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('/login')
        
    student_id = request.session['student_id']
    student = Student.objects.get(id=student_id)
    
    # Calculate current semester
    batch_str = student.batch
    try:
        parts = batch_str.split()
        session_name = parts[0].capitalize()
        session_year = int(parts[1])
        if session_year < 100:
            session_year += 2000
            
        seasons = {'Spring': 0, 'Summer': 1, 'Fall': 2}
        if session_name in seasons:
            start_val = session_year * 3 + seasons[session_name]
            
            # Current date logic
            current_date = date.today()
            curr_year = current_date.year
            curr_month = current_date.month
            if curr_month <= 4:
                curr_season = 'Spring'
            elif curr_month <= 8:
                curr_season = 'Summer'
            else:
                curr_season = 'Fall'
                
            curr_val = curr_year * 3 + seasons[curr_season]
            current_semester = (curr_val - start_val) + 1
        else:
            current_semester = 1
    except Exception:
        current_semester = 1
        
    all_results = StudentResult.objects.filter(student=student).select_related('result_sheet')
    
    completed_credits = Decimal('0.0')
    total_cgpa_points = Decimal('0.0')
    
    current_courses = []
    finished_courses = []
    
    today = date.today()
    for sr in all_results:
        if sr.result_sheet.end_date and sr.result_sheet.end_date < today:
            finished_courses.append(sr)
            if sr.cgpa is not None and sr.cgpa > 0:
                completed_credits += sr.result_sheet.course_credit
                total_cgpa_points += (sr.result_sheet.course_credit * sr.cgpa)
        else:
            current_courses.append(sr)
            
    if completed_credits > 0:
        cumulative_cgpa = total_cgpa_points / completed_credits
    else:
        cumulative_cgpa = Decimal('0.00')
        
    department = Department.objects.filter(name=student.dept).first()
    syllabus_courses = Course.objects.filter(dept=student.dept).order_by('course_code')
        
    context = {
        'student': student,
        'current_semester': current_semester,
        'completed_credits': completed_credits,
        'cumulative_cgpa': round(cumulative_cgpa, 2),
        'current_courses': current_courses,
        'finished_courses': finished_courses,
        'department': department,
        'syllabus_courses': syllabus_courses,
    }
    return render(request, 'portal/student_dashboard.html', context)

def student_download_syllabus_pdf(request):
    if 'student_id' not in request.session:
        return redirect('/login')
        
    student_id = request.session['student_id']
    student = Student.objects.get(id=student_id)
    
    department = Department.objects.filter(name=student.dept).first()
    courses = Course.objects.filter(dept=student.dept).order_by('course_code')
    
    if not department:
        # Fallback if department model doesn't exist for some reason
        class DummyDept:
            name = student.dept
            num_courses = courses.count()
            total_credits = sum(c.credit for c in courses)
            num_semesters = 'N/A'
        department = DummyDept()
    
    template_path = 'portal/admin/syllabus_pdf.html'
    context = {'department': department, 'courses': courses}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="syllabus_{student.dept}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
       
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def teacher_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        teacher = Teacher.objects.filter(email=email).first()
        if teacher and check_password(password, teacher.password):
            if teacher.status == 'pending':
                messages.error(request, "Your account is pending approval.")
                return render(request, 'portal/teachers/login.html', {'old_email': email})
                
            request.session['teacher_id'] = teacher.id
            request.session['teacher_name'] = teacher.teacher_name
            request.session['teacher_email'] = teacher.email
            messages.success(request, f"Welcome back, {teacher.teacher_name}!")
            return redirect('/teachers/dashboard')
        else:
            messages.error(request, "These credentials do not match our records.")
            return render(request, 'portal/teachers/login.html', {
                'old_email': email
            })

    return render(request, 'portal/teachers/login.html')

def teacher_signup(request):
    if request.method == 'POST':
        teacher_name = request.POST.get('teacher_name', '')
        email = request.POST.get('email', '')
        dept = request.POST.get('dept', '')
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')

        errors = []
        if not teacher_name or not email or not dept or not password:
            errors.append("All fields are required.")
        if password != password_confirmation:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if Teacher.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'portal/teachers/signup.html', {
                'old_data': request.POST
            })

        hashed_password = make_password(password)
        teacher = Teacher.objects.create(
            teacher_name=teacher_name,
            email=email,
            dept=dept,
            password=hashed_password,
            plain_password=password
        )

        messages.success(request, "Account created successfully. Please wait for admin approval.")
        return redirect('portal:teachers.login')

    return render(request, 'portal/teachers/signup.html')

def teacher_dashboard(request):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
    return render(request, 'portal/teachers/dashboard.html')

def teacher_add_batch(request):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
    
    teacher_id = request.session['teacher_id']
    teacher = Teacher.objects.get(id=teacher_id)

    if request.method == 'POST':
        batch_to_add = request.POST.get('batch', '')
        section_to_add = request.POST.get('section', '')
        if batch_to_add and section_to_add:
            TeacherBatch.objects.get_or_create(teacher=teacher, batch=batch_to_add, section=section_to_add)
            messages.success(request, f"Batch {batch_to_add} - Section {section_to_add} added successfully!")
        return redirect('portal:teachers.addBatch')
    
    added_batches_records = TeacherBatch.objects.filter(teacher=teacher).order_by('batch', 'section')
    
    all_batches = Student.objects.values_list('batch', flat=True).distinct().order_by('batch')
    all_sections = Student.objects.values_list('section', flat=True).distinct().order_by('section')
    
    return render(request, 'portal/teachers/add_batch.html', {
        'added_batches_records': added_batches_records,
        'all_batches': all_batches,
        'all_sections': all_sections,
    })

def teacher_delete_batch(request, pk):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
    teacher_id = request.session['teacher_id']
    teacher = Teacher.objects.get(id=teacher_id)
    TeacherBatch.objects.filter(pk=pk, teacher=teacher).delete()
    messages.success(request, "Batch removed successfully.")
    return redirect('portal:teachers.addBatch')

def teacher_view_batch_students(request, batch_number, section):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
    
    students = Student.objects.filter(batch=batch_number, section=section).order_by('student_id')
    return render(request, 'portal/teachers/view_batch_students.html', {
        'batch_number': batch_number,
        'section': section,
        'students': students
    })

def teacher_results(request):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
    
    teacher_id = request.session['teacher_id']
    teacher = Teacher.objects.get(id=teacher_id)
    
    if request.method == 'POST':
        batch_id = request.POST.get('batch', '')
        semester = request.POST.get('semester', '')
        start_date_str = request.POST.get('start_date', '')
        end_date_str = request.POST.get('end_date', '')
        course_title = request.POST.get('course_title', '')
        course_credit = request.POST.get('course_credit', '')
        
        try:
            teacher_batch = TeacherBatch.objects.get(id=batch_id, teacher=teacher)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            result_sheet = ResultSheet.objects.create(
                teacher_batch=teacher_batch,
                semester=semester,
                start_date=start_date,
                end_date=end_date,
                course_title=course_title,
                course_credit=course_credit
            )
            
            # Create default StudentResult records
            students = Student.objects.filter(batch=teacher_batch.batch, section=teacher_batch.section)
            for student in students:
                StudentResult.objects.create(
                    result_sheet=result_sheet,
                    student=student
                )
                
            messages.success(request, f"Result sheet for {course_title} created successfully.")
            return redirect('portal:teachers.results')
        except Exception as e:
            messages.error(request, f"Error creating result sheet: {str(e)}")
            
    teacher_batches = TeacherBatch.objects.filter(teacher=teacher)
    result_sheets = ResultSheet.objects.filter(teacher_batch__in=teacher_batches).order_by('-created_at')
    
    return render(request, 'portal/teachers/results.html', {
        'teacher_batches': teacher_batches,
        'result_sheets': result_sheets
    })

def teacher_delete_result(request, sheet_id):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
        
    if request.method == 'POST':
        teacher_id = request.session['teacher_id']
        teacher = Teacher.objects.get(id=teacher_id)
        result_sheet = get_object_or_404(ResultSheet, id=sheet_id, teacher_batch__teacher=teacher)
        result_sheet.delete()
        messages.success(request, f"Result sheet for {result_sheet.course_title} deleted successfully.")
        
    return redirect('portal:teachers.results')

def teacher_update_result(request, sheet_id):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
        
    teacher_id = request.session['teacher_id']
    teacher = Teacher.objects.get(id=teacher_id)
    
    result_sheet = get_object_or_404(ResultSheet, id=sheet_id, teacher_batch__teacher=teacher)
    
    # Sync students to ensure newly added students are included
    batch_students = Student.objects.filter(batch=result_sheet.teacher_batch.batch, section=result_sheet.teacher_batch.section)
    for student in batch_students:
        StudentResult.objects.get_or_create(result_sheet=result_sheet, student=student)
        
    student_results = StudentResult.objects.filter(result_sheet=result_sheet).order_by('student__student_id')
    
    is_editable = timezone.now().date() <= result_sheet.end_date
    
    if request.method == 'POST' and is_editable:
        for sr in student_results:
            attendance = request.POST.get(f'attendance_{sr.id}', '')
            ct1 = request.POST.get(f'ct1_{sr.id}', '')
            ct2 = request.POST.get(f'ct2_{sr.id}', '')
            assignment = request.POST.get(f'assignment_{sr.id}', '')
            mid_term = request.POST.get(f'mid_term_{sr.id}', '')
            final_term = request.POST.get(f'final_term_{sr.id}', '')
            
            try:
                # pyrefly: ignore [bad-assignment]
                sr.attendance = float(attendance) if attendance else None
                # pyrefly: ignore [bad-assignment]
                sr.ct1 = float(ct1) if ct1 else None
                # pyrefly: ignore [bad-assignment]
                sr.ct2 = float(ct2) if ct2 else None
                # pyrefly: ignore [bad-assignment]
                sr.assignment = float(assignment) if assignment else None
                # pyrefly: ignore [bad-assignment]
                sr.mid_term = float(mid_term) if mid_term else None
                # pyrefly: ignore [bad-assignment]
                sr.final_term = float(final_term) if final_term else None
                
                # Calculate total
                components = [sr.attendance, sr.ct1, sr.ct2, sr.assignment, sr.mid_term, sr.final_term]
                valid_components = [c for c in components if c is not None]
                if valid_components:
                    # pyrefly: ignore [bad-assignment]
                    sr.total = sum(valid_components)
                else:
                    sr.total = None
                    
                # UGC CGPA calculation
                if sr.total is not None:
                    # pyrefly: ignore [bad-assignment]
                    if sr.total >= 80: sr.cgpa = 4.00
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 75: sr.cgpa = 3.75
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 70: sr.cgpa = 3.50
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 65: sr.cgpa = 3.25
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 60: sr.cgpa = 3.00
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 55: sr.cgpa = 2.75
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 50: sr.cgpa = 2.50
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 45: sr.cgpa = 2.25
                    # pyrefly: ignore [bad-assignment]
                    elif sr.total >= 40: sr.cgpa = 2.00
                    # pyrefly: ignore [bad-assignment]
                    else: sr.cgpa = 0.00
                else:
                    # pyrefly: ignore [bad-assignment]
                    sr.cgpa = None
                    
                sr.save()
            except ValueError:
                pass # Ignore invalid inputs
                
        messages.success(request, "Results updated successfully.")
        return redirect('portal:teachers.updateResult', sheet_id=sheet_id)
        
    return render(request, 'portal/teachers/update_result.html', {
        'result_sheet': result_sheet,
        'student_results': student_results,
        'is_editable': is_editable
    })

def teacher_export_result_pdf(request, sheet_id):
    if 'teacher_id' not in request.session:
        return redirect('/teachers/')
        
    teacher_id = request.session['teacher_id']
    teacher = Teacher.objects.get(id=teacher_id)
    
    result_sheet = get_object_or_404(ResultSheet, id=sheet_id, teacher_batch__teacher=teacher)
    student_results = StudentResult.objects.filter(result_sheet=result_sheet).order_by('student__student_id')
    
    template_path = 'portal/teachers/result_pdf.html'
    context = {'result_sheet': result_sheet, 'student_results': student_results}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="results_{result_sheet.course_title}_{result_sheet.teacher_batch.batch}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
       
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def teacher_logout(request):
    # Laravel uses session()->forget(['teacher_id','teacher_name','teacher_email']);
    # We will remove them from Django's session.
    request.session.pop('teacher_id', None)
    request.session.pop('teacher_name', None)
    request.session.pop('teacher_email', None)
    messages.success(request, "Logged out successfully")
    return redirect('/teachers/')

# ---- Error Handlers ----
def error_404(request, exception=None):
    return render(request, 'portal/error.html', {'error_code': '404', 'error_message': 'Page Not Found'}, status=404)

def error_500(request, exception=None):
    return render(request, 'portal/error.html', {'error_code': '500', 'error_message': 'Internal Server Error'}, status=500)

def error_403(request, exception=None):
    return render(request, 'portal/error.html', {'error_code': '403', 'error_message': 'Forbidden'}, status=403)

def error_400(request, exception=None):
    return render(request, 'portal/error.html', {'error_code': '400', 'error_message': 'Bad Request'}, status=400)


# ============================================================
# ADMIN VIEWS
# ============================================================

ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = 'admin123'

def _admin_required(request):
    """Returns True if admin is logged in."""
    return request.session.get('is_admin') is True


def admin_login(request):
    if _admin_required(request):
        return redirect('portal:admin_dashboard')
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            return redirect('portal:admin_dashboard')
        error = 'Invalid credentials. Please try again.'
    return render(request, 'portal/admin/login.html', {'error': error})


def admin_logout(request):
    request.session.pop('is_admin', None)
    return redirect('portal:admin_login')


def admin_verify_password(request):
    """AJAX endpoint: verify admin password and return plain passwords."""
    import json
    from django.http import JsonResponse
    if not _admin_required(request):
        return JsonResponse({'success': False, 'message': 'Not authenticated'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    data = json.loads(request.body)
    entered = data.get('password', '')
    if entered != ADMIN_PASSWORD:
        return JsonResponse({'success': False, 'message': 'Wrong admin password.'})
    # Return all plain passwords
    students = list(Student.objects.values('id', 'plain_password'))
    teachers = list(Teacher.objects.values('id', 'plain_password'))
    return JsonResponse({'success': True, 'students': students, 'teachers': teachers})


def admin_dashboard(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_notices = Notice.objects.count()
    active_notices = Notice.objects.filter(is_active=True).count()
    recent_students = Student.objects.order_by('-created_at')[:5]
    recent_teachers = Teacher.objects.order_by('-created_at')[:5]
    return render(request, 'portal/admin/dashboard.html', {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_notices': total_notices,
        'active_notices': active_notices,
        'recent_students': recent_students,
        'recent_teachers': recent_teachers,
    })


def admin_students(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    query = request.GET.get('q', '')
    students = Student.objects.all().order_by('-created_at')
    if query:
        students = students.filter(student_name__icontains=query) | students.filter(student_id__icontains=query) | students.filter(email__icontains=query)
    return render(request, 'portal/admin/students.html', {
        'students': students,
        'query': query,
    })


def admin_teachers(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    query = request.GET.get('q', '')
    teachers = Teacher.objects.all().order_by('-created_at')
    if query:
        teachers = teachers.filter(teacher_name__icontains=query) | teachers.filter(email__icontains=query)
    return render(request, 'portal/admin/teachers.html', {
        'teachers': teachers,
        'query': query,
    })


def admin_notices(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    notices = Notice.objects.all()
    return render(request, 'portal/admin/notices.html', {'notices': notices})


def admin_create_notice(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        if title and body:
            Notice.objects.create(title=title, body=body, is_active=is_active)
            return redirect('portal:admin_notices')
    return render(request, 'portal/admin/create_notice.html')


def admin_edit_notice(request, notice_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        notice.title = request.POST.get('title', '').strip()
        notice.body = request.POST.get('body', '').strip()
        notice.is_active = request.POST.get('is_active') == 'on'
        notice.save()
        return redirect('portal:admin_notices')
    return render(request, 'portal/admin/create_notice.html', {'notice': notice})


def admin_toggle_notice(request, notice_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    notice = get_object_or_404(Notice, id=notice_id)
    notice.is_active = not notice.is_active
    notice.save()
    return redirect('portal:admin_notices')


def admin_delete_notice(request, notice_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    notice = get_object_or_404(Notice, id=notice_id)
    notice.delete()
    return redirect('portal:admin_notices')


def admin_delete_student(request, student_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('portal:admin_students')


def admin_delete_teacher(request, teacher_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    return redirect('portal:admin_teachers')


def admin_toggle_student_status(request, student_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    student = get_object_or_404(Student, id=student_id)
    if student.status == 'pending':
        student.status = 'approved'
    else:
        student.status = 'pending'
    student.save()
    return redirect('portal:admin_students')


def admin_toggle_teacher_status(request, teacher_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if teacher.status == 'pending':
        teacher.status = 'approved'
    else:
        teacher.status = 'pending'
    teacher.save()
    return redirect('portal:admin_teachers')


def admin_approve_all_students(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    
    Student.objects.filter(status='pending').update(status='approved')
    return redirect('portal:admin_students')


def admin_approve_all_teachers(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    
    Teacher.objects.filter(status='pending').update(status='approved')
    return redirect('portal:admin_teachers')

def admin_departments(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
    
    departments = Department.objects.all().order_by('-created_at')
    return render(request, 'portal/admin/departments.html', {'departments': departments})

def admin_create_department(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        num_courses = request.POST.get('num_courses', 0)
        total_credits = request.POST.get('total_credits', 0.0)
        num_semesters = request.POST.get('num_semesters', 0)
        
        if name:
            Department.objects.create(
                name=name,
                num_courses=num_courses,
                total_credits=total_credits,
                num_semesters=num_semesters
            )
            return redirect('portal:admin_departments')
            
    return render(request, 'portal/admin/departments.html')

def admin_department_details(request, dept_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
        
    dept = get_object_or_404(Department, id=dept_id)
    courses = Course.objects.filter(dept=dept.name).order_by('course_code')
    return render(request, 'portal/admin/department_details.html', {
        'department': dept,
        'courses': courses
    })

def admin_add_course(request, dept_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
        
    dept = get_object_or_404(Department, id=dept_id)
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        credit = request.POST.get('credit')
        
        if course_code and course_title and credit:
            # Check if course code already exists globally, as it's unique in the model
            if Course.objects.filter(course_code=course_code).exists():
                messages.error(request, f"Course code {course_code} already exists.")
            else:
                Course.objects.create(
                    course_code=course_code,
                    course_title=course_title,
                    credit=credit,
                    dept=dept.name
                )
    return redirect('portal:admin_department_details', dept_id=dept.id)

def admin_delete_course(request, dept_id, course_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
        
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('portal:admin_department_details', dept_id=dept_id)

def admin_download_syllabus_pdf(request, dept_id):
    if not _admin_required(request):
        return redirect('portal:admin_login')
        
    dept = get_object_or_404(Department, id=dept_id)
    courses = Course.objects.filter(dept=dept.name).order_by('course_code')
    
    template_path = 'portal/admin/syllabus_pdf.html'
    context = {'department': dept, 'courses': courses}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="syllabus_{dept.name.replace(" ", "_")}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def admin_email_result(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')

    import json
    from django.core.mail import EmailMessage
    from django.conf import settings as django_settings

    search_results = []
    selected_student = None
    is_all_students = False
    query = request.GET.get('q', '').strip()

    if query:
        search_results = Student.objects.filter(
            student_name__icontains=query
        ) | Student.objects.filter(
            student_id__icontains=query
        )
        search_results = search_results.order_by('student_name')

    selected_student_id = request.GET.get('student', '')
    if selected_student_id == 'all':
        is_all_students = True
    elif selected_student_id:
        selected_student = Student.objects.filter(id=selected_student_id).first()

    if request.method == 'POST':
        student_id_post = request.POST.get('student_id')
        mail_subject = request.POST.get('mail_subject', '').strip()
        mail_body = request.POST.get('mail_body', '').strip()
        result_type = request.POST.get('result_type', 'full_history')

        if student_id_post == 'all':
            students = Student.objects.filter(status='approved')
            if not students.exists():
                messages.error(request, '❌ No approved students found to email.')
                return redirect('portal:admin_email_result')

            success_count = 0
            error_count = 0
            errors = []
            today = date.today()

            for student in students:
                if not student.email:
                    continue

                all_results = StudentResult.objects.filter(student=student).select_related('result_sheet')

                if result_type == 'current_semester':
                    results_to_send = [sr for sr in all_results if not (sr.result_sheet.end_date and sr.result_sheet.end_date < today)]
                    pdf_filename = f"current_semester_result_{student.student_id}.pdf"
                else:
                    results_to_send = list(all_results)
                    pdf_filename = f"full_result_{student.student_id}.pdf"

                # Calculate CGPA
                completed_credits = Decimal('0.0')
                total_cgpa_points = Decimal('0.0')
                for sr in all_results:
                    if sr.result_sheet.end_date and sr.result_sheet.end_date < today:
                        if sr.cgpa is not None and sr.cgpa > 0:
                            completed_credits += sr.result_sheet.course_credit
                            total_cgpa_points += (sr.result_sheet.course_credit * sr.cgpa)
                cumulative_cgpa = round(total_cgpa_points / completed_credits, 2) if completed_credits > 0 else Decimal('0.00')

                # Build PDF in memory
                template = get_template('portal/admin/result_email_pdf.html')
                context = {
                    'student': student,
                    'results': results_to_send,
                    'result_type': result_type,
                    'cumulative_cgpa': cumulative_cgpa,
                    'completed_credits': completed_credits,
                }
                html_content = template.render(context)

                pdf_buffer = BytesIO()
                pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

                if pisa_status.err:
                    error_count += 1
                    continue

                pdf_buffer.seek(0)

                # Template replacements
                custom_subject = mail_subject.replace("{{ student.student_name }}", student.student_name).replace("{{ student.student_id }}", student.student_id)
                custom_body = mail_body.replace("{{ selected_student.student_name }}", student.student_name).replace("{{ selected_student.student_id }}", student.student_id)
                custom_body = custom_body.replace("{{ student.student_name }}", student.student_name).replace("{{ student.student_id }}", student.student_id)

                try:
                    email = EmailMessage(
                        subject=custom_subject or f"Your Result — Metropolitan University",
                        body=custom_body or f"Dear {student.student_name},\n\nPlease find your academic result attached.\n\nBest regards,\nMetropolitan University",
                        from_email=django_settings.DEFAULT_FROM_EMAIL,
                        to=[student.email],
                    )
                    email.attach(pdf_filename, pdf_buffer.read(), 'application/pdf')
                    email.send()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(str(e))

            if success_count > 0:
                messages.success(request, f"✅ Result emails sent successfully to {success_count} students!")
            if error_count > 0:
                messages.error(request, f"❌ Failed to send to {error_count} students. Error: {', '.join(set(errors[:3]))}")

            return redirect('portal:admin_email_result')

        else:
            recipient_email = request.POST.get('recipient_email', '').strip()
            student = get_object_or_404(Student, id=student_id_post)

            all_results = StudentResult.objects.filter(student=student).select_related('result_sheet')
            today = date.today()

            if result_type == 'current_semester':
                results_to_send = [sr for sr in all_results if not (sr.result_sheet.end_date and sr.result_sheet.end_date < today)]
                pdf_filename = f"current_semester_result_{student.student_id}.pdf"
            else:
                results_to_send = list(all_results)
                pdf_filename = f"full_result_{student.student_id}.pdf"

            # Calculate CGPA
            completed_credits = Decimal('0.0')
            total_cgpa_points = Decimal('0.0')
            for sr in all_results:
                if sr.result_sheet.end_date and sr.result_sheet.end_date < today:
                    if sr.cgpa is not None and sr.cgpa > 0:
                        completed_credits += sr.result_sheet.course_credit
                        total_cgpa_points += (sr.result_sheet.course_credit * sr.cgpa)
            cumulative_cgpa = round(total_cgpa_points / completed_credits, 2) if completed_credits > 0 else Decimal('0.00')

            # Build PDF in memory
            template = get_template('portal/admin/result_email_pdf.html')
            context = {
                'student': student,
                'results': results_to_send,
                'result_type': result_type,
                'cumulative_cgpa': cumulative_cgpa,
                'completed_credits': completed_credits,
            }
            html_content = template.render(context)

            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

            if pisa_status.err:
                messages.error(request, 'Failed to generate PDF. Please try again.')
                return redirect('portal:admin_email_result')

            pdf_buffer.seek(0)

            # Template replacements
            custom_subject = mail_subject.replace("{{ student.student_name }}", student.student_name).replace("{{ student.student_id }}", student.student_id)
            custom_body = mail_body.replace("{{ selected_student.student_name }}", student.student_name).replace("{{ selected_student.student_id }}", student.student_id)
            custom_body = custom_body.replace("{{ student.student_name }}", student.student_name).replace("{{ student.student_id }}", student.student_id)

            try:
                email = EmailMessage(
                    subject=custom_subject or f"Your Result — Metropolitan University",
                    body=custom_body or f"Dear {student.student_name},\n\nPlease find your academic result attached.\n\nBest regards,\nMetropolitan University",
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email],
                )
                email.attach(pdf_filename, pdf_buffer.read(), 'application/pdf')
                email.send()
                messages.success(request, f"✅ Result email sent successfully to {recipient_email}!")
            except Exception as e:
                messages.error(request, f"❌ Failed to send email: {str(e)}")

            return redirect('portal:admin_email_result')

    return render(request, 'portal/admin/email_result.html', {
        'search_results': search_results,
        'selected_student': selected_student,
        'is_all_students': is_all_students,
        'query': query,
    })


def admin_general_email(request):
    if not _admin_required(request):
        return redirect('portal:admin_login')

    from django.core.mail import EmailMessage
    from django.conf import settings as django_settings

    if request.method == 'POST':
        send_type = request.POST.get('send_type', 'custom')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()

        to_list = []
        if send_type == 'custom':
            to_emails_raw = request.POST.get('to_emails', '').strip()
            to_list = [e.strip() for e in to_emails_raw.split(',') if e.strip()]
            if not to_list:
                messages.error(request, '❌ Please enter at least one recipient email address.')
                return redirect('portal:admin_general_email')
        elif send_type == 'students':
            to_list = list(Student.objects.filter(status='approved').values_list('email', flat=True))
            if not to_list:
                messages.error(request, '❌ No approved students found to email.')
                return redirect('portal:admin_general_email')
        elif send_type == 'teachers':
            to_list = list(Teacher.objects.filter(status='approved').values_list('email', flat=True))
            if not to_list:
                messages.error(request, '❌ No approved teachers found to email.')
                return redirect('portal:admin_general_email')
        elif send_type == 'everyone':
            student_emails = list(Student.objects.filter(status='approved').values_list('email', flat=True))
            teacher_emails = list(Teacher.objects.filter(status='approved').values_list('email', flat=True))
            to_list = list(set(student_emails + teacher_emails)) # Unique emails
            if not to_list:
                messages.error(request, '❌ No approved students or teachers found to email.')
                return redirect('portal:admin_general_email')

        if not subject:
            messages.error(request, '❌ Subject cannot be empty.')
            return redirect('portal:admin_general_email')
        if not body:
            messages.error(request, '❌ Email body cannot be empty.')
            return redirect('portal:admin_general_email')

        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=to_list,
            )
            email.send()
            count = len(to_list)
            messages.success(request, f"✅ Email sent successfully to {count} recipient{'s' if count > 1 else ''}!")
        except Exception as e:
            messages.error(request, f"❌ Failed to send email: {str(e)}")

        return redirect('portal:admin_general_email')

    return render(request, 'portal/admin/general_email.html')
