"""
AirAd Backend — seed_geo_pk Management Command

Seeds Pakistan geo hierarchy for Islamabad and Faisalabad with all
real neighbourhoods/areas.

Idempotent — safe to run multiple times. Uses get_or_create() throughout.
Pakistan country record is shared with seed_data (Karachi) — no duplicate.

Usage:
    python manage.py seed_geo_pk
    python manage.py seed_geo_pk --city islamabad
    python manage.py seed_geo_pk --city faisalabad
"""

import logging
from typing import Any

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Area data — Islamabad
# ---------------------------------------------------------------------------

ISLAMABAD_AREAS = [
    # Sectors — F series
    {
        "name": "F-6",
        "slug": "f-6-islamabad",
        "lon": 73.0551,
        "lat": 33.7294,
        "aliases": ["F6", "Sector F-6"],
    },
    {
        "name": "F-7",
        "slug": "f-7-islamabad",
        "lon": 73.0479,
        "lat": 33.7215,
        "aliases": ["F7", "Sector F-7", "Jinnah Super"],
    },
    {
        "name": "F-8",
        "slug": "f-8-islamabad",
        "lon": 73.0390,
        "lat": 33.7150,
        "aliases": ["F8", "Sector F-8"],
    },
    {
        "name": "F-9",
        "slug": "f-9-islamabad",
        "lon": 73.0290,
        "lat": 33.7080,
        "aliases": ["F9", "Sector F-9", "Fatima Jinnah Park area"],
    },
    {
        "name": "F-10",
        "slug": "f-10-islamabad",
        "lon": 73.0200,
        "lat": 33.7010,
        "aliases": ["F10", "Sector F-10", "Markaz F-10"],
    },
    {
        "name": "F-11",
        "slug": "f-11-islamabad",
        "lon": 73.0100,
        "lat": 33.6950,
        "aliases": ["F11", "Sector F-11"],
    },
    # Sectors — G series
    {
        "name": "G-5",
        "slug": "g-5-islamabad",
        "lon": 73.0630,
        "lat": 33.7230,
        "aliases": ["G5", "Sector G-5", "Diplomatic Enclave area"],
    },
    {
        "name": "G-6",
        "slug": "g-6-islamabad",
        "lon": 73.0600,
        "lat": 33.7160,
        "aliases": ["G6", "Sector G-6", "Aabpara"],
    },
    {
        "name": "G-7",
        "slug": "g-7-islamabad",
        "lon": 73.0530,
        "lat": 33.7090,
        "aliases": ["G7", "Sector G-7", "Melody Market area"],
    },
    {
        "name": "G-8",
        "slug": "g-8-islamabad",
        "lon": 73.0450,
        "lat": 33.7020,
        "aliases": ["G8", "Sector G-8", "Karachi Company"],
    },
    {
        "name": "G-9",
        "slug": "g-9-islamabad",
        "lon": 73.0360,
        "lat": 33.6950,
        "aliases": ["G9", "Sector G-9", "Sabzi Mandi"],
    },
    {
        "name": "G-10",
        "slug": "g-10-islamabad",
        "lon": 73.0270,
        "lat": 33.6880,
        "aliases": ["G10", "Sector G-10"],
    },
    {
        "name": "G-11",
        "slug": "g-11-islamabad",
        "lon": 73.0170,
        "lat": 33.6810,
        "aliases": ["G11", "Sector G-11"],
    },
    {
        "name": "G-13",
        "slug": "g-13-islamabad",
        "lon": 72.9980,
        "lat": 33.6670,
        "aliases": ["G13", "Sector G-13"],
    },
    {
        "name": "G-14",
        "slug": "g-14-islamabad",
        "lon": 72.9880,
        "lat": 33.6600,
        "aliases": ["G14", "Sector G-14"],
    },
    {
        "name": "G-15",
        "slug": "g-15-islamabad",
        "lon": 72.9780,
        "lat": 33.6530,
        "aliases": ["G15", "Sector G-15"],
    },
    # Sectors — I series
    {
        "name": "I-8",
        "slug": "i-8-islamabad",
        "lon": 73.0600,
        "lat": 33.6820,
        "aliases": ["I8", "Sector I-8"],
    },
    {
        "name": "I-9",
        "slug": "i-9-islamabad",
        "lon": 73.0520,
        "lat": 33.6750,
        "aliases": ["I9", "Sector I-9", "Industrial Area I-9"],
    },
    {
        "name": "I-10",
        "slug": "i-10-islamabad",
        "lon": 73.0430,
        "lat": 33.6680,
        "aliases": ["I10", "Sector I-10"],
    },
    {
        "name": "I-11",
        "slug": "i-11-islamabad",
        "lon": 73.0330,
        "lat": 33.6610,
        "aliases": ["I11", "Sector I-11"],
    },
    # Sectors — E series
    {
        "name": "E-7",
        "slug": "e-7-islamabad",
        "lon": 73.0620,
        "lat": 33.7310,
        "aliases": ["E7", "Sector E-7"],
    },
    {
        "name": "E-11",
        "slug": "e-11-islamabad",
        "lon": 73.0050,
        "lat": 33.7200,
        "aliases": ["E11", "Sector E-11", "Margalla Hills area"],
    },
    # DHA Islamabad
    {
        "name": "DHA Phase 1",
        "slug": "dha-phase-1-islamabad",
        "lon": 73.1800,
        "lat": 33.5300,
        "aliases": ["DHA-1 Islamabad", "Defence Phase 1 Islamabad"],
    },
    {
        "name": "DHA Phase 2",
        "slug": "dha-phase-2-islamabad",
        "lon": 73.1900,
        "lat": 33.5200,
        "aliases": ["DHA-2 Islamabad", "Defence Phase 2 Islamabad"],
    },
    {
        "name": "DHA Phase 3",
        "slug": "dha-phase-3-islamabad",
        "lon": 73.2000,
        "lat": 33.5100,
        "aliases": ["DHA-3 Islamabad"],
    },
    # Bahria Town Islamabad
    {
        "name": "Bahria Town Phase 1-6",
        "slug": "bahria-town-phase-1-6-islamabad",
        "lon": 73.1500,
        "lat": 33.5500,
        "aliases": ["Bahria Islamabad", "Bahria Phase 1-6"],
    },
    {
        "name": "Bahria Town Phase 7",
        "slug": "bahria-town-phase-7-islamabad",
        "lon": 73.1600,
        "lat": 33.5400,
        "aliases": ["Bahria Phase 7 Islamabad"],
    },
    {
        "name": "Bahria Town Phase 8",
        "slug": "bahria-town-phase-8-islamabad",
        "lon": 73.1700,
        "lat": 33.5350,
        "aliases": ["Bahria Phase 8 Islamabad", "Safari Valley"],
    },
    # PWD / Gulberg
    {
        "name": "PWD Housing Society",
        "slug": "pwd-housing-islamabad",
        "lon": 73.0900,
        "lat": 33.6500,
        "aliases": ["PWD Islamabad", "PWD Colony"],
    },
    {
        "name": "Gulberg Islamabad",
        "slug": "gulberg-islamabad",
        "lon": 73.0800,
        "lat": 33.6600,
        "aliases": ["Gulberg Green Islamabad"],
    },
    # Rawalpindi border areas / satellite towns commonly associated
    {
        "name": "Bani Gala",
        "slug": "bani-gala-islamabad",
        "lon": 73.1100,
        "lat": 33.6800,
        "aliases": ["Banigala"],
    },
    {
        "name": "Saidpur Village",
        "slug": "saidpur-village-islamabad",
        "lon": 73.0750,
        "lat": 33.7500,
        "aliases": ["Saidpur", "Saidpur Road"],
    },
    {
        "name": "Tarlai",
        "slug": "tarlai-islamabad",
        "lon": 73.0300,
        "lat": 33.6400,
        "aliases": ["Tarlai Kalan"],
    },
    {
        "name": "Bhara Kahu",
        "slug": "bhara-kahu-islamabad",
        "lon": 73.1400,
        "lat": 33.6700,
        "aliases": ["Bharakahu"],
    },
    {
        "name": "Golra",
        "slug": "golra-islamabad",
        "lon": 72.9900,
        "lat": 33.6900,
        "aliases": ["Golra Sharif", "Golra Mor"],
    },
    {
        "name": "Noon",
        "slug": "noon-islamabad",
        "lon": 72.9700,
        "lat": 33.7100,
        "aliases": ["Noon area Islamabad"],
    },
    {
        "name": "Koral",
        "slug": "koral-islamabad",
        "lon": 73.1200,
        "lat": 33.6600,
        "aliases": ["Koral Chowk"],
    },
    {
        "name": "Humak",
        "slug": "humak-islamabad",
        "lon": 73.1600,
        "lat": 33.6500,
        "aliases": [],
    },
    # Blue Area / Commercial
    {
        "name": "Blue Area",
        "slug": "blue-area-islamabad",
        "lon": 73.0480,
        "lat": 33.7280,
        "aliases": ["Jinnah Avenue", "Blue Area Islamabad"],
    },
    {
        "name": "Centaurus Area",
        "slug": "centaurus-islamabad",
        "lon": 73.0470,
        "lat": 33.7270,
        "aliases": ["The Centaurus", "F-8 Markaz"],
    },
    # CDA Sectors — H series
    {
        "name": "H-8",
        "slug": "h-8-islamabad",
        "lon": 73.0520,
        "lat": 33.6900,
        "aliases": ["H8", "Sector H-8", "PIMS area"],
    },
    {
        "name": "H-9",
        "slug": "h-9-islamabad",
        "lon": 73.0430,
        "lat": 33.6830,
        "aliases": ["H9", "Sector H-9"],
    },
    {
        "name": "H-11",
        "slug": "h-11-islamabad",
        "lon": 73.0240,
        "lat": 33.6700,
        "aliases": ["H11", "Sector H-11", "Graveyard sector"],
    },
    # Margalla / Northern
    {
        "name": "Margalla Hills",
        "slug": "margalla-hills-islamabad",
        "lon": 73.0600,
        "lat": 33.7700,
        "aliases": ["Margalla", "Margalla National Park"],
    },
    {
        "name": "Shakarparian",
        "slug": "shakarparian-islamabad",
        "lon": 73.0550,
        "lat": 33.7050,
        "aliases": ["Shakarparian Hills"],
    },
]


