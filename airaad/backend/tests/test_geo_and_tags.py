"""
AirAd — tests/test_geo_and_tags.py

Targeted tests for geo/services.py and tags/services.py to boost coverage.
"""
from __future__ import annotations

import pytest

from apps.geo.models import Area, City, Country, Landmark
from apps.geo.services import (
    create_area,
    create_city,
    create_country,
    create_landmark,
    update_city,
)
from apps.tags.models import Tag, TagType
from apps.tags.services import create_tag, delete_tag, update_tag
from tests.factories import (
    AdminUserFactory,
    AreaFactory,
    CityFactory,
    CountryFactory,
    TagFactory,
)


# ---------------------------------------------------------------------------
# Geo — Country
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateCountry:
    def test_creates_country(self) -> None:
        actor = AdminUserFactory()
        country = create_country("Testland", "TL", actor, None)
        assert Country.objects.filter(code="TL").exists()
        assert country.name == "Testland"

    def test_code_uppercased(self) -> None:
        actor = AdminUserFactory()
        country = create_country("Lowercase", "lc", actor, None)
        assert country.code == "LC"

    def test_invalid_code_raises(self) -> None:
        actor = AdminUserFactory()
        with pytest.raises(ValueError, match="2 characters"):
            create_country("Bad", "XYZ", actor, None)

    def test_duplicate_code_raises(self) -> None:
        actor = AdminUserFactory()
        create_country("First", "FX", actor, None)
        with pytest.raises(ValueError, match="already exists"):
            create_country("Second", "FX", actor, None)


# ---------------------------------------------------------------------------
# Geo — City
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateCity:
    def test_creates_city(self) -> None:
        country = CountryFactory()
        actor = AdminUserFactory()
        city = create_city(country, "Metropolis", "metropolis", 67.0, 24.8, actor, None)
        assert City.objects.filter(slug="metropolis").exists()
        assert city.name == "Metropolis"

    def test_duplicate_slug_raises(self) -> None:
        country = CountryFactory()
        actor = AdminUserFactory()
        create_city(country, "City A", "unique-city", 67.0, 24.8, actor, None)
        with pytest.raises(ValueError, match="already exists"):
            create_city(country, "City B", "unique-city", 67.1, 24.9, actor, None)

    def test_aliases_default_to_empty_list(self) -> None:
        country = CountryFactory()
        actor = AdminUserFactory()
        city = create_city(country, "NoAlias", "no-alias-city", 67.0, 24.8, actor, None)
        assert city.aliases == []


