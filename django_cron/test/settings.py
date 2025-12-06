from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent

SECRET_KEY = "not-a-secure-key"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_cron",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_cron.test.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

# since django is meant for developers with deadlines...
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "USER": "djangocron",
        "NAME": "djangocron",
        "TEST_NAME": "djangocron_test",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django_cron": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

STATIC_URL = "/static/"

_CRON_PATH = "django_cron.test.cron."
CRON_CLASSES = [
    f"{_CRON_PATH}TestSuccessCronJob",
    f"{_CRON_PATH}TestErrorCronJob",
    f"{_CRON_PATH}Test5minsCronJob",
    f"{_CRON_PATH}TestRunAtTimesCronJob",
    f"{_CRON_PATH}Wait3secCronJob",
    "django_cron.cron.FailedRunsNotificationCronJob",
]

USE_TZ = False
