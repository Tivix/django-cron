import threading
from time import sleep
from datetime import timedelta

from django import db
from django.test import TransactionTestCase
from django.core.management import call_command
from django.test.utils import override_settings
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import User

from freezegun import freeze_time

from django_cron.helpers import humanize_duration
from django_cron.models import CronJobLog


class OutBuffer(object):
    content = []
    modified = False
    _str_cache = ''

    def write(self, *args):
        self.content.extend(args)
        self.modified = True

    def str_content(self):
        if self.modified:
            self._str_cache = ''.join((str(x) for x in self.content))
            self.modified = False

        return self._str_cache


class TestCase(TransactionTestCase):

    success_cron = 'test_crons.TestSucessCronJob'
    error_cron = 'test_crons.TestErrorCronJob'
    five_mins_cron = 'test_crons.Test5minsCronJob'
    run_at_times_cron = 'test_crons.TestRunAtTimesCronJob'
    wait_3sec_cron = 'test_crons.Wait3secCronJob'
    does_not_exist_cron = 'ThisCronObviouslyDoesntExist'
    test_failed_runs_notification_cron = 'django_cron.cron.FailedRunsNotificationCronJob'

    def setUp(self):
        CronJobLog.objects.all().delete()

    def test_success_cron(self):
        logs_count = CronJobLog.objects.all().count()
        call_command('runcrons', self.success_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_failed_cron(self):
        logs_count = CronJobLog.objects.all().count()
        call_command('runcrons', self.error_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_not_exists_cron(self):
        logs_count = CronJobLog.objects.all().count()
        out_buffer = OutBuffer()
        call_command('runcrons', self.does_not_exist_cron, force=True, stdout=out_buffer)

        self.assertIn('Make sure these are valid cron class names', out_buffer.str_content())
        self.assertIn(self.does_not_exist_cron, out_buffer.str_content())
        self.assertEqual(CronJobLog.objects.all().count(), logs_count)

    @override_settings(DJANGO_CRON_LOCK_BACKEND='django_cron.backends.lock.file.FileLock')
    def test_file_locking_backend(self):
        logs_count = CronJobLog.objects.all().count()
        call_command('runcrons', self.success_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_runs_every_mins(self):
        logs_count = CronJobLog.objects.all().count()

        with freeze_time("2014-01-01 00:00:00"):
            call_command('runcrons', self.five_mins_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:04:59"):
            call_command('runcrons', self.five_mins_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:05:01"):
            call_command('runcrons', self.five_mins_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 2)

    def test_runs_at_time(self):
        logs_count = CronJobLog.objects.all().count()
        with freeze_time("2014-01-01 00:00:01"):
            call_command('runcrons', self.run_at_times_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:04:50"):
            call_command('runcrons', self.run_at_times_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:05:01"):
            call_command('runcrons', self.run_at_times_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 2)

    def test_admin(self):
        password = 'test'
        user = User.objects.create_superuser(
            'test',
            'test@tivix.com',
            password
        )
        self.client = Client()
        self.client.login(username=user.username, password=password)

        # edit CronJobLog object
        call_command('runcrons', self.success_cron, force=True)
        log = CronJobLog.objects.all()[0]
        url = reverse('admin:django_cron_cronjoblog_change', args=(log.id,))
        response = self.client.get(url)
        self.assertIn('Cron job logs', str(response.content))

    def run_cronjob_in_thread(self, logs_count):
        call_command('runcrons', self.wait_3sec_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)
        db.close_old_connections()

    def test_cache_locking_backend(self):
        """
        with cache locking backend
        """
        logs_count = CronJobLog.objects.all().count()
        t = threading.Thread(target=self.run_cronjob_in_thread, args=(logs_count,))
        t.daemon = True
        t.start()
        # this shouldn't get running
        sleep(0.1)  # to avoid race condition
        call_command('runcrons', self.wait_3sec_cron)
        t.join(10)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    # TODO: this test doesn't pass - seems that second cronjob is locking file
    # however it should throw an exception that file is locked by other cronjob
    # @override_settings(
    #     DJANGO_CRON_LOCK_BACKEND='django_cron.backends.lock.file.FileLock',
    #     DJANGO_CRON_LOCKFILE_PATH=os.path.join(os.getcwd())
    # )
    # def test_file_locking_backend_in_thread(self):
    #     """
    #     with file locking backend
    #     """
    #     logs_count = CronJobLog.objects.all().count()
    #     t = threading.Thread(target=self.run_cronjob_in_thread, args=(logs_count,))
    #     t.daemon = True
    #     t.start()
    #     # this shouldn't get running
    #     sleep(1)  # to avoid race condition
    #     call_command('runcrons', self.wait_3sec_cron)
    #     t.join(10)
    #     self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_failed_runs_notification(self):
        CronJobLog.objects.all().delete()
        logs_count = CronJobLog.objects.all().count()

        for i in range(10):
            call_command('runcrons', self.error_cron, force=True)
        call_command('runcrons', self.test_failed_runs_notification_cron)

        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 11)

    def test_humanize_duration(self):
        test_subjects = (
            (timedelta(days=1, hours=1, minutes=1, seconds=1), '1 day, 1 hour, 1 minute, 1 second'),
            (timedelta(days=2), '2 days'),
            (timedelta(days=15, minutes=4), '15 days, 4 minutes'),
            (timedelta(), '< 1 second'),
        )

        for duration, humanized in test_subjects:
            self.assertEqual(
                humanize_duration(duration),
                humanized
            )
