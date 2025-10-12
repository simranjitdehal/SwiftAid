from django.urls import path
from emergency import views

urlpatterns = [
    path('', views.home, name='home'),

    # path('register/patient/', views.register_patient, name='register_patient'),

    path('register/staff/', views.register_staff, name='register_staff'),

    path('login/staff/', views.staff_login, name='staff_login'),

    # path('register/hospital-admin/', views.register_hospital_admin, name='register_hospital_admin'),

    path('login/', views.login_choice, name='login'),

    path('login_choice/', views.login_choice, name='login_choice'),


    path('logout/', views.logout_view, name='logout'),

    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),

    path('login/admin/', views.login_view, name='login_admin'),

    path('signup/', views.signup_choice, name='signup_choice'),

    path('hospital-admin/manage-staff/', views.manage_staff, name='manage_staff'),

    path('dashboard/', views.admin_dash, name='admin_dash'),

    path('hospital-admin/emergencies/', views.view_emergency_requests, name='view_emergencies'),

    path('hospital-admin/manage-beds/', views.manage_beds, name='manage_beds'),

    path('ambulances/', views.edit_ambulance_info, name='manage_ambulances'),

    path('manage-patients/', views.manage_patients, name='manage_patients'),
    # path('assign-staff/<int:emergency_id>/', views.assign_staff_to_patient, name='assign_staff'),
    path('assign-staff-to-patient/<int:emergency_id>/', views.assign_staff_to_patient, name='assign_staff_to_patient'),
    path('delete-emergency/<int:emergency_id>/', views.delete_emergency, name='delete_emergency'),

    path('register/staff/', views.register_staff, name='register_staff'),

    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),

    path('staff/assigned/', views.staff_assigned_requests, name='staff_assigned'),

    path('staff/requests', views.assigned_requests, name = 'assigned_requests'),

#patients urls
    path('reset_guest_password/', views.reset_guest_password, name= 'reset_guest_password'),

    path('staff/patient-status/', views.patient_status, name='staff_patient_status'),

    path('signup/patient/', views.patient_signup, name='patient_signup'),

    path('login/patient/', views.patient_login, name='patient_login'),

     path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),

     path('emergency/', views.emergency_form_view, name='emergency_form'),

     path('emergency-status/', views.emergency_status, name='emergency_status'),

    #Find nearby hospitals
     path("get_hospitals/", views.get_hospitals, name="get_hospitals"),
]
