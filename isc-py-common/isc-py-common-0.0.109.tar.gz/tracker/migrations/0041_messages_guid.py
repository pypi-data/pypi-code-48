# Generated by Django 2.2.5 on 2019-09-02 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0040_messages_theme_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='guid',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
