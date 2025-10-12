from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import DateInput
from .models import HospitalStaff, PatientProfile, Hospital

class StaffSignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:  # ✅ Capitalized
        model = HospitalStaff
        fields = [ 'hospital', 'role']  # Fields from HospitalStaff model

    def save(self, commit=True):  # ✅ Now placed outside Meta
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
        )
        staff = super().save(commit=False)
        staff.user = user
        if commit:
            staff.save()
        return staff

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields =['username', 'password', 'email', 'first_name', 'last_name']

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields =['dob', 'address']
        widgets = {
            'dob': DateInput(attrs={'type': 'date'})  # This shows calendar picker
        }


class AmbulanceInfoForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['total_ambulances', 'available_ambulances']