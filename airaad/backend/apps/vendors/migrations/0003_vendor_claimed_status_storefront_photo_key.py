"""
AirAd — vendors migration 0003

Adds:
  - Vendor.claimed_status  (BooleanField, default=False) — spec §3.1 "claimed_status: Boolean"
  - Vendor.storefront_photo_key (CharField, blank=True) — spec §3.1 "storefront_photo: Image URL"
    (stored as S3 object key, never a public URL — presigned URL generated on read)
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0002_add_flagged_qc_status"),
    ]

    operations = [
        # -----------------------------------------------------------------------
        # Vendor.claimed_status — spec §3.1 "claimed_status: Boolean, default=False"
        # -----------------------------------------------------------------------
        migrations.AddField(
            model_name="vendor",
            name="claimed_status",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="True once the business owner has verified and claimed this listing.",
            ),
        ),
        # -----------------------------------------------------------------------
        # Vendor.storefront_photo_key — spec §3.1 "storefront_photo: Image URL (optional)"
        # Stored as S3 object key only — presigned URL generated on read.
        # -----------------------------------------------------------------------
        migrations.AddField(
            model_name="vendor",
            name="storefront_photo_key",
            field=models.CharField(
                blank=True,
                help_text="S3 object key for the primary storefront photo. Generate presigned URL on read.",
                max_length=500,
            ),
        ),
    ]
