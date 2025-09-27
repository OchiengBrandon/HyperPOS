# django_pos/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import pymysql

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-@%7099(yo(0b_o*&x#qpi_zaz1_awoxf1)gnu*qf$8ml)8!jvq')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Allowed hosts
ALLOWED_HOSTS_ENV = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'pos_app',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'widget_tweaks',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_pos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pos_app.context_processors.business_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_pos.wsgi.application'

# Database configuration - uses MySQL for both local and production
def get_database_config():
    # Always use MySQL, but with different default settings for local vs production
    is_production = (
        ENVIRONMENT == 'production' or 
        os.path.exists('/home') and 'public_html' in str(BASE_DIR)
    )
    
    if is_production:
        # Production MySQL configuration for cPanel
        return {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.getenv('DATABASE_NAME', 'your_database_name'),
                'USER': os.getenv('DATABASE_USER', 'your_database_user'),
                'PASSWORD': os.getenv('DATABASE_PASSWORD', 'your_database_password'),
                'HOST': os.getenv('DATABASE_HOST', 'localhost'),
                'PORT': os.getenv('DATABASE_PORT', '3306'),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        }
    else:
        # Local development MySQL configuration
        return {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.getenv('DATABASE_NAME', 'hyperpos_local'),
                'USER': os.getenv('DATABASE_USER', 'root'),
                'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
                'HOST': os.getenv('DATABASE_HOST', 'localhost'),
                'PORT': os.getenv('DATABASE_PORT', '3306'),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        }

DATABASES = get_database_config()

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

# Email Configuration - adapts to environment
def get_email_config():
    is_production = (
        ENVIRONMENT == 'production' or 
        os.path.exists('/home') and 'public_html' in str(BASE_DIR) or 
        os.getenv('EMAIL_HOST')
    )
    
    if is_production:
        # Production email configuration
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': os.getenv('EMAIL_HOST'),
            'EMAIL_PORT': int(os.getenv('EMAIL_PORT', '587')),
            'EMAIL_USE_TLS': os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true',
            'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER'),
            'EMAIL_HOST_PASSWORD': os.getenv('EMAIL_HOST_PASSWORD'),
        }
    else:
        # Local development - console backend
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
        }

# Apply email configuration
email_config = get_email_config()
for key, value in email_config.items():
    globals()[key] = value

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Static and media files configuration - adapts to environment
def get_static_media_config():
    # Check environment setting or detect cPanel
    is_production = (
        ENVIRONMENT == 'production' or 
        os.path.exists('/home') and 'public_html' in str(BASE_DIR)
    )
    
    if is_production:
        # Production configuration for cPanel
        # Static files are collected to the Django app directory
        static_root = os.getenv('STATIC_ROOT', '/home1/naviposc/pos.navipos.co.ke/static')
        media_root = os.getenv('MEDIA_ROOT', '/home1/naviposc/pos.navipos.co.ke/media')
        # Include staticfiles dirs for collectstatic to find source files
        staticfiles_dirs = [os.path.join(BASE_DIR, 'static')]
        return static_root, media_root, staticfiles_dirs
    else:
        # Local development configuration
        static_root = os.path.join(BASE_DIR, 'staticfiles')
        media_root = os.path.join(BASE_DIR, 'media')
        staticfiles_dirs = [os.path.join(BASE_DIR, 'static')]
        return static_root, media_root, staticfiles_dirs

STATIC_ROOT, MEDIA_ROOT, STATICFILES_DIRS = get_static_media_config()

# Media files
MEDIA_URL = '/media/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URL
LOGIN_URL = 'pos:login'  # Use the namespace for the login URL
LOGIN_REDIRECT_URL = 'pos:dashboard'  # Use the namespace for the dashboard URL
LOGOUT_REDIRECT_URL = 'core:index'  # Use the namespace for the login URL after logout

# CORS settings - adapts to environment
def get_cors_config():
    is_production = (
        ENVIRONMENT == 'production' or 
        os.path.exists('/home') and 'public_html' in str(BASE_DIR) or 
        not DEBUG
    )
    
    if is_production:
        # Production CORS - restrictive
        cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
        return {
            'CORS_ALLOW_ALL_ORIGINS': False,
            'CORS_ALLOWED_ORIGINS': [origin.strip() for origin in cors_origins.split(',') if origin.strip()],
        }
    else:
        # Local development CORS - permissive
        return {
            'CORS_ALLOW_ALL_ORIGINS': True,
        }

# Apply CORS configuration
cors_config = get_cors_config()
for key, value in cors_config.items():
    globals()[key] = value

# Security Settings - enabled for production
def get_security_config():
    is_production = (
        ENVIRONMENT == 'production' or 
        os.path.exists('/home') and 'public_html' in str(BASE_DIR) or 
        not DEBUG
    )
    
    if is_production:
        return {
            'SECURE_BROWSER_XSS_FILTER': True,
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'X_FRAME_OPTIONS': 'DENY',
            'SECURE_HSTS_SECONDS': 31536000,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            'SECURE_SSL_REDIRECT': True,
        }
    else:
        return {}

# Apply security configuration
security_config = get_security_config()
for key, value in security_config.items():
    globals()[key] = value

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# WhiteNoise settings for static files serving in production
# Use simple static files storage for cPanel compatibility
if ENVIRONMENT == 'production':
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# WhiteNoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True if not (ENVIRONMENT == 'production') else False