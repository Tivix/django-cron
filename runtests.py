# This file mainly exists to allow python setup.py test to work.
import os
import sys


test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)


SETTING_MODULES = (
    'settings_sqllite',
    'settings_postgres',
    'settings_mysql',
)


def runtests():
    failures = 0
    for module in SETTING_MODULES:
        os.environ['DJANGO_SETTINGS_MODULE'] = module
        import django
        from django.test.utils import get_runner
        from django.conf import settings

        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=1, interactive=True)
        if hasattr(django, 'setup'):
            django.setup()
        failures += test_runner.run_tests(['django_cron'])

    sys.exit(bool(failures))
