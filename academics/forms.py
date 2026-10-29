from django import forms
from .models import Department, Course, StudentCourseEnrollment

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Department Name'}),
            'code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Department Code'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'title', 'description', 'unit', 'department', 'assigned_lecturer']
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g., CSC301'}),
            'title': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Course Title'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'unit': forms.NumberInput(attrs={'class': 'input'}),
            'department': forms.Select(attrs={'class': 'input'}),
            'assigned_lecturer': forms.Select(attrs={'class': 'input'}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = StudentCourseEnrollment
        fields = ['student', 'course']
        widgets = {
            'student': forms.Select(attrs={'class': 'input'}),
            'course': forms.Select(attrs={'class': 'input'}),
        }
