#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test


setup(
    name='django-cron',
    version='0.1',
    author='Sumit Chachra',
    author_email='chachra@tivix.com',
    url='http://github.com/tivix/django-cron',
    description = 'Running python crons in a Django project',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django==1.2.5',
        'South==0.7.2'
    ],
    # test_suite = 'django_cron.tests',
    include_package_data=True,
    # cmdclass={},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
