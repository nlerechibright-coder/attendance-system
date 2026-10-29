from django.shortcuts import render, get_object_or_404, redirect
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
