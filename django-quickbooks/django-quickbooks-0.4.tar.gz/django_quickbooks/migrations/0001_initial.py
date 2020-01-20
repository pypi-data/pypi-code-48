# Generated by Django 2.2.4 on 2019-12-24 14:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Realm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=155)),
                ('password', models.CharField(max_length=128)),
                ('schema_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RealmSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='Ticket for QBWC session')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(null=True)),
                ('realm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='django_quickbooks.Realm')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
