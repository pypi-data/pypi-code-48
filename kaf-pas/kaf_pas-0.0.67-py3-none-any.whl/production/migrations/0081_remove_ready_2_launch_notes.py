# Generated by Django 2.2.6 on 2019-10-29 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0080_auto_20191028_1406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ready_2_launch',
            name='notes',
        ),
    ]
