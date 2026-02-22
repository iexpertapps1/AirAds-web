"""
AirAd — tags initial migration
Creates Tag with 6 type choices and composite index.
"""

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(db_index=True, max_length=120, unique=True)),
                (
                    "tag_type",
                    models.CharField(
                        choices=[
                            ("LOCATION", "Location"),
                            ("CATEGORY", "Category"),
                            ("INTENT", "Intent"),
                            ("PROMOTION", "Promotion"),
                            ("TIME", "Time"),
                            ("SYSTEM", "System"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("display_label", models.CharField(blank=True, max_length=150)),
                ("display_order", models.PositiveIntegerField(db_index=True, default=0)),
                ("icon_name", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
                "ordering": ["tag_type", "display_order", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="tag",
            index=models.Index(
                fields=["tag_type", "is_active"],
                name="tags_tag_type_active_idx",
            ),
        ),
    ]
