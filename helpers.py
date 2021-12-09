from django.utils.translation import gettext_lazy as _


def humanize_duration(duration):
    """
    Returns a humanized string representing time difference

    For example: 2 days 1 hour 25 minutes 10 seconds
    """
    days = duration.days
    hours = duration.seconds / 3600
    minutes = duration.seconds % 3600 / 60
    seconds = duration.seconds % 3600 % 60

    parts = []
    if days > 0:
        parts.append(u'%s %s' % (days, _('day') if days == 1 else _('days')))

    if hours > 0:
        parts.append(u'%s %s' % (hours, _('hour') if hours == 1 else _('hours')))

    if minutes > 0:
        parts.append(u'%s %s' % (minutes, _('minute') if minutes == 1 else _('minutes')))

    if seconds > 0:
        parts.append(u'%s %s' % (seconds, _('second') if seconds == 1 else _('seconds')))

    return ' '.join(parts) if len(parts) != 0 else _('< 1 second')
