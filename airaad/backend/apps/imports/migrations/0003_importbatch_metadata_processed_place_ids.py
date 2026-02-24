from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("imports", "0002_google_places_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="importbatch",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Arbitrary metadata dict for import context (enhanced Google Places params, etc.).",
            ),
        ),
        migrations.AddField(
            model_name="importbatch",
            name="processed_place_ids",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="List of google_place_ids already processed in this batch. Enables crash-resume.",
            ),
        ),
    ]
