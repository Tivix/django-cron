Changelog
=========

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
