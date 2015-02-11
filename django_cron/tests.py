import threading
from time import sleep
import os

from django import db
from django.utils import unittest
from django_cron.models import CronJobLog
from django.core.management import call_command
from django.test.utils import override_settings
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from freezegun import freeze_time


class TestCase(unittest.TestCase):

    success_cron = 'test_crons.TestSucessCronJob'
    error_cron = 'test_crons.TestErrorCronJob'
    five_mins_cron = 'test_crons.Test5minsCronJob'
    run_at_times_cron = 'test_crons.TestRunAtTimesCronJob'
    wait_3sec_cron = 'test_crons.Wiat3secCronJob'
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
        user = User.objects.create_superuser('test', 'test@tivix.com',
            password)
        self.client = Client()
        self.client.login(username=user.username, password=password)

        # get list of CronJobLogs
        url = reverse('admin:django_cron_cronjoblog_changelist')
        response = self.client.get(url)

        # edit CronJobLog object
        call_command('runcrons', self.success_cron, force=True)
        log = CronJobLog.objects.all()[0]
        url = reverse('admin:django_cron_cronjoblog_change', args=(log.id,))
        response = self.client.get(url)
        self.assertIn('Cron job logs', str(response.content))

    def run_cronjob_in_thread(self, logs_count):
        call_command('runcrons', self.wait_3sec_cron)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)
        db.close_connection()

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
