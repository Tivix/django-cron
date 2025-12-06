from datetime import timedelta

from django.template.defaultfilters import pluralize
from django.utils import timezone
from django.utils.translation import gettext as _


def humanize_duration(duration: timedelta) -> str:
    """
    Returns a humanized string representing time difference

    For example: 2 days 1 hour 25 minutes 10 seconds
    """
    days = duration.days
    hours = int(duration.seconds / 3600)
    minutes = int(duration.seconds % 3600 / 60)
    seconds = int(duration.seconds % 3600 % 60)

    parts = []
    if days > 0:
        parts.append("%s %s" % (days, pluralize(days, _("day,days"))))

    if hours > 0:
        parts.append("%s %s" % (hours, pluralize(hours, _("hour,hours"))))

    if minutes > 0:
        parts.append("%s %s" % (minutes, pluralize(minutes, _("minute,minutes"))))

    if seconds > 0:
        parts.append("%s %s" % (seconds, pluralize(seconds, _("second,seconds"))))

    return ", ".join(parts) if len(parts) != 0 else _("< 1 second")


def get_class(kls: str) -> type:
    """
    Converts a string to a class.
    Courtesy: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname/452981#452981
    """
    parts = kls.split(".")

    if len(parts) == 1:
        raise ImportError("'{0}'' is not a valid import path".format(kls))

    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_current_time():
    now = timezone.now()
    return now if timezone.is_naive(now) else timezone.localtime(now)
