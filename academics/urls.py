from django.urls import path
from . import views

urlpatterns = [
    path('faculties/', views.FacultyListView.as_view(), name='faculty_list'),
    path('faculties/add/', views.FacultyCreateView.as_view(), name='faculty_create'),
    path('faculties/<int:pk>/edit/', views.FacultyUpdateView.as_view(), name='faculty_update'),
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/add/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/add/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),
]
