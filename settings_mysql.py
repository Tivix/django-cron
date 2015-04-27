from settings_base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'travis',
        'PASSWORD': '',
        'NAME': 'travis',
        'TEST_NAME': 'travis_test',
    }
}
