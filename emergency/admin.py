from django.contrib import admin
from .models import Hospital, HospitalStaff, EmergencyRequest, PatientProfile

admin.site.register(Hospital)
admin.site.register(HospitalStaff)
admin.site.register(EmergencyRequest)
admin.site.register(PatientProfile)
