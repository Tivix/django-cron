import logging
from datetime import timedelta, datetime
import traceback
import time

from django_cron.models import CronJobLog

try:
    from django.utils import timezone
except ImportError:
    # timezone added in Django 1.4
    import timezone


class Schedule(object):
    def __init__(self, run_every_mins=None, run_at_times=[], retry_after_failure_mins=None):
        self.run_every_mins = run_every_mins
        self.run_at_times = run_at_times
        self.retry_after_failure_mins = retry_after_failure_mins


class CronJobBase(object):
    """
    Sub-classes should have the following properties:
    + code - This should be a code specific to the cron being run. Eg. 'general.stats' etc.
    + schedule

    Following functions:
    + do - This is the actual business logic to be run at the given schedule
    """
    pass


class CronJobManager(object):
    """
    A manager instance should be created per cron job to be run. Does all the logging tracking etc. for it.
    """

    @classmethod
    def __should_run_now(self, cron_job, force=False):
        """
        Returns a boolean determining whether this cron should run now or not!
        """
        # If we pass --force options, we force cron run
        self.user_time = None
        if force:
            return True
        if cron_job.schedule.run_every_mins != None:

            # We check last job - success or not
            last_job = None
            try:
                last_job = CronJobLog.objects.filter(code=cron_job.code).latest('start_time')
            except CronJobLog.DoesNotExist:
                pass
            if last_job:
                if not last_job.is_success and cron_job.schedule.retry_after_failure_mins:
                    if timezone.now() > last_job.start_time + timedelta(minutes=cron_job.schedule.retry_after_failure_mins):
                        return True
                    else:
                        return False

            previously_ran_successful_cron = None
            try:
                previously_ran_successful_cron = CronJobLog.objects.filter(code=cron_job.code, is_success=True, ran_at_time__isnull=True).latest('start_time')
            except CronJobLog.DoesNotExist:
                pass
            if previously_ran_successful_cron:
                if timezone.now() > previously_ran_successful_cron.start_time + timedelta(minutes=cron_job.schedule.run_every_mins):
                    return True
            else:
                return True
        if cron_job.schedule.run_at_times:
            for time_data in cron_job.schedule.run_at_times:
                user_time = time.strptime(time_data, "%H:%M")
                actual_time = time.strptime("%s:%s" % (datetime.now().hour, datetime.now().minute), "%H:%M")
                if actual_time >= user_time:
                    qset = CronJobLog.objects.filter(code=cron_job.code, start_time__gt=datetime.today().date(), ran_at_time=time_data)
                    if not qset:
                        self.user_time = time_data
                        return True
        return False

    @classmethod
    def run(self, cron_job, force=False, silent=False):
        """
        apply the logic of the schedule and call do() on the CronJobBase class
        """
        if not isinstance(cron_job, CronJobBase):
            raise Exception('The cron_job to be run should be a subclass of %s' % CronJobBase.__class__)
        if CronJobManager.__should_run_now(cron_job, force):
            logging.debug("Running cron: %s" % cron_job)
            cron_log = CronJobLog(code=cron_job.code, start_time=timezone.now())
            try:
                msg = cron_job.do()
                cron_log.is_success = True
                cron_log.message = msg or ''
            except Exception:
                error = traceback.format_exc()
                if not silent:
                    print(error)
                cron_log.is_success = False
                cron_log.message = error[-1000:]
            cron_log.ran_at_time = self.user_time if self.user_time else None
            cron_log.end_time = timezone.now()
            cron_log.save()
