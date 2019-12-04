from importlib import import_module
from django.conf import settings


def get_object_from_path(object_path):
    path_split = object_path.split('.')
    object_module_path = '.'.join(path_split[:-1])
    object_name = path_split[-1]
    object_module = import_module(object_module_path)
    return getattr(object_module, object_name, None)


class Settings:
    DEFAULT_MANAGER_CLASS = 'django_cron.CronJobManager'

    @staticmethod
    def get_manager():
        manager_class = getattr(settings, 'CRON_MANAGER', Settings.DEFAULT_MANAGER_CLASS)
        return get_object_from_path(manager_class)


cron_settings = Settings()
