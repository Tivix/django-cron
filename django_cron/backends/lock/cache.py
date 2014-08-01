from base import DjangCronJobLock
from django.conf import settings

import warnings

try:
    from django.core.cache import caches
except ImportError:
    # `caches` added in 1.7
    from django.core.cache import get_cache

try:
    from django.utils import timezone
except ImportError:
    # timezone added in Django 1.4
    from django_cron import timezone


class CacheLock(DjangCronJobLock):
    """
    One of simpliest lock backends, uses django cache to
    prevent parallel runs of commands.
    """
    DEFAULT_LOCK_TIME = 24 * 60 * 60  # 24 hours
    def __init__(self, cron_class, *args, **kwargs):
        super(CacheLock, self).__init__(cron_class, *args, **kwargs)

        self.cache     = self.get_cache_by_name()
        self.lock_name = self.get_lock_name()
        self.timeout   = self.get_cache_timeout(cron_class)

    def lock(self):
        """
        This method sets a cache variable to mark current job as "already running".
        """
        if self.cache.get(self.lock_name):
            self.notice_lock_failed()
            return False
        else:
            self.cache.set(self.lock_name, timezone.now(), self.timeout)
            return True

    def release(self):
        self.cache.delete(self.lock_name)

    def notice_lock_failed(self):
        if self.silent:
            return

        started = self.get_running_lock_date()
        print "%s: lock has been found. Other cron started at %s" % \
            (self.job_name, started)
        print "Current timeout for job %s is %s seconds (cache key name is '%s')." % \
            (self.job_name, self.timeout, self.lock_name)

    def get_cache_by_name(self):
        '''
        Gets a specified cache (or the `default` cache if CRON_CACHE is not set)
        '''
        cache_name = getattr(settings, 'CRON_CACHE', 'default')

        # Allow the possible InvalidCacheBackendError to happen here
        # instead of allowing unexpected parallel runs of cron jobs
        try:
            # Django >= 1.7.*
            return caches[cache_name]
        except NameError:
            # Django <= 1.6.*
            return get_cache(cache_name)

    def get_lock_name(self):
        return self.job_name

    def get_cache_timeout(self, cron_class):
        timeout = self.DEFAULT_LOCK_TIME
        try:
            timeout = getattr(cron_class, 'DJANGO_CRON_LOCK_TIME', settings.DJANGO_CRON_LOCK_TIME)
        except:
            pass
        return timeout

    def get_running_lock_date(self):
        return timezone.make_aware(self.cache.get(self.lock_name), timezone.get_current_timezone())
