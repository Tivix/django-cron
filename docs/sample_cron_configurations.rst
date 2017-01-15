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

By default parallel runs are not allowed (for security reasons). However if you
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

This sample cron job checks for any unreported failed jobs for each job class
provided in your ``CRON_CLASSES`` list, and reports them as necessary. The job
is set to run on each ``runcrons`` task, and the default process is to email
all the users specified in the ``ADMINS`` settings list when a job fails more
than 10 times in a row.

Install required dependencies: ``Django>=1.7.0``, ``django-common>=0.5.1``.

Add ``django_cron.cron.FailedRunsNotificationCronJob`` to *the end* of your
``CRON_CLASSES`` list within your settings file.

.. code-block:: python

    CRON_CLASSES = [
        ...
        'django_cron.cron.FailedRunsNotificationCronJob'
    ]

Each cron job can specify the minimum number of failures required before an email is sent by setting a ``MIN_NUM_FAILURES`` attribute: ::

    class MyCronJob(CronJobBase):
        MIN_NUM_FAILURES = 3
        ...

**Configuration**

By adding a ``CRON_FAILURE_REPORT`` dictionary to your Django settings you can configure the reporter in a variety of ways:

.. code-block:: python

    # settings.py
    CRON_FAILURE_REPORT = dict()

The possible options are:

* ``RUN_EVERY_MINS (int)``

  After how many minutes should the reporter run (default: 0).

* ``EMAIL_PREFIX (str)``

  The prefix for all failure emails (default: "[Cron Failure] - ").

* ``MIN_NUM_FAILURES (int)``

  The default number of times an individual cron job can fail before an email is sent.
  Job classes can always override this value by setting a class attribute
  with the same name (default: 10).

* ``FROM_EMAIL (str)``

  The email address the fail reports are sent from (default: settings.DEFAULT_FROM_EMAIL)

* ``EMAIL_RECIPIENTS (list<str>)``

  A list of email addresses controlling who the reports are sent to (default: email addresses defined in settings.ADMIN)

For more advanced usage, you can subclass ``FailedRunsNotificationCronJob``, and define a custom ``report_failure()`` method to be notified of failures in whichever way you like (e.g. via slack, text etc.). For example: ::

    class FailedNotifier(FailedRunsNotificationCronJob):
        def report_failure(self, cron_cls, failed_jobs):
            """
            Report in Slack that the given Cron job failed.
            """
            slack.post("ERROR - Cron job '{0}' failed.".format(cron_cls.code))
