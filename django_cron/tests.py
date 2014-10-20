from django.utils import unittest
from django_cron.models import CronJobLog
from django.core.management import call_command
from django.test.utils import override_settings


class TestCase(unittest.TestCase):

    success_cron = 'test_crons.TestSucessCronJob'
    error_cron = 'test_crons.TestErrorCronJob'
    sleeping_cron = 'test_crons.TestSleepingCronJob'

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
