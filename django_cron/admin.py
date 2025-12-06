from datetime import timedelta

from django.contrib import admin
from django.db.models import DurationField, ExpressionWrapper, F
from django.utils.translation import gettext_lazy as _

from .helpers import humanize_duration
from .models import CronJobLock, CronJobLog


class DurationFilter(admin.SimpleListFilter):
    title = _("duration")
    parameter_name = "duration"

    def lookups(self, request, model_admin):
        return (
            ("lte_minute", _("<= 1 minute")),
            ("gt_minute", _("> 1 minute")),
            ("gt_hour", _("> 1 hour")),
            ("gt_day", _("> 1 day")),
        )

    def queryset(self, request, queryset):
        if self.value() == "lte_minute":
            return queryset.filter(end_time__lte=F("start_time") + timedelta(minutes=1))
        if self.value() == "gt_minute":
            return queryset.filter(end_time__gt=F("start_time") + timedelta(minutes=1))
        if self.value() == "gt_hour":
            return queryset.filter(end_time__gt=F("start_time") + timedelta(hours=1))
        if self.value() == "gt_day":
            return queryset.filter(end_time__gt=F("start_time") + timedelta(days=1))

@admin.register(CronJobLog)
class CronJobLogAdmin(admin.ModelAdmin):
    class Meta:
        model = CronJobLog

    search_fields = ("code", "message")
    ordering = ("-start_time",)
    list_display = ("code", "start_time", "end_time", "humanize_duration", "is_success")
    list_filter = ("code", "start_time", "is_success", DurationFilter)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                duration=ExpressionWrapper(
                    F("end_time") - F("start_time"), DurationField()
                ),
            )
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and not getattr(request.user, "is_superuser", False):
            names = [f.name for f in CronJobLog._meta.fields if f.name != "id"]
            return *self.readonly_fields, *names
        return self.readonly_fields

    @admin.display(description=_("Duration"), ordering="duration")
    def humanize_duration(self, obj):
        return humanize_duration(obj.end_time - obj.start_time)


admin.site.register(CronJobLock)
