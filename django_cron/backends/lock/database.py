from django.db import transaction

from django_cron.models import CronJobLock

from .base import DjangoCronJobLock


class DatabaseLock(DjangoCronJobLock):
    """
    Locking cron jobs with database. Its good when you have not parallel run and want to make sure 2 jobs won't be
    fired at the same time - which may happened when job execution is longer that job interval.
    """

    @transaction.atomic
    def lock(self) -> bool:
        lock, _ = CronJobLock.objects.get_or_create(job_name=self.job_name)
        if lock.locked:
            return False

        lock.locked = True
        lock.save(update_fields=["locked"])
        return True

    @transaction.atomic
    def release(self):
        lock = CronJobLock.objects.filter(job_name=self.job_name, locked=True)[0]
        lock.locked = False
        lock.save(update_fields=["locked"])
