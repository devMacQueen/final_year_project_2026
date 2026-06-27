from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ALLOWED_HOSTS = [
#     'final-year-project-2026-jmzz.onrender.com',
#     'localhost',
#     '127.0.0.1',
# ]

# import os

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# =============================================
#  Security
# ============================================== 
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-insecure-key-change-this')
DEBUG      = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# ==============================================
#  Installed Apps
# ==============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # project apps
    'accounts',
    'patients',
    'doctors',
    'admin_portal',
]

# ==============================================
# Middleware
# ==============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'healthaccess.urls'

# ==============================================
#  Templates 
# ==============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ROOT_DIR / 'frontend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'healthaccess.wsgi.application'

# ==============================================
#  Database  PostgreSQL 
# ==============================================
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.getenv('DB_NAME',     'plasu_clinic'),
        'USER':     os.getenv('DB_USER',     'plasu_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST':     os.getenv('DB_HOST',     'localhost'),
        'PORT':     os.getenv('DB_PORT',     '5432'),
    }
}

# ==============================================
#  Password Validation 
# ==============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================
#  Internationalisation 
# ==============================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Lagos'
USE_I18N      = True
USE_TZ        = True

# ==============================================
# Static Files 
# ==============================================
STATIC_URL     = '/static/'
STATICFILES_DIRS = [ROOT_DIR / 'frontend' / 'static']
STATIC_ROOT    = BASE_DIR / 'staticfiles'

# ==============================================
#  Media Files 
# ==============================================
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================
# Auth 
# ==============================================
AUTH_USER_MODEL       = 'accounts.User'
LOGIN_URL             = '/login/'
LOGIN_REDIRECT_URL    = '/dashboard/'
LOGOUT_REDIRECT_URL   = '/login/'
DEFAULT_AUTO_FIELD    = 'django.db.models.BigAutoField'

# ==================================================
# Email 
# Development: prints to terminal
# Production:  switch to smtp backend below
#====================================================
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Uncomment and fill .env to send real emails:
# EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER',     '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = f"PLASU Clinic <{os.getenv('EMAIL_HOST_USER', 'noreply@plasu.edu.ng')}>"

# =================================
#  Session Security 
# =================================
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE  = 'Lax'
CSRF_COOKIE_HTTPONLY     = True

# ==============================================
# Production Security (only active when DEBUG=False) 
# ==============================================
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER       = True
    SECURE_CONTENT_TYPE_NOSNIFF     = True
    X_FRAME_OPTIONS                  = 'DENY'