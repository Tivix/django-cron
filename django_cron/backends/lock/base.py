class DjangCronJobLock(object):
    """
    The lock class to use in runcrons management command.
    Intendent usage is
    with CacheLock(cron_class, allow_parallel_runs, silent) as lock:
        if lock.success:
            do work
    """
    def __init__(self, cron_class, silent, *args, **kwargs):
        """
        This method inits the class.
        You should take care of getting all
        nessesary thing from input parameters here
        Base class processes
            * self.job_name
            * self.job_code
            * self.parallel
            * self.silent
        for you. The rest is backend-specific.
        """
        self.job_name  = cron_class.__name__
        self.job_code  = cron_class.code
        self.parallel  = getattr(cron_class, 'ALLOW_PARALLEL_RUNS', False)
        self.silent    = silent

    def lock(self):
        """
        This method called to acquire lock. Typically. it will
        be called from __enter__ method.
        Return True is success,
        False if fail.
        Here you can optionally call self.notice_lock_failed().
        """
        raise NotImplementedError('You have to implement lock(self) method for your class')

    def release(self):
        """
        This method called to release lock.
        Tipically called from __exit__ method.
        No need to return anything currently.
        """
        raise NotImplementedError('You have to implement release(self) method for your class')

    def notice_lock_failed(self):
        if self.silent:
            return
        print "%s: lock found. Will try later." % self.job_name

    """
    Status of acquiring lock:
    True  means ok, lock acquired successfully
    False means lock failed
    """
    success   = None

    def __enter__(self):
        if self.parallel:
            # Skip real lock
            self.success = True
        else:
            self.success = self.lock()
        return self

    def __exit__(self, type, value, traceback):
        if self.success and not self.parallel:
            self.release()
