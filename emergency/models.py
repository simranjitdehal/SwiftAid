from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField(default=0)
    available_beds = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    total_ambulances = models.PositiveIntegerField(default=0)
    available_ambulances = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class HospitalStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    is_occupied = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default="Staff")

    def __str__(self):
        return self.user.username
    
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    address = models.TextField()

    def __str__(self):
        return self.user.username

class EmergencyRequest(models.Model):
    EMERGENCY_CHOICES = [
        ('trauma', 'Trauma'),
        ('cardiac', 'Cardiac'),
        ('stroke', 'Stroke'),
        ('snakebite', 'Snakebite'),
        ('fire', 'Fire'),
        ('gunshot', 'Gunshot or Stab Wound'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    SEVERITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    emergency_type = models.CharField(max_length=50, choices=EMERGENCY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')

    other_emergency_text = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    assigned_hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    ambulance_required = models.BooleanField(default=False)
    ambulance_dispatched = models.BooleanField(default=False)

    assigned_staff = models.ForeignKey(HospitalStaff, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')

    def __str__(self):
        return f"{self.user.username}- {self.emergency_type}"


