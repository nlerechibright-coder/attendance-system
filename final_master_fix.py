import os

# --- 1. UPDATE URLS ---
academics_urls = """from django.urls import path
from . import views
urlpatterns = [
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/add/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/add/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),
]
"""
with open('academics/urls.py', 'w', encoding='utf-8') as f: f.write(academics_urls)

accounts_urls = """from django.urls import path
from . import views
urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
    path('lecturers/add/', views.LecturerCreateView.as_view(), name='lecturer_create'),
    path('lecturers/<int:pk>/edit/', views.LecturerUpdateView.as_view(), name='lecturer_update'),
]
"""
with open('accounts/urls.py', 'w', encoding='utf-8') as f: f.write(accounts_urls)

attendance_urls = """from django.urls import path
from . import views
urlpatterns = [
    path('fingerprints/', views.FingerprintListView.as_view(), name='fingerprint_list'),
    path('fingerprints/enroll/<int:student_id>/', views.fingerprint_enroll, name='fingerprint_enroll'),
    path('fingerprints/toggle/<int:profile_id>/', views.fingerprint_toggle, name='fingerprint_toggle'),
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/<int:course_id>/', views.session_create, name='session_create'),
    path('sessions/close/<int:session_id>/', views.session_close, name='session_close'),
    path('scan/', views.scan_view, name='scan_select'),
    path('scan/<int:session_id>/', views.scan_view, name='scan_view'),
    path('mark/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('reports/', views.report_dashboard, name='report_dashboard'),
    path('reports/export/', views.export_attendance_csv, name='export_attendance_csv'),
]
"""
with open('attendance/urls.py', 'w', encoding='utf-8') as f: f.write(attendance_urls)

