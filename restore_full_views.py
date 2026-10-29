import os

# 1. Restore full accounts/views.py
accounts_views = """from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
import json
import csv
from django.utils import timezone
from functools import wraps

from academics.models import Course, Department, StudentCourseEnrollment
from attendance.models import AttendanceRecord, AttendanceSession, DemoFingerprintProfile
from accounts.models import LecturerProfile, StudentProfile
from .forms import CustomAuthenticationForm, LecturerProfileForm, StudentProfileForm

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    role = getattr(request.user, 'role', None)
    if role == 'admin':
        context = {
            'total_students': StudentProfile.objects.count(),
            'total_lecturers': LecturerProfile.objects.count(),
            'total_departments': Department.objects.count(),
            'total_courses': Course.objects.count(),
            'active_sessions': AttendanceSession.objects.filter(is_active=True, closed_at__isnull=True).count(),
            'total_records': AttendanceRecord.objects.count(),
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    elif role == 'lecturer':
        courses = Course.objects.filter(assigned_lecturer=request.user.lecturer_profile)
        active_sessions = AttendanceSession.objects.filter(lecturer=request.user.lecturer_profile, is_active=True, closed_at__isnull=True)
        return render(request, 'dashboard/lecturer_dashboard.html', {'courses': courses, 'active_sessions': active_sessions})
    else:
        logout(request)
        messages.error(request, 'Unauthorized role.')
        return redirect('login')

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@method_decorator(admin_required, name='dispatch')
class StudentListView(ListView):
    model = StudentProfile
    template_name = 'accounts/student_list.html'
    context_object_name = 'students'
    paginate_by = 10
    def get_queryset(self):
        qs = StudentProfile.objects.select_related('user', 'department').order_by('registration_number')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(registration_number__icontains=q) | Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
        return qs

@method_decorator(admin_required, name='dispatch')
class StudentCreateView(CreateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'accounts/student_form.html'
    success_url = reverse_lazy('student_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'], first_name=form.cleaned_data.get('first_name', ''), last_name=form.cleaned_data.get('last_name', ''), role='student', is_staff=False, is_superuser=False)
                student = form.save(commit=False)
                student.user = user
                student.save()
                self.object = student
        except Exception:
            form.add_error(None, 'Could not create the student account. Verify all fields and try again.')
            return self.form_invalid(form)
        messages.success(self.request, f'Student {student.registration_number} created successfully.')
        return redirect('student_list')

@method_decorator(admin_required, name='dispatch')
class StudentUpdateView(UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'accounts/student_form.html'
    success_url = reverse_lazy('student_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                student = form.save(commit=False)
                user = student.user
                user.username = form.cleaned_data['username']
                user.first_name = form.cleaned_data.get('first_name', '')
                user.last_name = form.cleaned_data.get('last_name', '')
                user.is_active = student.is_active
                password = form.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
                student.save()
                self.object = student
        except Exception:
            form.add_error(None, 'Could not update the student record.')
            return self.form_invalid(form)
        messages.success(self.request, f'Student {student.registration_number} updated.')
        return redirect('student_list')

@method_decorator(admin_required, name='dispatch')
class LecturerListView(ListView):
    model = LecturerProfile
    template_name = 'accounts/lecturer_list.html'
    context_object_name = 'lecturers'
    paginate_by = 10
    def get_queryset(self):
        qs = LecturerProfile.objects.select_related('user', 'department').order_by('staff_id')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(staff_id__icontains=q) | Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
        return qs

@method_decorator(admin_required, name='dispatch')
class LecturerCreateView(CreateView):
    model = LecturerProfile
    form_class = LecturerProfileForm
    template_name = 'accounts/lecturer_form.html'
    success_url = reverse_lazy('lecturer_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'], first_name=form.cleaned_data.get('first_name', ''), last_name=form.cleaned_data.get('last_name', ''), role='lecturer', is_staff=False, is_superuser=False)
                lecturer = form.save(commit=False)
                lecturer.user = user
                lecturer.save()
                self.object = lecturer
        except Exception:
            form.add_error(None, 'Could not create the lecturer account.')
            return self.form_invalid(form)
        messages.success(self.request, f'Lecturer {lecturer.staff_id} created successfully.')
        return redirect('lecturer_list')

@method_decorator(admin_required, name='dispatch')
class LecturerUpdateView(UpdateView):
    model = LecturerProfile
    form_class = LecturerProfileForm
    template_name = 'accounts/lecturer_form.html'
    success_url = reverse_lazy('lecturer_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                lecturer = form.save(commit=False)
                user = lecturer.user
                user.username = form.cleaned_data['username']
                user.first_name = form.cleaned_data.get('first_name', '')
                user.last_name = form.cleaned_data.get('last_name', '')
                user.is_active = lecturer.is_active
                password = form.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
                lecturer.save()
                self.object = lecturer
        except Exception:
            form.add_error(None, 'Could not update the lecturer record.')
            return self.form_invalid(form)
        messages.success(self.request, f'Lecturer {lecturer.staff_id} updated.')
        return redirect('lecturer_list')
"""

