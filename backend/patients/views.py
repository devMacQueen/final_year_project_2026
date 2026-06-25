from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .models import Patient, MedicalRecord, Appointment
from accounts.models import User


@never_cache
@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('logout_view')

    records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')
    appointments = Appointment.objects.filter(patient=patient).order_by('-created_at')

    context = {
        'patient': patient,
        'records': records,
        'appointments': appointments,
        'has_smartcard': bool(patient.smartcard_id),
        'has_biometric': bool(patient.biometric_pin),
    }

    return render(request, 'patients/dashboard.html', context)


@never_cache
@login_required
def book_appointment(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('logout_view')

    doctors = User.objects.filter(role='doctor')

    if request.method == 'POST':
        doctor_id = request.POST['doctor']
        date = request.POST['date']
        time = request.POST['time']
        reason = request.POST['reason']

        doctor = User.objects.get(id=doctor_id)

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason,
        )

        messages.success(request, 'Appointment booked successfully!')
        return redirect('patient_dashboard')

    return render(request, 'patients/book_appointment.html', {'doctors': doctors})


@never_cache
@login_required
def virtual_card(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('logout_view')

    return render(request, 'patients/virtual_card.html', {'patient': patient})
