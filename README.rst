Django-cron lets you run Django/Python code on a recurring basis proving basic plumbing to track and execute tasks. The 2 most common ways in which most people go about this is either writing custom python scripts or a management command per cron (leads to too many management commands!). Along with that some mechanism to track success, failure etc. is also usually necesary.

This app solves both issues to a reasonable extent. This is by no means a replacement for queues like <a href="http://celeryproject.org/">Celery</a> etc.

To use this app:
* Install django_cron (ideally in your virtualenv!) using pip or simply getting a copy of the code and putting it in a
directory in your codebase.
* Add ``django_cron`` to your Django settings ``INSTALLED_APPS``
* If you're using South for schema migrations run ``python manage.py migrate django_cron`` or simply do a ``syncdb``.
* Write a cron class somewhere in your code, that extends the `CronJobBase` class. This class will look something like:
	``
	class MyCronJob(CronJobBase):
	    RUN_EVERY_MINS = 120 # every 2 hours
		
	    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	    code = 'my_app.my_cron_job'	# a unique code
		
	    def do(self):
			pass	# do your thing here
	``
* Add a variable called ``CRON_CLASSES`` (similar to ``MIDDLEWARE_CLASSES`` etc.) thats a list of strings, each being
a cron class. Eg. ``CRON_CLASSES=['my_app.cron.MyCronJob']``
* Now everytime you run the management command ``python manage.py runcrons`` all the crons will run if required. Depending on the application the management command can be called from the Unix crontab as often as required. Every 5 minutes usually works for most of my applications.

This opensource app is brought to you by <a href="http://tivix.com/">Tivix, Inc.</a>