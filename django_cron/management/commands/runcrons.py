from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache
from django_cron import CronJobManager
try:
    from django.utils import timezone
except ImportError:
    # timezone added in Django 1.4
    from django_cron import timezone

from datetime import datetime
from optparse import make_option

DEFAULT_LOCK_TIME = 24*60*60  # 24 hours

def get_class( kls ):
    """TODO: move to django-common app.
    Converts a string to a class. Courtesy: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname/452981#452981"""
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

CRONS_TO_RUN = map(lambda x: get_class(x), settings.CRON_CLASSES)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', help='Force cron runs'),
    )
    def handle(self, *args, **options):
        for cron_class in CRONS_TO_RUN:
            if not cache.get(cron_class.__name__):
                instance = cron_class()
                timeout = DEFAULT_LOCK_TIME
                try:
                    timeout = settings.DJANGO_CRON_LOCK_TIME
                except:
                    pass
                cache.set(cron_class.__name__, timezone.now(), timeout)
                CronJobManager.run(instance, options['force'])
                cache.delete(cron_class.__name__)
            else:
                print "%s failed: lock has been found. Other cron started at %s" % (cron_class.__name__, cache.get(cron_class.__name__)) 