"""Brand safety tests."""

import pytest
from services.brand_safety_service import BrandSafetyService


@pytest.fixture
def brand_safety():
    return BrandSafetyService(
        prohibited_brands=["Nike", "Under Armour"],
        excluded_content=["violence"],
    )


def test_exclusion_check_rejects_nike(brand_safety):
    """Test exclusion check rejects Nike."""
    result = brand_safety.check_excluded_brands(
        clip_id="clip-001",
        excluded_brands=["Nike"],
        detected_brands=["Nike", "Adidas"],
    )
    assert result["passed"] is False
    assert "Nike" in result["found_brands"]


def test_exclusion_check_passes_no_excluded(brand_safety):
    """Test exclusion check passes when no excluded brands."""
    result = brand_safety.check_excluded_brands(
        clip_id="clip-001",
        excluded_brands=["Nike"],
        detected_brands=["Adidas", "Pepsi"],
    )
    assert result["passed"] is True


def test_required_brands_check_finds_missing(brand_safety):
    """Test required brands check finds missing brands."""
    result = brand_safety.check_required_brands(
        clip_id="clip-001",
        required_brands=["Adidas"],
        detected_brands=["Pepsi"],
    )
    assert result["passed"] is False
    assert "Adidas" in result["missing_brands"]


def test_brand_safety_check_passes(brand_safety):
    """Test brand safety passes for clean clip."""
    result = brand_safety.check_brand_safety(
        clip_id="clip-001",
        detected_brands=["Adidas", "Pepsi"],
        content_tags=["sports"],
    )
    assert result["passed"] is True