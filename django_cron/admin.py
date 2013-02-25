from django.contrib import admin

from django_cron.models import CronJobLog


class CronJobLogAdmin(admin.ModelAdmin):
    class Meta:
        model = CronJobLog

    search_fields = ('code', 'message')
    ordering = ('-start_time',)
    list_display = ('code', 'start_time', 'end_time', 'is_success')
    list_filter = ('code', 'start_time', 'is_success')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj is not None:
            names = [f.name for f in CronJobLog._meta.fields if f.name != 'id']
            return self.readonly_fields + tuple(names)
        return self.readonly_fields


admin.site.register(CronJobLog, CronJobLogAdmin)
