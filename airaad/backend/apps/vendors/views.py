"""
AirAd Backend — Vendors Views

Zero business logic — all delegated to vendors/services.py (R4).
Every view uses RolePermission.for_roles() (R3).
get_queryset() always filters is_deleted=False via ActiveVendorManager.
All views decorated with @extend_schema.
"""

import logging

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import AdminRole
from apps.accounts.permissions import RolePermission
from core.exceptions import success_response
from core.pagination import StandardResultsPagination

from .models import Vendor
from .serializers import (
    CreateVendorSerializer,
    QCStatusUpdateSerializer,
    UpdateVendorSerializer,
    VendorListSerializer,
    VendorSerializer,
)
from .services import create_vendor, soft_delete_vendor, update_qc_status, update_vendor

logger = logging.getLogger(__name__)


class VendorListCreateView(APIView):
    """List vendors (paginated) or create a new one."""

    permission_classes = [RolePermission.for_roles(
        AdminRole.SUPER_ADMIN, AdminRole.CITY_MANAGER,
        AdminRole.DATA_ENTRY, AdminRole.QA_REVIEWER, AdminRole.ANALYST,
    )]

    @extend_schema(
        tags=["Vendors"],
        summary="List vendors (paginated)",
        parameters=[
            OpenApiParameter(name="city_id", description="Filter by city UUID", required=False, type=str),
            OpenApiParameter(name="area_id", description="Filter by area UUID", required=False, type=str),
            OpenApiParameter(name="qc_status", description="Filter by QC status", required=False, type=str),
            OpenApiParameter(name="data_source", description="Filter by data source", required=False, type=str),
        ],
        responses={200: VendorListSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return paginated list of non-deleted vendors with optional filters.

        Args:
            request: Authenticated HTTP request.

        Returns:
            Paginated vendor list.
        """
        qs = (
            Vendor.objects
            .select_related("city", "area", "landmark")
            .order_by("-created_at")
        )

        city_id = request.query_params.get("city_id")
        if city_id:
            qs = qs.filter(city_id=city_id)

        area_id = request.query_params.get("area_id")
        if area_id:
            qs = qs.filter(area_id=area_id)

        qc_status = request.query_params.get("qc_status")
        if qc_status:
            qs = qs.filter(qc_status=qc_status)

        data_source = request.query_params.get("data_source")
        if data_source:
            qs = qs.filter(data_source=data_source)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(VendorListSerializer(page, many=True).data)

    @extend_schema(
        tags=["Vendors"],
        summary="Create vendor (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY)",
        request=CreateVendorSerializer,
        responses={201: VendorSerializer, 400: OpenApiResponse(description="Validation error")},
    )
    def post(self, request: Request) -> Response:
        """Create a new vendor. Phone is encrypted in services.py.

        Args:
            request: HTTP request with vendor creation data.

        Returns:
            201 with new vendor data on success.
        """
        serializer = CreateVendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            vendor = create_vendor(
                business_name=d["business_name"],
                slug=d["slug"],
                city_id=str(d["city_id"]),
                area_id=str(d["area_id"]),
                gps_lon=d["longitude"],
                gps_lat=d["latitude"],
                actor=request.user,
                request=request._request,
                phone=d.get("phone", ""),
                description=d.get("description", ""),
                address_text=d.get("address_text", ""),
                landmark_id=str(d["landmark_id"]) if d.get("landmark_id") else None,
                business_hours=d.get("business_hours"),
                data_source=d.get("data_source", "MANUAL_ENTRY"),
            )
        except ValueError as e:
            return Response(
                {"success": False, "data": None, "message": str(e), "errors": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(
            data=VendorSerializer(vendor).data,
            message="Vendor created",
            status_code=status.HTTP_201_CREATED,
        )


class VendorDetailView(APIView):
    """Retrieve, update, or soft-delete a single vendor."""

    permission_classes = [RolePermission.for_roles(
        AdminRole.SUPER_ADMIN, AdminRole.CITY_MANAGER,
        AdminRole.DATA_ENTRY, AdminRole.QA_REVIEWER, AdminRole.FIELD_AGENT,
    )]

    def _get_vendor(self, pk: str) -> Vendor | None:
        """Fetch non-deleted vendor by PK.

        Args:
            pk: UUID string of the vendor.

        Returns:
            Vendor instance or None.
        """
        try:
            return Vendor.objects.select_related(
                "city", "area", "landmark", "qc_reviewed_by"
            ).get(id=pk)
        except Vendor.DoesNotExist:
            return None

    @extend_schema(tags=["Vendors"], summary="Get vendor detail", responses={200: VendorSerializer})
    def get(self, request: Request, pk: str) -> Response:
        """Return a single vendor by ID. Phone is decrypted in serializer.

        Args:
            request: Authenticated HTTP request.
            pk: Vendor UUID.

        Returns:
            200 with vendor data, 404 if not found.
        """
        vendor = self._get_vendor(pk)
        if vendor is None:
            return Response(
                {"success": False, "data": None, "message": "Vendor not found", "errors": {}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return success_response(data=VendorSerializer(vendor).data)

    @extend_schema(
        tags=["Vendors"],
        summary="Update vendor (SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY)",
        request=UpdateVendorSerializer,
        responses={200: VendorSerializer},
    )
    def patch(self, request: Request, pk: str) -> Response:
        """Partially update a vendor. Phone re-encrypted in services.py.

        Args:
            request: HTTP request with update data.
            pk: Vendor UUID.

        Returns:
            200 with updated vendor data.
        """
        vendor = self._get_vendor(pk)
        if vendor is None:
            return Response(
                {"success": False, "data": None, "message": "Vendor not found", "errors": {}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UpdateVendorSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            vendor = update_vendor(
                vendor=vendor,
                updates=serializer.validated_data,
                actor=request.user,
                request=request._request,
            )
        except ValueError as e:
            return Response(
                {"success": False, "data": None, "message": str(e), "errors": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(data=VendorSerializer(vendor).data)

    @extend_schema(
        tags=["Vendors"],
        summary="Soft-delete vendor (SUPER_ADMIN, CITY_MANAGER)",
        responses={204: OpenApiResponse(description="Soft-deleted — record preserved in DB")},
    )
    def delete(self, request: Request, pk: str) -> Response:
        """Soft-delete a vendor — sets is_deleted=True, never hard-deletes (R6).

        Args:
            request: Authenticated HTTP request.
            pk: Vendor UUID.

        Returns:
            204 on success, 404 if not found.
        """
        vendor = self._get_vendor(pk)
        if vendor is None:
            return Response(
                {"success": False, "data": None, "message": "Vendor not found", "errors": {}},
                status=status.HTTP_404_NOT_FOUND,
            )
        soft_delete_vendor(vendor=vendor, actor=request.user, request=request._request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorQCStatusView(APIView):
    """Update the QC status of a vendor. QA_REVIEWER and above only."""

    permission_classes = [RolePermission.for_roles(
        AdminRole.SUPER_ADMIN, AdminRole.CITY_MANAGER, AdminRole.QA_REVIEWER,
    )]

    @extend_schema(
        tags=["Vendors"],
        summary="Update vendor QC status (SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER)",
        request=QCStatusUpdateSerializer,
        responses={200: VendorSerializer},
    )
    def patch(self, request: Request, pk: str) -> Response:
        """Update QC status and reviewer notes.

        Args:
            request: HTTP request with qc_status and optional qc_notes.
            pk: Vendor UUID.

        Returns:
            200 with updated vendor data.
        """
        try:
            vendor = Vendor.objects.get(id=pk)
        except Vendor.DoesNotExist:
            return Response(
                {"success": False, "data": None, "message": "Vendor not found", "errors": {}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = QCStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            vendor = update_qc_status(
                vendor=vendor,
                new_status=serializer.validated_data["qc_status"],
                reviewer=request.user,
                request=request._request,
                notes=serializer.validated_data.get("qc_notes", ""),
            )
        except ValueError as e:
            return Response(
                {"success": False, "data": None, "message": str(e), "errors": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(data=VendorSerializer(vendor).data)
