# Generated by Django 2.2.1 on 2019-05-21 18:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import isc_common.fields.code_field
import isc_common.fields.description_field
import isc_common.fields.related


class Migration(migrations.Migration):

    dependencies = [
        ('ckk', '0043_auto_20190521_1853'),
        ('sales', '0007_customer_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Клиент'},
        ),
    ]
