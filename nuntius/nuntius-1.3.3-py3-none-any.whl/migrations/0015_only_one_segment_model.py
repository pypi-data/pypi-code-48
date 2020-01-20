# Generated by Django 2.2.5 on 2019-09-18 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def null_other_models(apps, schema_editor):
    new_segment_class = apps.get_model(*settings.NUNTIUS_SEGMENT_MODEL.split("."))
    Campaign = apps.get_model("nuntius", "Campaign")
    db_alias = schema_editor.connection.alias
    for c in Campaign.objects.using(db_alias).all():
        ct = c.segment_content_type
        if (
            c.segment_content_type is not None
            and apps.get_model(ct.app_label, ct.model) != new_segment_class
        ):
            c.segment_id = None
            c.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.NUNTIUS_SEGMENT_MODEL),
        ("nuntius", "0014_campaign_signature_key"),
    ]

    operations = [
        migrations.RunPython(null_other_models),
        migrations.RemoveField(model_name="campaign", name="segment_content_type"),
        migrations.AlterField(
            model_name="campaign",
            name="segment_id",
            field=models.CharField(max_length=255, null=True, db_column="segment_id"),
        ),
        migrations.RenameField(
            model_name="campaign", old_name="segment_id", new_name="segment"
        ),
        migrations.AlterField(
            model_name="campaign",
            name="segment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.NUNTIUS_SEGMENT_MODEL,
                verbose_name="Subscriber segment",
            ),
        ),
    ]
