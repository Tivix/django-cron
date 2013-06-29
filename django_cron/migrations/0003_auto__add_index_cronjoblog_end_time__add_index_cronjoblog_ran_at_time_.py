# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'CronJobLog', fields ['end_time']
        db.create_index(u'django_cron_cronjoblog', ['end_time'])

        # Adding index on 'CronJobLog', fields ['ran_at_time', 'is_success', 'code']
        db.create_index(u'django_cron_cronjoblog', ['ran_at_time', 'is_success', 'code'])

        # Adding index on 'CronJobLog', fields ['ran_at_time', 'start_time', 'code']
        db.create_index(u'django_cron_cronjoblog', ['ran_at_time', 'start_time', 'code'])

        # Adding index on 'CronJobLog', fields ['start_time', 'code']
        db.create_index(u'django_cron_cronjoblog', ['start_time', 'code'])


    def backwards(self, orm):
        # Removing index on 'CronJobLog', fields ['start_time', 'code']
        db.delete_index(u'django_cron_cronjoblog', ['start_time', 'code'])

        # Removing index on 'CronJobLog', fields ['ran_at_time', 'start_time', 'code']
        db.delete_index(u'django_cron_cronjoblog', ['ran_at_time', 'start_time', 'code'])

        # Removing index on 'CronJobLog', fields ['ran_at_time', 'is_success', 'code']
        db.delete_index(u'django_cron_cronjoblog', ['ran_at_time', 'is_success', 'code'])

        # Removing index on 'CronJobLog', fields ['end_time']
        db.delete_index(u'django_cron_cronjoblog', ['end_time'])


    models = {
        u'django_cron.cronjoblog': {
            'Meta': {'object_name': 'CronJobLog', 'index_together': "[('code', 'is_success', 'ran_at_time'), ('code', 'start_time', 'ran_at_time'), ('code', 'start_time')]"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'ran_at_time': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['django_cron']