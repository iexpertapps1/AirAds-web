"""
AirAd Backend — AdminUser Model

Custom user model using AbstractBaseUser with 7 RBAC roles.
UUID primary key with default=uuid.uuid4 (callable — never uuid.uuid4()).
All auth events are logged to AuditLog from services.py, never via signals.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class AdminRole(models.TextChoices):
    """Seven RBAC roles for the AirAd admin portal.

    These values must match the RBAC matrix exactly.
    RolePermission.for_roles() is the ONLY mechanism to enforce them (R3).
    """

    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    CITY_MANAGER = "CITY_MANAGER", "City Manager"
    DATA_ENTRY = "DATA_ENTRY", "Data Entry"
    QA_REVIEWER = "QA_REVIEWER", "QA Reviewer"
    FIELD_AGENT = "FIELD_AGENT", "Field Agent"
    ANALYST = "ANALYST", "Analyst"
    SUPPORT = "SUPPORT", "Support"


class AdminUserManager(BaseUserManager["AdminUser"]):
    """Custom manager for AdminUser.

    Provides create_user() and create_superuser() with full type hints.
    """

    def create_user(
        self,
        email: str,
        password: str | None = None,
        role: str = AdminRole.DATA_ENTRY,
        **extra_fields: object,
    ) -> "AdminUser":
        """Create and save a regular AdminUser.

        Args:
            email: Unique email address — used as USERNAME_FIELD.
            password: Raw password (will be hashed). May be None for
                unusable-password accounts.
            role: AdminRole value. Defaults to DATA_ENTRY.
            **extra_fields: Additional model field values.

        Returns:
            Saved AdminUser instance.

        Raises:
            ValueError: If email is empty.
        """
        if not email:
            raise ValueError("AdminUser must have an email address")

        email = self.normalize_email(email)
        user: AdminUser = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> "AdminUser":
        """Create and save a SuperAdmin user.

        Args:
            email: Unique email address.
            password: Raw password.
            **extra_fields: Additional model field values.

        Returns:
            Saved AdminUser instance with SUPER_ADMIN role.

        Raises:
            ValueError: If email is empty.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            password=password,
            role=AdminRole.SUPER_ADMIN,
            **extra_fields,
        )


class AdminUser(AbstractBaseUser, PermissionsMixin):
    """Custom admin user model for the AirAd internal portal.

    Uses email as the login identifier. Supports 7 RBAC roles via
    AdminRole TextChoices. Account lockout is enforced in services.py.

    Attributes:
        id: UUID primary key — default=uuid.uuid4 (callable, not evaluated once).
        email: Unique email address used as USERNAME_FIELD.
        full_name: Display name.
        role: One of 7 AdminRole values.
        is_active: Whether the account is active.
        is_staff: Django admin access flag.
        failed_login_count: Incremented on each failed login attempt.
        locked_until: Datetime until which the account is locked (nullable).
        last_login_ip: IP address of the most recent successful login.
        created_at: Auto-set on creation.
        updated_at: Auto-updated on every save.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,  # callable — NOT uuid.uuid4() (mutable default bug)
        editable=False,
    )
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=AdminRole.choices,
        default=AdminRole.DATA_ENTRY,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Lockout tracking
    failed_login_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    # Audit fields
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AdminUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"

    def is_locked(self) -> bool:
        """Check whether this account is currently locked out.

        Returns:
            True if locked_until is set and in the future, False otherwise.
        """
        if self.locked_until is None:
            return False
        return timezone.now() < self.locked_until