# ---------------------------------------------------------------------------
# Area data — Faisalabad
# ---------------------------------------------------------------------------

FAISALABAD_AREAS = [
    # Clock Tower / Old City divisions
    {
        "name": "Ghanta Ghar",
        "slug": "ghanta-ghar-faisalabad",
        "lon": 73.0851,
        "lat": 31.4180,
        "aliases": ["Clock Tower", "Chowk Ghanta Ghar"],
    },
    {
        "name": "Katchery Bazaar",
        "slug": "katchery-bazaar-faisalabad",
        "lon": 73.0870,
        "lat": 31.4200,
        "aliases": ["Kachehri Bazaar"],
    },
    {
        "name": "Aminpur Bazaar",
        "slug": "aminpur-bazaar-faisalabad",
        "lon": 73.0820,
        "lat": 31.4220,
        "aliases": ["Aminpur Bazar"],
    },
    {
        "name": "Karkhana Bazaar",
        "slug": "karkhana-bazaar-faisalabad",
        "lon": 73.0800,
        "lat": 31.4240,
        "aliases": ["Karkhana Bazar", "Factory Area"],
    },
    {
        "name": "Chiniot Bazaar",
        "slug": "chiniot-bazaar-faisalabad",
        "lon": 73.0840,
        "lat": 31.4160,
        "aliases": ["Chiniot Bazar"],
    },
    {
        "name": "Bhawana Bazaar",
        "slug": "bhawana-bazaar-faisalabad",
        "lon": 73.0860,
        "lat": 31.4140,
        "aliases": ["Bhawana Bazar"],
    },
    {
        "name": "Montgomery Bazaar",
        "slug": "montgomery-bazaar-faisalabad",
        "lon": 73.0880,
        "lat": 31.4120,
        "aliases": ["Montgomery Bazar"],
    },
    {
        "name": "Rail Bazaar",
        "slug": "rail-bazaar-faisalabad",
        "lon": 73.0900,
        "lat": 31.4100,
        "aliases": ["Railway Bazaar", "Rail Bazar"],
    },
    # Main residential / commercial areas
    {
        "name": "Peoples Colony",
        "slug": "peoples-colony-faisalabad",
        "lon": 73.0700,
        "lat": 31.4300,
        "aliases": ["People's Colony No.1", "People's Colony No.2"],
    },
    {
        "name": "Gulberg",
        "slug": "gulberg-faisalabad",
        "lon": 73.0650,
        "lat": 31.4350,
        "aliases": ["Gulberg Faisalabad"],
    },
    {
        "name": "Madina Town",
        "slug": "madina-town-faisalabad",
        "lon": 73.0600,
        "lat": 31.4400,
        "aliases": ["Madina Town Faisalabad"],
    },
    {
        "name": "Jinnah Colony",
        "slug": "jinnah-colony-faisalabad",
        "lon": 73.0750,
        "lat": 31.4250,
        "aliases": ["Jinnah Colony Faisalabad"],
    },
    {
        "name": "Samanabad",
        "slug": "samanabad-faisalabad",
        "lon": 73.0550,
        "lat": 31.4450,
        "aliases": ["Samanabad Faisalabad"],
    },
    {
        "name": "Millat Town",
        "slug": "millat-town-faisalabad",
        "lon": 73.0500,
        "lat": 31.4500,
        "aliases": ["Millat Town Faisalabad"],
    },
    {
        "name": "Kohinoor City",
        "slug": "kohinoor-city-faisalabad",
        "lon": 73.0450,
        "lat": 31.4550,
        "aliases": ["Kohinoor Faisalabad"],
    },
    {
        "name": "Susan Road",
        "slug": "susan-road-faisalabad",
        "lon": 73.0400,
        "lat": 31.4600,
        "aliases": ["Susan Road Area"],
    },
    {
        "name": "Sargodha Road",
        "slug": "sargodha-road-faisalabad",
        "lon": 73.0300,
        "lat": 31.4700,
        "aliases": ["Sargodha Road Faisalabad"],
    },
    {
        "name": "Jaranwala Road",
        "slug": "jaranwala-road-faisalabad",
        "lon": 73.1100,
        "lat": 31.4000,
        "aliases": ["Jaranwala Road Area"],
    },
    {
        "name": "Sheikhupura Road",
        "slug": "sheikhupura-road-faisalabad",
        "lon": 73.0200,
        "lat": 31.4800,
        "aliases": ["Sheikhupura Road Area"],
    },
    {
        "name": "Satiana Road",
        "slug": "satiana-road-faisalabad",
        "lon": 73.0950,
        "lat": 31.3900,
        "aliases": ["Satiana Road Area"],
    },
    # DHA Faisalabad
    {
        "name": "DHA Faisalabad",
        "slug": "dha-faisalabad",
        "lon": 73.0350,
        "lat": 31.4650,
        "aliases": ["Defence Housing Authority Faisalabad", "DHA FSD"],
    },
    # Bahria Town Faisalabad
    {
        "name": "Bahria Town Faisalabad",
        "slug": "bahria-town-faisalabad",
        "lon": 73.0250,
        "lat": 31.4750,
        "aliases": ["Bahria Faisalabad"],
    },
    # Industrial / textile zones
    {
        "name": "Industrial Estate",
        "slug": "industrial-estate-faisalabad",
        "lon": 73.1000,
        "lat": 31.4050,
        "aliases": ["FIEDMC", "Faisalabad Industrial Estate"],
    },
    {
        "name": "Khurrianwala",
        "slug": "khurrianwala-faisalabad",
        "lon": 73.1500,
        "lat": 31.4200,
        "aliases": ["Khurrianwala Industrial Area"],
    },
    # Other key areas
    {
        "name": "Dijkot",
        "slug": "dijkot-faisalabad",
        "lon": 73.0200,
        "lat": 31.3900,
        "aliases": ["Dijkot Road"],
    },
    {
        "name": "Chak Jhumra",
        "slug": "chak-jhumra-faisalabad",
        "lon": 73.1800,
        "lat": 31.5600,
        "aliases": ["Chak Jhumra Town"],
    },
    {
        "name": "Sammundri Road",
        "slug": "sammundri-road-faisalabad",
        "lon": 73.1200,
        "lat": 31.3800,
        "aliases": ["Sammundri Road Area"],
    },
    {
        "name": "Lyallpur Town",
        "slug": "lyallpur-town-faisalabad",
        "lon": 73.0900,
        "lat": 31.4150,
        "aliases": ["Lyallpur", "Old Faisalabad"],
    },
    {
        "name": "Batala Colony",
        "slug": "batala-colony-faisalabad",
        "lon": 73.0800,
        "lat": 31.4350,
        "aliases": ["Batala Colony Faisalabad"],
    },
    {
        "name": "Nishatabad",
        "slug": "nishatabad-faisalabad",
        "lon": 73.0750,
        "lat": 31.4400,
        "aliases": ["Nishatabad Faisalabad"],
    },
    {
        "name": "Shadman Colony",
        "slug": "shadman-colony-faisalabad",
        "lon": 73.0680,
        "lat": 31.4380,
        "aliases": ["Shadman Faisalabad"],
    },
    {
        "name": "Gulshan-e-Iqbal",
        "slug": "gulshan-e-iqbal-faisalabad",
        "lon": 73.0620,
        "lat": 31.4420,
        "aliases": ["Gulshan Iqbal Faisalabad"],
    },
    {
        "name": "Canal Road",
        "slug": "canal-road-faisalabad",
        "lon": 73.0580,
        "lat": 31.4460,
        "aliases": ["Canal Road Faisalabad", "Canal Bank Road"],
    },
    {
        "name": "D-Ground",
        "slug": "d-ground-faisalabad",
        "lon": 73.0920,
        "lat": 31.4080,
        "aliases": ["D Ground Faisalabad"],
    },
    {
        "name": "Iqbal Stadium Area",
        "slug": "iqbal-stadium-faisalabad",
        "lon": 73.0870,
        "lat": 31.4190,
        "aliases": ["Iqbal Stadium", "Stadium Road Faisalabad"],
    },
]


