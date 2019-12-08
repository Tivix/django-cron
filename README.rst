===========
django-cron
===========

.. image:: https://travis-ci.org/Tivix/django-cron.png
    :target: https://travis-ci.org/Tivix/django-cron


.. image:: https://coveralls.io/repos/Tivix/django-cron/badge.png
    :target: https://coveralls.io/r/Tivix/django-cron?branch=master


.. image:: https://readthedocs.org/projects/django-cron/badge/?version=latest
    :target: https://readthedocs.org/projects/django-cron/?badge=latest

Django-cron lets you run Django/Python code on a recurring basis providing basic plumbing to track and execute tasks. The 2 most common ways in which most people go about this is either writing custom python scripts or a management command per cron (leads to too many management commands!). Along with that some mechanism to track success, failure etc. is also usually necesary.

This app solves both issues to a reasonable extent. This is by no means a replacement for queues like Celery ( http://celeryproject.org/ ) etc.


Documentation
=============
http://django-cron.readthedocs.org/en/latest/

This open-source app is brought to you by Tivix, Inc. ( http://tivix.com/ )


Summary of fork changes
=======================
1. Access to change CronJobManager from django settings if required.

```python
CRON_MANAGER = 'path.to.custom.MyManager'
```

2. Add day config to CronJob schedule:

```python
day_of_month='*',  # cron format: '*/3' '5,15,25' or list: [1] * 31
month_numbers='*',  # cron format: '*/3' '5,15,25' or list: [1] * 12
day_of_week='*',  # cron format: '*/3' '5,15,25' or list: [1] * 7
```

Example:
```python
from django_cron import CronJobBase, Schedule

class ExampleCronJob(CronJobBase):
    RUN_AT_TIMES = ['10:10', '22:10']
    schedule = Schedule(run_at_times=RUN_AT_TIMES, day_of_week='2')
    code = 'cron.ExampleCronJob'
    def do(self):
        pass

```

3. Add a method to CronJob to get future run times in future by this parameters:
`from_datetime` and `to_datetime`

4. Move should_run_now method to CronJob to override it if required.