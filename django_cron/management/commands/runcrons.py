from django.core.management.base import BaseCommand
from django.conf import settings

from django_cron import CronJobManager


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
            instance = cron_class()
            CronJobManager.run(instance)
