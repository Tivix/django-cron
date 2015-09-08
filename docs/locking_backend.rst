Locking Backend
===============

You can use one of two built-in locking backends by setting ``DJANGO_CRON_LOCK_BACKEND`` with one of:

    - ``django_cron.backends.lock.cache.CacheLock`` (default)
    - ``django_cron.backends.lock.file.FileLock``


Cache Lock
----------
This backend sets a cache variable to mark current job as "already running", and delete it when lock is released.


File Lock
---------
This backend creates a file to mark current job as "already running", and delete it when lock is released.


Custom Lock
-----------
You can also write your custom backend as a subclass of ``django_cron.backends.lock.base.DjangoCronJobLock`` and defining ``lock()`` and ``release()`` methods.
