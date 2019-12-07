import logging
from datetime import timedelta, datetime
import traceback
import time

from django.conf import settings
from django.utils.timezone import now as utc_now, localtime, is_naive
from django.db.models import Q


DEFAULT_LOCK_BACKEND = 'django_cron.backends.lock.cache.CacheLock'
logger = logging.getLogger('django_cron')


def get_class(kls):
    """
    TODO: move to django-common app.
    Converts a string to a class.
    Courtesy: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname/452981#452981
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_current_time():
    now = utc_now()
    return now if is_naive(now) else localtime(now)


def validate_dates_index(validator, index):
    """
    :param validator: list format: [1, 0, 0, 1, 0, 0, 1, ...] or cron format: '*/3' , '5,15,25', '1-5'
    :param index: integer index that starts from 0.
    :return: a boolean that validate that index matches with validator.
    """
    if isinstance(validator, list):
        # Ex: [1, 1, 0, 0, 1, ...]
        return bool(validator[index])
    elif '*' in validator:
        # Ex: '*', '*/3', '*/5'
        return bool(eval(validator.replace('*', str(index))) % 1 == 0)
    elif '-' in validator:
        # Ex: '1-5'
        start, end = [int(i) for i in validator.split('-')]
        return start <= index <= end
    else:
        # Ex: '5,15,25'
        valid_indexes = [int(vi) for vi in validator.split(',')]
        return bool(index in valid_indexes)


class Schedule(object):
    def __init__(self, run_every_mins=None, run_at_times=None, retry_after_failure_mins=None,
                 day_of_month='*',  # cron format: '*/3' '5,15,25' or list: [1] * 31
                 month_numbers='*',  # cron format: '*/3' '5,15,25' or list: [1] * 12
                 day_of_week='*',  # cron format: '*/3' '5,15,25' or list: [1] * 7
                 ):
        if run_at_times is None:
            run_at_times = []
        self.run_every_mins = run_every_mins
        self.run_at_times = run_at_times
        self.retry_after_failure_mins = retry_after_failure_mins
        self.day_of_month = day_of_month
        self.month_numbers = month_numbers
        self.day_of_week = day_of_week


class CronJobBase(object):
    """
    Sub-classes should have the following properties:
    + code - This should be a code specific to the cron being run. Eg. 'general.stats' etc.
    + schedule

    Following functions:
    + do - This is the actual business logic to be run at the given schedule
    """
    def __init__(self):
        self.prev_success_cron = None

    def set_prev_success_cron(self, prev_success_cron):
        self.prev_success_cron = prev_success_cron

    def get_prev_success_cron(self):
        return self.prev_success_cron

    @classmethod
    def get_time_until_run(cls):
        from django_cron.models import CronJobLog
        try:
            last_job = CronJobLog.objects.filter(
                code=cls.code).latest('start_time')
        except CronJobLog.DoesNotExist:
            return timedelta()
        return (last_job.start_time +
                timedelta(minutes=cls.schedule.run_every_mins) - utc_now())


class CronJobManager(object):
    """
    A manager instance should be created per cron job to be run.
    Does all the logger tracking etc. for it.
    Used as a context manager via 'with' statement to ensure
    proper logger in cases of job failure.
    """

    def __init__(self, cron_job_class, silent=False, *args, **kwargs):
        super(CronJobManager, self).__init__(*args, **kwargs)

        self.cron_job_class = cron_job_class
        self.silent = silent
        self.lock_class = self.get_lock_class()
        self.previously_ran_successful_cron = None

    def should_run_today(self):
        """
        :return: a boolean determining whether this cron should run today or not.
        """
        cron_job = self.cron_job
        now = get_current_time()
        today = now.date()
        today_month_day_index = today.day - 1
        today_month_index = today.month - 1
        today_week_day_index = today.weekday()

        result = validate_dates_index(cron_job.schedule.month_numbers, today_month_index) and\
            validate_dates_index(cron_job.schedule.day_of_month, today_month_day_index) and\
            validate_dates_index(cron_job.schedule.day_of_week, today_week_day_index)

        return result

    def should_run_now(self, force=False):
        from django_cron.models import CronJobLog
        cron_job = self.cron_job
        """
        Returns a boolean determining whether this cron should run now or not!
        """

        self.user_time = None
        self.previously_ran_successful_cron = None

        # If we pass --force options, we force cron run
        if force:
            return True

        if not self.should_run_today():
            return False

        if cron_job.schedule.run_every_mins is not None:

            # We check last job - success or not
            last_job = None
            try:
                last_job = CronJobLog.objects.filter(code=cron_job.code).latest('start_time')
            except CronJobLog.DoesNotExist:
                pass
            if last_job:
                if not last_job.is_success and cron_job.schedule.retry_after_failure_mins:
                    if get_current_time() > last_job.start_time + timedelta(minutes=cron_job.schedule.retry_after_failure_mins):
                        return True
                    else:
                        return False

            try:
                self.previously_ran_successful_cron = CronJobLog.objects.filter(
                    code=cron_job.code,
                    is_success=True,
                    ran_at_time__isnull=True
                ).latest('start_time')
            except CronJobLog.DoesNotExist:
                pass

            if self.previously_ran_successful_cron:
                if get_current_time() > self.previously_ran_successful_cron.start_time + timedelta(minutes=cron_job.schedule.run_every_mins):
                    return True
            else:
                return True

        if cron_job.schedule.run_at_times:
            for time_data in cron_job.schedule.run_at_times:
                user_time = time.strptime(time_data, "%H:%M")
                now = get_current_time()
                actual_time = time.strptime("%s:%s" % (now.hour, now.minute), "%H:%M")
                if actual_time >= user_time:
                    qset = CronJobLog.objects.filter(
                        code=cron_job.code,
                        ran_at_time=time_data,
                        is_success=True
                    ).filter(
                        Q(start_time__gt=now) | Q(end_time__gte=now.replace(hour=0, minute=0, second=0, microsecond=0))
                    )
                    if not qset:
                        self.user_time = time_data
                        return True

        return False

    def get_run_times_in_future(self, from_datetime, to_datetime):
        from django_cron.models import CronJobLog
        cron_job = self.cron_job

        # ignore previous times
        from_datetime = max(from_datetime, get_current_time())
        if to_datetime < from_datetime:
            return []

        future_run_datetimes = []
        if cron_job.schedule.run_at_times:
            run_at_times = cron_job.schedule.run_at_times
            # Convert time strings to time
            run_at_times_ptime = []
            for run_time_string in run_at_times:
                run_time = time.strptime(run_time_string, "%H:%M")
                run_at_times_ptime.append(run_time)

            # append start day times
            from_date = from_datetime.date()
            for run_time in run_at_times_ptime:
                run_datetime = datetime(from_date.year, from_date.month, from_date.day, run_time.tm_hour, run_time.tm_min)
                if run_datetime >= from_datetime:
                    future_run_datetimes.append(run_datetime)

            # append middle times
            mid_date = from_datetime + timedelta(days=1)
            while mid_date < to_datetime:
                for run_time in run_at_times_ptime:
                    run_datetime = datetime(from_date.year, from_date.month, from_date.day, run_time.tm_hour, run_time.tm_min)
                    future_run_datetimes.append(run_datetime)

            # append last day times
            to_date = to_datetime.date()
            for run_time in run_at_times_ptime:
                run_datetime = datetime(to_date.year, to_date.month, to_date.day, run_time.tm_hour, run_time.tm_min)
                if run_datetime <= to_datetime:
                    future_run_datetimes.append(run_datetime)
        else:
            pass  # Todo: run_every_mins

        return future_run_datetimes

    def make_log(self, *messages, **kwargs):
        cron_log = self.cron_log

        cron_job = getattr(self, 'cron_job', self.cron_job_class)
        cron_log.code = cron_job.code

        cron_log.is_success = kwargs.get('success', True)
        cron_log.message = self.make_log_msg(*messages)
        cron_log.ran_at_time = getattr(self, 'user_time', None)
        cron_log.end_time = get_current_time()
        cron_log.save()

    def make_log_msg(self, msg, *other_messages):
        MAX_MESSAGE_LENGTH = 1000
        if not other_messages:
            # assume that msg is a single string
            return msg[-MAX_MESSAGE_LENGTH:]
        else:
            if len(msg):
                msg += "\n...\n"
                NEXT_MESSAGE_OFFSET = MAX_MESSAGE_LENGTH - len(msg)
            else:
                NEXT_MESSAGE_OFFSET = MAX_MESSAGE_LENGTH

            if NEXT_MESSAGE_OFFSET > 0:
                msg += other_messages[0][-NEXT_MESSAGE_OFFSET:]
                return self.make_log_msg(msg, *other_messages[1:])
            else:
                return self.make_log_msg(msg)

    def __enter__(self):
        from django_cron.models import CronJobLog
        self.cron_log = CronJobLog(start_time=get_current_time())

        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type == self.lock_class.LockFailedException:
            if not self.silent:
                logger.info(ex_value)

        elif ex_type is not None:
            try:
                trace = "".join(traceback.format_exception(ex_type, ex_value, ex_traceback))
                self.make_log(self.msg, trace, success=False)
            except Exception as e:
                err_msg = "Error saving cronjob log message: %s" % e
                logger.error(err_msg)

        return True  # prevent exception propagation

    def run(self, force=False):
        """
        apply the logic of the schedule and call do() on the CronJobBase class
        """
        cron_job_class = self.cron_job_class
        if not issubclass(cron_job_class, CronJobBase):
            raise Exception('The cron_job to be run must be a subclass of %s' % CronJobBase.__name__)

        with self.lock_class(cron_job_class, self.silent):
            self.cron_job = cron_job_class()

            if self.should_run_now(force):
                logger.debug("Running cron: %s code %s", cron_job_class.__name__, self.cron_job.code)
                self.msg = self.cron_job.do()
                self.make_log(self.msg, success=True)
                self.cron_job.set_prev_success_cron(self.previously_ran_successful_cron)

    def get_lock_class(self):
        name = getattr(settings, 'DJANGO_CRON_LOCK_BACKEND', DEFAULT_LOCK_BACKEND)
        try:
            return get_class(name)
        except Exception as err:
            raise Exception("invalid lock module %s. Can't use it: %s." % (name, err))

    @property
    def msg(self):
        return getattr(self, '_msg', '')

    @msg.setter
    def msg(self, msg):
        if msg is None:
            msg = ''
        self._msg = msg
