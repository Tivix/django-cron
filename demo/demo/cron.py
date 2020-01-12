from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
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


class EmailUsercountCronJob2(CronJobBase):
    """
    Send an email with the user count.
    """
    RUN_AT_TIMES = ['10:10', '22:10']

    schedule = Schedule(run_at_times=RUN_AT_TIMES, day_of_week='2')
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


class TestCronJob(CronJobBase):
    RUN_AT_TIMES = ['10:10', '22:10']
    schedule = Schedule(
        run_at_times=RUN_AT_TIMES,
        # day_of_week='*/2',
    )

    code = 'demo.TestCronJob'

    def do(self):
        print('do TestCronJob')
        return f'do TestCronJob at {datetime.now()}'

    def should_run_now(self, force=False):
        print('override should_run_now in cron job')
        '''
        if some_conditions_to_avoid_run_job:
            return False
        '''
        return super(TestCronJob, self).should_run_now(force=force)
