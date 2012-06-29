from datetime import datetime

from django.db import models


class CronJobLog(models.Model):
    """
    Keeps track of the cron jobs that ran etc. and any error messages if they failed.
    """
    code = models.CharField(max_length=64, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    is_success = models.BooleanField(default=False)
    message = models.TextField(max_length=1000, blank=True)  # TODO: db_index=True, 

    def __unicode__(self):
        return '%s (%s)' % (self.code, 'Success' if self.is_success else 'Fail')
