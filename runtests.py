# This file mainly exists to allow python setup.py test to work.
import os
import sys
from test_util import reload_settings


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
        django.setup()

        from django.test.utils import get_runner
        from django.conf import settings
        from django.core.cache import cache

        reload_settings(settings)

        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=1, interactive=False)
        if hasattr(django, 'setup'):
            django.setup()
        failures += test_runner.run_tests(['django_cron'])

        cache.clear()

    sys.exit(bool(failures))
