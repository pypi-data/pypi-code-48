# Generated by Django 2.2.6 on 2019-10-14 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kd', '0082_auto_20191011_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='document_attributes',
            name='value_int',
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True, verbose_name='Значение атрибута'),
        ),
    ]
