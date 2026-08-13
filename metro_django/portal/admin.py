from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import Student, Teacher, Course, CourseFaculty, TeacherBatch, ResultSheet, StudentResult

# Register your models here.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(CourseFaculty)
admin.site.register(TeacherBatch)
admin.site.register(ResultSheet)
admin.site.register(StudentResult)
