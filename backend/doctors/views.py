from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from patients.models import Patient, MedicalRecord, Appointment


@never_cache
@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return redirect('login_page')

    records = MedicalRecord.objects.filter(doctor=request.user).order_by('-created_at')
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-created_at')

    search = request.GET.get('search', '')
    patients = Patient.objects.all()

    if search:
        patients = patients.filter(full_name__icontains=search) | patients.filter(matric_number__icontains=search)

    context = {
        'records': records,
        'appointments': appointments,
        'patients': patients,
        'pending_appointments': appointments.filter(status='pending').count(),
        'search': search,
    }

    return render(request, 'doctors/dashboard.html', context)


@never_cache
@login_required
def create_medical_record(request):
    if request.user.role != 'doctor':
        return redirect('login_page')

    patients = Patient.objects.all()

    if request.method == 'POST':
        patient_id = request.POST['patient']
        diagnosis = request.POST['diagnosis']
        prescription = request.POST['prescription']
        notes = request.POST.get('notes', '')

        patient = Patient.objects.get(id=patient_id)

        MedicalRecord.objects.create(
            patient=patient,
            doctor=request.user,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes,
        )

        messages.success(request, 'Medical record created successfully!')
        return redirect('doctor_dashboard')

    return render(request, 'doctors/create_record.html', {'patients': patients})


@never_cache
@login_required
def manage_appointment(request, appointment_id):
    if request.user.role != 'doctor':
        return redirect('login_page')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'approve':
            appointment.status = 'approved'
            appointment.save()
            messages.success(request, 'Appointment approved!')

        elif action == 'decline':
            decline_reason = request.POST['decline_reason']
            appointment.status = 'declined'
            appointment.decline_reason = decline_reason
            appointment.save()
            messages.success(request, 'Appointment declined!')

        return redirect('doctor_dashboard')

    return render(request, 'doctors/manage_appointment.html', {'appointment': appointment})
