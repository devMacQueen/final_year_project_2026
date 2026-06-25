from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import OTPRecord, AccountStatus
from patients.models import Patient, FACULTY_CHOICES
import re
import time

User = get_user_model()


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _mask_phone(phone):
    phone = str(phone).strip()
    if len(phone) >= 7:
        return phone[:3] + '****' + phone[-4:]
    return '***'


def _mask_email(email):
    try:
        local, domain = email.split('@')
        masked_local = local[:2] + '**' if len(local) > 2 else local[0] + '*'
        return f"{masked_local}@{domain}"
    except Exception:
        return '***@***'


def _send_otp_email(user, otp_code):
    send_mail(
        subject='Your PLASU Clinic Verification Code',
        message=(
            f"Hello {user.get_full_name() or user.username},\n\n"
            f"Your PLASU Health Access System verification code is:\n\n"
            f"    {otp_code}\n\n"
            f"This code is valid for 5 minutes and can only be used once.\n"
            f"Do not share this code with anyone.\n\n"
            f"If you did not request this code, please contact the clinic admin immediately.\n\n"
            f"— PLASU Health Access System"
        ),
        from_email='PLASU Clinic <noreply@plasu.edu.ng>',
        recipient_list=[user.email],
        fail_silently=False,
    )


# ══════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════

@never_cache
def home(request):
    return render(request, 'accounts/home.html')


# ══════════════════════════════════════════════════════════════════
# REGISTRATION
# ══════════════════════════════════════════════════════════════════

@never_cache
def register_patient(request):
    if request.method == 'POST':
        username      = request.POST['username']
        email         = request.POST.get('email', '').strip()
        matric_number = request.POST['matric_number'].upper().strip()
        password      = request.POST['password']
        confirm_password = request.POST['confirm_password']
        full_name     = request.POST['full_name']
        date_of_birth = request.POST['date_of_birth']
        gender        = request.POST['gender']
        phone         = request.POST['phone']
        address       = request.POST['address']
        faculty       = request.POST['faculty']

        pattern = r'^PLASU/\d{4}/[A-Z]+/\d{4}$'
        if not re.match(pattern, matric_number):
            messages.error(request, 'Invalid matric number format! Use: PLASU/YEAR/FACULTY/NUMBER')
            return redirect('register_patient')
        
        phone_pattern = r'^(\+234|0)[0-9]{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Invalid phone number! Use format: 08012345678 or +2348012345678')
            return redirect('register_patient')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register_patient')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_patient')

        if Patient.objects.filter(matric_number=matric_number).exists():
            messages.error(request, 'Matric number already registered!')
            return redirect('register_patient')
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email address format!')
            return redirect('register_patient')

        # Check email not already used
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists!')
            return redirect('register_patient')

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
            blood_group=request.POST.get('blood_group', ''),
            genotype=request.POST.get('genotype', ''),
            allergies=request.POST.get('allergies', ''),
            chronic_conditions=request.POST.get('chronic_conditions', ''),
            current_medications=request.POST.get('current_medications', ''),
            emergency_contact_name=request.POST.get('emergency_contact_name', ''),
            emergency_contact_phone=request.POST.get('emergency_contact_phone', ''),
            emergency_contact_relationship=request.POST.get('emergency_contact_relationship', ''),
            biometric_pin=None,
        )

        messages.success(request, 'Registration successful! You can now login.')
        return redirect('login_page')

    return render(request, 'accounts/register.html', {'faculties': FACULTY_CHOICES})


# ══════════════════════════════════════════════════════════════════
# LOGIN — Password
# ══════════════════════════════════════════════════════════════════

@never_cache
def login_page(request):
    return render(request, 'accounts/login.html')


@never_cache
def login_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user     = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.role == 'admin':   return redirect('admin_dashboard')
            if user.role == 'doctor':  return redirect('doctor_dashboard')
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login_page')

    return redirect('login_page')


# ══════════════════════════════════════════════════════════════════
# LOGIN — Smartcard + OTP (Step 1)
# ══════════════════════════════════════════════════════════════════

