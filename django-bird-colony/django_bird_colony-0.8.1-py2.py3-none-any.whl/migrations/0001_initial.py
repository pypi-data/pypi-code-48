# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-21 20:27
from __future__ import unicode_literals

import birds.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Age',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('min_days', models.PositiveIntegerField()),
                ('max_days', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('sex', models.CharField(choices=[('M', 'male'), ('F', 'female'), ('U', 'unknown')], max_length=2)),
                ('band_number', models.IntegerField(blank=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['band_color', 'band_number'],
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12, unique=True)),
                ('abbrv', models.CharField(max_length=3, unique=True, verbose_name='Abbreviation')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DataCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='a short name for the collection', max_length=16, unique=True)),
                ('uri', models.CharField(help_text='canonical URL for retrieving a recording in this collection', max_length=512)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='birds.Animal')),
                ('entered_by', models.ForeignKey(on_delete=models.SET(birds.models.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='birds.Animal')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='birds.Animal')),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('common_name', models.CharField(max_length=45)),
                ('genus', models.CharField(max_length=45)),
                ('species', models.CharField(max_length=45)),
                ('code', models.CharField(max_length=4, unique=True)),
            ],
            options={
                'ordering': ['common_name'],
                'verbose_name_plural': 'species',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
                ('count', models.SmallIntegerField(choices=[(0, '0'), (-1, '-1'), (1, '+1')], default=0, help_text='1: animal acquired; -1: animal lost; 0: no change')),
                ('category', models.CharField(blank=True, choices=[('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=2, null=True)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'status codes',
            },
        ),
        migrations.AlterUniqueTogether(
            name='species',
            unique_together=set([('genus', 'species')]),
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='birds.Location'),
        ),
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='birds.Status'),
        ),
        migrations.AddField(
            model_name='animal',
            name='band_color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='birds.Color'),
        ),
        migrations.AddField(
            model_name='animal',
            name='parents',
            field=models.ManyToManyField(related_name='children', through='birds.Parent', to='birds.Animal'),
        ),
        migrations.AddField(
            model_name='animal',
            name='reserved_by',
            field=models.ForeignKey(blank=True, help_text='mark a bird as reserved for a specific user', null=True, on_delete=models.SET(birds.models.get_sentinel_user), to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='animal',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='birds.Species'),
        ),
        migrations.AddField(
            model_name='age',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='birds.Species'),
        ),
        migrations.AlterUniqueTogether(
            name='age',
            unique_together=set([('name', 'species')]),
        ),
    ]
