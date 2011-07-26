from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache

from django_cron import CronJobManager

from datetime import datetime

DEFAULT_LOCK_TIME = 15*60

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
    def handle(self, *args, **options):
        for cron_class in CRONS_TO_RUN:
            if not cache.get(cron_class.__name__):
                instance = cron_class()
                timeout = DEFAULT_LOCK_TIME
                try:
                    timeout = settings.DJANGO_CRON_LOCK_TIME
                except:
                    pass
                cache.set(cron_class.__name__, datetime.now(), timeout)
                CronJobManager.run(instance)
                cache.delete(cron_class.__name__)
            else:
                print "%s failed: lock has been found. Other cron started at %s" % (cron_class.__name__, cache.get(cron_class.__name__)) 