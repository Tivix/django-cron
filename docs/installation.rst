Installation
============

1. Install ``django_cron`` (ideally in your virtualenv!) using pip or simply getting a copy of the code and putting it in a directory in your codebase.

2. Add ``django_cron`` to your Django settings ``INSTALLED_APPS``:

   .. code-block:: python

       INSTALLED_APPS = [
           # ...
           "django_cron",
       ]

3. Run ``python manage.py migrate django_cron``

4. Write a cron class somewhere in your code, that extends the ``CronJobBase`` class. This class will look something like this:

   .. code-block:: python

       from django_cron import CronJobBase, Schedule

       class MyCronJob(CronJobBase):
           RUN_EVERY_MINS = 120 # every 2 hours

           schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
           code = 'my_app.my_cron_job'    # a unique code

           def do(self):
               pass    # do your thing here

5. Add a variable called ``CRON_CLASSES`` (similar to ``MIDDLEWARE_CLASSES`` etc.) thats a list of strings, each being a cron class. Eg.:

   .. code-block:: python

       CRON_CLASSES = [
           "my_app.cron.MyCronJob",
           # ...
       ]

6. Now everytime you run the management command ``python manage.py runcrons`` all the crons will run if required. Depending on the application the management command can be called from the Unix crontab as often as required. Every 5 minutes usually works for most of my applications, for example: ::

       > crontab -e
       */5 * * * * source /home/ubuntu/.bashrc && source /home/ubuntu/work/your-project/bin/activate && python /home/ubuntu/work/your-project/src/manage.py runcrons > /home/ubuntu/cronjob.log

  Management Commands:

  I. run a specific cron with ``python manage.py runcrons cron_class ...``, for example: ::

        # only run "my_app.cron.MyCronJob"
        $ python manage.py runcrons "my_app.cron.MyCronJob"

        # run "my_app.cron.MyCronJob" and "my_app.cron.AnotherCronJob"
        $ python manage.py runcrons "my_app.cron.MyCronJob" "my_app.cron.AnotherCronJob"

  II. force run your crons with ``python manage.py runcrons --force``, for example: ::

        # run all crons, immediately, regardless of run time
        $ python manage.py runcrons --force

  III. perform a dry-run with ``python manage.py runcrons --dry-run``, for example: ::

        # just report which crons would run, don't actually do anything
        $ python manage.py runcrons --dry-run

  IIII. run without any messages to the console ``python manage.py runcrons --silent``, for example: ::

        # run crons, if required, without message to console
        $ python manage.py runcrons --silent


  IV. run jobs multiple times ``python manage.py runcrons``, for example: ::

        # run crons, 2 times, waiting between runs 10 seconds
        $ python manage.py runcrons --repeat 2 --sleep 10
  You may also run only chosen cron jobs ``python manage.py runcrons cron_class ...``
  Without ``repeat`` it will run as long as user stops it with keyboard interruption.
