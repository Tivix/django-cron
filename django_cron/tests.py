import threading
from time import sleep
from datetime import timedelta

from mock import patch
from freezegun import freeze_time

from django import db
from django.conf import settings
from django.test import TransactionTestCase
from django.core.management import call_command, CommandError
from django.test.utils import override_settings
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_cron import get_class
from django_cron.cron import FailedRunsNotificationCronJob
from django_cron.helpers import humanize_duration
from django_cron.models import CronJobLog
from test_crons import TestErrorCronJob


SUCCESS_CRON = 'test_crons.TestSucessCronJob'
ERROR_CRON = 'test_crons.TestErrorCronJob'
FIVE_MINS_CRON = 'test_crons.Test5minsCronJob'
RUN_AT_TIMES_CRON = 'test_crons.TestRunAtTimesCronJob'
WAIT_3SEC_CRON = 'test_crons.Wait3secCronJob'
DOES_NOT_EXIST_CRON = 'ThisCronObviouslyDoesntExist'
FAILED_RUNS_CRON = 'django_cron.cron.FailedRunsNotificationCronJob'

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


class DjangoCronTestCase(TransactionTestCase):
    def setUp(self):
        CronJobLog.objects.all().delete()


class BaseTests(DjangoCronTestCase):
    def test_success_cron(self):
        logs_count = CronJobLog.objects.all().count()
        call_command('runcrons', SUCCESS_CRON, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_failed_cron(self):
        logs_count = CronJobLog.objects.all().count()
        call_command('runcrons', ERROR_CRON, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_not_exists_cron(self):
        logs_count = CronJobLog.objects.all().count()
        out_buffer = OutBuffer()
        call_command('runcrons', DOES_NOT_EXIST_CRON, force=True, stdout=out_buffer)

        self.assertIn('Make sure these are valid cron class names', out_buffer.str_content())
        self.assertIn(DOES_NOT_EXIST_CRON, out_buffer.str_content())
        self.assertEqual(CronJobLog.objects.all().count(), logs_count)

    @override_settings(DJANGO_CRON_LOCK_BACKEND='django_cron.backends.lock.file.FileLock')
    def test_file_locking_backend(self):
        logs_count = CronJobLog.objects.all().count()
        call_command('runcrons', SUCCESS_CRON, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_runs_every_mins(self):
        logs_count = CronJobLog.objects.all().count()

        with freeze_time("2014-01-01 00:00:00"):
            call_command('runcrons', FIVE_MINS_CRON)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:04:59"):
            call_command('runcrons', FIVE_MINS_CRON)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:05:01"):
            call_command('runcrons', FIVE_MINS_CRON)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 2)

    def test_runs_at_time(self):
        logs_count = CronJobLog.objects.all().count()
        with freeze_time("2014-01-01 00:00:01"):
            call_command('runcrons', RUN_AT_TIMES_CRON)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:04:50"):
            call_command('runcrons', RUN_AT_TIMES_CRON)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:05:01"):
            call_command('runcrons', RUN_AT_TIMES_CRON)
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
        call_command('runcrons', SUCCESS_CRON, force=True)
        log = CronJobLog.objects.all()[0]
        url = reverse('admin:django_cron_cronjoblog_change', args=(log.id,))
        response = self.client.get(url)
        self.assertIn('Cron job logs', str(response.content))

    def run_cronjob_in_thread(self, logs_count):
        call_command('runcrons', WAIT_3SEC_CRON)
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
        call_command('runcrons', WAIT_3SEC_CRON)
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
    #     call_command('runcrons', WAIT_3SEC_CRON)
    #     t.join(10)
    #     self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

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


class FailureReportTests(DjangoCronTestCase):
    """
    Unit tests for the FailedRunsNotificationCronJob.
    """
    def _error_cron(self):
        call_command('runcrons', ERROR_CRON, force=True)

    def _report_cron(self):
        call_command(
            'runcrons', FAILED_RUNS_CRON,
            force=True
        )

    def _error_and_report(self):
        self._error_cron()
        self._report_cron()

    def _resolve_reported_failures(self, cron_cls, failed_jobs):
        """
        Resolve the failed jobs passed to the notifier's report_failure().

        This allows us to assert the jobs passed given that failed jobs is a
        queryset which shouldn't match any instances after the notifier runs
        as it should make all log entries as having been reported.
        """
        self.reported_cls = cron_cls
        self.reported_jobs = set(failed_jobs)

    @override_settings(
        CRON_CLASSES=(
            SUCCESS_CRON,
            FIVE_MINS_CRON,
            ERROR_CRON,
            FAILED_RUNS_CRON
        )
    )
    @patch.object(FailedRunsNotificationCronJob, 'check_for_failures')
    def test_checks_according_to_cron_classes(self, mock_check):
        """
        The FailedRunsNotificationCronJob checks for failures in CRON_CLASSES.
        """
        self._report_cron()
        self.assertEquals(3, mock_check.call_count)

        # It should also ignore itself
        expected_checked_classes = {
            get_class(cron_class_name)
            for cron_class_name in settings.CRON_CLASSES
            if cron_class_name != FAILED_RUNS_CRON
        }
        actual_checked_classes = {
            cron_class
            for call_args, call_kwargs in mock_check.call_args_list
            for cron_class in call_args
        }
        self.assertEquals(
            actual_checked_classes, expected_checked_classes
        )

    @patch.object(FailedRunsNotificationCronJob, 'do')
    def test_runs_always_by_default(self, mock_do):
        mock_do.return_value = 'OK'

        with freeze_time("2017-01-01") as frozen_datetime:
            call_command('runcrons', FAILED_RUNS_CRON)
            self.assertEqual(1, mock_do.call_count)

            frozen_datetime.tick(delta=timedelta(minutes=2))
            call_command('runcrons', FAILED_RUNS_CRON)
            self.assertEqual(2, mock_do.call_count)

            frozen_datetime.tick(delta=timedelta(minutes=2))
            call_command('runcrons', FAILED_RUNS_CRON)
            self.assertEqual(3, mock_do.call_count)

    @override_settings(CRON_FAILURE_REPORT=dict(RUN_EVERY_MINS=10))
    @patch.object(FailedRunsNotificationCronJob, 'do')
    def test_settings_can_override_run_every(self, mock_do):
        mock_do.return_value = 'OK'

        with freeze_time("2017-01-01") as frozen_datetime:
            call_command('runcrons', FAILED_RUNS_CRON)
            self.assertEqual(1, mock_do.call_count)

            # Less than 10 minutes, should not run again
            frozen_datetime.tick(delta=timedelta(minutes=9))
            call_command('runcrons', FAILED_RUNS_CRON)
            self.assertEqual(1, mock_do.call_count)

            # More than 10 minutes, should run again
            frozen_datetime.tick(delta=timedelta(minutes=2))
            call_command('runcrons', FAILED_RUNS_CRON)
            self.assertEqual(2, mock_do.call_count)

    @patch.object(FailedRunsNotificationCronJob, 'report_failure')
    def test_failed_notifications(self, mock_report):
        """
        By default, the user should be notified after 10 job failures.
        """
        mock_report.side_effect = self._resolve_reported_failures

        for _ in range(9):
            self._error_and_report()
            self.assertEquals(0, mock_report.call_count)

        # The tenth error triggers the report
        self._error_and_report()
        self.assertEqual(1, mock_report.call_count)

        # The correct job class and entries should be included
        self.assertEquals(TestErrorCronJob, self.reported_cls)
        self.assertEquals(
            set(CronJobLog.objects.filter(code=TestErrorCronJob.code)),
            self.reported_jobs
        )

    @patch.object(FailedRunsNotificationCronJob, 'report_failure')
    @override_settings(CRON_FAILURE_REPORT=dict(MIN_NUM_FAILURES=1))
    def test_settings_can_override_number_of_failures(self, mock_report):
        mock_report.side_effect = self._resolve_reported_failures
        self._error_and_report()
        self.assertEqual(1, mock_report.call_count)

    @patch.object(FailedRunsNotificationCronJob, 'report_failure')
    @override_settings(CRON_FAILURE_REPORT=dict(MIN_NUM_FAILURES=1))
    def test_logs_all_unreported(self, mock_report):
        mock_report.side_effect = self._resolve_reported_failures
        self._error_cron()
        self._error_and_report()
        self.assertEqual(1, mock_report.call_count)
        self.assertEqual(2, len(self.reported_jobs))

    @patch.object(FailedRunsNotificationCronJob, 'report_failure')
    @override_settings(CRON_FAILURE_REPORT=dict(MIN_NUM_FAILURES=1))
    def test_only_logs_failures(self, mock_report):
        mock_report.side_effect = self._resolve_reported_failures
        call_command('runcrons', SUCCESS_CRON, force=True)
        self._error_and_report()
        self.assertEqual(
            self.reported_jobs,
            {CronJobLog.objects.get(code=TestErrorCronJob.code)}
        )

    @patch.object(FailedRunsNotificationCronJob, 'report_failure')
    @override_settings(CRON_FAILURE_REPORT=dict(MIN_NUM_FAILURES=1))
    def test_only_reported_once(self, mock_report):
        mock_report.side_effect = self._resolve_reported_failures
        self._error_and_report()
        self.assertEqual(1, mock_report.call_count)

        # Calling the notifier for a second time doesn't report a second time
        self._report_cron()
        self.assertEqual(1, mock_report.call_count)

    @patch('django_cron.cron.send_mail')
    @override_settings(
        CRON_FAILURE_REPORT=dict(
            MIN_NUM_FAILURES=1,
            FROM_EMAIL='from@email.com',
            EMAIL_RECIPIENTS=['foo@bar.com', 'x@y.com'],
            EMAIL_PREFIX='ERROR!!!'
        )
    )
    def test_uses_send_mail(self, mock_send_mail):
        """
        Test that django_common is used to send the email notifications.
        """
        self._error_and_report()
        self.assertEquals(1, mock_send_mail.call_count)
        kwargs = mock_send_mail.call_args[1]

        self.assertIn('ERROR!!!', kwargs['subject'])
        self.assertEquals('from@email.com', kwargs['from_email'])
        self.assertEquals(
            ['foo@bar.com', 'x@y.com'], kwargs['recipient_emails']
        )
