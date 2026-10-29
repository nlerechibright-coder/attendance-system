from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
]
