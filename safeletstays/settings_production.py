"""
Django Production Settings for Safe Let Stays
PythonAnywhere Deployment Configuration

INSTRUCTIONS:
1. Upload your project to PythonAnywhere (via git clone or zip upload)
2. In PythonAnywhere Web tab, set:
   - Source code: /home/YOUR_USERNAME/safeletstays
   - Working directory: /home/YOUR_USERNAME/safeletstays
   - WSGI configuration file: Click to edit and paste contents of wsgi_pythonanywhere.py
3. Set virtualenv path if using one
4. Configure static files (see STATIC/MEDIA section below)
5. Reload web app
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file explicitly
load_dotenv(BASE_DIR / '.env')

# =============================================================================
# CORE SETTINGS
# =============================================================================

# BASE_DIR is defined above


# SECURITY: Generate a new secret key for production!
# Run this in Python: 
# from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'CHANGE-THIS-TO-A-REAL-SECRET-KEY-IN-PRODUCTION')

# SECURITY: Set to False in production
DEBUG = False

# IMPORTANT: Add your PythonAnywhere domain here
# Example: ['yourusername.pythonanywhere.com', 'www.safeletstays.co.uk']
ALLOWED_HOSTS = [
    'slpm-webflareuk.pythonanywhere.com',
    'SLPM-WebFlareUK.pythonanywhere.com',
    'www.safeletstays.co.uk',
    'safeletstays.co.uk',
    'localhost',
    '127.0.0.1',
]

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yourapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'safeletstays.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'safeletstays.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For MySQL on PythonAnywhere (optional - uncomment if using MySQL):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'yourusername$safeletstays',
#         'USER': 'yourusername',
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': 'yourusername.mysql.pythonanywhere-services.com',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================

# URL prefix for static files
STATIC_URL = '/static/'

# Directory where collectstatic will gather all static files
# PythonAnywhere will serve files from this directory
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional directories to search for static files during development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# =============================================================================
# MEDIA FILES (User uploads - property images, etc.)
# =============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# SECURITY SETTINGS (Production)
# =============================================================================

# HTTPS settings (enable when you have SSL certificate)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'

# HSTS (enable after confirming HTTPS works)
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# STRIPE INTEGRATION
# =============================================================================

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# =============================================================================
# EMAIL SETTINGS (MailerSend SMTP & API)
# =============================================================================

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Safe Let Stays <daniel@webflare.studio>')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'daniel@webflare.studio')

# Mailjet API Configuration
MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# =============================================================================
# PYTHONANYWHERE STATIC FILES CONFIGURATION
# =============================================================================
"""
In the PythonAnywhere Web tab, configure static files:

URL              | Directory
-----------------|-------------------------------------------------
/static/         | /home/YOUR_USERNAME/safeletstays/staticfiles
/media/          | /home/YOUR_USERNAME/safeletstays/media

Replace YOUR_USERNAME with your actual PythonAnywhere username.

After uploading your project, run these commands in a Bash console:
    cd ~/safeletstays
    python manage.py collectstatic --settings=safeletstays.settings_production
    python manage.py migrate --settings=safeletstays.settings_production
"""
