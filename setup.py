#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test
import os


here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here,  'README.rst'))
long_description = f.read().strip()
f.close()

setup(
    name='django-cron',
    version='0.3.6',
    author='Sumit Chachra',
    author_email='chachra@tivix.com',
    url='http://github.com/tivix/django-cron',
    description='Running python crons in a Django project',
    packages=find_packages(),
    long_description=long_description,
    keywords='django cron',
    zip_safe=False,
    install_requires=[
        'Django>=1.6.0',
        'South>=0.8.1',
        'django-common-helpers>=0.6.4'
    ],
    test_suite='runtests.runtests',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ]
)
