import json
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

from accounts.views import admin_required
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
    content_type = request.content_type or ''
    if 'application/json' in content_type:
        try:
            data = json.loads(request.body)
            profile_id = data.get('profile_id')
        except (json.JSONDecodeError, ValueError):
            profile_id = None
    else:
        profile_id = request.POST.get('profile_id')
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


@login_required
def lecturer_classes(request):
    if getattr(request.user, 'role', None) != 'lecturer' or not hasattr(request.user, 'lecturer_profile'):
        messages.error(request, 'You do not have a lecturer profile.')
        return redirect('dashboard')
    lecturer = request.user.lecturer_profile
    classes = (Course.objects.filter(assigned_lecturer=lecturer)
               .select_related('department')
               .annotate(enrolled_count=Count('enrolled_students', distinct=True),
                         session_count=Count('sessions', distinct=True))
               .order_by('course_code'))
    return render(request, 'attendance/lecturer_classes.html', {'classes': classes, 'lecturer': lecturer})


@login_required
def lecturer_history(request):
    if getattr(request.user, 'role', None) != 'lecturer' or not hasattr(request.user, 'lecturer_profile'):
        messages.error(request, 'You do not have a lecturer profile.')
        return redirect('dashboard')
    lecturer = request.user.lecturer_profile
    course_id = request.GET.get('course')
    selected_course = None
    if course_id:
        selected_course = get_object_or_404(Course, pk=course_id, assigned_lecturer=lecturer)
    base = AttendanceSession.objects.filter(lecturer=lecturer)
    recs = AttendanceRecord.objects.filter(session__lecturer=lecturer)
    if course_id:
        base = base.filter(course_id=course_id)
        recs = recs.filter(session__course_id=course_id)
    sessions = (base.select_related('course', 'course__department')
                .annotate(present_count=Count('records', distinct=True))
                .order_by('-session_date', '-start_time'))
    context = {
        'sessions': sessions,
        'total_sessions': base.count(),
        'total_records': recs.count(),
        'active_now': base.filter(is_active=True, closed_at__isnull=True).count(),
        'selected_course': selected_course,
        'lecturer': lecturer,
    }
    return render(request, 'attendance/lecturer_history.html', context)
