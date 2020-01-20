# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-10-31 11:08
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IevvLoggingEventBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(db_index=True, max_length=255, unique=True)),
                ('last_started', models.DateTimeField()),
                ('last_finished', models.DateTimeField(blank=True, null=True)),
                ('time_spent', models.CharField(blank=True, default='', max_length=255)),
                ('time_spent_in_seconds', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IevvLoggingEventItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_spent', models.CharField(blank=True, default='', max_length=255)),
                ('time_spent_in_seconds', models.IntegerField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('logging_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ievv_logging.IevvLoggingEventBase')),
            ],
        ),
    ]
