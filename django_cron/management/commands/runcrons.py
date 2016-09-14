import traceback
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django_cron import CronJobManager, get_class, get_current_time
from django_cron.models import CronJobLog
try:
    from django.db import close_old_connections as close_connection
except ImportError:
    from django.db import close_connection


DEFAULT_LOCK_TIME = 24 * 60 * 60  # 24 hours


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'cron_classes',
            nargs='*'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cron runs'
        )
        parser.add_argument(
            '--silent',
            action='store_true',
            help='Do not push any message on console'
        )

    def handle(self, *args, **options):
        """
        Iterates over all the CRON_CLASSES (or if passed in as a commandline argument)
        and runs them.
        """
        cron_classes = options['cron_classes']
        if cron_classes:
            cron_class_names = cron_classes
        else:
            cron_class_names = getattr(settings, 'CRON_CLASSES', [])

        try:
            crons_to_run = [get_class(x) for x in cron_class_names]
        except Exception:
            error = traceback.format_exc()
            self.stdout.write('Make sure these are valid cron class names: %s\n%s' % (cron_class_names, error))
            return

        for cron_class in crons_to_run:
            run_cron_with_cache_check(
                cron_class,
                force=options['force'],
                silent=options['silent']
            )

        clear_old_log_entries()
        close_connection()


def run_cron_with_cache_check(cron_class, force=False, silent=False):
    """
    Checks the cache and runs the cron or not.

    @cron_class - cron class to run.
    @force      - run job even if not scheduled
    @silent     - suppress notifications
    """

    with CronJobManager(cron_class, silent) as manager:
        manager.run(force)


def clear_old_log_entries():
    """
    Removes older log entries, if the appropriate setting has been set
    """
    if hasattr(settings, 'DJANGO_CRON_DELETE_LOGS_OLDER_THAN'):
        delta = timedelta(days=settings.DJANGO_CRON_DELETE_LOGS_OLDER_THAN)
        CronJobLog.objects.filter(end_time__lt=get_current_time() - delta).delete()
