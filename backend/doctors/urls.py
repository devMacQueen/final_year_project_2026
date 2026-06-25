from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('create-record/', views.create_medical_record, name='create_medical_record'),
    path('appointment/<int:appointment_id>/', views.manage_appointment, name='manage_appointment'),
]
