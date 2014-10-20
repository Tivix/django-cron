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
    sleeping_cron = 'test_crons.TestSleepingCronJob'
    five_mins_cron = 'test_crons.Test5minsCronJob'
    run_at_times_cron = 'test_crons.TestRunAtTimesCronJob'

    def setUp(self):
        pass

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

        url = reverse('admin:django_cron_cronjoblog_changelist')
        response = self.client.get(url)
        self.assertIn('Cron job logs', response.content)
