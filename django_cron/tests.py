import threading
from time import sleep
from datetime import timedelta
from unittest import skip

from mock import patch
from freezegun import freeze_time

from django import db
from django.test import TransactionTestCase
from django.core.management import call_command
from django.test.utils import override_settings
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import User

from django_cron.helpers import humanize_duration
from django_cron.models import CronJobLog, CronJobLock
import test_crons


class OutBuffer(object):
    def __init__(self):
        self._str_cache = ''
        self.content = []
        self.modified = False

    def write(self, *args):
        self.content.extend(args)
        self.modified = True

    def str_content(self):
        if self.modified:
            self._str_cache = ''.join((str(x) for x in self.content))
            self.modified = False

        return self._str_cache


def call(command, *args, **kwargs):
    """
    Run the runcrons management command with a supressed output.
    """
    out_buffer = OutBuffer()
    call_command(command, *args, stdout=out_buffer, **kwargs)
    return out_buffer.str_content()


class TestRunCrons(TransactionTestCase):
    success_cron = 'test_crons.TestSuccessCronJob'
    error_cron = 'test_crons.TestErrorCronJob'
    five_mins_cron = 'test_crons.Test5minsCronJob'
    run_at_times_cron = 'test_crons.TestRunAtTimesCronJob'
    wait_3sec_cron = 'test_crons.Wait3secCronJob'
    run_on_wkend_cron = 'test_crons.RunOnWeekendCronJob'
    does_not_exist_cron = 'ThisCronObviouslyDoesntExist'
    no_code_cron = 'test_crons.NoCodeCronJob'
    test_failed_runs_notification_cron = (
        'django_cron.cron.FailedRunsNotificationCronJob'
    )
    run_on_month_days = 'test_crons.RunOnMonthDaysCronJob'

    def _call(self, *args, **kwargs):
        return call('runcrons', *args, **kwargs)

    def setUp(self):
        CronJobLog.objects.all().delete()

    def assertReportedRun(self, job_cls, response):
        expected_log = u"[\N{HEAVY CHECK MARK}] {0}".format(job_cls.code)
        self.assertIn(expected_log, response)

    def assertReportedNoRun(self, job_cls, response):
        expected_log = u"[ ] {0}".format(job_cls.code)
        self.assertIn(expected_log, response)

    def assertReportedFail(self, job_cls, response):
        expected_log = u"[\N{HEAVY BALLOT X}] {0}".format(job_cls.code)
        self.assertIn(expected_log, response)

    def test_success_cron(self):
        logs_count = CronJobLog.objects.all().count()
        self._call(self.success_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_failed_cron(self):
        logs_count = CronJobLog.objects.all().count()
        response = self._call(self.error_cron, force=True)
        self.assertReportedFail(test_crons.TestErrorCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    def test_not_exists_cron(self):
        logs_count = CronJobLog.objects.all().count()
        response = self._call(self.does_not_exist_cron, force=True)
        self.assertIn('Make sure these are valid cron class names', response)
        self.assertIn(self.does_not_exist_cron, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count)

    @patch('django_cron.logger')
    def test_requires_code(self, mock_logger):
        response = self._call(self.no_code_cron, force=True)
        self.assertIn('does not have a code attribute', response)
        mock_logger.info.assert_called()

    @override_settings(
        DJANGO_CRON_LOCK_BACKEND='django_cron.backends.lock.file.FileLock'
    )
    def test_file_locking_backend(self):
        logs_count = CronJobLog.objects.all().count()
        self._call(self.success_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    @override_settings(
        DJANGO_CRON_LOCK_BACKEND='django_cron.backends.lock.database.DatabaseLock'
    )
    def test_database_locking_backend(self):
        # TODO: to test it properly we would need to run multiple jobs at the same time
        logs_count = CronJobLog.objects.all().count()
        cron_job_locks = CronJobLock.objects.all().count()
        for _ in range(3):
            self._call(self.success_cron, force=True)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 3)
        self.assertEqual(CronJobLock.objects.all().count(), cron_job_locks + 1)
        self.assertEqual(CronJobLock.objects.first().locked, False)

    @patch.object(test_crons.TestSuccessCronJob, 'do')
    def test_dry_run_does_not_perform_task(self, mock_do):
        response = self._call(self.success_cron, dry_run=True)
        self.assertReportedRun(test_crons.TestSuccessCronJob, response)
        mock_do.assert_not_called()
        self.assertFalse(CronJobLog.objects.exists())

    @patch.object(test_crons.TestSuccessCronJob, 'do')
    def test_non_dry_run_performs_task(self, mock_do):
        mock_do.return_value = 'message'
        response = self._call(self.success_cron)
        self.assertReportedRun(test_crons.TestSuccessCronJob, response)
        mock_do.assert_called_once()
        self.assertEqual(1, CronJobLog.objects.count())
        log = CronJobLog.objects.get()
        self.assertEqual(
            'message', log.message.strip()
        )  # CronJobManager adds new line at the end of each message
        self.assertTrue(log.is_success)

    def test_runs_every_mins(self):
        logs_count = CronJobLog.objects.all().count()

        with freeze_time("2014-01-01 00:00:00"):
            response = self._call(self.five_mins_cron)
        self.assertReportedRun(test_crons.Test5minsCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:04:59"):
            response = self._call(self.five_mins_cron)
        self.assertReportedNoRun(test_crons.Test5minsCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:05:01"):
            response = self._call(self.five_mins_cron)
        self.assertReportedRun(test_crons.Test5minsCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 2)

    def test_runs_at_time(self):
        logs_count = CronJobLog.objects.all().count()
        with freeze_time("2014-01-01 00:00:01"):
            response = self._call(self.run_at_times_cron)
        self.assertReportedRun(test_crons.TestRunAtTimesCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:04:50"):
            response = self._call(self.run_at_times_cron)
        self.assertReportedNoRun(test_crons.TestRunAtTimesCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        with freeze_time("2014-01-01 00:05:01"):
            response = self._call(self.run_at_times_cron)
        self.assertReportedRun(test_crons.TestRunAtTimesCronJob, response)
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 2)

    def test_run_on_weekend(self):
        for test_date in ("2017-06-17", "2017-06-18"):  # Saturday and Sunday
            logs_count = CronJobLog.objects.all().count()
            with freeze_time(test_date):
                call_command('runcrons', self.run_on_wkend_cron)
            self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        for test_date in (
            "2017-06-19",
            "2017-06-20",
            "2017-06-21",
            "2017-06-22",
            "2017-06-23",
        ):  # Mon-Fri
            logs_count = CronJobLog.objects.all().count()
            with freeze_time(test_date):
                call_command('runcrons', self.run_on_wkend_cron)
            self.assertEqual(CronJobLog.objects.all().count(), logs_count)

    def test_run_on_month_days(self):
        for test_date in ("2010-10-1", "2010-10-10", "2010-10-20"):
            logs_count = CronJobLog.objects.all().count()
            with freeze_time(test_date):
                call_command('runcrons', self.run_on_month_days)
            self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

        for test_date in (
            "2010-10-2",
            "2010-10-9",
            "2010-10-11",
            "2010-10-19",
            "2010-10-21",
        ):
            logs_count = CronJobLog.objects.all().count()
            with freeze_time(test_date):
                call_command('runcrons', self.run_on_month_days)
            self.assertEqual(CronJobLog.objects.all().count(), logs_count)

    def test_silent_produces_no_output_success(self):
        response = self._call(self.success_cron, silent=True)
        self.assertEqual(1, CronJobLog.objects.count())
        self.assertEqual('', response)

    def test_silent_produces_no_output_no_run(self):
        with freeze_time("2014-01-01 00:00:00"):
            response = self._call(self.run_at_times_cron, silent=True)
        self.assertEqual(1, CronJobLog.objects.count())
        self.assertEqual('', response)

        with freeze_time("2014-01-01 00:00:01"):
            response = self._call(self.run_at_times_cron, silent=True)
        self.assertEqual(1, CronJobLog.objects.count())
        self.assertEqual('', response)

    def test_silent_produces_no_output_failure(self):
        response = self._call(self.error_cron, silent=True)
        self.assertEqual('', response)

    def test_admin(self):
        password = 'test'
        user = User.objects.create_superuser('test', 'test@tivix.com', password)
        self.client = Client()
        self.client.login(username=user.username, password=password)

        # edit CronJobLog object
        self._call(self.success_cron, force=True)
        log = CronJobLog.objects.all()[0]
        url = reverse('admin:django_cron_cronjoblog_change', args=(log.id,))
        response = self.client.get(url)
        self.assertIn('Cron job logs', str(response.content))

    def run_cronjob_in_thread(self, logs_count):
        self._call(self.wait_3sec_cron)
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
        self._call(self.wait_3sec_cron)
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
    #     self._call(self.wait_3sec_cron)
    #     t.join(10)
    #     self.assertEqual(CronJobLog.objects.all().count(), logs_count + 1)

    @skip  # TODO check why the test is failing
    def test_failed_runs_notification(self):
        CronJobLog.objects.all().delete()
        logs_count = CronJobLog.objects.all().count()

        for i in range(10):
            self._call(self.error_cron, force=True)
        self._call(self.test_failed_runs_notification_cron)

        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 11)

    def test_humanize_duration(self):
        test_subjects = (
            (
                timedelta(days=1, hours=1, minutes=1, seconds=1),
                '1 day, 1 hour, 1 minute, 1 second',
            ),
            (timedelta(days=2), '2 days'),
            (timedelta(days=15, minutes=4), '15 days, 4 minutes'),
            (timedelta(), '< 1 second'),
        )

        for duration, humanized in test_subjects:
            self.assertEqual(humanize_duration(duration), humanized)


class TestCronLoop(TransactionTestCase):
    success_cron = 'test_crons.TestSuccessCronJob'

    def _call(self, *args, **kwargs):
        return call('cronloop', *args, **kwargs)

    def setUp(self):
        CronJobLog.objects.all().delete()

    def test_repeat_twice(self):
        logs_count = CronJobLog.objects.all().count()
        self._call(
            cron_classes=[self.success_cron, self.success_cron], repeat=2, sleep=1
        )
        self.assertEqual(CronJobLog.objects.all().count(), logs_count + 4)