# 2. Restore full academics/views.py
academics_views = """from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from accounts.views import admin_required
from .forms import DepartmentForm, CourseForm, EnrollmentForm
from .models import Department, Course, StudentCourseEnrollment

@method_decorator(admin_required, name='dispatch')
class DepartmentListView(ListView):
    model = Department
    template_name = 'academics/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10
    def get_queryset(self):
        qs = Department.objects.all().order_by('name')
        q = self.request.GET.get('q', '').strip()
        if q: qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs

@method_decorator(admin_required, name='dispatch')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'academics/department_form.html'
    success_url = reverse_lazy('department_list')
    def form_valid(self, form):
        messages.success(self.request, f'Department "{form.instance.name}" created.')
        return super().form_valid(form)

@method_decorator(admin_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'academics/department_form.html'
    success_url = reverse_lazy('department_list')
    def form_valid(self, form):
        messages.success(self.request, f'Department "{form.instance.name}" updated.')
        return super().form_valid(form)

@method_decorator(admin_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    template_name = 'academics/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    def get_queryset(self):
        qs = Course.objects.select_related('department', 'assigned_lecturer__user').order_by('course_code')
        q = self.request.GET.get('q', '').strip()
        if q: qs = qs.filter(Q(course_code__icontains=q) | Q(title__icontains=q))
        return qs

@method_decorator(admin_required, name='dispatch')
class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'academics/course_form.html'
    success_url = reverse_lazy('course_list')
    def form_valid(self, form):
        try:
            with transaction.atomic(): self.object = form.save()
        except IntegrityError:
            form.add_error('course_code', 'A course with this code already exists.')
            return self.form_invalid(form)
        messages.success(self.request, f'Course "{self.object.course_code}" created.')
        return redirect(self.get_success_url())

@method_decorator(admin_required, name='dispatch')
class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'academics/course_form.html'
    success_url = reverse_lazy('course_list')
    def form_valid(self, form):
        try:
            with transaction.atomic(): self.object = form.save()
        except IntegrityError:
            form.add_error('course_code', 'A course with this code already exists.')
            return self.form_invalid(form)
        messages.success(self.request, f'Course "{self.object.course_code}" updated.')
        return redirect(self.get_success_url())

@method_decorator(admin_required, name='dispatch')
class EnrollmentListView(ListView):
    model = StudentCourseEnrollment
    template_name = 'academics/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 12
    def get_queryset(self):
        qs = StudentCourseEnrollment.objects.select_related('student__user', 'course').order_by('-enrolled_date')
        q = self.request.GET.get('q', '').strip()
        if q: qs = qs.filter(Q(student__registration_number__icontains=q) | Q(course__course_code__icontains=q))
        return qs

@method_decorator(admin_required, name='dispatch')
class EnrollmentCreateView(CreateView):
    model = StudentCourseEnrollment
    form_class = EnrollmentForm
    template_name = 'academics/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')
    def form_valid(self, form):
        try:
            with transaction.atomic(): self.object = form.save()
        except IntegrityError:
            form.add_error(None, 'This student is already enrolled in the selected course.')
            return self.form_invalid(form)
        messages.success(self.request, 'Student enrolled successfully.')
        return redirect(self.get_success_url())
"""

with open('accounts/views.py', 'w', encoding='utf-8') as f: f.write(accounts_views)
with open('academics/views.py', 'w', encoding='utf-8') as f: f.write(academics_views)

print("FULL VIEWS RESTORED SUCCESSFULLY!")
