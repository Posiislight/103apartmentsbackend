"""
Django settings template for realestatebackend project.
Copy this to settings.py and fill in your actual values.
"""

from pathlib import Path
import os 

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

CORS_ALLOWED_ORIGINS = [
    "https://dondaxlimited.com",
    "https://opulent-haven-homes.vercel.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://yourdomain.com",
    "https://opulent-haven-homes.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'your_db_name'),
        'USER': os.environ.get('DB_USER', 'your_db_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_db_password'),
        'HOST': os.environ.get('DB_HOST', 'your_db_host'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Rest of your settings... 