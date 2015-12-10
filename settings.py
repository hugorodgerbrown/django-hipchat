# -*- coding: utf-8 -*-
from os import environ

DEBUG = True

DATABASES= {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'nps.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'hipchat',
)

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

SECRET_KEY = "hipchat"

ROOT_URLCONF = 'urls'

APPEND_SLASH = True

STATIC_URL = '/static/'

SITE_ID = 1

assert DEBUG is True, "This project is only intended to be used for testing."

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'level': environ.get('LOGGING_LEVEL_DJANGO', 'WARNING'),
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'yunojuno': {
            'handlers': ['console'],
            'level': environ.get('LOGGING_LEVEL_YUNOJUNO', 'DEBUG'),
            'propagate': False,
        },
        'pyelasticsearch': {
            'handlers': ['console'],
            'level': environ.get('LOGGING_LEVEL_SEARCH', 'WARNING'),
            'propagate': False,
        },
        'requests': {
            'handlers': ['console'],
            'level': environ.get('LOGGING_LEVEL_REQUESTS', 'WARNING'),
            'propagate': False,
        },
        # Log errors from the Opbeat module to the console (recommended)
        'opbeat.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}
