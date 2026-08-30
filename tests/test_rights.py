"""Rights tests."""

import pytest
from services.rights_service import check_territory_rights


def test_rights_check_allows_germany_duration():
    """Test Germany digital highlights allows 30 seconds."""
    result = check_territory_rights("Germany", "digital_highlights", 30)
    assert result["rights_cleared"] is True
    assert "30" in result["explanation"]


def test_rights_check_rejects_germany_exceeds_duration():
    """Test Germany rejects clips exceeding 30 seconds."""
    result = check_territory_rights("Germany", "digital_highlights", 60)
    assert result["rights_cleared"] is False
    assert "exceeds" in result["explanation"].lower()


def test_rights_check_usa_allows_90_seconds():
    """Test USA digital highlights allows 90 seconds."""
    result = check_territory_rights("USA", "digital_highlights", 90)
    assert result["rights_cleared"] is True


def test_rights_check_unsupported_territory():
    """Test unsupported territory returns not cleared."""
    result = check_territory_rights("France", "digital_highlights", 30)
    assert result["rights_cleared"] is False