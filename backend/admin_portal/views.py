from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from accounts.models import User, AccountStatus
from patients.models import Patient
from doctors.models import Doctor
import re


@never_cache
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login_page')
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_admins = User.objects.filter(role='admin').count()
    patients_no_card = Patient.objects.filter(smartcard_id='')
    patients_no_biometric = Patient.objects.filter(biometric_pin__isnull=True) | Patient.objects.filter(biometric_pin='')
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'patients_no_card': patients_no_card,
        'patients_no_biometric': patients_no_biometric,
    }
    return render(request, 'admin_portal/dashboard.html', context)


@never_cache
@login_required
def create_doctor(request):
    if request.user.role != 'admin':
        return redirect('login_page')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']
        specialization = request.POST['specialization']
        phone = request.POST['phone']
        
        phone_pattern = r'^(\+234|0)[0-9]{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Invalid phone number! Use format: 08012345678 or +2348012345678')
            return redirect('create_doctor')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('create_doctor')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='doctor'
        )
        Doctor.objects.create(
            user=user,
            full_name=full_name,
            specialization=specialization,
            phone=phone,
        )
        messages.success(request, f'Doctor {full_name} created successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_portal/create_doctor.html')


@never_cache
@login_required
def create_admin(request):
    if request.user.role != 'admin':
        return redirect('login_page')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('create_admin')
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='admin',
            first_name=full_name,
        )
        messages.success(request, f'Admin {full_name} created successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_portal/create_admin.html')


@never_cache
@login_required
def assign_credentials(request, patient_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        biometric_pin = request.POST.get('biometric_pin', '')
        if biometric_pin:
            patient.biometric_pin = biometric_pin
        patient.save()
        messages.success(request, f'Credentials assigned to {patient.full_name} successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_portal/assign_credentials.html', {'patient': patient})


@never_cache
@login_required
def all_patients(request):
    if request.user.role != 'admin':
        return redirect('login_page')
    search = request.GET.get('search', '')
    patients = Patient.objects.all().order_by('-created_at')
    if search:
        patients = patients.filter(full_name__icontains=search) | patients.filter(matric_number__icontains=search)
    return render(request, 'admin_portal/all_patients.html', {'patients': patients, 'search': search})


@never_cache
@login_required
def all_doctors(request):
    if request.user.role != 'admin':
        return redirect('login_page')
    doctors = Doctor.objects.all().order_by('-created_at')
    return render(request, 'admin_portal/all_doctors.html', {'doctors': doctors})


@never_cache
@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect!')
            return redirect('change_password')
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password')
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully! Please login again.')
        return redirect('login_page')
    return render(request, 'admin_portal/change_password.html')


@never_cache
@login_required
def create_patient(request):
    if request.user.role != 'admin':
        return redirect('login_page')
    from patients.models import FACULTY_CHOICES
    import re
    if request.method == 'POST':
        username = request.POST['username']
        matric_number = request.POST['matric_number'].upper().strip()
        password = request.POST['password']
        full_name = request.POST['full_name']
        date_of_birth = request.POST['date_of_birth']
        gender = request.POST['gender']
        phone = request.POST['phone']
        address = request.POST['address']
        faculty = request.POST['faculty']
        email = request.POST.get('email', '').strip()
        
        pattern = r'^PLASU/\d{4}/[A-Z]+/\d{4}$'
        
        phone_pattern = r'^(\+234|0)[0-9]{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Invalid phone number! Use format: 08012345678 or +2348012345678')
            return redirect('create_patient')
        
        if not re.match(pattern, matric_number):
            messages.error(request, 'Invalid matric number format!')
            return redirect('create_patient')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('create_patient')
        
        if Patient.objects.filter(matric_number=matric_number).exists():
            messages.error(request, 'Matric number already registered!')
            return redirect('create_patient')

        

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email address format!')
            return redirect('create_patient')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists!')
            return redirect('create_patient')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='patient'
        )
        Patient.objects.create(
            user=user,
            full_name=full_name,
            matric_number=matric_number,
            faculty=faculty,
            date_of_birth=date_of_birth,
            gender=gender,
            phone=phone,
            address=address,
            biometric_pin='None',
        )
        messages.success(request, f'Patient {full_name} created successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_portal/create_patient.html', {'faculties': FACULTY_CHOICES})


# ══════════════════════════════════════════════════════════════════
# ACCOUNT STATUS HELPER
# ══════════════════════════════════════════════════════════════════

