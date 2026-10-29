from django.urls import path
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
    path('lecturer/classes/', views.lecturer_classes, name='lecturer_classes'),
    path('lecturer/history/', views.lecturer_history, name='lecturer_history'),
]
