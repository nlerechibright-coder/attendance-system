from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.views import admin_required
from .models import Department, Course, StudentCourseEnrollment

@method_decorator(admin_required, name='dispatch')
class DepartmentListView(ListView):
    model = Department
    template_name = 'academics/department_list.html'
    context_object_name = 'departments'

@method_decorator(admin_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    template_name = 'academics/course_list.html'
    context_object_name = 'courses'

@method_decorator(admin_required, name='dispatch')
class EnrollmentListView(ListView):
    model = StudentCourseEnrollment
    template_name = 'academics/enrollment_list.html'
    context_object_name = 'enrollments'