def _set_status(profile, user, new_status, reason=''):
    """Sets account_status on Patient/Doctor and syncs user.is_active."""
    profile.account_status = new_status
    profile.status_reason  = reason
    profile.save()
    user.is_active = (new_status == AccountStatus.ACTIVE)
    user.save()


# ══════════════════════════════════════════════════════════════════
# PATIENT ACCOUNT MANAGEMENT
# ══════════════════════════════════════════════════════════════════

@never_cache
@login_required
def suspend_patient(request, patient_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        _set_status(patient, patient.user, AccountStatus.SUSPENDED, reason)
        messages.success(request, f'"{patient.full_name}" has been suspended.')
        return redirect('all_patients')
    return render(request, 'admin_portal/account_action.html', {
        'action':          'Suspend',
        'action_color':    'warning',
        'icon':            'fa-pause-circle',
        'target_name':     patient.full_name,
        'target_detail':   f'Matric: {patient.matric_number}',
        'cancel_url':      'all_patients',
        'show_reason':     True,
        'require_confirm': False,
        'description':     'Suspending this account is temporary. The patient cannot log in '
                           'but all their records are preserved. You can lift this at any time.',
    })


@never_cache
@login_required
def deactivate_patient(request, patient_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            reason = request.POST.get('reason', '').strip()
            _set_status(patient, patient.user, AccountStatus.DEACTIVATED, reason)
            messages.success(request, f'"{patient.full_name}" has been deactivated. Records preserved.')
        else:
            messages.info(request, 'Deactivation cancelled.')
        return redirect('all_patients')
    return render(request, 'admin_portal/account_action.html', {
        'action':          'Deactivate',
        'action_color':    'danger',
        'icon':            'fa-user-times',
        'target_name':     patient.full_name,
        'target_detail':   f'Matric: {patient.matric_number} · {patient.faculty}',
        'cancel_url':      'all_patients',
        'show_reason':     True,
        'require_confirm': True,
        'description':     "Deactivating removes this patient's login access. "
                           "All medical records and history are fully preserved.",
    })


@never_cache
@login_required
def reactivate_patient(request, patient_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    patient = get_object_or_404(Patient, id=patient_id)
    _set_status(patient, patient.user, AccountStatus.ACTIVE)
    messages.success(request, f'"{patient.full_name}" has been reactivated and can now log in.')
    return redirect('all_patients')


# ══════════════════════════════════════════════════════════════════
# DOCTOR ACCOUNT MANAGEMENT
# ══════════════════════════════════════════════════════════════════

@never_cache
@login_required
def suspend_doctor(request, doctor_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        _set_status(doctor, doctor.user, AccountStatus.SUSPENDED, reason)
        messages.success(request, f'Dr. "{doctor.full_name}" has been suspended.')
        return redirect('all_doctors')
    return render(request, 'admin_portal/account_action.html', {
        'action':          'Suspend',
        'action_color':    'warning',
        'icon':            'fa-pause-circle',
        'target_name':     f'Dr. {doctor.full_name}',
        'target_detail':   f'Username: {doctor.user.username}',
        'cancel_url':      'all_doctors',
        'show_reason':     True,
        'require_confirm': False,
        'description':     'Suspending this doctor account is temporary and reversible immediately.',
    })


@never_cache
@login_required
def deactivate_doctor(request, doctor_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            reason = request.POST.get('reason', '').strip()
            _set_status(doctor, doctor.user, AccountStatus.DEACTIVATED, reason)
            messages.success(request, f'Dr. "{doctor.full_name}" has been deactivated.')
        else:
            messages.info(request, 'Deactivation cancelled.')
        return redirect('all_doctors')
    return render(request, 'admin_portal/account_action.html', {
        'action':          'Deactivate',
        'action_color':    'danger',
        'icon':            'fa-user-times',
        'target_name':     f'Dr. {doctor.full_name}',
        'target_detail':   f'Username: {doctor.user.username}',
        'cancel_url':      'all_doctors',
        'show_reason':     True,
        'require_confirm': True,
        'description':     "Deactivating removes this doctor's login access. "
                           "All medical records they created are fully preserved.",
    })


@never_cache
@login_required
def reactivate_doctor(request, doctor_id):
    if request.user.role != 'admin':
        return redirect('login_page')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    _set_status(doctor, doctor.user, AccountStatus.ACTIVE)
    messages.success(request, f'Dr. "{doctor.full_name}" has been reactivated and can now log in.')
    return redirect('all_doctors')