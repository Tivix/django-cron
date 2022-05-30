Changelog
=========
0.6.0
------

    - Update requirements to Django 3.2.0 (long-term support)

    - Django 4.0 fixes

    - Removed message length limit to reflect database

    - Locking backend with database

    - Name locks by module_name.class_name for higher distinction

    - Run CronJobs on days in month/ monthly

    - Command for making cron jobs running in loop or running several times with the sleep time between

    - New features: Run cron on specific days and output errors to a specified log

    - Add cron feedback and dry-run functionality

0.5.1
------

    - Fixed error in file locking backend with Python 3

    - Fixed `'NoneType' object has no attribute 'utcoffset'` error

    - Updated unit tests and demo for Django 2.0 compatibility


0.5.0
------

    - Added support for Django 1.10

    - Minimum Django version required is 1.8

    - Use parser.add_argument() instead of optparse.make_option() in runcrons command


0.4.6
------

    - Model import error fix for Django 1.9.X


0.4.5
------

    - Added ability to check how many time left until next run.

0.4.4
------

    - Remove max_length from CronJobLog.message field.


0.4.3
------

    - Added DJANGO_CRON_DELETE_LOGS_OLDER_THAN setting to allow automated log clearing.


0.4.2
------

    - Fix for #57 (ignoring Django timezone settings)


0.4.1
------

    - Added get_prev_success_cron method to Schedule (Issue #26)

    - Improvements to Admin interface (PR #42)


0.4.0
------

    - Added support for Django 1.8

    - Minimum Django version required is 1.7

    - Dropped South in favor of Django migrations

    - WARNING! When upgrading you might need to remove existing South migrations, read more: https://docs.djangoproject.com/en/1.7/topics/migrations/#upgrading-from-south


0.3.6
------

    - Added Django 1.7 support

    - Added python3 support


0.3.5
------

    - Added locking backends

    - Added tests


0.3.4
------

    - Added CRON_CACHE settings parameter for cache select

    - Handle database connection errors

    - Upping requirement to Django 1.5+


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
