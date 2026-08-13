# pyrefly: ignore [missing-import]
from django.urls import path
# pyrefly: ignore [missing-import]
from . import views

app_name = 'portal'

urlpatterns = [
    # Student Auth & Pages
    path('', views.welcome, name='welcome'),
    path('signup', views.student_signup, name='signup'),
    path('login', views.student_login, name='login'),
    path('logout', views.student_logout, name='logout'),
    path('dashboard', views.student_dashboard, name='dashboard'),

    # Teacher Auth & Pages
    path('teachers/', views.teacher_login, name='teachers.login'),
    path('teachers/signup', views.teacher_signup, name='teachers.signup'),
    path('teachers/login', views.teacher_login, name='teachers.authenticate'),
    path('teachers/dashboard', views.teacher_dashboard, name='teachers.dashboard'),
    path('teachers/add-batch', views.teacher_add_batch, name='teachers.addBatch'),
    path('teachers/batch/<str:batch_number>/<str:section>/students', views.teacher_view_batch_students, name='teachers.viewBatchStudents'),
    path('teachers/batch/<int:pk>/delete', views.teacher_delete_batch, name='teachers.deleteBatch'),
    path('teachers/results', views.teacher_results, name='teachers.results'),
    path('teachers/results/<int:sheet_id>/update', views.teacher_update_result, name='teachers.updateResult'),
    path('teachers/results/<int:sheet_id>/delete', views.teacher_delete_result, name='teachers.deleteResult'),
    path('teachers/results/<int:sheet_id>/export-pdf', views.teacher_export_result_pdf, name='teachers.exportResultPdf'),
    path('teachers/logout', views.teacher_logout, name='teachers.logout'),

    # ---- Main Navbar Pages ----
    path('academics/', views.academics, name='academics'),
    path('research/', views.research, name='research'),
    path('campus-life/', views.campus_life, name='campus_life'),
    path('athletics/', views.athletics, name='athletics'),
    path('admission/', views.admission, name='admission'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('events/', views.events, name='events'),

    # ---- Top Bar Audience Pages ----
    path('students/', views.students, name='students'),
    path('staff/', views.staff, name='staff'),
    path('visitors/', views.visitors, name='visitors'),
    path('alumni/', views.alumni, name='alumni'),

    # ---- Error Test Route ----
    path('error-test/', views.error_404, name='error_test'),

    # ---- Admin Routes ----
    path('mu-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('mu-admin/login/', views.admin_login, name='admin_login'),
    path('mu-admin/logout/', views.admin_logout, name='admin_logout'),
    path('mu-admin/verify-password/', views.admin_verify_password, name='admin_verify_password'),
    path('mu-admin/students/', views.admin_students, name='admin_students'),
    path('mu-admin/teachers/', views.admin_teachers, name='admin_teachers'),
    path('mu-admin/notices/', views.admin_notices, name='admin_notices'),
    path('mu-admin/notices/create/', views.admin_create_notice, name='admin_create_notice'),
    path('mu-admin/notices/<int:notice_id>/edit/', views.admin_edit_notice, name='admin_edit_notice'),
    path('mu-admin/notices/<int:notice_id>/toggle/', views.admin_toggle_notice, name='admin_toggle_notice'),
    path('mu-admin/notices/<int:notice_id>/delete/', views.admin_delete_notice, name='admin_delete_notice'),
    path('mu-admin/students/<int:student_id>/delete/', views.admin_delete_student, name='admin_delete_student'),
    path('mu-admin/students/<int:student_id>/toggle-status/', views.admin_toggle_student_status, name='admin_toggle_student_status'),
    path('mu-admin/students/approve-all/', views.admin_approve_all_students, name='admin_approve_all_students'),
    path('mu-admin/teachers/<int:teacher_id>/delete/', views.admin_delete_teacher, name='admin_delete_teacher'),
    path('mu-admin/teachers/<int:teacher_id>/toggle-status/', views.admin_toggle_teacher_status, name='admin_toggle_teacher_status'),
    path('mu-admin/teachers/approve-all/', views.admin_approve_all_teachers, name='admin_approve_all_teachers'),
]
