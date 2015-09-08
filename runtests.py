# This file mainly exists to allow python setup.py test to work.
# flake8: noqa
import os
import sys

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_sqllite'

test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

import django
from django.test.utils import get_runner
from django.conf import settings


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=False)
    if hasattr(django, 'setup'):
        django.setup()
    failures = test_runner.run_tests(['django_cron'])
    sys.exit(bool(failures))
