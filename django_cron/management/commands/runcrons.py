import sys
from datetime import datetime
from optparse import make_option
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache
from django_cron import CronJobManager
try:
    from django.utils import timezone
except ImportError:
    # timezone added in Django 1.4
    from django_cron import timezone
from django.db import close_connection


DEFAULT_LOCK_TIME = 24 * 60 * 60  # 24 hours


def get_class(kls):
    """
    TODO: move to django-common app.
    Converts a string to a class.
    Courtesy: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname/452981#452981
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', help='Force cron runs'),
        make_option('--silent', action='store_true', help='Do not push any message on console'),
    )

    def handle(self, *args, **options):
        """
        Iterates over all the CRON_CLASSES (or if passed in as a commandline argument)
        and runs them.
        """
        if args:
            cron_class_names = args
        else:
            cron_class_names = getattr(settings, 'CRON_CLASSES', [])

        try:
            crons_to_run = map(lambda x: get_class(x), cron_class_names)
        except:
            error = traceback.format_exc()
            print('Make sure these are valid cron class names: %s\n%s' % (cron_class_names, error))
            sys.exit()

        for cron_class in crons_to_run:
            run_cron_with_cache_check(cron_class, force=options['force'],
                silent=options['silent'])
        close_connection()


def run_cron_with_cache_check(cron_class, force=False, silent=False):
    """
    Checks the cache and runs the cron or not.

    @cron_class - cron class to run.
    """
    if not cache.get(cron_class.__name__) or getattr(cron_class, 'ALLOW_PARALLEL_RUNS', False):
        timeout = DEFAULT_LOCK_TIME
        try:
            timeout = cron_class.DJANGO_CRON_LOCK_TIME if getattr(cron_class, 'DJANGO_CRON_LOCK_TIME', False) else settings.DJANGO_CRON_LOCK_TIME
        except:
            pass
        cache.set(cron_class.__name__, timezone.now(), timeout)
        instance = cron_class()
        CronJobManager.run(instance, force, silent)
        cache.delete(cron_class.__name__)
    else:
        if not silent:
            print("%s failed: lock has been found. Other cron started at %s" % \
                  (cron_class.__name__, cache.get(cron_class.__name__)))
