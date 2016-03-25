from django_cron.backends.lock.base import DjangoCronJobLock

from django.conf import settings
from django.core.files import locks
import os


class FileLock(DjangoCronJobLock):
    """
    Quite a simple lock backend that uses kernel based locking
    """

    def lock(self):
        lock_name = self.get_lock_name()
        try:
            f = open(lock_name, 'w+', 0)
            locks.lock(f, locks.LOCK_EX | locks.LOCK_NB)
        except IOError:
            return False
        return True
        # TODO: perhaps on windows I need to catch different exception type

    def release(self):
        lock_name = self.get_lock_name()
        f = open(lock_name, 'w+', 0)
        locks.lock(f, locks.LOCK_UN)
        f.close()

    def get_lock_name(self):
        default_path = '/tmp'
        path = getattr(settings, 'DJANGO_CRON_LOCKFILE_PATH', default_path)
        if not os.path.isdir(path):
            # let it die if failed, can't run further anyway
            os.makedirs(path)

        filename = self.job_name + '.lock'
        return os.path.join(path, filename)
