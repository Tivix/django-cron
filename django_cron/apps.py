from django.apps import AppConfig


class DjangoCronDefaultAppConfig(AppConfig):
    name = 'django_cron'  # must be unique across project
    label = 'django_cron'  # must be unique across project
    verbose_name = 'Django Cron'
