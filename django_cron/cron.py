from django.conf import settings
from django_cron import CronJobBase, Schedule, get_class
from django_cron.models import CronJobLog

from django_common.helper import send_mail


class FailedRunsNotificationCronJob(CronJobBase):
    """
    A regular job to send email reports for failed Cron jobs.

    The job log is used to check for all unreported failures for each job
    classes specified within the CRON_CLASSES dictionary. When the number of
    failures for each job type exceeds the limit (which can be specified
    either per-job or project wide) an email is sent to all relevant parties
    detailing the error.
    """
    RUN_EVERY_MINS = 0

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'django_cron.FailedRunsNotificationCronJob'

    def do(self):
        self.config = self.get_config()
        cron_classes = [get_class(c_name) for c_name in settings.CRON_CLASSES]
        cron_classes = [c for c in cron_classes if not isinstance(self, c)]

        for cron_cls in cron_classes:
            self.check_for_failures(cron_cls)

    def get_config(self):
        """
        Combine the default configuration with any project-specific ones.
        """
        defaults = dict(
            FAILED_RUNS_CRONJOB_EMAIL_PREFIX='[Cron Failure] - ',
            CRON_MIN_NUM_FAILURES=10,
            CRON_FAILURE_FROM_EMAIL=settings.DEFAULT_FROM_EMAIL,
            CRON_FAILURE_EMAIL_RECIPIENTS=[
                email for _, email in settings.ADMINS
            ]
        )
        return {
            key: getattr(settings, key, defaults[key])
            for key in defaults
        }

    def check_for_failures(self, cron_cls):
        """
        Check the given Cron task for failed jobs, and report if required.
        """
        min_failures = getattr(
            cron_cls, 'MIN_NUM_FAILURES', self.config['CRON_MIN_NUM_FAILURES']
        )

        failed_jobs = CronJobLog.objects.filter(
            code=cron_cls.code, is_success=False, failure_reported=False
        )

        if failed_jobs.count() < min_failures:
            return

        self.report_failure(cron_cls, failed_jobs)
        failed_jobs.update(failure_reported=True)

    def report_failure(self, cron_cls, failed_jobs):
        """
        Report the failed jobs by sending an email (using django-common).
        """
        send_mail(**self.get_send_mail_kwargs(cron_cls, failed_jobs))

    def get_send_mail_kwargs(self, cron_cls, failed_jobs):
        """
        Return the arguments to pass to send_mail for the given failed jobs.
        """
        failed_reports = []

        for job in failed_jobs:
            failed_reports.append(
                u"Job ran at {start_time}:\n{message}"
                .format(start_time=job.start_time, message=job.message)
            )

        divider = "\n\n{0}\n\n".format("=" * 80)
        message = divider.join(failed_reports)
        subject = "{prefix}{code} failed".format(
            prefix=self.config['FAILED_RUNS_CRONJOB_EMAIL_PREFIX'],
            code=cron_cls.code
        )

        if len(failed_reports) > 1:
            subject = "{subject} {times} times".format(
                subject=subject, times=len(failed_reports)
            )

        return dict(
            subject=subject, message=message,
            from_email=self.config['CRON_FAILURE_FROM_EMAIL'],
            recipient_emails=self.config['CRON_FAILURE_EMAIL_RECIPIENTS']
        )
