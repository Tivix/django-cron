Locking Backend
===============

You can use one of three built-in locking backends by setting ``DJANGO_CRON_LOCK_BACKEND`` with one of:

    - ``django_cron.backends.lock.cache.CacheLock`` (default)
    - ``django_cron.backends.lock.file.FileLock``
    - ``django_cron.backends.lock.database.DatabaseLock``


Cache Lock
----------
This backend sets a cache variable to mark current job as "already running", and delete it when lock is released.


File Lock
---------
This backend creates a file to mark current job as "already running", and delete it when lock is released.

Database Lock
---------
This backend creates new model for jobs, saving their state as locked when they starts, and setting it to unlocked when
job is finished. It may help preventing multiple instances of the same job running.

Custom Lock
-----------
You can also write your custom backend as a subclass of ``django_cron.backends.lock.base.DjangoCronJobLock`` and defining ``lock()`` and ``release()`` methods.
