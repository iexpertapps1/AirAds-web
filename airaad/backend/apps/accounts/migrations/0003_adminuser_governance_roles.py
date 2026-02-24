"""
AirAd — accounts migration 0003
Adds 4 governance roles to AdminRole choices per spec §2.1:
  OPERATIONS_MANAGER, CONTENT_MODERATOR, DATA_QUALITY_ANALYST, ANALYTICS_OBSERVER
Also increases role max_length from 20 → 25 to fit DATA_QUALITY_ANALYST (21 chars).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_adminuser_must_change_password"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adminuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("SUPER_ADMIN", "Super Admin"),
                    ("CITY_MANAGER", "City Manager"),
                    ("DATA_ENTRY", "Data Entry"),
                    ("QA_REVIEWER", "QA Reviewer"),
                    ("FIELD_AGENT", "Field Agent"),
                    ("ANALYST", "Analyst"),
                    ("SUPPORT", "Support"),
                    ("OPERATIONS_MANAGER", "Operations Manager"),
                    ("CONTENT_MODERATOR", "Content Moderator"),
                    ("DATA_QUALITY_ANALYST", "Data Quality Analyst"),
                    ("ANALYTICS_OBSERVER", "Analytics Observer"),
                ],
                db_index=True,
                default="DATA_ENTRY",
                max_length=25,
            ),
        ),
    ]
