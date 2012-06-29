from django.contrib import admin

from django_cron.models import CronJobLog


class CronJobLogAdmin(admin.ModelAdmin):
    class Meta:
        model = CronJobLog
  
    search_fields = ('code', 'message')
    ordering = ('-start_time',)
    list_display = ('code', 'start_time', 'is_success')
    list_filter = ('code', 'start_time', 'is_success')

admin.site.register(CronJobLog, CronJobLogAdmin)
