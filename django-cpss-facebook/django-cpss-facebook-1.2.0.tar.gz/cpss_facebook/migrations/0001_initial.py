# Generated by Django 3.0.2 on 2020-01-11 22:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookClientOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook_api_version', models.CharField(choices=[('2.12', '2.12'), ('3.0', '3.0'), ('3.1', '3.1'), ('3.2', '3.2'), ('3.3', '3.3'), ('4.0', '4.0'), ('5.0', '5.0')], default='2.12', max_length=5, verbose_name='Facebook API Version')),
                ('facebook_longterm_access_token', models.CharField(default='', max_length=100, verbose_name='Facebook Long Term Token')),
                ('facebook_access_token', models.CharField(default='', max_length=100, verbose_name='Facebook Access Token')),
                ('facebook_token_secret', models.CharField(default='', max_length=100, verbose_name='Facebook Token Secret')),
                ('facebook_app_id', models.CharField(default='', max_length=100, verbose_name='Facebook APP Id')),
                ('facebook_page_id', models.CharField(default='', max_length=100, unique=True, verbose_name='Facebook Page ID')),
                ('facebook_user_id', models.CharField(default='', max_length=100, unique=True, verbose_name='Facebook User ID')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sites.Site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'CPSS Facebook Client Setting',
                'verbose_name_plural': 'CPSS Facebook Client Settings',
                'db_table': 'cpss_facebook_settings',
            },
        ),
    ]
