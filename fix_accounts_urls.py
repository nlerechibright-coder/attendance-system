urls_content = """from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
]
"""

with open('accounts/urls.py', 'w', encoding='utf-8') as f:
    f.write(urls_content)
print('ACCOUNTS/URLS.PY FIXED SUCCESSFULLY!')
