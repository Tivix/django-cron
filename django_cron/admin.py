from datetime import timedelta
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from helpers import humanize_duration
from models import CronJobLog


class DurationFilter(admin.SimpleListFilter):
    title = _('duration')
    parameter_name = 'duration'

    def lookups(self, request, model_admin):
        return (
            ('lt_minute', _('< 1 minute')),
            ('lt_hour', _('< 1 hour')),
            ('lt_day', _('< 1 day')),
            ('gte_day', _('>= 1 day')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'lt_minute':
            return queryset.extra(where=["end_time-start_time < %s"], params=[timedelta(minutes=1)])
        if self.value() == 'lt_hour':
            return queryset.extra(where=["end_time-start_time < %s"], params=[timedelta(hours=1)])
        if self.value() == 'lt_day':
            return queryset.extra(where=["end_time-start_time < %s"], params=[timedelta(days=1)])
        if self.value() == 'gte_day':
            return queryset.extra(where=["end_time-start_time >= %s"], params=[timedelta(days=1)])


class CronJobLogAdmin(admin.ModelAdmin):
    class Meta:
        model = CronJobLog

    search_fields = ('code', 'message')
    ordering = ('-start_time',)
    list_display = ('code', 'start_time', 'end_time', 'humanize_duration', 'is_success')
    list_filter = ('code', 'start_time', 'is_success', DurationFilter)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj is not None:
            names = [f.name for f in CronJobLog._meta.fields if f.name != 'id']
            return self.readonly_fields + tuple(names)
        return self.readonly_fields

    def queryset(self, request):
        qs = super(CronJobLogAdmin, self).queryset(request)
        qs = qs.extra(select={'duration': 'end_time-start_time'})
        return qs

    def humanize_duration(self, obj):
        return humanize_duration(obj.duration)
    humanize_duration.short_description = _("Duration")
    humanize_duration.admin_order_field = 'duration'

admin.site.register(CronJobLog, CronJobLogAdmin)
