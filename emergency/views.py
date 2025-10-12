from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Hospital, HospitalStaff, EmergencyRequest, PatientProfile
from emergency.models import Hospital, HospitalStaff, EmergencyRequest, PatientProfile
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User 
from django.contrib import messages
from django.http import HttpResponse,HttpResponseForbidden, JsonResponse
from django.db import models, transaction
from django.db.models import Q
import json, requests

from .forms import StaffSignupForm, UserForm, PatientProfileForm,AmbulanceInfoForm


def home(request):
    return render(request, 'emergency/home.html')

def signup_choice(request):
    return render(request, 'emergency/signup_choice.html')


def login_choice(request):
    return render(request, 'emergency/login_choice.html')


@login_required
def admin_dash(request):
    try:
        # This will only work if user has a Hospital object
        hospital = request.user.hospital
    except Hospital.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")
    return render(request, 'hospital_admin/admin_dashboard.html')

@login_required
def view_emergency_requests(request):
    hospital = get_object_or_404(Hospital, user =request.user)
    if request.method == 'POST':
        emergency_id = request.POST.get('emergency_id')
        emergency = get_object_or_404(EmergencyRequest, id= emergency_id)

        if emergency.ambulance_required and not emergency.ambulance_dispatched:
            if hospital.available_ambulances > 0:
                emergency.ambulance_dispatched = True
                emergency.assigned_hospital = hospital
                emergency.save()

                hospital.available_ambulances -= 1
                hospital.save()

                messages.success(request, "Ambulance dispatched successfully")
            else:
                messages.error(request, "No ambulance available")
        else:
            messages.error(request, "Ambulance already dispatched or not required")
        return redirect('view_emergencies')
    emergencies = EmergencyRequest.objects.filter(
    models.Q(assigned_hospital__isnull=True) | models.Q(assigned_hospital = hospital)).order_by('-timestamp')

    return render(request, 'hospital_admin/view_emergencies.html', {
        'emergencies': emergencies,
        'hospital': hospital,
    })

#revise from here
@login_required
def manage_patients(request):
    hospital = get_object_or_404(Hospital, user=request.user)

    # emergencies = EmergencyRequest.objects.filter(assigned_hospital=hospital)
    emergencies = EmergencyRequest.objects.filter(
        Q(assigned_hospital=hospital) | Q(assigned_hospital__isnull=True)
        ).order_by('-timestamp')
    
    staff_members = HospitalStaff.objects.filter(is_active=True, is_occupied=False, hospital=hospital)
    print("Staff Members:", staff_members)

    return render(request, 'hospital_admin/manage_patients.html', {
        'emergencies': emergencies,
        'staff_members': staff_members,
        'hospital': hospital,
    })

@login_required
def assign_staff_to_patient(request, emergency_id):
    print("Assign staff view called!")
    hospital = get_object_or_404(Hospital, user=request.user)

    emergency = get_object_or_404(EmergencyRequest, id=emergency_id)

    # Block assigning staff to someone else's emergency
    if emergency.assigned_hospital is not None and emergency.assigned_hospital != hospital:
        return HttpResponseForbidden("You cannot assign staff to emergencies not assigned to your hospital.")

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        staff = get_object_or_404(HospitalStaff, id=staff_id, hospital=hospital)

        # If no hospital was assigned yet, assign it now
        if emergency.assigned_hospital is None:
            emergency.assigned_hospital = hospital

        emergency.assigned_staff = staff
        emergency.save()

        staff.is_occupied = True
        staff.save()

        return redirect('manage_patients')

    # GET request fallback
    staff_members = HospitalStaff.objects.filter(hospital=hospital, is_active=True, is_occupied=False)
    return render(request, 'hospital_admin/manage_patients.html', {
        'emergency': emergency,
        'staff_members': staff_members,
    })


@login_required
def delete_emergency(request, emergency_id):
    if request.method == "POST":
        emergency = get_object_or_404(EmergencyRequest, id=emergency_id)
        
        # Free up the assigned staff before deletion
        if emergency.assigned_staff:
            staff = emergency.assigned_staff
            staff.is_occupied = False
            staff.save()
        
        emergency.delete()
        messages.success(request, "Emergency case deleted successfully")
        return redirect('manage_patients')
    
    return redirect('manage_patients')

