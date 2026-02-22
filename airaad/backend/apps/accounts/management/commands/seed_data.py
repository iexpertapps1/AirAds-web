"""
AirAd Backend — seed_data Management Command

Creates a complete Karachi geo hierarchy, 6 taxonomy tags, 1 SUPER_ADMIN user,
and 3 sample vendors with encrypted phone numbers and business hours.

Idempotent — safe to run multiple times. Uses get_or_create() throughout.
All business logic delegated to services.py (R4).
All mutations produce AuditLog entries via log_action() (R5).
Phone numbers encrypted via AES-256-GCM (R2).

Usage:
    python manage.py seed_data
    python manage.py seed_data --no-vendors   # skip vendor creation
"""

import logging
from typing import Any

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Seed the database with Karachi geo hierarchy, tags, admin user, and sample vendors."""

    help = "Seed database with Karachi geo hierarchy, tags, admin user, and 3 sample vendors"

    def add_arguments(self, parser: Any) -> None:
        """Register command-line arguments.

        Args:
            parser: ArgumentParser instance.
        """
        parser.add_argument(
            "--no-vendors",
            action="store_true",
            default=False,
            help="Skip vendor creation (geo hierarchy and tags still created).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the seed_data command.

        Args:
            *args: Positional arguments (unused).
            **options: Parsed command-line options.
        """
        self.stdout.write(self.style.MIGRATE_HEADING("AirAd seed_data starting..."))

        try:
            with transaction.atomic():
                admin_user = self._seed_admin_user()
                country = self._seed_country(admin_user)
                city = self._seed_city(country, admin_user)
                area = self._seed_area(city, admin_user)
                landmark = self._seed_landmark(area, admin_user)
                self._seed_tags(admin_user)

                if not options["no_vendors"]:
                    self._seed_vendors(city, area, landmark, admin_user)

        except Exception as exc:
            raise CommandError(f"seed_data failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("seed_data complete."))

    # -------------------------------------------------------------------------
    # Admin user
    # -------------------------------------------------------------------------

    def _seed_admin_user(self) -> Any:
        """Create or retrieve the SUPER_ADMIN seed user.

        Returns:
            AdminUser instance.
        """
        from apps.accounts.models import AdminRole, AdminUser

        user, created = AdminUser.objects.get_or_create(
            email="admin@airaad.com",
            defaults={
                "full_name": "AirAd Super Admin",
                "role": AdminRole.SUPER_ADMIN,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("Admin@12345!")
            user.save(update_fields=["password"])
            self.stdout.write(f"  Created SUPER_ADMIN: {user.email}")
        else:
            self.stdout.write(f"  SUPER_ADMIN exists: {user.email}")

        return user

    # -------------------------------------------------------------------------
    # Geo hierarchy — Pakistan → Karachi → DHA → Zamzama
    # -------------------------------------------------------------------------

    def _seed_country(self, actor: Any) -> Any:
        """Create or retrieve Pakistan.

        Args:
            actor: AdminUser for AuditLog.

        Returns:
            Country instance.
        """
        from apps.geo.models import Country

        country, created = Country.objects.get_or_create(
            code="PK",
            defaults={"name": "Pakistan", "is_active": True},
        )
        if created:
            from apps.audit.utils import log_action
            log_action("COUNTRY_CREATED", actor, country, None, {}, {"name": "Pakistan", "code": "PK"})
            self.stdout.write("  Created Country: Pakistan (PK)")
        else:
            self.stdout.write("  Country exists: Pakistan (PK)")
        return country

    def _seed_city(self, country: Any, actor: Any) -> Any:
        """Create or retrieve Karachi.

        Args:
            country: Parent Country instance.
            actor: AdminUser for AuditLog.

        Returns:
            City instance.
        """
        from apps.geo.models import City

        city, created = City.objects.get_or_create(
            slug="karachi",
            defaults={
                "country": country,
                "name": "Karachi",
                "aliases": ["Karāchi", "کراچی", "City of Lights"],
                "centroid": Point(67.0099, 24.8607, srid=4326),  # lon/lat
                "is_active": True,
                "display_order": 1,
            },
        )
        if created:
            from apps.audit.utils import log_action
            log_action("CITY_CREATED", actor, city, None, {}, {"name": "Karachi", "slug": "karachi"})
            self.stdout.write("  Created City: Karachi")
        else:
            self.stdout.write("  City exists: Karachi")
        return city

    def _seed_area(self, city: Any, actor: Any) -> Any:
        """Create or retrieve DHA Phase 6 area.

        Args:
            city: Parent City instance.
            actor: AdminUser for AuditLog.

        Returns:
            Area instance.
        """
        from apps.geo.models import Area

        area, created = Area.objects.get_or_create(
            slug="dha-phase-6-karachi",
            defaults={
                "city": city,
                "name": "DHA Phase 6",
                "aliases": ["Defence Phase 6", "DHA-6", "Defence Housing Authority Phase 6"],
                "centroid": Point(67.0680, 24.8200, srid=4326),
                "is_active": True,
            },
        )
        if created:
            from apps.audit.utils import log_action
            log_action("AREA_CREATED", actor, area, None, {}, {"name": "DHA Phase 6", "slug": "dha-phase-6-karachi"})
            self.stdout.write("  Created Area: DHA Phase 6")
        else:
            self.stdout.write("  Area exists: DHA Phase 6")
        return area

    def _seed_landmark(self, area: Any, actor: Any) -> Any:
        """Create or retrieve Zamzama Boulevard landmark.

        Args:
            area: Parent Area instance.
            actor: AdminUser for AuditLog.

        Returns:
            Landmark instance.
        """
        from apps.geo.models import Landmark

        landmark, created = Landmark.objects.get_or_create(
            slug="zamzama-boulevard-karachi",
            defaults={
                "area": area,
                "name": "Zamzama Boulevard",
                "aliases": ["Zamzama", "Zamzama Street", "Zamzama Commercial Area"],
                "location": Point(67.0600, 24.8270, srid=4326),
                "is_active": True,
            },
        )
        if created:
            from apps.audit.utils import log_action
            log_action("LANDMARK_CREATED", actor, landmark, None, {}, {"name": "Zamzama Boulevard"})
            self.stdout.write("  Created Landmark: Zamzama Boulevard")
        else:
            self.stdout.write("  Landmark exists: Zamzama Boulevard")
        return landmark

    # -------------------------------------------------------------------------
    # Tags — 6 taxonomy tags (2 per type, no SYSTEM tags via API)
    # -------------------------------------------------------------------------

    def _seed_tags(self, actor: Any) -> None:
        """Create 10 seed tags covering LOCATION, CATEGORY, INTENT, TIME, and PROMOTION types.

        Args:
            actor: AdminUser for AuditLog.
        """
        from apps.audit.utils import log_action
        from apps.tags.models import Tag, TagType

        seed_tags = [
            {"name": "Karachi", "slug": "location-karachi", "tag_type": TagType.LOCATION,
             "display_label": "Karachi", "display_order": 1, "icon_name": "map-pin"},
            {"name": "DHA", "slug": "location-dha", "tag_type": TagType.LOCATION,
             "display_label": "DHA", "display_order": 2, "icon_name": "map-pin"},
            {"name": "Restaurant", "slug": "category-restaurant", "tag_type": TagType.CATEGORY,
             "display_label": "Restaurant", "display_order": 1, "icon_name": "utensils"},
            {"name": "Retail", "slug": "category-retail", "tag_type": TagType.CATEGORY,
             "display_label": "Retail", "display_order": 2, "icon_name": "shopping-bag"},
            {"name": "Dine In", "slug": "intent-dine-in", "tag_type": TagType.INTENT,
             "display_label": "Dine In", "display_order": 1, "icon_name": "coffee"},
            {"name": "Takeaway", "slug": "intent-takeaway", "tag_type": TagType.INTENT,
             "display_label": "Takeaway", "display_order": 2, "icon_name": "package"},
            {"name": "Happy Hour", "slug": "time-happy-hour", "tag_type": TagType.TIME,
             "display_label": "Happy Hour", "display_order": 1, "icon_name": "clock"},
            {"name": "Weekend Special", "slug": "time-weekend-special", "tag_type": TagType.TIME,
             "display_label": "Weekend Special", "display_order": 2, "icon_name": "calendar"},
            {"name": "20% Off", "slug": "promo-20-off", "tag_type": TagType.PROMOTION,
             "display_label": "20% Off", "display_order": 1, "icon_name": "tag"},
            {"name": "Buy 1 Get 1", "slug": "promo-bogo", "tag_type": TagType.PROMOTION,
             "display_label": "Buy 1 Get 1", "display_order": 2, "icon_name": "gift"},
        ]

        new_count = 0
        existing_count = 0
        for tag_data in seed_tags:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data["slug"],
                defaults=tag_data,
            )
            if created:
                log_action("TAG_CREATED", actor, tag, None, {}, {"name": tag.name, "tag_type": tag.tag_type})
                self.stdout.write(f"  Created Tag: {tag.name} [{tag.tag_type}]")
                new_count += 1
            else:
                self.stdout.write(f"  Tag exists: {tag.name}")
                existing_count += 1
        self.stdout.write(
            f"  Seeded {new_count + existing_count} tags ({new_count} new, {existing_count} existing)"
        )

    # -------------------------------------------------------------------------
    # Vendors — 3 sample vendors with encrypted phones and business hours
    # -------------------------------------------------------------------------

    def _seed_vendors(self, city: Any, area: Any, landmark: Any, actor: Any) -> None:
        """Create 3 sample vendors with encrypted phone numbers and business hours.

        Args:
            city: Karachi City instance.
            area: DHA Phase 6 Area instance.
            landmark: Zamzama Landmark instance.
            actor: AdminUser for AuditLog.
        """
        from apps.vendors.models import DataSource, Vendor
        from apps.vendors.services import create_vendor

        _STANDARD_HOURS = {
            "MON": {"open": "09:00", "close": "22:00", "is_closed": False},
            "TUE": {"open": "09:00", "close": "22:00", "is_closed": False},
            "WED": {"open": "09:00", "close": "22:00", "is_closed": False},
            "THU": {"open": "09:00", "close": "22:00", "is_closed": False},
            "FRI": {"open": "09:00", "close": "23:00", "is_closed": False},
            "SAT": {"open": "10:00", "close": "23:00", "is_closed": False},
            "SUN": {"open": "00:00", "close": "00:00", "is_closed": True},
        }

        vendors_data = [
            {
                "business_name": "Zamzama Grill House",
                "slug": "zamzama-grill-house",
                "gps_lon": 67.0601,
                "gps_lat": 24.8271,
                "phone": "+923001234567",
                "address_text": "Shop 12, Zamzama Boulevard, DHA Phase 6, Karachi",
                "description": "Premium grill restaurant on Zamzama Boulevard.",
                "data_source": DataSource.MANUAL_ENTRY,
            },
            {
                "business_name": "DHA Pharmacy Plus",
                "slug": "dha-pharmacy-plus",
                "gps_lon": 67.0610,
                "gps_lat": 24.8265,
                "phone": "+923009876543",
                "address_text": "Plot 45, Phase 6 Commercial, DHA, Karachi",
                "description": "24/7 pharmacy serving DHA Phase 6.",
                "data_source": DataSource.MANUAL_ENTRY,
            },
            {
                "business_name": "Karachi Artisan Bakery",
                "slug": "karachi-artisan-bakery",
                "gps_lon": 67.0595,
                "gps_lat": 24.8280,
                "phone": "+923331122334",
                "address_text": "Unit 3, Zamzama Lane, DHA Phase 6, Karachi",
                "description": "Artisan breads and pastries, freshly baked daily.",
                "data_source": DataSource.MANUAL_ENTRY,
            },
        ]

        for vd in vendors_data:
            if Vendor.all_objects.filter(slug=vd["slug"]).exists():
                self.stdout.write(f"  Vendor exists: {vd['business_name']}")
                continue

            vendor = create_vendor(
                business_name=vd["business_name"],
                slug=vd["slug"],
                city_id=str(city.id),
                area_id=str(area.id),
                gps_lon=vd["gps_lon"],
                gps_lat=vd["gps_lat"],
                actor=actor,
                request=None,
                phone=vd["phone"],
                description=vd["description"],
                address_text=vd["address_text"],
                landmark_id=str(landmark.id),
                business_hours=_STANDARD_HOURS,
                data_source=vd["data_source"],
            )
            self.stdout.write(f"  Created Vendor: {vendor.business_name}")
