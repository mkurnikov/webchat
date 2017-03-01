import os

from path import Path
from tenv import initialize_env


ROOT_DIR = Path(__file__).parent.parent.parent
APPS_DIR = ROOT_DIR.joinpath('apps')

ENV_FILE = ROOT_DIR.parent.joinpath('.env')
if os.path.isfile(ENV_FILE):
    tenv = initialize_env(ENV_FILE)
else:
    tenv = initialize_env()

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
)

LOCAL_APPS = (
    'apps.chat',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middlewares
MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'apps.chat.middlewares.ResponseLoggingMiddleware',
)

# Debug
DEBUG = tenv.getbool('DJANGO_DEBUG', default=True)

SECRET_KEY = tenv.get("DJANGO_SECRET_KEY",
                      default='h@z@&1zuwxd%dy#%2o(vfivq7r^+8pu0y4re4ua1=!25=$kd@#')

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = '_config.urls'

WSGI_APPLICATION = '_config.wsgi.application'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = APPS_DIR.joinpath('static')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': ['django.contrib.auth.context_processors.auth',
                                   'django.contrib.messages.context_processors.messages']
        }
        
    }
]

SWAGGER_ROOT_FOLDER = 'docs/'

ALLOWED_HOSTS = ['*']