@login_required
def edit_ambulance_info(request):
    hospital = Hospital.objects.get(user = request.user)
    if request.method =='POST':
        form = AmbulanceInfoForm(request.POST, instance = hospital)
        if form.is_valid():
            form.save()
            return redirect('admin_dash')
    else:
        form = AmbulanceInfoForm(instance=hospital)
    return render(request, 'hospital_admin/edit_ambulance_info.html', {'form': form})
                
@login_required
def manage_beds(request):
    hospital = get_object_or_404(Hospital, user= request.user)

    if request.method=='POST':
        is_active= request.POST.get('is_active')=='on'
        capacity = int(request.POST.get('capacity',0))
        available_beds = int(request.POST.get('available_beds',0))

        if available_beds > capacity:
            messages.error(request, "Available beds cant exceed the capacity")
        else:
            hospital.is_active = is_active
            hospital.capacity = capacity
            hospital.available_beds = available_beds
            hospital.save()
            messages.success(request, "Beds details created successfully")

            return redirect('manage_beds')
        return render(request, 'hospital_admin/manage_beds.html', {'hospital':hospital})
    return render(request, 'hospital_admin/manage_beds.html', {'hospital': hospital})

@login_required
def manage_staff(request):
    hospital = get_object_or_404(Hospital, user=request.user)
    staff_members = HospitalStaff.objects.filter(hospital=hospital)

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        action = request.POST.get('action')
        staff_member = get_object_or_404(HospitalStaff, id=staff_id, hospital=hospital)

        if action == 'activate':
            staff_member.is_active = True
        elif action == 'deactivate':
            staff_member.is_active = False
        staff_member.save()
        messages.success(request, f"{staff_member.user.username} updated.")
        return redirect('manage_staff')

    return render(request, 'hospital_admin/manage_staff.html', {'staff_members': staff_members})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'emergency/login.html')

def logout_confirm(request):
    return render(request, 'emergency/logout_confirm.html')

def logout_view(request):
    if request.method== 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'emergency/logout_confirm.html')


def dashboard(request):
    return HttpResponse("Dashboard - Redirect based on user role")

#staff stuff
def register_staff(request):
    if request.method == 'POST':
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful, wait for admin's response")
            return redirect('login_choice')
    else:
        form = StaffSignupForm()
    return render(request, 'hospital_staff/register_staff.html', {'form': form})

def staff_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username= username, password=password)

        if user is not None:
            try:
                staff = HospitalStaff.objects.get(user= user)
                if staff.is_active:
                    login(request, user)
                    return redirect('staff_dashboard')
                else:
                    messages.error(request, "Your account is not activated by admin yet")
            except HospitalStaff.DoesNotExist:
                messages.error(request, "You are not registerd as hospital staff")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'hospital_staff/staff_login.html',{})

@login_required
def staff_dashboard(request):
    try:
        staff = request.user.hospitalstaff  # this is the key check!
        return render(request, 'hospital_staff/staff_dashboard.html', {'staff': staff})

    except:
        return HttpResponseForbidden("You are not medical staff.")
    
@login_required
def staff_assigned_requests(request):
    staff = request.user.hospitalstaff
    assigned_requests = EmergencyRequest.objects.filter(assigned_staff =staff)

    return render(request, 'hospital_staff/assigned_requests.html', {'assigned_requests':assigned_requests})

@login_required
def assigned_requests(request):
    staff = get_object_or_404(HospitalStaff, user = request.user)
    requests = EmergencyRequest.objects.filter(assigned_staff = staff)
    return render(request, 'hospital_staff/assigned_requests.html', {'assigned_requests':requests})


#FOr patient
@login_required
def patient_status(request):
    staff = get_object_or_404(HospitalStaff, user= request.user)
    requests = EmergencyRequest.objects.filter(assigned_staff= staff).exclude(status= 'Not Started')
    return render (request, 'hospital_staff/patient_status.html', {'active_requests': requests})

