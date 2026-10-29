from django.db import models

LEVEL_CHOICES = [('', 'Select level...')] + [(str(x), str(x) + ' Level') for x in (100, 200, 300, 400, 500)]
SEMESTER_CHOICES = [('', 'Select semester...'), ('First', 'First Semester'), ('Second', 'Second Semester')]


class Faculty(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_five_year = models.BooleanField(default=False, help_text='Tick if this faculty runs a 5-year programme (enables 500 Level for its students).')

    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name='departments', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True, default='')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, blank=True, default='')
    unit = models.IntegerField(default=1)
    assigned_lecturer = models.ForeignKey(
        'accounts.LecturerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    def __str__(self):
        return f"{self.course_code} - {self.title}"


class StudentCourseEnrollment(models.Model):
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.registration_number} enrolled in {self.course.course_code}"
