from shared.models import MagnetLink, MagnetCategory


def test_magnet_link_model_has_required_fields():
    fields = [c.name for c in MagnetLink.__table__.c]
    assert "info_hash" in fields
    assert "title" in fields
    assert "seeders" in fields
    assert "leechers" in fields


def test_magnet_category_values():
    assert MagnetCategory.adult_eu.value == "adult_eu"
    assert MagnetCategory.general.value == "general"