@pytest.mark.django_db
class TestUpdateCity:
    def test_updates_name(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        updated = update_city(city, {"name": "New Name"}, actor, None)
        assert updated.name == "New Name"

    def test_slug_immutable_raises(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        with pytest.raises(ValueError, match="immutable"):
            update_city(city, {"slug": "new-slug"}, actor, None)

    def test_updates_is_active(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        updated = update_city(city, {"is_active": False}, actor, None)
        assert updated.is_active is False


# ---------------------------------------------------------------------------
# Tags — create_tag
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateTag:
    def test_creates_tag(self) -> None:
        actor = AdminUserFactory()
        tag = create_tag("Happy Hour", "happy-hour", TagType.TIME, actor, None)
        assert Tag.objects.filter(slug="happy-hour").exists()
        assert tag.tag_type == TagType.TIME

    def test_system_tag_raises(self) -> None:
        actor = AdminUserFactory()
        with pytest.raises(PermissionError, match="SYSTEM"):
            create_tag("System Tag", "sys-tag", TagType.SYSTEM, actor, None)

    def test_duplicate_slug_raises(self) -> None:
        actor = AdminUserFactory()
        create_tag("Tag One", "dup-slug", TagType.CATEGORY, actor, None)
        with pytest.raises(ValueError, match="already exists"):
            create_tag("Tag Two", "dup-slug", TagType.CATEGORY, actor, None)

    def test_display_label_defaults_to_name(self) -> None:
        actor = AdminUserFactory()
        tag = create_tag("Auto Label", "auto-label", TagType.INTENT, actor, None)
        assert tag.display_label == "Auto Label"


# ---------------------------------------------------------------------------
# Tags — update_tag
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUpdateTag:
    def test_updates_name(self) -> None:
        tag = TagFactory(tag_type=TagType.CATEGORY)
        actor = AdminUserFactory()
        updated = update_tag(tag, {"name": "Updated Name"}, actor, None)
        assert updated.name == "Updated Name"

    def test_slug_immutable_raises(self) -> None:
        tag = TagFactory(tag_type=TagType.CATEGORY)
        actor = AdminUserFactory()
        with pytest.raises(ValueError, match="immutable"):
            update_tag(tag, {"slug": "new-slug"}, actor, None)

    def test_system_tag_update_raises(self) -> None:
        tag = TagFactory(tag_type=TagType.SYSTEM)
        actor = AdminUserFactory()
        with pytest.raises(PermissionError, match="SYSTEM"):
            update_tag(tag, {"name": "Hacked"}, actor, None)

    def test_cannot_change_type_to_system(self) -> None:
        tag = TagFactory(tag_type=TagType.CATEGORY)
        actor = AdminUserFactory()
        with pytest.raises(PermissionError, match="SYSTEM"):
            update_tag(tag, {"tag_type": TagType.SYSTEM}, actor, None)

    def test_deactivate_tag(self) -> None:
        tag = TagFactory(tag_type=TagType.CATEGORY)
        actor = AdminUserFactory()
        updated = update_tag(tag, {"is_active": False}, actor, None)
        assert updated.is_active is False


# ---------------------------------------------------------------------------
# Tags — delete_tag
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDeleteTag:
    def test_deletes_tag(self) -> None:
        tag = TagFactory(tag_type=TagType.CATEGORY)
        tag_id = tag.id
        actor = AdminUserFactory()
        delete_tag(tag, actor, None)
        assert not Tag.objects.filter(id=tag_id).exists()

    def test_system_tag_delete_raises(self) -> None:
        tag = TagFactory(tag_type=TagType.SYSTEM)
        actor = AdminUserFactory()
        with pytest.raises(PermissionError, match="SYSTEM"):
            delete_tag(tag, actor, None)


# ---------------------------------------------------------------------------
# Tags — usage_count annotation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTagUsageCount:
    def test_usage_count_zero_for_unassigned_tag(self) -> None:
        """Tag with no vendors assigned returns usage_count=0."""
        from django.db.models import Count

        tag = TagFactory(tag_type=TagType.CATEGORY)
        annotated = Tag.objects.annotate(usage_count=Count("vendors")).get(id=tag.id)
        assert annotated.usage_count == 0

    def test_usage_count_reflects_vendor_assignments(self) -> None:
        """usage_count equals the number of vendors the tag is assigned to."""
        from django.db.models import Count

        from tests.factories import VendorFactory

        tag = TagFactory(tag_type=TagType.CATEGORY)
        v1 = VendorFactory()
        v2 = VendorFactory()
        v1.tags.add(tag)
        v2.tags.add(tag)

        annotated = Tag.objects.annotate(usage_count=Count("vendors")).get(id=tag.id)
        assert annotated.usage_count == 2


# ---------------------------------------------------------------------------
# Geo — Area
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateArea:
    def test_creates_area(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        area = create_area(city, "Test Area", "test-area-svc", actor, None)
        assert Area.objects.filter(slug="test-area-svc").exists()
        assert area.name == "Test Area"

    def test_duplicate_slug_raises(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        create_area(city, "Area One", "dup-area-slug", actor, None)
        with pytest.raises(ValueError, match="already exists"):
            create_area(city, "Area Two", "dup-area-slug", actor, None)

    def test_with_centroid(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        area = create_area(city, "Centroid Area", "centroid-area", actor, None,
                           centroid_lon=67.06, centroid_lat=24.82)
        assert area.centroid is not None

    def test_aliases_default_to_empty(self) -> None:
        city = CityFactory()
        actor = AdminUserFactory()
        area = create_area(city, "No Alias Area", "no-alias-area", actor, None)
        assert area.aliases == []


# ---------------------------------------------------------------------------
# Geo — Landmark
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateLandmark:
    def test_creates_landmark(self) -> None:
        area = AreaFactory()
        actor = AdminUserFactory()
        lm = create_landmark(area, "Test Landmark", "test-landmark-svc",
                             67.06, 24.82, actor, None)
        assert Landmark.objects.filter(slug="test-landmark-svc").exists()
        assert lm.name == "Test Landmark"

    def test_duplicate_slug_raises(self) -> None:
        area = AreaFactory()
        actor = AdminUserFactory()
        create_landmark(area, "LM One", "dup-lm-slug", 67.0, 24.8, actor, None)
        with pytest.raises(ValueError, match="already exists"):
            create_landmark(area, "LM Two", "dup-lm-slug", 67.1, 24.9, actor, None)

    def test_aliases_default_to_empty(self) -> None:
        area = AreaFactory()
        actor = AdminUserFactory()
        lm = create_landmark(area, "No Alias LM", "no-alias-lm", 67.0, 24.8, actor, None)
        assert lm.aliases == []
