from django.db import models
from django.utils import timezone

class DemoFingerprintProfile(models.Model):
    student = models.OneToOneField('accounts.StudentProfile', on_delete=models.CASCADE, related_name='fingerprint_profile')
    profile_id = models.CharField(max_length=50, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profile_id:
            last_profile = DemoFingerprintProfile.objects.order_by('-id').first()
            next_num = (int(last_profile.profile_id.split('-')[-1]) + 1) if last_profile else 1
            self.profile_id = f"DEMO-FP-{next_num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile_id} -> {self.student.registration_number}"


class AttendanceSession(models.Model):
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, related_name='sessions')
    lecturer = models.ForeignKey('accounts.LecturerProfile', on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(default=15)
    is_active = models.BooleanField(default=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self):
        if self.closed_at: return True
        return timezone.now() > (self.start_time + timezone.timedelta(minutes=self.duration_minutes))

    def __str__(self):
        return f"{self.course.course_code} Session on {self.session_date}"


class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, related_name='attendance_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Present')
    verification_method = models.CharField(max_length=50, default='Demo Fingerprint Simulation')

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.registration_number} - {self.session.course.course_code}"
