# Generated by Django 3.0.2 on 2020-01-18 14:39

from django.db import migrations
import django.db.models.deletion
import isc_common.fields.related


class Migration(migrations.Migration):

    dependencies = [
        ('planing', '0060_auto_20200118_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operations',
            name='status',
            field=isc_common.fields.related.ForeignKeyProtect(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='planing.Status_operation_types'),
        ),
    ]
