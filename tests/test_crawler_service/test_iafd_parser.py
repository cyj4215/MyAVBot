import pytest
from crawler_service.parsers.iafd_parser import IAFDParser


def test_extract_fields_parses_birthday():
    parser = IAFDParser()
    lines = [
        "BIRTHDAY",
        "March 4, 1985 (41 years old)",
        "BIRTHPLACE",
        "Sydney, Australia",
        "HEIGHT",
        "5 feet, 2 inches (157 cm)",
        "MEASUREMENTS",
        "32GG-28-38",
        "NATIONALITY",
        "Australian",
        "YEARS ACTIVE AS PERFORMER",
        "2003-2026 (Started around 18 years old)",
    ]
    result = parser._extract_fields(lines)
    assert result.get("birthday") == "1985-03-04"
    assert result.get("birthplace") == "Sydney, Australia"
    assert result.get("height") == 157
    assert result.get("measurements") == "32GG-28-38"
    assert result.get("country") == "Australian"
    assert result.get("career_start") == 2003


def test_extract_works_parses_table():
    parser = IAFDParser()
    text = """Angela White
Performer Credits (1209)
Search:
Movie Title\tYear\tDistributor\tNotes\tRev\tFormats
001 Test Title\t2020\tStudioA\tNotes\t\tO
002 Another Title\t2021\tStudioB\t\t\tO
"""
    works = parser._extract_works(text)
    assert len(works) == 2
    assert works[0]["title"] == "Test Title"
    assert works[0]["year"] == 2020
    assert works[0]["distributor"] == "StudioA"
    assert works[1]["title"] == "Another Title"
    assert works[1]["year"] == 2021


def test_extract_works_empty_when_no_header():
    parser = IAFDParser()
    works = parser._extract_works("no data here")
    assert works == []


def test_extract_fields_empty_lines():
    parser = IAFDParser()
    result = parser._extract_fields(["SOME_UNKNOWN_LABEL", "value"])
    assert result == {}
