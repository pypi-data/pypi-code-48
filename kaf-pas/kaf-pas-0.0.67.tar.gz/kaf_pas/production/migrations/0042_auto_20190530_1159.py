# Generated by Django 2.2.1 on 2019-05-30 11:59

from django.db import migrations
import isc_common.fields.code_field
import isc_common.fields.description_field
import isc_common.fields.name_field


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0041_auto_20190530_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='operations',
            name='code',
            field=isc_common.fields.code_field.CodeField(),
        ),
        migrations.AddField(
            model_name='operations',
            name='description',
            field=isc_common.fields.description_field.DescriptionField(),
        ),
        migrations.AddField(
            model_name='operations',
            name='name',
            field=isc_common.fields.name_field.NameField(),
        ),
    ]
