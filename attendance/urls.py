from django.urls import path
from . import views

urlpatterns = [
    path('fingerprints/', views.FingerprintListView.as_view(), name='fingerprint_list'),
    path('sessions/', views.session_list, name='session_list'),
    path('scan/', views.scan_view, name='scan_select'),
    path('scan/<int:session_id>/', views.scan_view, name='scan_view'),
    path('mark/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('reports/', views.report_dashboard, name='report_dashboard'),
]
