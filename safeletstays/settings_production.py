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
_secret_key = os.environ.get('DJANGO_SECRET_KEY')
if not _secret_key:
    raise ValueError(
        "DJANGO_SECRET_KEY environment variable is required in production. "
        "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )
SECRET_KEY = _secret_key

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
    'yourapp.apps.YourappConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom security middleware
    'yourapp.security.SecurityHeadersMiddleware',
    'yourapp.security.RequestValidationMiddleware',
    'yourapp.security.SQLInjectionProtectionMiddleware',
    'yourapp.security.BruteForceProtectionMiddleware',
    'yourapp.security.SessionSecurityMiddleware',
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
# DATABASE (MED-02)
# =============================================================================

# Default: SQLite (for PythonAnywhere without paid database)
# For production with high traffic, PostgreSQL is recommended
_db_engine = os.environ.get('DB_ENGINE', 'sqlite3')

if _db_engine == 'postgresql':
    # PostgreSQL configuration (recommended for production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'safeletstays'),
            'USER': os.environ.get('DB_USER', 'safeletstays'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # Connection pooling
            'OPTIONS': {
                'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),
            },
        }
    }
elif _db_engine == 'mysql':
    # MySQL configuration (for PythonAnywhere)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'yourusername$safeletstays'),
            'USER': os.environ.get('DB_USER', 'yourusername'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'yourusername.mysql.pythonanywhere-services.com'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # SQLite (development/simple deployments only)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10}
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# CACHE CONFIGURATION (MED-03 - for rate limiting and session storage)
# =============================================================================

_cache_backend = os.environ.get('CACHE_BACKEND', 'locmem')

if _cache_backend == 'redis':
    # Redis configuration (recommended for production with brute force protection)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'TIMEOUT': 300,
        }
    }
    # Use Redis for sessions when Redis is available
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
elif _cache_backend == 'memcached':
    # Memcached configuration
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
            'LOCATION': os.environ.get('MEMCACHED_URL', '127.0.0.1:11211'),
            'TIMEOUT': 300,
        }
    }
else:
    # Local memory cache (not recommended for multi-process deployments)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'safeletstays-prod-cache',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 5000,
            }
        }
    }

# =============================================================================
# FILE UPLOAD SECURITY
# =============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100

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

# HTTPS settings - ENABLED for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS Configuration
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session Security
SESSION_COOKIE_NAME = 'safeletstays_session'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://slpm-webflareuk.pythonanywhere.com',
    'https://www.safeletstays.co.uk',
    'https://safeletstays.co.uk',
]

# Admin Security
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')  # Change this in production!

# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# STRIPE INTEGRATION
# =============================================================================

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')


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

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'security',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'yourapp.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
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
