from django import forms
from .models import Faculty, Department, Course, StudentCourseEnrollment


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'code', 'is_five_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Faculty Name'}),
            'code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Faculty Code'}),
            'is_five_year': forms.CheckboxInput(attrs={'class': 'h-6 w-6 rounded-lg border-slate-300 accent-indigo-600'}),
        }


class DepartmentForm(forms.ModelForm):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), required=True, empty_label='Select faculty...', widget=forms.Select(attrs={'class': 'input'}))

    class Meta:
        model = Department
        fields = ['faculty', 'name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Department Name'}),
            'code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Department Code'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'title', 'department', 'level', 'semester', 'unit', 'assigned_lecturer', 'description']
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g., CSC301'}),
            'title': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Course Title / Topic'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'unit': forms.NumberInput(attrs={'class': 'input'}),
            'department': forms.Select(attrs={'class': 'input'}),
            'level': forms.Select(attrs={'class': 'input'}),
            'semester': forms.Select(attrs={'class': 'input'}),
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
