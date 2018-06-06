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