# --- 2. RESTORE FULL ATTENDANCE VIEWS ---
attendance_views = """import json
import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from accounts.decorators import admin_required
from accounts.models import LecturerProfile, StudentProfile
from academics.models import Course, StudentCourseEnrollment, Department
from .forms import SessionActivationForm
from .models import AttendanceRecord, AttendanceSession, DemoFingerprintProfile

@method_decorator(admin_required, name='dispatch')
class FingerprintListView(ListView):
    model = StudentProfile
    template_name = 'attendance/fingerprint_list.html'
    context_object_name = 'students'
    paginate_by = 10
    def get_queryset(self):
        return StudentProfile.objects.select_related('user', 'fingerprint_profile', 'department').order_by('registration_number')

@admin_required
def fingerprint_enroll(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(StudentProfile, pk=student_id)
        profile, created = DemoFingerprintProfile.objects.get_or_create(student=student)
        if created: messages.success(request, f'Demo fingerprint profile {profile.profile_id} enrolled for {student.registration_number}.')
        else: messages.info(request, f'Student already has a profile: {profile.profile_id}.')
    return redirect('fingerprint_list')

@admin_required
def fingerprint_toggle(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(DemoFingerprintProfile, pk=profile_id)
        profile.is_active = not profile.is_active
        profile.save()
        state = 'activated' if profile.is_active else 'deactivated'
        messages.success(request, f'Profile {profile.profile_id} {state}.')
    return redirect('fingerprint_list')

@login_required
def session_list(request):
    if request.user.role == 'admin': sessions = AttendanceSession.objects.select_related('course', 'lecturer__user').order_by('-start_time')
    elif request.user.role == 'lecturer': sessions = AttendanceSession.objects.filter(lecturer=request.user.lecturer_profile).select_related('course', 'lecturer__user').order_by('-start_time')
    else: sessions = AttendanceSession.objects.none()
    return render(request, 'attendance/session_list.html', {'sessions': sessions})

@login_required
def session_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.role == 'lecturer':
        if not hasattr(request.user, 'lecturer_profile') or course.assigned_lecturer != request.user.lecturer_profile:
            messages.error(request, 'You are not authorized to activate attendance for this course.')
            return redirect('dashboard')
        lecturer = request.user.lecturer_profile
    else:
        lecturer = course.assigned_lecturer
        if not lecturer:
            messages.error(request, 'This course has no assigned lecturer.')
            return redirect('course_list')

    if request.method == 'POST':
        form = SessionActivationForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.course = course
            session.lecturer = lecturer
            session.session_date = timezone.now().date()
            session.save()
            messages.success(request, f'Attendance session activated for {course.course_code}.')
            return redirect('scan_view', session_id=session.pk)
    else: form = SessionActivationForm()
    return render(request, 'attendance/session_create.html', {'form': form, 'course': course})

@login_required
def session_close(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(AttendanceSession, pk=session_id)
        if request.user.role == 'lecturer' and session.lecturer != request.user.lecturer_profile and request.user.role != 'admin':
            messages.error(request, 'Unauthorized.')
            return redirect('session_list')
        session.is_active = False
        session.closed_at = timezone.now()
        session.save()
        messages.success(request, f'Session for {session.course.course_code} closed.')
    return redirect('session_list')

@login_required
def scan_view(request, session_id=None):
    active_sessions = AttendanceSession.objects.filter(is_active=True, closed_at__isnull=True).select_related('course', 'lecturer__user')
    selected_session = None
    profiles = []
    if session_id:
        selected_session = get_object_or_404(AttendanceSession, pk=session_id)
        enrolled_students = StudentCourseEnrollment.objects.filter(course=selected_session.course).select_related('student__user', 'student__fingerprint_profile')
        for enrollment in enrolled_students:
            student = enrollment.student
            if hasattr(student, 'fingerprint_profile') and student.fingerprint_profile.is_active:
                profiles.append(student.fingerprint_profile)
    else: profiles = DemoFingerprintProfile.objects.filter(is_active=True).select_related('student__user')
    context = {'active_sessions': active_sessions, 'selected_session': selected_session, 'profiles': profiles}
    return render(request, 'attendance/scan.html', context)

@require_POST
def mark_attendance(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    if not session.is_active or session.closed_at: return JsonResponse({'success': False, 'error': 'This attendance session is closed.'}, status=400)
    if session.is_expired: return JsonResponse({'success': False, 'error': 'This attendance session has expired.'}, status=400)
    try:
        data = json.loads(request.body)
        profile_id = data.get('profile_id')
    except json.JSONDecodeError: profile_id = request.POST.get('profile_id')
    if not profile_id: return JsonResponse({'success': False, 'error': 'No fingerprint profile selected.'}, status=400)
    try: profile = DemoFingerprintProfile.objects.get(profile_id=profile_id, is_active=True)
    except DemoFingerprintProfile.DoesNotExist: return JsonResponse({'success': False, 'error': 'Unknown or inactive fingerprint profile.'}, status=400)
    student = profile.student
    if not StudentCourseEnrollment.objects.filter(student=student, course=session.course).exists():
        return JsonResponse({'success': False, 'error': 'Student is not enrolled in this course.'}, status=400)
    try:
        with transaction.atomic():
            AttendanceRecord.objects.create(session=session, student=student, status='Present', verification_method='Demo Fingerprint Simulation')
    except IntegrityError: return JsonResponse({'success': False, 'error': 'Attendance already recorded for this student in this session.'}, status=400)
    return JsonResponse({'success': True, 'student_name': student.user.get_full_name() or student.user.username, 'reg_no': student.registration_number, 'message': 'Attendance marked successfully.'})

@login_required
def report_dashboard(request):
    if request.user.role not in ['admin', 'lecturer']:
        messages.error(request, 'Unauthorized.')
        return redirect('dashboard')
    departments = Department.objects.all()
    courses = Course.objects.all()
    if request.user.role == 'lecturer': courses = courses.filter(assigned_lecturer=request.user.lecturer_profile)
    dept_id = request.GET.get('department')
    course_id = request.GET.get('course')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    records = AttendanceRecord.objects.select_related('student__user', 'session__course', 'session__lecturer__user')
    if request.user.role == 'lecturer': records = records.filter(session__lecturer=request.user.lecturer_profile)
    if dept_id: records = records.filter(student__department_id=dept_id)
    if course_id: records = records.filter(session__course_id=course_id)
    if start_date: records = records.filter(timestamp__date__gte=start_date)
    if end_date: records = records.filter(timestamp__date__lte=end_date)
    total_records = records.count()
    unique_students = records.values('student').distinct().count()
    course_stats = records.values('session__course__course_code', 'session__course__title').annotate(total_present=Count('id')).order_by('-total_present')
    context = {'departments': departments, 'courses': courses, 'records': records[:50], 'total_records': total_records, 'unique_students': unique_students, 'course_stats': course_stats, 'filters': {'department': dept_id, 'course': course_id, 'start_date': start_date, 'end_date': end_date}}
    return render(request, 'attendance/reports.html', context)

@login_required
def export_attendance_csv(request):
    if request.user.role not in ['admin', 'lecturer']: return HttpResponse("Unauthorized", status=403)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Course Code', 'Course Title', 'Lecturer', 'Student Reg No', 'Student Name', 'Status', 'Verification Method'])
    records = AttendanceRecord.objects.select_related('student__user', 'session__course', 'session__lecturer__user').order_by('-timestamp')
    if request.user.role == 'lecturer': records = records.filter(session__lecturer=request.user.lecturer_profile)
    if request.GET.get('department'): records = records.filter(student__department_id=request.GET.get('department'))
    if request.GET.get('course'): records = records.filter(session__course_id=request.GET.get('course'))
    if request.GET.get('start_date'): records = records.filter(timestamp__date__gte=request.GET.get('start_date'))
    if request.GET.get('end_date'): records = records.filter(timestamp__date__lte=request.GET.get('end_date'))
    for rec in records:
        writer.writerow([rec.timestamp.strftime('%Y-%m-%d'), rec.timestamp.strftime('%H:%M:%S'), rec.session.course.course_code, rec.session.course.title, rec.session.lecturer.user.get_full_name() or rec.session.lecturer.user.username, rec.student.registration_number, rec.student.user.get_full_name() or rec.student.user.username, rec.status, rec.verification_method])
    return response
"""
with open('attendance/views.py', 'w', encoding='utf-8') as f: f.write(attendance_views)

