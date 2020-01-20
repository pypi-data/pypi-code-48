# Generated by Django 2.0.6 on 2018-06-30 04:54
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import nuntius.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.NUNTIUS_SUBSCRIBER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "task_uuid",
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        default=None,
                        null=True,
                        verbose_name="Celery tasks identifier",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, verbose_name="Name (invisible to subscribers)"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "message_from_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name='"From" name'
                    ),
                ),
                (
                    "message_from_email",
                    models.EmailField(
                        max_length=255, verbose_name='"From" email address'
                    ),
                ),
                (
                    "message_reply_to_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name='"Reply to" name'
                    ),
                ),
                (
                    "message_reply_to_email",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name='"Reply to" email address',
                    ),
                ),
                (
                    "message_subject",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Message subject line"
                    ),
                ),
                (
                    "message_content_html",
                    models.TextField(blank=True, verbose_name="Message content (HTML)"),
                ),
                (
                    "message_content_text",
                    models.TextField(verbose_name="Message content (text)"),
                ),
                ("segment_id", models.CharField(max_length=255)),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Waiting"),
                            (1, "Sending"),
                            (2, "Sent"),
                            (3, "Error"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "segment_content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CampaignSentEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, verbose_name="Email adress at event time"
                    ),
                ),
                ("datetime", models.DateTimeField(auto_now_add=True)),
                (
                    "result",
                    models.CharField(
                        default="P", max_length=2, verbose_name="Operation result"
                    ),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Campaign",
                        to="nuntius.Campaign",
                    ),
                ),
                (
                    "subscriber",
                    models.ForeignKey(
                        null=True,
                        blank=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="Subscriber",
                        to=settings.NUNTIUS_SUBSCRIBER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="campaignsentevent", unique_together={("campaign", "subscriber")}
        ),
    ]
