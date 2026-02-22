"""
Tests for core/schemas.py — BusinessHoursSchema Pydantic v2 validation.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from core.schemas import BusinessHoursSchema, DayHoursSchema


VALID_HOURS = {
    "MON": {"open": "09:00", "close": "18:00", "is_closed": False},
    "TUE": {"open": "09:00", "close": "18:00", "is_closed": False},
    "WED": {"open": "09:00", "close": "18:00", "is_closed": False},
    "THU": {"open": "09:00", "close": "18:00", "is_closed": False},
    "FRI": {"open": "09:00", "close": "18:00", "is_closed": False},
    "SAT": {"open": "10:00", "close": "14:00", "is_closed": False},
    "SUN": {"open": "00:00", "close": "00:00", "is_closed": True},
}


@pytest.mark.unit
class TestDayHoursSchema:
    """Unit tests for DayHoursSchema."""

    def test_valid_day(self):
        """Valid open/close/is_closed passes validation."""
        day = DayHoursSchema(open="09:00", close="18:00", is_closed=False)
        assert day.open == "09:00"
        assert day.close == "18:00"

    def test_invalid_time_format_raises(self):
        """Non-HH:MM format raises ValidationError."""
        with pytest.raises(PydanticValidationError):
            DayHoursSchema(open="9:00", close="18:00", is_closed=False)

    def test_invalid_hour_raises(self):
        """Hour > 23 raises ValidationError."""
        with pytest.raises(PydanticValidationError):
            DayHoursSchema(open="25:00", close="26:00", is_closed=False)

    def test_invalid_minute_raises(self):
        """Minute > 59 raises ValidationError."""
        with pytest.raises(PydanticValidationError):
            DayHoursSchema(open="09:60", close="18:00", is_closed=False)

    def test_open_after_close_raises(self):
        """open >= close raises ValidationError when not closed."""
        with pytest.raises(PydanticValidationError):
            DayHoursSchema(open="18:00", close="09:00", is_closed=False)

    def test_open_equals_close_raises(self):
        """open == close raises ValidationError when not closed."""
        with pytest.raises(PydanticValidationError):
            DayHoursSchema(open="09:00", close="09:00", is_closed=False)

    def test_closed_day_ignores_times(self):
        """is_closed=True does not validate open/close order."""
        day = DayHoursSchema(open="00:00", close="00:00", is_closed=True)
        assert day.is_closed is True


@pytest.mark.unit
class TestBusinessHoursSchema:
    """Unit tests for BusinessHoursSchema."""

    def test_valid_full_week(self):
        """Valid 7-day hours passes validation."""
        schema = BusinessHoursSchema(**VALID_HOURS)
        assert schema.MON.open == "09:00"

    def test_to_dict_returns_dict(self):
        """to_dict() returns a plain dict."""
        schema = BusinessHoursSchema(**VALID_HOURS)
        result = schema.to_dict()
        assert isinstance(result, dict)
        assert "MON" in result
        assert result["SUN"]["is_closed"] is True

    def test_missing_day_raises(self):
        """Missing a day key raises ValidationError."""
        incomplete = {k: v for k, v in VALID_HOURS.items() if k != "SUN"}
        with pytest.raises(PydanticValidationError):
            BusinessHoursSchema(**incomplete)
