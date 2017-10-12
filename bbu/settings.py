"""
Django settings for bbu project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g09)et^$8rjua)2^tsgv!l=9c!u#=170cv8kqb!p%90mvcn!=b'

# SECURITY WARNING: don't run with debug turned on in production!
if 'localhost' in os.environ.get('HOSTNAME', ''):
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['52.91.40.99', 'bbu.tlinvestmentllc.com', '127.0.0.1', 'localhost',
                 '54.242.48.0']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap_tables',
    'corsheaders',
    'rest_framework',
]

INSTALLED_APPS += [
    'bbu',
    'accounts',
    'landing',
    'WorkSchedule.WorkConfig',
    'WorkSchedule.WorkTasks',
    'WorkSchedule.WorkWorkers',
    'WorkSchedule.WorkScheduler',
    'WorkSchedule.WorkReports',

    'Reports.ReportConfig',
    'Reports.ReportTimeDetail',

    # 'spider.somax'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bbu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bbu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# if 'EC2_HOME' in os.environ:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'bbu',
#         'USER': 'tlinvestment',
#         'PASSWORD': 'Tsh19920328',
#         'HOST': 'tlinvestment.comop3eprq5n.us-east-1.rds.amazonaws.com',
#         'PORT': '3306',
#     }
# }

# else:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static_public'),]

# MEDIA_ROOT = "/Users/mayaroselip/Documents/LodgIQ/_source/lodgiq_ingestor/webadmin/didash/didash/media/"
# MEDIA_URL = "http://localhost:8000/tracking/static/"
MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'

# Custom User
AUTH_USER_MODEL='accounts.User'

# CORS setting
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Django Rest Framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ]
}

# Celery settings
from kombu import Exchange, Queue

CELERY_BROKER_URL = 'redis://localhost:6379/0'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
# CELERY_RESULT_BACKEND = 'db+sqlite:///db.sqlite3'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# timezone = TIME_ZONE

CELERYD_CONCURRENCY = 1
CELERYD_MAX_TASKS_PER_CHILD = 1

# Celery import tasks
CELERY_IMPORTS = ('spider.somax.tasks', )

# Queues and Router
CELERY_QUEUES = (
    # Queue('queue_add_reduce', exchange=Exchange('calculate_exchange', type='direct'), routing_key='key1'),
    Queue('celery', Exchange('celery'), routing_key='celery'),
)

CELERY_ROUTES = {
    'spider.somax.tasks': {'queue': 'celery', 'routing_key': 'celery'},
    # 'celeryservice.tasks.reduce': {'queue': 'queue_add_reduce', 'routing_key': 'key1', 'delivery_mode': 1},
}
