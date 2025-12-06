import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import BufferedRandom

from django.conf import settings
from django.core.files import locks

from .base import DjangoCronJobLock


class FileLock(DjangoCronJobLock):
    """
    Quite a simple lock backend that uses kernel based locking
    """

    __lock_fd: "BufferedRandom | None" = None

    def lock(self):
        lock_name = self.get_lock_name()
        try:
            self.__lock_fd = open(lock_name, "w+b", 1)
            locks.lock(self.__lock_fd, locks.LOCK_EX | locks.LOCK_NB)
        except IOError:
            return False
        return True

    def release(self):
        lock = self.__lock_fd
        if lock is None:
            raise RuntimeError("cannot release an unacquired lock")

        locks.unlock(lock)
        lock.close()

    def get_lock_name(self):
        default_path = "/tmp"
        path = getattr(settings, "DJANGO_CRON_LOCKFILE_PATH", default_path)
        if not os.path.isdir(path):
            # let it die if failed, can't run further anyway
            os.makedirs(path, exist_ok=True)

        filename = self.job_name + ".lock"
        return os.path.join(path, filename)
