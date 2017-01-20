Sample Cron Configurations
==========================

Retry after failure feature
---------------------------

You can run cron by passing ``RETRY_AFTER_FAILURE_MINS`` param.

This will re-runs not next time runcrons is run, but at least ``RETRY_AFTER_FAILURE_MINS`` after last failure:

.. code-block:: python

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 60 # every hours
        RETRY_AFTER_FAILURE_MINS = 5

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)


Run at times feature
--------------------

You can run cron by passing ``RUN_EVERY_MINS`` or ``RUN_AT_TIMES`` params.

This will run job every hour:

.. code-block:: python

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 60 # every hours

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

This will run job at given hours:

.. code-block:: python

    class MyCronJob(CronJobBase):
        RUN_AT_TIMES = ['11:30', '14:00', '23:15']

        schedule = Schedule(run_at_times=RUN_AT_TIMES)

Hour format is ``HH:MM`` (24h clock). ``django-cron`` will interpret
these times in the local timezone of your site, as specified by
the ``TIME_ZONE`` setting.

You can also mix up both of these methods:

.. code-block:: python

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 120 # every 2 hours
        RUN_AT_TIMES = ['6:30']

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS, run_at_times=RUN_AT_TIMES)

This will run job every 2h plus one run at 6:30.

Allowing parallels runs
-----------------------

By default parallels runs are not allowed (for security reasons). However if you
want enable them just add:

.. code-block:: python

    ALLOW_PARALLEL_RUNS = True

in your CronJob class.


.. note:: Note this requires a caching framework to be installed, as per https://docs.djangoproject.com/en/dev/topics/cache/

If you wish to override which cache is used, put this in your settings file:

.. code-block:: python

    DJANGO_CRON_CACHE = 'cron_cache'


FailedRunsNotificationCronJob
-----------------------------

This example cron check last cron jobs results. If they were unsuccessfull 10 times in row, it sends email to user.

Install required dependencies: ``Django>=1.7.0``, ``django-common>=0.5.1``.

Add ``django_cron.cron.FailedRunsNotificationCronJob`` to your ``CRON_CLASSES`` in settings file.

To set up minimal number of failed runs set up ``MIN_NUM_FAILURES`` in your cron class (default = 10). For example: ::

    class MyCronJob(CronJobBase):
        RUN_EVERY_MINS = 10
        MIN_NUM_FAILURES = 3

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
        code = 'app.MyCronJob'

        def do(self):
            ... some action here ...

Emails are imported from ``ADMINS`` in settings file

To set up email prefix, you must add ``FAILED_RUNS_CRONJOB_EMAIL_PREFIX`` in your settings file (default is empty). For example: ::

    FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Server check]: "

``FailedRunsNotificationCronJob`` checks every cron from ``CRON_CLASSES``