class Command(BaseCommand):
    """Seed Pakistan geo hierarchy: Islamabad and Faisalabad with all areas."""

    help = "Seed Pakistan → Islamabad + Faisalabad with all real areas (idempotent)"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--city",
            choices=["islamabad", "faisalabad", "both"],
            default="both",
            help="Which city to seed (default: both).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(self.style.MIGRATE_HEADING("AirAd seed_geo_pk starting..."))

        try:
            with transaction.atomic():
                actor = self._get_or_create_actor()
                country = self._seed_country(actor)

                city_choice = options["city"]

                if city_choice in ("islamabad", "both"):
                    islamabad = self._seed_city_islamabad(country, actor)
                    self._seed_areas(islamabad, ISLAMABAD_AREAS, actor)

                if city_choice in ("faisalabad", "both"):
                    faisalabad = self._seed_city_faisalabad(country, actor)
                    self._seed_areas(faisalabad, FAISALABAD_AREAS, actor)

        except Exception as exc:
            raise CommandError(f"seed_geo_pk failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("seed_geo_pk complete."))

    # -------------------------------------------------------------------------
    # Actor — reuse existing SUPER_ADMIN or create a system actor
    # -------------------------------------------------------------------------

    def _get_or_create_actor(self) -> Any:
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
            self.stdout.write(f"  Using actor: {user.email}")
        return user

    # -------------------------------------------------------------------------
    # Country
    # -------------------------------------------------------------------------

    def _seed_country(self, actor: Any) -> Any:
        from apps.geo.models import Country

        country, created = Country.objects.get_or_create(
            code="PK",
            defaults={"name": "Pakistan", "is_active": True},
        )
        if created:
            from apps.audit.utils import log_action

            log_action(
                "COUNTRY_CREATED",
                actor,
                country,
                None,
                {},
                {"name": "Pakistan", "code": "PK"},
            )
            self.stdout.write("  Created Country: Pakistan (PK)")
        else:
            self.stdout.write("  Country exists: Pakistan (PK)")
        return country

    # -------------------------------------------------------------------------
    # Cities
    # -------------------------------------------------------------------------

    def _seed_city_islamabad(self, country: Any, actor: Any) -> Any:
        from apps.geo.models import City

        city, created = City.objects.get_or_create(
            slug="islamabad",
            defaults={
                "country": country,
                "name": "Islamabad",
                "aliases": ["اسلام آباد", "ICT", "Federal Capital"],
                "centroid": Point(73.0479, 33.6844, srid=4326),
                "is_active": True,
                "display_order": 2,
            },
        )
        if created:
            from apps.audit.utils import log_action

            log_action(
                "CITY_CREATED",
                actor,
                city,
                None,
                {},
                {"name": "Islamabad", "slug": "islamabad"},
            )
            self.stdout.write("  Created City: Islamabad")
        else:
            self.stdout.write("  City exists: Islamabad")
        return city

    def _seed_city_faisalabad(self, country: Any, actor: Any) -> Any:
        from apps.geo.models import City

        city, created = City.objects.get_or_create(
            slug="faisalabad",
            defaults={
                "country": country,
                "name": "Faisalabad",
                "aliases": ["فیصل آباد", "Lyallpur", "Manchester of Pakistan"],
                "centroid": Point(73.0851, 31.4180, srid=4326),
                "is_active": True,
                "display_order": 3,
            },
        )
        if created:
            from apps.audit.utils import log_action

            log_action(
                "CITY_CREATED",
                actor,
                city,
                None,
                {},
                {"name": "Faisalabad", "slug": "faisalabad"},
            )
            self.stdout.write("  Created City: Faisalabad")
        else:
            self.stdout.write("  City exists: Faisalabad")
        return city

    # -------------------------------------------------------------------------
    # Areas — bulk idempotent
    # -------------------------------------------------------------------------

    def _seed_areas(self, city: Any, areas_data: list[dict], actor: Any) -> None:
        from apps.audit.utils import log_action
        from apps.geo.models import Area

        new_count = 0
        existing_count = 0

        for data in areas_data:
            centroid = Point(data["lon"], data["lat"], srid=4326)
            area, created = Area.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "city": city,
                    "name": data["name"],
                    "aliases": data.get("aliases", []),
                    "centroid": centroid,
                    "is_active": True,
                },
            )
            if created:
                log_action(
                    "AREA_CREATED",
                    actor,
                    area,
                    None,
                    {},
                    {"name": area.name, "slug": area.slug, "city": city.name},
                )
                self.stdout.write(f"    + Area: {area.name} ({city.name})")
                new_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  {city.name}: {new_count} new areas, {existing_count} already existed"
            )
        )
