"""
AirAd — accounts migration 0002
Adds must_change_password BooleanField to AdminUser.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminuser",
            name="must_change_password",
            field=models.BooleanField(
                default=False,
                help_text="Set True on creation via temp password. Cleared on first successful login.",
            ),
        ),
    ]
