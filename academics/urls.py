from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
]
