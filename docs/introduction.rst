Introduction
============

Django-cron lets you run Django/Python code on a recurring basis proving basic plumbing to track and execute tasks. The two most common ways in which most people go about this is either writing custom python scripts or a management command per cron (leads to too many management commands!). Along with that some mechanism to track success, failure etc. is also usually necesary.

This app solves both issues to a reasonable extent. This is by no means a replacement for queues like Celery ( http://celeryproject.org/ ) etc.

This open-source app is brought to you by `Tivix <https://www.tivix.com/>`_.
