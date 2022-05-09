import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django_cron import CronJobBase, Schedule


class EmailUserCountCronJob(CronJobBase):
    """
    Send an email with the user count.
    """

    RUN_EVERY_MINS = 0 if settings.DEBUG else 360  # 6 hours when not DEBUG

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.EmailUserCountCronJob'

    def do(self):
        message = 'Active users: %d' % User.objects.count()
        print(message)
        send_mail(
            '[django-cron demo] Active user count',
            message,
            'no-reply@django-cron-demo.com',
            ['test@django-cron-demo.com'],
        )


class WriteDateToFileCronJob(CronJobBase):
    """
    Write current date to file.
    """

    schedule = Schedule(run_at_times=["12:20", "12:25"], retry_after_failure_mins=1)
    code = 'cron.WriteDateToFileCronJob'

    def do(self):
        message = f"Current date: {datetime.datetime.now()} \n"
        with open("cron-demo.txt", "w") as myfile:
            myfile.write(message)
