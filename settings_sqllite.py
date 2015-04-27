from settings_base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': 'travis',
        'NAME': 'djangocron',
        'TEST_NAME': 'djangocron_test',
    }
}
