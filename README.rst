===========
django-cron
===========

Django-cron lets you run Django/Python code on a recurring basis proving basic plumbing to track and execute tasks. The 2 most common ways in which most people go about this is either writing custom python scripts or a management command per cron (leads to too many management commands!). Along with that some mechanism to track success, failure etc. is also usually necesary.

This app solves both issues to a reasonable extent. This is by no means a replacement for queues like Celery ( http://celeryproject.org/ ) etc.


Retry after failure feature
---------------------------

You can run cron by passing RETRY_AFTER_FAILURE_MINS param.

This will re-runs not next time runcrons is run, but at least RETRY_AFTER_FAILURE_MINS after last failure::

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 60 # every hours
        RETRY_AFTER_FAILURE_MINS = 5

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)


Run at times feature
--------------------

You can run cron by passing RUN_EVERY_MINS or RUN_AT_TIMES params.

This will run job every hour::

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 60 # every hours

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

This will run job at given hours::

    class MyCronJob(CronJobBase):
        RUN_AT_TIMES = ['11:30', '14:00', '23:15']

        schedule = Schedule(run_at_times=RUN_AT_TIMES)

Hour format is HH:MM (24h clock)

You can also mix up both of these methods::

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 120 # every 2 hours
        RUN_AT_TIMES = ['6:30']

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS, run_at_times=RUN_AT_TIMES)

This will run job every 2h plus one run at 6:30.

Allowing parallels runs
-----------------------

By deafult parallels runs are not allowed (for security reasons). However if you
want enable them just add:

    ALLOW_PARALLEL_RUNS = True

in your CronJob class.


* Note this requires a caching framework to be installed, as per https://docs.djangoproject.com/en/dev/topics/cache/

If you wish to override which cache is used, put this in your settings file:

    CRON_CACHE = 'cron_cache'


Installation
------------

- Install django_cron (ideally in your virtualenv!) using pip or simply getting a copy of the code and putting it in a directory in your codebase.

- Add ``django_cron`` to your Django settings ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        # ...
        "django_cron",
    ]

- If you're using South for schema migrations run ``python manage.py migrate django_cron`` or simply do a ``syncdb``.

- Write a cron class somewhere in your code, that extends the `CronJobBase` class. This class will look something like this::

    from django_cron import CronJobBase, Schedule
    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 120 # every 2 hours

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
        code = 'my_app.my_cron_job'    # a unique code

        def do(self):
            pass    # do your thing here

- Add a variable called ``CRON_CLASSES`` (similar to ``MIDDLEWARE_CLASSES`` etc.) thats a list of strings, each being a cron class. Eg.::

    CRON_CLASSES = [
        "my_app.cron.MyCronJob",
        # ...
    ]

- Now everytime you run the management command ``python manage.py runcrons`` all the crons will run if required. Depending on the application the management command can be called from the Unix crontab as often as required. Every 5 minutes usually works for most of my applications.

FailedRunsNotificationCronJob
-----------------------------

This example cron check last cron jobs results. If they were unsuccessfull 10 times in row, it sends email to user.

- Install required dependencies: 'Django>=1.4.0', 'South>=0.7.2', 'django-common>=0.5.1'.
- Add 'django_cron.cron.FailedRunsNotificationCronJob' to your CRON_CLASSES in settings file.

- To set up minimal number of failed runs set up MIN_NUM_FAILURES in your cron class (default = 10). For example::

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 10
        MIN_NUM_FAILURES = 3

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
        code = 'app.MyCronJob'

        def do(self):
            ... some action here ...

- Emails are imported from ADMINS in settings file
- To set up email prefix, you must add FAILED_RUNS_CRONJOB_EMAIL_PREFIX in your settings file (default is empty). For example:

    FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Server check]: "

- FailedRunsNotificationCronJob checks every cron from CRON_CLASSES

This opensource app is brought to you by Tivix, Inc. ( http://tivix.com/ )


Changelog
=========

0.3.3
------

    - Python 3 compatibility.

0.3.2
------

    - Added database connection close.

    - Added better exceptions handler.

0.3.1
------

    - Added index_together entries for faster queries on large cron log db tables.

    - Upgraded requirement hence to Django 1.5 and South 0.8.1 since ``index_together`` is new to Django 1.5


0.3.0
-----

    - Added Django 1.4+ support. Updated requirements.


0.2.9
-----

    - Changed log level to debug() in CronJobManager.run() function.


0.2.8
-----

    - Bug fix

    - Optimized queries. Used latest() instead of order_by()


0.2.7
-----

    - Bug fix.


0.2.6
-----

    - Added `end_time` to list_display in CronJobLog admin


0.2.5
-----

    - Added a helper function ( run_cron_with_cache_check ) in runcrons.py


0.2.4
-----

    - Capability to run specific crons using the runcrons management command. Useful when in the list of crons there are few slow onces and you might want to run some quicker ones via a separate crontab entry to make sure they are not blocked / slowed down.

    - pep8 cleanup and reading from settings more carefully (getattr).
