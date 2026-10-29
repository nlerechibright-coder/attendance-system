from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import StudentProfile, LecturerProfile

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))

class StudentProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Login username'}))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last name'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'input'}), help_text='Required for new students.')

    class Meta:
        model = StudentProfile
        fields = ['registration_number', 'department', 'level', 'gender', 'is_active']
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g., CSC/21/1024'}),
            'department': forms.Select(attrs={'class': 'input'}),
            'level': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g., 300'}),
            'gender': forms.Select(attrs={'class': 'input'}, choices=[('', 'Select gender...'), ('Male', 'Male'), ('Female', 'Female')]),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-6 w-6 rounded-lg border-slate-300 accent-indigo-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk: qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists(): raise forms.ValidationError('This username is already taken.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password: validate_password(password)
        return password

class LecturerProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Login username'}))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last name'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'input'}), help_text='Required for new lecturers.')

    class Meta:
        model = LecturerProfile
        fields = ['staff_id', 'department', 'is_active']
        widgets = {
            'staff_id': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g., STF-0042'}),
            'department': forms.Select(attrs={'class': 'input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-6 w-6 rounded-lg border-slate-300 accent-indigo-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk: qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists(): raise forms.ValidationError('This username is already taken.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password: validate_password(password)
        return password
