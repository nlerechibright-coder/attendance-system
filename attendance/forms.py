from django import forms
from .models import AttendanceSession

class SessionActivationForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['duration_minutes']
        widgets = {
            'duration_minutes': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'e.g., 15'}),
        }