def patient_signup(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = PatientProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():  # Ensures both save or neither saves
                    # Create user
                    user = user_form.save(commit=False)
                    user.set_password(user.password)
                    user.save()

                    # Create profile
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()

                    # Log in and redirect
                    login(request, user)
                    return redirect('patient_dashboard')

            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below")
    
    else:
        user_form = UserForm()
        profile_form = PatientProfileForm()

    return render(request, 'patients/patient_signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # First check if user exists and is active
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect('patient_login')

        # Then verify patient profile
        if not hasattr(user, 'patientprofile'):
            messages.error(request, "No patient profile found for this account")
            return redirect('patient_login')

        # Everything checks out
        login(request, user)
        return redirect('patient_dashboard')
    
    return render(request, 'patients/patient_login.html')

#patient and emergency
@login_required
def patient_dashboard(request):
    if not hasattr(request.user, 'patientprofile'):
        return HttpResponseForbidden("Patient access only")
    return render(request, 'patients/patient_dashboard.html')

@login_required
def emergency_status(request):
    emergency = EmergencyRequest.objects.filter(user = request.user).order_by('-timestamp').first()
    if emergency:
        context = {
            'emergency': emergency,
            'hospital': emergency.assigned_hospital,
            'now': timezone.now()
        }
    else:
        context = {
            'emergency': None,
            'hospital': None,
        }

    return render(request, 'patients/emergency_status.html', context)

#This is for emergency button
import uuid, secrets
def create_guest_user():
    random_username = "guest_"+ uuid.uuid4().hex[:6]
    random_password = secrets.token_urlsafe(8)
    user = User.objects.create_user(username= random_username, password=random_password)
    return user, random_password

#reset guest password
def reset_guest_password(request):
    if not request.user.username.startswith("guest_"):
        messages.error(request, "Only guest account can reset password here")
        return redirect("home")
    if request.method=='POST':
        new_password = request.POST.get("new_password")
        confirm_pasword = request.POST.get("confirm_password")

        if new_password!= confirm_pasword:
            messages.error(request, "Passwords do not match")
            return redirect("reset_guest_password")
        
        user = request.user
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "password reset successfully")
        return redirect("home")
    return render(request, "guest_login/reset_guest_password.html")

#emergency request logic
def emergency_form_view(request):
    if request.method == 'POST':
        emergency_type = request.POST.get('emergency_type')
        other_emergency_text = request.POST.get('other_emergency_text', '')
        location = request.POST.get('location')
        description = request.POST.get('description', '')

        ambulance_required = request.POST.get('ambulance_required') == 'on'  # checkbox
        severity = request.POST.get('severity')

        hospital_id = request.POST.get('assigned_hospital')
        if not hospital_id:
            messages.error(request, "Please select a hospital")
            return redirect('emergency_form')  # <- INDENTED inside if

        try:
            assigned_hospital = Hospital.objects.get(id=hospital_id)
        except Hospital.DoesNotExist:
            messages.error(request, "Invalid hospital selected")
            return redirect('emergency_form')  # <- INDENTED inside except
        if request.user.is_authenticated:
            user= request.user
        else:
            user, temp_password = create_guest_user()
            login(request, user)

        EmergencyRequest.objects.create(
            user=user,
            emergency_type=emergency_type,
            severity=severity,
            other_emergency_text=other_emergency_text,
            location=location,
            description=description,
            assigned_hospital=assigned_hospital,
            ambulance_required=ambulance_required,
            ambulance_dispatched=False,
            status='Not Started'
        )

        messages.success(request, "Emergency submitted successfully.")
        return redirect('emergency_status')  # or your desired redirect

    hospitals = Hospital.objects.all()
    return render(request, 'emergency/emergencyButton/emergency_form.html', {'hospitals': hospitals})

#for saving location in DB
# def save_location(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         location = data.get("location")

#         EmergencyRequest.objects.create(location =location)
#         return JsonResponse({"message":"Location saved successfully"})


#nearby hospitals thing
def get_hospitals(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    # Query OSM Overpass API
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:15000,{lat},{lon});
    out;
    """
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()

    hospitals = []
    for element in data.get("elements", []):
        hospitals.append({
            "id": element["id"],
            "name": element["tags"].get("name", "Unnamed Hospital"),
            "lat": element["lat"],
            "lon": element["lon"],
        })

    return JsonResponse({"hospitals": hospitals})
