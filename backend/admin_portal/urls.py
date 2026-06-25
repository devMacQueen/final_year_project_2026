from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-doctor/', views.create_doctor, name='create_doctor'),
    path('create-patient/', views.create_patient, name='create_patient'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('assign/<int:patient_id>/', views.assign_credentials, name='assign_credentials'),
    path('patients/', views.all_patients, name='all_patients'),
    path('doctors/', views.all_doctors, name='all_doctors'),
    path('change-password/', views.change_password, name='change_password'),

    # Patient Account Management
    path('patient/<int:patient_id>/suspend/', views.suspend_patient, name='suspend_patient'),
    path('patient/<int:patient_id>/deactivate/', views.deactivate_patient, name='deactivate_patient'),
    path('patient/<int:patient_id>/reactivate/', views.reactivate_patient, name='reactivate_patient'),

    # Doctor Account Management
    path('doctor/<int:doctor_id>/suspend/', views.suspend_doctor, name='suspend_doctor'),
    path('doctor/<int:doctor_id>/deactivate/', views.deactivate_doctor, name='deactivate_doctor'),
    path('doctor/<int:doctor_id>/reactivate/', views.reactivate_doctor, name='reactivate_doctor'),
]