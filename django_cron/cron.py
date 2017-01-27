from django.conf import settings
from django_cron import CronJobBase, Schedule, get_class
from django_cron.models import CronJobLog

from django_common.helper import send_mail


class FailedRunsNotificationCronJob(CronJobBase):
    """
    A regular job to send email reports for failed Cron jobs.

    The job log is used to check for all unreported failures for each job
    class specified within the CRON_CLASSES dictionary. When the number of
    failures for each job type exceeds the limit (which can be specified
    either per-job or project wide) an email is sent to all relevant parties
    detailing the error.
    """
    code = 'django_cron.FailedRunsNotificationCronJob'

    def __init__(self, *args, **kwargs):
        super(FailedRunsNotificationCronJob, self).__init__(*args, **kwargs)
        self.config = self.get_config()
        self.schedule = Schedule(run_every_mins=self.config['RUN_EVERY_MINS'])

    def do(self):
        """
        Check all Cron jobs defined in CRON_CLASSES for failed runs.
        """
        cron_classes = [
            get_class(class_name) for class_name in settings.CRON_CLASSES
        ]

        for cron_class in cron_classes:
            # The FailedRuns Cron job should ignore itself
            if isinstance(self, cron_class):
                continue

            self.check_for_failures(cron_class)

    def get_config(self):
        """
        Combine the default configuration with any project-specific ones.
        """
        config = dict(
            RUN_EVERY_MINS=0,
            EMAIL_PREFIX='[Cron Failure] - ',
            MIN_NUM_FAILURES=10,
            FROM_EMAIL=settings.DEFAULT_FROM_EMAIL,
            EMAIL_RECIPIENTS=[email for _, email in settings.ADMINS]
        )
        config.update(getattr(settings, 'CRON_FAILURE_REPORT', {}))
        return config

    def check_for_failures(self, cron_cls):
        """
        Check the given Cron task for failed jobs, and report if required.
        """
        min_failures = getattr(
            cron_cls, 'MIN_NUM_FAILURES', self.config['MIN_NUM_FAILURES']
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
            prefix=self.config['EMAIL_PREFIX'],
            code=cron_cls.code
        )

        if len(failed_reports) > 1:
            subject = "{subject} {times} times".format(
                subject=subject, times=len(failed_reports)
            )

        return dict(
            subject=subject, message=message,
            from_email=self.config['FROM_EMAIL'],
            recipient_emails=self.config['EMAIL_RECIPIENTS']
        )