@never_cache
def login_smartcard(request):
    if request.method != 'POST':
        return redirect('login_page')

    smartcard_id = request.POST.get('smartcard_id', '').strip()

    try:
        patient = Patient.objects.select_related('user').get(smartcard_id=smartcard_id)
    except Patient.DoesNotExist:
        messages.error(request, 'Invalid Smartcard ID. Please check and try again.')
        return redirect('login_page')

    # Check account status
    status = getattr(patient, 'account_status', 'active')
    if status == 'suspended':
        messages.error(request, 'Your account has been temporarily suspended. Contact the clinic admin.')
        return redirect('login_page')
    if status == 'deactivated':
        messages.error(request, 'This account has been deactivated. Contact the clinic admin.')
        return redirect('login_page')

    # Check email exists
    if not patient.user.email:
        messages.error(
            request,
            'No email address found on your account. '
            'Please visit the clinic admin office to add your email.'
        )
        return redirect('login_page')

    # Generate OTP
    otp = OTPRecord.generate_for(patient.user)
    request.session['otp_user_id'] = patient.user.id

    # Send OTP via email
    try:
        _send_otp_email(patient.user, otp.otp_code)
        email_sent = True
    except Exception:
        email_sent = False

    return render(request, 'accounts/otp_verify.html', {
        'email':             _mask_email(patient.user.email),
        'seconds_remaining': otp.seconds_remaining(),
        'purpose':           'Smartcard Login',
        'email_sent':        email_sent,
        'dev_otp':           otp.otp_code,  # remove in production
    })


# ══════════════════════════════════════════════════════════════════
# LOGIN — Smartcard + OTP (Step 2: Verify)
# ══════════════════════════════════════════════════════════════════

@never_cache
def verify_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('login_page')

    if request.method != 'POST':
        return redirect('login_page')

    entered = request.POST.get('otp_code', '').strip()
    user    = get_object_or_404(User, id=user_id)

    try:
        record = OTPRecord.objects.get(user=user, otp_code=entered)
    except OTPRecord.DoesNotExist:
        # Wrong code — generate new OTP and resend
        new_otp = OTPRecord.generate_for(user)
        try:
            _send_otp_email(user, new_otp.otp_code)
            email_sent = True
        except Exception:
            email_sent = False

        email = _mask_email(user.email) if user.email else '***'
        return render(request, 'accounts/otp_verify.html', {
            'email':             email,
            'seconds_remaining': new_otp.seconds_remaining(),
            'purpose':           'Smartcard Login',
            'email_sent':        email_sent,
            'error':             'Incorrect OTP. A new code has been sent to your email.',
            'dev_otp':           new_otp.otp_code,  # remove in production
        })

    if not record.is_valid():
        del request.session['otp_user_id']
        messages.error(request, 'Your OTP has expired. Please restart the smartcard login process.')
        return redirect('login_page')

    # ── Success ───────────────────────────────────────────────────
    record.is_used = True
    record.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    request.session.pop('otp_user_id', None)

    role = getattr(user, 'role', None)
    if role == 'admin':   return redirect('admin_dashboard')
    if role == 'doctor':  return redirect('doctor_dashboard')
    return redirect('patient_dashboard')


# ══════════════════════════════════════════════════════════════════
# LOGIN — Smartcard + OTP (Resend)
# ══════════════════════════════════════════════════════════════════

@never_cache
def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('login_page')

    user = get_object_or_404(User, id=user_id)

    # 60-second cooldown
    last_resent = request.session.get('otp_resent_at')
    if last_resent:
        elapsed = time.time() - last_resent
        if elapsed < 60:
            wait = int(60 - elapsed)
            otp  = OTPRecord.objects.filter(user=user).first()
            email = _mask_email(user.email) if user.email else '***'
            return render(request, 'accounts/otp_verify.html', {
                'email':             email,
                'seconds_remaining': otp.seconds_remaining() if otp else 0,
                'purpose':           'Smartcard Login',
                'resend_wait':       wait,
                'warning':           f'Please wait {wait} seconds before requesting a new code.',
                'dev_otp':           otp.otp_code if otp else '',
            })

    # Generate and send new OTP
    new_otp = OTPRecord.generate_for(user)
    request.session['otp_resent_at'] = time.time()

    try:
        _send_otp_email(user, new_otp.otp_code)
        email_sent = True
    except Exception:
        email_sent = False

    email = _mask_email(user.email) if user.email else '***'
    return render(request, 'accounts/otp_verify.html', {
        'email':             email,
        'seconds_remaining': new_otp.seconds_remaining(),
        'purpose':           'Smartcard Login',
        'email_sent':        email_sent,
        'info':              'A new verification code has been sent to your email.',
        'dev_otp':           new_otp.otp_code,  # remove in production
    })


