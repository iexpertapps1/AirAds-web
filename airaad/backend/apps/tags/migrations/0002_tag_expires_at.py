"""
AirAd — tags migration 0002

Adds:
  - Tag.expires_at (DateTimeField, nullable) — spec §4.3 Layer 3 Promotion tag time-bound expiry.
    Null = tag never auto-expires.
    expire_promotion_tags Celery task (Phase B) deactivates PROMOTION tags past this datetime.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tags", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tag",
            name="expires_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text=(
                    "Optional expiry datetime for PROMOTION tags (spec §4.3). "
                    "Null means the tag never auto-expires. "
                    "expire_promotion_tags Celery task deactivates tags past this datetime."
                ),
                null=True,
            ),
        ),
    ]
