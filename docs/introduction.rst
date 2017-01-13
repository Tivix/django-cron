Introduction
============

Django-cron lets you run Django/Python code on a recurring basis proving basic plumbing to track and execute tasks. The two most common ways in which most people go about this is either writing custom python scripts or a management command per cron (leads to too many management commands!). Along with that some mechanism to track success, failure etc. is also usually necesary.

Django-cron is an abstraction of the linux utility cron. The advantage of using Django-cron over cron directly is that it easier to inject into a django app and
offers bookeeping of all crons.
Django-cron itself is setup as a cron. This allows django-cron tasks to be run in the background. This is required and is explained in :doc:`Installation <installation>`

This is by no means a replacement for queues like Celery ( http://celeryproject.org/ ) etc.
