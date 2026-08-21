from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    plain_password = models.CharField(max_length=255, blank=True, default='')
    batch = models.CharField(max_length=50)
    dept = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"


class Teacher(models.Model):
    teacher_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    plain_password = models.CharField(max_length=255, blank=True, default='')
    dept = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.teacher_name


class Course(models.Model):
    course_code = models.CharField(max_length=50, unique=True)
    course_title = models.CharField(max_length=255)
    credit = models.DecimalField(max_digits=3, decimal_places=1)
    dept = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.course_code}: {self.course_title}"


class CourseFaculty(models.Model):
    name = models.CharField(max_length=255)
    dept = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.name} - {self.dept}"


class TeacherBatch(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    batch = models.CharField(max_length=50)
    section = models.CharField(max_length=50, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        unique_together = ('teacher', 'batch', 'section')

    def __str__(self):
        return f"{self.teacher.teacher_name} - Batch {self.batch} Section {self.section}"


class ResultSheet(models.Model):
    teacher_batch = models.ForeignKey(TeacherBatch, on_delete=models.CASCADE, related_name='result_sheets')
    semester = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    course_title = models.CharField(max_length=255)
    course_credit = models.DecimalField(max_digits=3, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.course_title} - {self.teacher_batch}"


class StudentResult(models.Model):
    result_sheet = models.ForeignKey(ResultSheet, on_delete=models.CASCADE, related_name='student_results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    
    # Marks components (allowing null/blank initially)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ct1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ct2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assignment = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mid_term = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_term = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Calculated fields
    total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        unique_together = ('result_sheet', 'student')

    def __str__(self):
        return f"{self.student.student_name} - {self.result_sheet.course_title}"


class Notice(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    num_courses = models.IntegerField(default=0)
    total_credits = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    num_semesters = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.name
