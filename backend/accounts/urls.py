from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_patient, name='register_patient'),
    path('login/', views.login_page, name='login_page'),
    path('login/password/', views.login_password, name='login_password'),
    path('login/smartcard/', views.login_smartcard, name='login_smartcard'),
    path('login/biometric/', views.login_biometric, name='login_biometric'),
    path('logout/', views.logout_view, name='logout_view'),

    # OTP verification — belongs here because it is part of login
    path('otp/verify/', views.verify_otp, name='verify_otp'),
    path('otp/resend/', views.resend_otp, name='resend_otp'),
    
    # forgot password path
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset/verify-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset/set-password/', views.set_new_password, name='set_new_password'),
]