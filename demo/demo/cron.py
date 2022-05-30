from django.conf import settings
from django.contrib.auth.models import User

from django_common.helper import send_mail
from django_cron import CronJobBase, Schedule


class EmailUsercountCronJob(CronJobBase):
    """
    Send an email with the user count.
    """
    RUN_EVERY_MINS = 0 if settings.DEBUG else 360   # 6 hours when not DEBUG

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.EmailUsercountCronJob'

    def do(self):
        message = 'Active users: %d' % User.objects.count()
        print(message)
        send_mail(
            '[django-cron demo] Active user count',
            message,
            'no-reply@django-cron-demo.com',
            ['test@django-cron-demo.com']
        )
