from django.contrib.auth import authenticate, login, logout, get_user_model
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

from academics.models import Course, Department, StudentCourseEnrollment
from attendance.models import AttendanceRecord, AttendanceSession, DemoFingerprintProfile
from accounts.models import LecturerProfile, StudentProfile

User = get_user_model()

# ---------------- AUTHENTICATION ----------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

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

# ---------------- ADMIN DECORATOR ----------------

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ---------------- STUDENTS ----------------

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

# ---------------- LECTURERS ----------------

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
