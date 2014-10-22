
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'travis',
        'NAME': 'djangocron',
        'TEST_NAME': 'djangocron_test',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',

    'django_cron',
]

SECRET_KEY = "wknfgl34qtnjo&Yk3jqfjtn2k3jtnk4wtnk"


CRON_CLASSES = [
    'test_crons.TestSucessCronJob',
    'test_crons.TestErrorCronJob',
    'test_crons.Test5minsCronJob',
    'test_crons.TestRunAtTimesCronJob',
    'test_crons.Wiat3secCronJob',
    'django_cron.cron.FailedRunsNotificationCronJob'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        'django_cron': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': 'django_cache',
    }
}

ROOT_URLCONF = 'test_urls'
SITE_ID = 1
STATIC_URL = '/static/'
