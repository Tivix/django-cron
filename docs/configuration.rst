Configuration
=============

**CRON_CLASSES** - list of cron classes

**DJANGO_CRON_LOCK_BACKEND** - path to lock class, default: ``django_cron.backends.lock.cache.CacheLock``

**DJANGO_CRON_LOCKFILE_PATH** - path where to store files for FileLock, default: ``/tmp``

**DJANGO_CRON_LOCK_TIME** - timeout value for CacheLock backend, default: ``24 * 60 * 60  # 24 hours``

**DJANGO_CRON_CACHE** - cache name used in CacheLock backend, default: ``default``


For more details, see :doc:`Sample Cron Configurations <sample_cron_configurations>` and :doc:`Locking backend <locking_backend>`