# ══════════════════════════════════════════════════════════════════
# LOGIN — Biometric
# ══════════════════════════════════════════════════════════════════

@never_cache
def login_biometric(request):
    if request.method == 'POST':
        biometric_pin = request.POST['biometric_pin']

        try:
            patient = Patient.objects.get(biometric_pin=biometric_pin)

            if not patient.biometric_pin:
                messages.error(request, 'Biometric not yet assigned!')
                return redirect('login_page')

            login(request, patient.user)
            return redirect('patient_dashboard')

        except Patient.MultipleObjectsReturned:
            messages.error(request, 'Biometric PIN conflict! Please contact admin.')
            return redirect('login_page')

        except Patient.DoesNotExist:
            messages.error(request, 'Invalid Biometric PIN!')
            return redirect('login_page')

    return redirect('login_page')


# ══════════════════════════════════════════════════════════════════
# LOGOUT
# ══════════════════════════════════════════════════════════════════

@never_cache
def logout_view(request):
    logout(request)
    request.session.flush()
    response = redirect('login_page')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma']  = 'no-cache'
    response['Expires'] = '0'
    return response


import secrets

#================================
# forget password
#=================================

@never_cache
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.success(
                request,
                'If that email is registered, a reset code has been sent to it.'
            )
            return redirect('forgot_password')

        # Block admin accounts from email reset
        if user.role == 'admin':
            messages.error(
                request,
                'Admin accounts cannot be reset via email. '
                'Please contact your system administrator or use the terminal.'
            )
            return redirect('forgot_password')

        # Generate OTP and store in session
        otp = OTPRecord.generate_for(user)
        request.session['reset_user_id'] = user.id

        # Send OTP via email
        try:
            send_mail(
                subject='PLASU Clinic — Password Reset Code',
                message=(
                    f"Hello {user.get_full_name() or user.username},\n\n"
                    f"You requested a password reset for your PLASU Health Access account.\n\n"
                    f"Your reset code is:\n\n"
                    f"    {otp.otp_code}\n\n"
                    f"This code is valid for 5 minutes and can only be used once.\n"
                    f"If you did not request this, please ignore this email.\n\n"
                    f"— PLASU Health Access System"
                ),
                from_email='PLASU Clinic <noreply@plasu.edu.ng>',
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            pass

        messages.success(
            request,
            'If that email is registered, a reset code has been sent to it.'
        )
        return redirect('verify_reset_otp')

    return render(request, 'accounts/forgot_password.html')


@never_cache
def verify_reset_otp(request):
    """
    Step 2: User enters the 6-digit OTP from their email.
    On success, redirect to the set new password page.
    """
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        entered = request.POST.get('otp_code', '').strip()
        user    = get_object_or_404(User, id=user_id)

        try:
            record = OTPRecord.objects.get(user=user, otp_code=entered)
        except OTPRecord.DoesNotExist:
            messages.error(request, 'Incorrect code. Please try again.')
            return render(request, 'accounts/verify_reset_otp.html', {
                'seconds_remaining': 300,
            })

        if not record.is_valid():
            del request.session['reset_user_id']
            messages.error(request, 'Code expired. Please request a new one.')
            return redirect('forgot_password')

        # Mark OTP used and grant reset permission
        record.is_used = True
        record.save()
        request.session['reset_verified_user_id'] = user_id
        request.session.pop('reset_user_id', None)
        return redirect('set_new_password')

    user    = get_object_or_404(User, id=user_id)
    email   = _mask_email(user.email) if user.email else '***'
    otp_obj = OTPRecord.objects.filter(user=user).first()
    return render(request, 'accounts/verify_reset_otp.html', {
        'email':             email,
        'seconds_remaining': otp_obj.seconds_remaining() if otp_obj else 300,
    })
#==============================
# set new password
#==============================
@never_cache
def set_new_password(request):
    """
    Step 3: User sets their new password.
    Only accessible after OTP verification.
    """
    user_id = request.session.get('reset_verified_user_id')
    if not user_id:
        messages.error(request, 'Unauthorized. Please start the reset process again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password        = request.POST.get('password', '')
        confirm         = request.POST.get('confirm_password', '')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/set_new_password.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/set_new_password.html')

        user = get_object_or_404(User, id=user_id)
        user.set_password(password)
        user.save()

        # Clear session
        request.session.pop('reset_verified_user_id', None)

        messages.success(request, 'Password reset successful! You can now log in.')
        return redirect('login_page')

    return render(request, 'accounts/set_new_password.html')