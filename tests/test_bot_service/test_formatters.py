from bot_service.formatters import format_actress_card, format_work_card, format_magnet_result, format_size


def test_format_actress_card_minimal():
    result = format_actress_card({"name": "Test Actress"})
    assert "Test Actress" in result


def test_format_actress_card_with_birthday():
    result = format_actress_card({"name": "Test", "birthday": "1985-03-04", "country": "Australia"})
    assert "1985-03-04" in result
    assert "Australia" in result


def test_format_work_card():
    result = format_work_card({"title": "Test Movie", "work_id": "TM-001", "release_date": "2023-01-01"})
    assert "Test Movie" in result
    assert "TM-001" in result


def test_format_magnet_result():
    result = format_magnet_result({
        "info_hash": "abc123", "title": "Test Torrent",
        "file_size": 1073741824, "seeders": 10, "leechers": 5, "source_site": "test",
    })
    assert "abc123" in result
    assert "1.0GB" in result


def test_format_size_bytes():
    assert format_size(500) == "500.0B"


def test_format_size_kb():
    assert format_size(2048) == "2.0KB"


def test_format_size_gb():
    assert format_size(1073741824) == "1.0GB"
