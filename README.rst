===========
django-cron
===========

Django-cron lets you run Django/Python code on a recurring basis proving basic plumbing to track and execute tasks. The 2 most common ways in which most people go about this is either writing custom python scripts or a management command per cron (leads to too many management commands!). Along with that some mechanism to track success, failure etc. is also usually necesary.

This app solves both issues to a reasonable extent. This is by no means a replacement for queues like Celery ( http://celeryproject.org/ ) etc.


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
	    code = 'my_app.my_cron_job'	# a unique code
		
	    def do(self):
			pass	# do your thing here

- Add a variable called ``CRON_CLASSES`` (similar to ``MIDDLEWARE_CLASSES`` etc.) thats a list of strings, each being a cron class. Eg.::

	CRON_CLASSES = [
        "my_app.cron.MyCronJob",
		# ...
    ]

- Now everytime you run the management command ``python manage.py runcrons`` all the crons will run if required. Depending on the application the management command can be called from the Unix crontab as often as required. Every 5 minutes usually works for most of my applications.

FailedRunsNotificationCronJob
-----------------------------

This example cron check last cron jobs results. If they were unsuccessfull 10 times in row, it sends email to user.
    
- Install required dependencies: 'Django>=1.2.3', 'South>=0.7.2', 'django-common>=0.1'.
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
