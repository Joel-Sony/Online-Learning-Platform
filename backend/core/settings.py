import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Behind a TLS-terminating proxy (e.g. Render): trust the forwarded protocol so
# request.build_absolute_uri() emits https URLs for media/thumbnail links and
# DRF pagination — otherwise they come back as http and are blocked as mixed
# content on an https frontend.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    'cloudinary',
    'cloudinary_storage',

    # Local apps
    'users',
    'courses',
    'enrollments',
    'progress',
    'interactions',
    'notifications',
    'qna',
]






AUTH_USER_MODEL = 'users.User'


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serves static files (e.g. the Django admin CSS/JS) when
    # DEBUG=False. Must sit directly after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.pubsub.RedisPubSubChannelLayer',
        'CONFIG': {
            # RedisPubSubChannelLayer expects a plain URL string in hosts,
            # not a dict. Render provides a rediss:// (TLS) URL — pass it
            # directly; channels_redis handles TLS automatically.
            "hosts": [env('REDIS_URL', default='redis://redis:6379/1')],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}



# Database
DATABASES = {
    'default': env.db(),
}


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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Let WhiteNoise compress and serve collected static files in production.
# (CompressedStaticFilesStorage, not the Manifest variant, to avoid a hard
# failure if any referenced asset is missing.)
STORAGES = {
    "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Cloudinary — media uploads (course thumbnails, lesson files)
import cloudinary
cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME', default=''),
    api_key=env('CLOUDINARY_API_KEY', default=''),
    api_secret=env('CLOUDINARY_API_SECRET', default=''),
    secure=True,
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configurations
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

}

# CORS settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# CSRF: with DEBUG=False over HTTPS, Django checks the request Origin against
# this list (needed for admin login POSTs on the deployed domain).
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# JWT settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Stripe Settings (Test Mode)
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# PayPal Settings
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = env('PAYPAL_CLIENT_SECRET', default='')
# Explicit and safe-by-default: stays in sandbox unless PAYPAL_MODE=live is set
# deliberately. (Previously any DEBUG=False deploy silently flipped to live,
# even with sandbox credentials — a real charging risk.)
PAYPAL_MODE = env('PAYPAL_MODE', default='sandbox')
PAYPAL_CURRENCY = env('PAYPAL_CURRENCY', default='USD')

# Frontend URL
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173').rstrip('/')

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='no-reply@onlinelearning.com')



