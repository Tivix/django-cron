# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CronJobLog.ran_at_time'
        db.add_column('django_cron_cronjoblog', 'ran_at_time', self.gf('django.db.models.fields.TimeField')(db_index=True, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CronJobLog.ran_at_time'
        db.delete_column('django_cron_cronjoblog', 'ran_at_time')


    models = {
        'django_cron.cronjoblog': {
            'Meta': {'object_name': 'CronJobLog'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'ran_at_time': ('django.db.models.fields.TimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['django_cron']
