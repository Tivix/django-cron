import traceback
from datetime import timedelta
import threading

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import close_old_connections

from django_cron import CronJobManager, get_class, get_current_time
from django_cron.models import CronJobLog

from datetime import datetime
import pytz, os, logging

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

        main_cron = False

        cron_classes = options['cron_classes']
        if cron_classes:
            cron_class_names = cron_classes
        else:
            #main_cron = True
            cron_class_names = getattr(settings, 'CRON_CLASSES', [])

        if main_cron:
            #for handler in logging.root.handlers[:]:
            #    logging.root.removeHandler(handler)

            logger = logging.getLogger(__name__)

            today = datetime.utcnow().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Berlin'))
            basename = os.path.join(os.path.dirname(__file__),"../../../log/",today.strftime("%Y/%m/%d"))
            try: os.makedirs(basename)
            except Exception: pass
            folder = os.path.normpath(os.path.join(basename,today.strftime("%d-%m-%Y_%H-%M")+"_runcrons.log"))

            handler = logging.FileHandler(folder)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            #logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',filename=folder,level=logging.INFO)

            logger.info("Running crons started "+today.strftime("%d-%m-%Y_%H-%M"))
            #logger.info("Crons to run: "+ " ".join(cron_class_names))

        try:
            crons_to_run = [get_class(x) for x in cron_class_names]
        except Exception:
            error = traceback.format_exc()
            self.stdout.write('Make sure these are valid cron class names: %s\n%s' % (cron_class_names, error))
            return

        threads = []
        single_threaded = []
        for cron_class in crons_to_run:
            if getattr(settings,'DJANGO_CRON_MULTITHREADED',False):
                if hasattr(cron_class,"single_threaded") and cron_class.single_threaded:
                    single_threaded.append(cron_class)
                else:
                    ## run all cron jobs in parallel as thread
                    th = threading.Thread(
                        target = run_cron_with_cache_check, 
                        kwargs={
                            "cron_class":cron_class,
                            "force":options['force'],
                            "silent":options['silent']
                        }
                    )
                    if main_cron: logger.info("Thread starting: "+str(cron_class))
                    th.start()
                    if main_cron: logger.info("\tdone")
                    threads.append([th,cron_class])
            else: single_threaded.append(cron_class)

        for cron_class in single_threaded:
            print("run singlethreaded: "+str(cron_class))
            run_cron_with_cache_check(
                cron_class,
                force=options['force'],
                silent=options['silent']
            )

        for th in threads:
            if main_cron: logger.info("Wait for thread: "+str(th[1]))
            th[0].join()
            if main_cron: logger.info("done")
        if main_cron: logger.info("clear old log entries")
        clear_old_log_entries()
        if main_cron: logger.info("done")
        if main_cron: logger.info("close old connections")
        close_old_connections()
        if main_cron: logger.info("done")
        if main_cron: logger.info("exit")


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
