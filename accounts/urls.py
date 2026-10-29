from django.urls import path
from . import views
urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
    path('lecturers/add/', views.LecturerCreateView.as_view(), name='lecturer_create'),
    path('lecturers/<int:pk>/edit/', views.LecturerUpdateView.as_view(), name='lecturer_update'),
]
