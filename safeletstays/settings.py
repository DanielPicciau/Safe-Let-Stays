"""
Django settings for Safe Let Stays project.
Minimal configuration for development preview.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# GUESTY API INTEGRATION (Uncomment when ready to use)
# =============================================================================
# 
# To activate Guesty integration:
# 1. Get API credentials from https://app.guesty.com/integrations/api-keys
# 2. Create a .env file in the project root with:
#    GUESTY_API_KEY=your_api_key_here
#    GUESTY_API_SECRET=your_api_secret_here
#    GUESTY_WEBHOOK_SECRET=your_webhook_secret_here
# 3. Install python-dotenv: pip install python-dotenv
# 4. Uncomment the settings below
# 5. Uncomment the code in yourapp/guesty_integration.py
# 6. Uncomment the Guesty fields in yourapp/models.py
# 7. Run migrations: python manage.py makemigrations && python manage.py migrate
# 8. Add API endpoints to urls.py
#
# from dotenv import load_dotenv
# load_dotenv()
#
# GUESTY_API_KEY = os.environ.get('GUESTY_API_KEY', '')
# GUESTY_API_SECRET = os.environ.get('GUESTY_API_SECRET', '')
# GUESTY_WEBHOOK_SECRET = os.environ.get('GUESTY_WEBHOOK_SECRET', '')
#
# # Cache configuration for Guesty API responses
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#         'TIMEOUT': 300,  # 5 minutes default
#     }
# }
#
# # For production, use Redis:
# # CACHES = {
# #     'default': {
# #         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
# #         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
# #     }
# # }
#
# # Logging configuration for Guesty integration debugging
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'logs' / 'guesty.log',
#         },
#     },
#     'loggers': {
#         'yourapp.guesty_integration': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }
# =============================================================================

# =============================================================================
# STRIPE INTEGRATION
# =============================================================================
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

LOGIN_REDIRECT_URL = '/my-bookings/'
LOGOUT_REDIRECT_URL = '/'

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
# Default to console backend for development (prints emails to terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, set these environment variables:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = 'Safe Let Stays <hello@safeletstays.co.uk>'
SERVER_EMAIL = 'admin@safeletstays.co.uk'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
