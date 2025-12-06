from django.db import models


class CronJobLog(models.Model):
    """
    Keeps track of the cron jobs that ran etc. and any error
    messages if they failed.
    """

    id: int

    code = models.CharField(max_length=64)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_success = models.BooleanField(default=False)
    message = models.TextField(default="", blank=True)

    # This field is used to mark jobs executed in exact time.
    # Jobs that run every X minutes, have this field empty.
    ran_at_time = models.TimeField(null=True, blank=True, editable=False)

    def __str__(self):
        status = "Success" if self.is_success else "Fail"
        return f"{self.code} ({status})"

    class Meta:
        app_label = "django_cron"
        get_latest_by = "start_time"
        indexes = (
            models.Index(fields=["code"]),
            models.Index(fields=["start_time"]),
            models.Index(fields=["end_time"]),
            models.Index(fields=["ran_at_time"]),
            models.Index(fields=["code", "start_time"]),
            models.Index(fields=["code", "start_time", "ran_at_time"]),
            models.Index(fields=["code", "is_success", "ran_at_time"]),
        )


class CronJobLock(models.Model):
    job_name = models.CharField(max_length=200, unique=True)
    locked = models.BooleanField(default=False)
