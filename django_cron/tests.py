from django.utils import unittest
from django_cron.models import CronJobLog
from django.core.management import call_command


class TestCase(unittest.TestCase):

    success_cron = 'test_crons.TestSucessCronJob'
    error_cron = 'test_crons.TestErrorCronJob'

    def setUp(self):
        pass

    def test_success_cron(self):
        lgos_count = CronJobLog.objects.all().count()
        call_command('runcrons', self.success_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), lgos_count + 1)

    def test_failed_cron(self):
        lgos_count = CronJobLog.objects.all().count()
        call_command('runcrons', self.error_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), lgos_count + 1)
