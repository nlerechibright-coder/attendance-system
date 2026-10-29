import os

# 1. accounts/urls.py
accounts_urls = """from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
]
"""

# 2. academics/urls.py
academics_urls = """from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
]
"""

# 3. attendance/urls.py
attendance_urls = """from django.urls import path
from . import views

urlpatterns = [
    path('fingerprints/', views.FingerprintListView.as_view(), name='fingerprint_list'),
    path('sessions/', views.session_list, name='session_list'),
    path('scan/', views.scan_view, name='scan_select'),
    path('scan/<int:session_id>/', views.scan_view, name='scan_view'),
    path('mark/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('reports/', views.report_dashboard, name='report_dashboard'),
]
"""

# 4. academics/views.py (Safe, working ListViews)
academics_views = """from django.views.generic import ListView
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
"""

# 5. attendance/views.py (Safe, working views)
attendance_views = """from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db import transaction, IntegrityError
from accounts.views import admin_required
from accounts.models import StudentProfile
from .models import AttendanceSession, AttendanceRecord, DemoFingerprintProfile

@method_decorator(admin_required, name='dispatch')
class FingerprintListView(ListView):
    model = StudentProfile
    template_name = 'attendance/fingerprint_list.html'
    context_object_name = 'students'

@login_required
def session_list(request):
    sessions = AttendanceSession.objects.select_related('course', 'lecturer__user').order_by('-start_time')
    return render(request, 'attendance/session_list.html', {'sessions': sessions})

@login_required
def scan_view(request, session_id=None):
    active_sessions = AttendanceSession.objects.filter(is_active=True, closed_at__isnull=True).select_related('course')
    selected_session = get_object_or_404(AttendanceSession, pk=session_id) if session_id else None
    profiles = DemoFingerprintProfile.objects.filter(is_active=True).select_related('student__user')
    return render(request, 'attendance/scan.html', {'active_sessions': active_sessions, 'selected_session': selected_session, 'profiles': profiles})

@login_required
def mark_attendance(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        try:
            profile = DemoFingerprintProfile.objects.get(profile_id=profile_id, is_active=True)
            with transaction.atomic():
                AttendanceRecord.objects.create(
                    session=session,
                    student=profile.student,
                    status='Present',
                    verification_method='Demo Fingerprint Simulation'
                )
            return JsonResponse({'success': True, 'message': 'Attendance marked successfully.'})
        except (DemoFingerprintProfile.DoesNotExist, IntegrityError):
            return JsonResponse({'success': False, 'error': 'Invalid profile or already marked.'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@login_required
def report_dashboard(request):
    records = AttendanceRecord.objects.select_related('student__user', 'session__course').order_by('-timestamp')
    return render(request, 'attendance/reports.html', {'records': records})
"""

# Ensure directories exist
os.makedirs('accounts', exist_ok=True)
os.makedirs('academics', exist_ok=True)
os.makedirs('attendance', exist_ok=True)

# Write files
with open('accounts/urls.py', 'w', encoding='utf-8') as f: f.write(accounts_urls)
with open('academics/urls.py', 'w', encoding='utf-8') as f: f.write(academics_urls)
with open('attendance/urls.py', 'w', encoding='utf-8') as f: f.write(attendance_urls)
with open('academics/views.py', 'w', encoding='utf-8') as f: f.write(academics_views)
with open('attendance/views.py', 'w', encoding='utf-8') as f: f.write(attendance_views)

print('ALL URLS AND VIEWS FIXED SUCCESSFULLY!')
