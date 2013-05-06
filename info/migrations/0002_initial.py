# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'info_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'info', ['User'])

        # Adding M2M table for field items on 'User'
        db.create_table(u'info_user_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'info.user'], null=False)),
            ('item', models.ForeignKey(orm[u'info.item'], null=False))
        ))
        db.create_unique(u'info_user_items', ['user_id', 'item_id'])

        # Adding model 'Item'
        db.create_table(u'info_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['info.User'], null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sub_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('event_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('claimed', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
        ))
        db.send_create_signal(u'info', ['Item'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'info_user')

        # Removing M2M table for field items on 'User'
        db.delete_table('info_user_items')

        # Deleting model 'Item'
        db.delete_table(u'info_item')


    models = {
        u'info.item': {
            'Meta': {'object_name': 'Item'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'claimed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'event_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['info.User']", 'null': 'True', 'blank': 'True'}),
            'sub_date': ('django.db.models.fields.DateField', [], {'null': 'True'})
        },
        u'info.user': {
            'Meta': {'object_name': 'User'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['info.Item']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['info']