# --- 3. GENERATE REMAINING TEMPLATES ---
templates = {
    'academics/course_list.html': """{% extends 'base.html' %}
{% block title %}Courses{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6"><h2 class="text-xl font-bold">Course Management</h2><a href="{% url 'course_create' %}" class="btn-primary btn-sm">+ Add Course</a></div>
    <div class="overflow-x-auto"><table class="w-full text-sm text-left">
        <thead class="text-xs uppercase bg-slate-50 text-slate-500"><tr><th class="px-4 py-3">Code</th><th class="px-4 py-3">Title</th><th class="px-4 py-3">Department</th><th class="px-4 py-3">Actions</th></tr></thead>
        <tbody>{% for course in courses %}<tr class="border-b bg-white">
            <td class="px-4 py-3 font-medium">{{ course.course_code }}</td><td class="px-4 py-3">{{ course.title }}</td><td class="px-4 py-3">{{ course.department.name|default:"N/A" }}</td>
            <td class="px-4 py-3"><a href="{% url 'course_update' course.pk %}" class="text-indigo-600 hover:underline mr-3">Edit</a>
            <a href="{% url 'session_create' course.pk %}" class="btn-primary btn-sm">Start Session</a></td>
        </tr>{% empty %}<tr><td colspan="4" class="px-4 py-3 text-center text-slate-500">No courses found.</td></tr>{% endfor %}</tbody>
    </table></div>
</div>{% endblock %}""",

    'academics/course_form.html': """{% extends 'base.html' %}
{% block title %}Course Form{% endblock %}
{% block content %}
<div class="card p-6 max-w-lg mx-auto"><h2 class="text-xl font-bold mb-6">Course Details</h2>
    <form method="post" class="space-y-4">{% csrf_token %}{{ form.as_p }}
    <div class="flex gap-3 pt-4"><button type="submit" class="btn-primary">Save Course</button><a href="{% url 'course_list' %}" class="btn-secondary">Cancel</a></div></form>
</div>{% endblock %}""",

    'academics/enrollment_list.html': """{% extends 'base.html' %}
{% block title %}Enrollments{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6"><h2 class="text-xl font-bold">Enrollment Management</h2><a href="{% url 'enrollment_create' %}" class="btn-primary btn-sm">+ Add Enrollment</a></div>
    <div class="overflow-x-auto"><table class="w-full text-sm text-left">
        <thead class="text-xs uppercase bg-slate-50 text-slate-500"><tr><th class="px-4 py-3">Student</th><th class="px-4 py-3">Course</th><th class="px-4 py-3">Date</th></tr></thead>
        <tbody>{% for enrollment in enrollments %}<tr class="border-b bg-white">
            <td class="px-4 py-3 font-medium">{{ enrollment.student.registration_number }}</td><td class="px-4 py-3">{{ enrollment.course.course_code }}</td><td class="px-4 py-3">{{ enrollment.enrolled_date }}</td>
        </tr>{% empty %}<tr><td colspan="3" class="px-4 py-3 text-center text-slate-500">No enrollments found.</td></tr>{% endfor %}</tbody>
    </table></div>
</div>{% endblock %}""",

    'academics/enrollment_form.html': """{% extends 'base.html' %}
{% block title %}Enrollment Form{% endblock %}
{% block content %}
<div class="card p-6 max-w-lg mx-auto"><h2 class="text-xl font-bold mb-6">Enroll Student</h2>
    <form method="post" class="space-y-4">{% csrf_token %}{{ form.as_p }}
    <div class="flex gap-3 pt-4"><button type="submit" class="btn-primary">Save Enrollment</button><a href="{% url 'enrollment_list' %}" class="btn-secondary">Cancel</a></div></form>
</div>{% endblock %}""",

    'accounts/lecturer_list.html': """{% extends 'base.html' %}
{% block title %}Lecturers{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6"><h2 class="text-xl font-bold">Lecturer Management</h2><a href="{% url 'lecturer_create' %}" class="btn-primary btn-sm">+ Add Lecturer</a></div>
    <div class="overflow-x-auto"><table class="w-full text-sm text-left">
        <thead class="text-xs uppercase bg-slate-50 text-slate-500"><tr><th class="px-4 py-3">Staff ID</th><th class="px-4 py-3">Name</th><th class="px-4 py-3">Department</th><th class="px-4 py-3">Actions</th></tr></thead>
        <tbody>{% for lecturer in lecturers %}<tr class="border-b bg-white">
            <td class="px-4 py-3 font-medium">{{ lecturer.staff_id }}</td><td class="px-4 py-3">{{ lecturer.user.get_full_name|default:lecturer.user.username }}</td><td class="px-4 py-3">{{ lecturer.department.name|default:"N/A" }}</td>
            <td class="px-4 py-3"><a href="{% url 'lecturer_update' lecturer.pk %}" class="text-indigo-600 hover:underline mr-3">Edit</a></td>
        </tr>{% empty %}<tr><td colspan="4" class="px-4 py-3 text-center text-slate-500">No lecturers found.</td></tr>{% endfor %}</tbody>
    </table></div>
</div>{% endblock %}""",

    'accounts/lecturer_form.html': """{% extends 'base.html' %}
{% block title %}Lecturer Form{% endblock %}
{% block content %}
<div class="card p-6 max-w-lg mx-auto"><h2 class="text-xl font-bold mb-6">Lecturer Details</h2>
    <form method="post" class="space-y-4">{% csrf_token %}{{ form.as_p }}
    <div class="flex gap-3 pt-4"><button type="submit" class="btn-primary">Save Lecturer</button><a href="{% url 'lecturer_list' %}" class="btn-secondary">Cancel</a></div></form>
</div>{% endblock %}""",

    'attendance/session_list.html': """{% extends 'base.html' %}
{% block title %}Attendance Sessions{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-6">Attendance Sessions</h2>
    <div class="overflow-x-auto"><table class="w-full text-sm text-left">
        <thead class="text-xs uppercase bg-slate-50 text-slate-500"><tr><th class="px-4 py-3">Course</th><th class="px-4 py-3">Date</th><th class="px-4 py-3">Status</th><th class="px-4 py-3">Actions</th></tr></thead>
        <tbody>{% for session in sessions %}<tr class="border-b bg-white">
            <td class="px-4 py-3 font-medium">{{ session.course.course_code }}</td><td class="px-4 py-3">{{ session.session_date }}</td>
            <td class="px-4 py-3">{% if session.is_active and not session.closed_at %}<span class="badge-green">Active</span>{% else %}<span class="badge-red">Closed</span>{% endif %}</td>
            <td class="px-4 py-3">
                {% if session.is_active and not session.closed_at %}
                    <a href="{% url 'scan_view' session.pk %}" class="btn-primary btn-sm mr-2">Scan</a>
                    <form method="post" action="{% url 'session_close' session.pk %}" class="inline"><{% csrf_token %}<button type="submit" class="btn-danger btn-sm">Close</button></form>
                {% else %}
                    <a href="{% url 'report_dashboard' %}?course={{ session.course.pk }}" class="text-indigo-600 hover:underline">View Report</a>
                {% endif %}
            </td>
        </tr>{% empty %}<tr><td colspan="4" class="px-4 py-3 text-center text-slate-500">No sessions found. Go to Courses to start one.</td></tr>{% endfor %}</tbody>
    </table></div>
</div>{% endblock %}""",

    'attendance/session_create.html': """{% extends 'base.html' %}
{% block title %}Start Session{% endblock %}
{% block content %}
<div class="card p-6 max-w-lg mx-auto"><h2 class="text-xl font-bold mb-6">Start Session for {{ course.course_code }}</h2>
    <form method="post" class="space-y-4">{% csrf_token %}{{ form.as_p }}
    <div class="flex gap-3 pt-4"><button type="submit" class="btn-primary">Activate Session</button><a href="{% url 'course_list' %}" class="btn-secondary">Cancel</a></div></form>
</div>{% endblock %}""",

    'attendance/scan.html': """{% extends 'base.html' %}
{% block title %}Scan Attendance{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-6">Demo Fingerprint Scanner</h2>
    {% if selected_session %}
        <div class="mb-6 p-4 bg-indigo-50 rounded-xl"><p class="font-bold">Active Session: {{ selected_session.course.course_code }}</p><p class="text-sm text-slate-600">Click a profile below to simulate a fingerprint scan.</p></div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {% for profile in profiles %}
            <div class="card p-4 text-center">
                <p class="font-bold text-lg">{{ profile.profile_id }}</p>
                <p class="text-sm text-slate-500 mb-4">{{ profile.student.user.get_full_name|default:profile.student.user.username }}</p>
                <form method="post" action="{% url 'mark_attendance' selected_session.pk %}" class="scan-form">
                    {% csrf_token %}<input type="hidden" name="profile_id" value="{{ profile.profile_id }}">
                    <button type="submit" class="btn-primary w-full">Simulate Scan</button>
                </form>
            </div>{% empty %}<p class="text-slate-500">No active profiles enrolled.</p>{% endfor %}
        </div>
    {% else %}
        <p class="text-slate-600">Please select an active session from the list below to begin scanning.</p>
        <div class="mt-6 space-y-3">{% for session in active_sessions %}
            <a href="{% url 'scan_view' session.pk %}" class="block p-4 bg-white rounded-xl ring-1 ring-slate-200 hover:ring-indigo-500 transition"><span class="font-bold">{{ session.course.course_code }}</span> - {{ session.session_date }}</a>
        {% empty %}<p class="text-slate-500">No active sessions.</p>{% endfor %}</div>
    {% endif %}
</div>
<script>
document.querySelectorAll('.scan-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        fetch(this.action, { method: 'POST', body: formData, headers: {'X-Requested-With': 'XMLHttpRequest'} })
        .then(response => response.json())
        .then(data => {
            if(data.success) { alert('✅ Success: ' + data.message + '\\nStudent: ' + data.student_name); location.reload(); }
            else { alert('❌ Error: ' + data.error); }
        });
    });
});
</script>{% endblock %}""",

    'attendance/reports.html': """{% extends 'base.html' %}
{% block title %}Reports{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6"><h2 class="text-xl font-bold">Attendance Reports</h2><a href="{% url 'export_attendance_csv' %}" class="btn-secondary btn-sm">Export CSV</a></div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-indigo-50 p-4 rounded-xl text-center"><p class="text-2xl font-black text-indigo-600">{{ total_records }}</p><p class="text-xs font-bold uppercase text-slate-500">Total Records</p></div>
        <div class="bg-emerald-50 p-4 rounded-xl text-center"><p class="text-2xl font-black text-emerald-600">{{ unique_students }}</p><p class="text-xs font-bold uppercase text-slate-500">Unique Students</p></div>
    </div>
    <h3 class="font-bold mb-4">Recent Records</h3>
    <div class="overflow-x-auto"><table class="w-full text-sm text-left">
        <thead class="text-xs uppercase bg-slate-50 text-slate-500"><tr><th class="px-4 py-3">Date</th><th class="px-4 py-3">Student</th><th class="px-4 py-3">Course</th><th class="px-4 py-3">Status</th></tr></thead>
        <tbody>{% for rec in records %}<tr class="border-b bg-white">
            <td class="px-4 py-3">{{ rec.timestamp|date:"M d, Y H:i" }}</td><td class="px-4 py-3 font-medium">{{ rec.student.registration_number }}</td><td class="px-4 py-3">{{ rec.session.course.course_code }}</td><td class="px-4 py-3"><span class="badge-green">{{ rec.status }}</span></td>
        </tr>{% empty %}<tr><td colspan="4" class="px-4 py-3 text-center text-slate-500">No records found.</td></tr>{% endfor %}</tbody>
    </table></div>
</div>{% endblock %}"""
}

for path, content in templates.items():
    full_path = os.path.join('templates', path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
    print(f"Updated: {full_path}")

print("\nALL UI AND LOGIC RESTORED SUCCESSFULLY!")
