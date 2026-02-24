"""
AirAd Backend E2E — Geo & Tags User Journey

Tests full end-to-end flows for geo hierarchy and tag management:

Journey 1: Country → City → Area → Landmark creation chain
Journey 2: City update and immutability constraints
Journey 3: Tag lifecycle (create → update → delete)
Journey 4: RBAC for geo and tag endpoints
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import AdminUser


# ---------------------------------------------------------------------------
# Journey 1: Full geo hierarchy creation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestGeoHierarchyCreationJourney:
    """Create Country → City → Area → Landmark in sequence."""

    def test_create_full_geo_hierarchy(self, auth_client: APIClient) -> None:
        """Create a complete geo hierarchy from scratch."""
        # Step 1: Create country
        country_resp = auth_client.post(
            reverse("geo-country-list"),
            {"name": "E2E Country", "code": "EC", "is_active": True},
            format="json",
        )
        assert country_resp.status_code == status.HTTP_201_CREATED
        assert country_resp.data["data"]["code"] == "EC"
        country_id = country_resp.data["data"]["id"]

        # Step 2: Create city under that country
        city_resp = auth_client.post(
            reverse("geo-city-list"),
            {
                "country_id": country_id,
                "name": "E2E City",
                "slug": "e2e-city",
                "centroid_lon": 67.0,
                "centroid_lat": 24.8,
                "is_active": True,
                "display_order": 99,
            },
            format="json",
        )
        assert city_resp.status_code == status.HTTP_201_CREATED
        assert city_resp.data["data"]["name"] == "E2E City"
        city_id = city_resp.data["data"]["id"]

        # Step 3: Verify city appears in list
        cities_resp = auth_client.get(reverse("geo-city-list"))
        assert cities_resp.status_code == status.HTTP_200_OK
        city_ids = [c["id"] for c in cities_resp.data["data"]]
        assert city_id in city_ids

        # Step 4: Create area under that city
        area_resp = auth_client.post(
            reverse("geo-area-list"),
            {
                "city_id": city_id,
                "name": "E2E Area",
                "slug": "e2e-area",
                "centroid_lon": 67.05,
                "centroid_lat": 24.82,
                "is_active": True,
            },
            format="json",
        )
        assert area_resp.status_code == status.HTTP_201_CREATED
        assert area_resp.data["data"]["name"] == "E2E Area"
        area_id = area_resp.data["data"]["id"]

        # Step 5: Create landmark under that area
        landmark_resp = auth_client.post(
            reverse("geo-landmark-list"),
            {
                "area_id": area_id,
                "name": "E2E Landmark",
                "slug": "e2e-landmark",
                "location_lon": 67.06,
                "location_lat": 24.83,
                "is_active": True,
            },
            format="json",
        )
        assert landmark_resp.status_code == status.HTTP_201_CREATED
        assert landmark_resp.data["data"]["name"] == "E2E Landmark"

    def test_duplicate_country_code_returns_400(self, auth_client: APIClient, country) -> None:
        """Creating a country with an existing code returns 400."""
        resp = auth_client.post(
            reverse("geo-country-list"),
            {"name": "Duplicate Pakistan", "code": "PK", "is_active": True},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_city_slug_returns_400(
        self, auth_client: APIClient, country, city
    ) -> None:
        """Creating a city with an existing slug returns 400."""
        resp = auth_client.post(
            reverse("geo-city-list"),
            {
                "country_id": str(country.id),
                "name": "Duplicate City",
                "slug": "karachi-test",  # same as fixture
                "centroid_lon": 67.0,
                "centroid_lat": 24.8,
                "is_active": True,
                "display_order": 99,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Journey 2: City update constraints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestCityUpdateJourney:
    """City name can be updated; slug is immutable."""

    def test_update_city_name(self, auth_client: APIClient, city) -> None:
        """PATCH city name succeeds."""
        resp = auth_client.patch(
            reverse("geo-city-detail", kwargs={"pk": str(city.id)}),
            {"name": "Updated Karachi"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["name"] == "Updated Karachi"

    def test_update_city_slug_returns_400(self, auth_client: APIClient, city) -> None:
        """PATCH city slug returns 400 (immutable)."""
        resp = auth_client.patch(
            reverse("geo-city-detail", kwargs={"pk": str(city.id)}),
            {"slug": "new-slug"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_deactivate_city(self, auth_client: APIClient, city) -> None:
        """PATCH is_active=False deactivates city."""
        resp = auth_client.patch(
            reverse("geo-city-detail", kwargs={"pk": str(city.id)}),
            {"is_active": False},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["is_active"] is False

    def test_get_city_detail(self, auth_client: APIClient, city) -> None:
        """GET city detail returns correct data."""
        resp = auth_client.get(
            reverse("geo-city-detail", kwargs={"pk": str(city.id)})
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["data"]["name"] == "Karachi"
        assert resp.data["data"]["slug"] == "karachi-test"


# ---------------------------------------------------------------------------
# Journey 3: Tag lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestTagLifecycleJourney:
    """Create → Update → Delete tag; SYSTEM tags are protected."""

    def test_full_tag_lifecycle(self, auth_client: APIClient) -> None:
        """Create, update, and delete a CATEGORY tag."""
        # Step 1: Create tag
        create_resp = auth_client.post(
            reverse("tag-list"),
            {
                "name": "E2E Tag",
                "slug": "e2e-tag",
                "tag_type": "CATEGORY",
                "display_label": "E2E Tag Label",
                "is_active": True,
            },
            format="json",
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        tag_id = create_resp.data["data"]["id"]
        assert create_resp.data["data"]["tag_type"] == "CATEGORY"

        # Step 2: Verify tag appears in list
        list_resp = auth_client.get(reverse("tag-list"))
        assert list_resp.status_code == status.HTTP_200_OK
        tag_ids = [t["id"] for t in list_resp.data["data"]]
        assert tag_id in tag_ids

        # Step 3: Update tag name
        update_resp = auth_client.patch(
            reverse("tag-detail", kwargs={"pk": tag_id}),
            {"name": "Updated E2E Tag"},
            format="json",
        )
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.data["data"]["name"] == "Updated E2E Tag"

        # Step 4: Deactivate tag
        deactivate_resp = auth_client.patch(
            reverse("tag-detail", kwargs={"pk": tag_id}),
            {"is_active": False},
            format="json",
        )
        assert deactivate_resp.status_code == status.HTTP_200_OK
        assert deactivate_resp.data["data"]["is_active"] is False

        # Step 5: Delete tag
        delete_resp = auth_client.delete(
            reverse("tag-detail", kwargs={"pk": tag_id})
        )
        assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

        # Step 6: Verify tag is gone
        from apps.tags.models import Tag
        assert not Tag.objects.filter(id=tag_id).exists()

    def test_cannot_create_system_tag(self, auth_client: APIClient) -> None:
        """Creating a SYSTEM tag returns 400/403."""
        resp = auth_client.post(
            reverse("tag-list"),
            {
                "name": "System Tag",
                "slug": "system-tag-e2e",
                "tag_type": "SYSTEM",
                "display_label": "System",
                "is_active": True,
            },
            format="json",
        )
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_cannot_update_system_tag(self, auth_client: APIClient, category_tag) -> None:
        """Updating a SYSTEM tag returns 400/403."""
        from apps.tags.models import Tag, TagType

        system_tag = Tag.objects.create(
            name="Protected System Tag",
            slug="protected-system-tag",
            tag_type=TagType.SYSTEM,
            display_label="Protected",
            is_active=True,
        )
        resp = auth_client.patch(
            reverse("tag-detail", kwargs={"pk": str(system_tag.id)}),
            {"name": "Hacked"},
            format="json",
        )
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tag_slug_immutable(self, auth_client: APIClient, category_tag) -> None:
        """Updating tag slug returns 400."""
        resp = auth_client.patch(
            reverse("tag-detail", kwargs={"pk": str(category_tag.id)}),
            {"slug": "new-slug"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_tag_slug_returns_400(
        self, auth_client: APIClient, category_tag
    ) -> None:
        """Creating a tag with an existing slug returns 400."""
        resp = auth_client.post(
            reverse("tag-list"),
            {
                "name": "Duplicate Tag",
                "slug": "category-restaurant-test",  # same as fixture
                "tag_type": "INTENT",
                "display_label": "Duplicate",
                "is_active": True,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Journey 4: Geo RBAC
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.integration
class TestGeoRBACJourney:
    """Geo endpoints enforce role-based access."""

    def test_unauthenticated_cannot_list_cities(self, api_client: APIClient) -> None:
        """Unauthenticated request to geo cities returns 401."""
        resp = api_client.get(reverse("geo-city-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_create_country(self, api_client: APIClient) -> None:
        """Unauthenticated request to create country returns 401."""
        resp = api_client.post(
            reverse("geo-country-list"),
            {"name": "Test", "code": "TX", "is_active": True},
            format="json",
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_field_agent_cannot_create_city(self, api_client: APIClient, country) -> None:
        """FIELD_AGENT cannot create cities."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.accounts.models import AdminUser, AdminRole

        agent = AdminUser.objects.create_user(
            email="agent_geo@test.airaad.com",
            password="TestPass@123!",
            full_name="Field Agent",
            role=AdminRole.FIELD_AGENT,
        )
        refresh = RefreshToken.for_user(agent)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        resp = api_client.post(
            reverse("geo-city-list"),
            {
                "country_id": str(country.id),
                "name": "Unauthorized City",
                "slug": "unauthorized-city",
                "centroid_lon": 67.0,
                "centroid_lat": 24.8,
                "is_active": True,
                "display_order": 99,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
