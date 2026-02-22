"""
AirAd Backend — Pydantic v2 Schemas

BusinessHoursSchema validates the business_hours JSONField on every write
to a Vendor. Called explicitly from vendors/services.py — never in serializers
or models.
"""

import logging
import re
from typing import Annotated

from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)

_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class DayHoursSchema(BaseModel):
    """Business hours for a single day.

    Attributes:
        open: Opening time in HH:MM format (24-hour). Ignored when is_closed=True.
        close: Closing time in HH:MM format (24-hour). Ignored when is_closed=True.
        is_closed: True if the business is closed on this day.
    """

    open: str
    close: str
    is_closed: bool

    @field_validator("open", "close")
    @classmethod
    def validate_time_format(cls, value: str) -> str:
        """Validate that time strings match HH:MM format.

        Args:
            value: Time string to validate.

        Returns:
            The validated time string unchanged.

        Raises:
            ValueError: If the string does not match HH:MM or represents
                an invalid time (e.g. 25:00, 12:99).
        """
        if not _TIME_RE.match(value):
            raise ValueError(f"Time must be in HH:MM format, got '{value}'")

        hour, minute = int(value[:2]), int(value[3:])
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be 0–23, got {hour}")
        if not (0 <= minute <= 59):
            raise ValueError(f"Minute must be 0–59, got {minute}")

        return value

    @model_validator(mode="after")
    def validate_open_before_close(self) -> "DayHoursSchema":
        """Validate that open time is before close time when not closed.

        Returns:
            Self after validation.

        Raises:
            ValueError: If open >= close and is_closed is False.
        """
        if not self.is_closed and self.open >= self.close:
            raise ValueError(
                f"open time '{self.open}' must be before close time '{self.close}'"
            )
        return self


class BusinessHoursSchema(BaseModel):
    """Business hours for all 7 days of the week.

    All 7 day keys are required. Each day specifies open/close times
    and whether the business is closed that day.

    Attributes:
        MON: Monday hours.
        TUE: Tuesday hours.
        WED: Wednesday hours.
        THU: Thursday hours.
        FRI: Friday hours.
        SAT: Saturday hours.
        SUN: Sunday hours.

    Example:
        >>> schema = BusinessHoursSchema(
        ...     MON={"open": "09:00", "close": "18:00", "is_closed": False},
        ...     TUE={"open": "09:00", "close": "18:00", "is_closed": False},
        ...     WED={"open": "09:00", "close": "18:00", "is_closed": False},
        ...     THU={"open": "09:00", "close": "18:00", "is_closed": False},
        ...     FRI={"open": "09:00", "close": "18:00", "is_closed": False},
        ...     SAT={"open": "10:00", "close": "14:00", "is_closed": False},
        ...     SUN={"open": "00:00", "close": "00:00", "is_closed": True},
        ... )
    """

    MON: Annotated[DayHoursSchema, ...]
    TUE: Annotated[DayHoursSchema, ...]
    WED: Annotated[DayHoursSchema, ...]
    THU: Annotated[DayHoursSchema, ...]
    FRI: Annotated[DayHoursSchema, ...]
    SAT: Annotated[DayHoursSchema, ...]
    SUN: Annotated[DayHoursSchema, ...]

    def to_dict(self) -> dict:
        """Serialise the schema to a plain dict for JSONField storage.

        Returns:
            Dictionary with day keys and nested open/close/is_closed values.
        """
        return self.model_dump()
