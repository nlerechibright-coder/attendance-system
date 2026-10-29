# Update academics/urls.py
academics_urls = """from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
]
"""
with open('academics/urls.py', 'w', encoding='utf-8') as f: f.write(academics_urls)

# Update accounts/urls.py
accounts_urls = """from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
]
"""
with open('accounts/urls.py', 'w', encoding='utf-8') as f: f.write(accounts_urls)

print("URLS UPDATED WITH CREATE/EDIT ROUTES!")
