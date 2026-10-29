from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('lecturer', 'Lecturer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='lecturer')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
