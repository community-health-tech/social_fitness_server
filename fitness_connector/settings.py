"""
Django settings for storytelling_server project.

Generated by 'django-admin startproject' using Django 1.11.

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
SECRET_KEY = '9)))$=x^-mv-qd1pd_$k6)2ltwhvr*3g)9s$dwqc(ycljxc(&z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [u'wellness.ccs.neu.edu', u'wellness-test.ccs.neu.edu']


# Application definition

INSTALLED_APPS = [
    'oauth2_provider',
    'rest_framework',
    'story_manager.apps.StoryManagerConfig',
    'people.apps.PeopleConfig',
    'fitness.apps.FitnessConfig',
    'fitness_connector.apps.FitnessConnectorConfig',
    'challenges.apps.ChallengesConfig',
    'api.apps.ApiConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'storytelling_server.urls'

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

WSGI_APPLICATION = 'storytelling_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storytelling_dev',  
        'USER': 'story_user',
        'PASSWORD': 'storyte111ngWhoah',
        'HOST': '127.0.0.1', 
        #'PORT': '3306',
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        
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

STATIC_URL = '/storytelling_static/'
STATIC_ROOT = '/Sites/httpsdocs/storytelling_static/'

# Django REST Framework
# Django REST Framework

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'djangorestframework_camel_case.render.CamelCaseJSONRenderer', # Any other renders
    # ),
    # 'DEFAULT_PARSER_CLASSES': (
    #     'djangorestframework_camel_case.parser.CamelCaseJSONParser', # Any other parsers
    # ),
}

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
}
