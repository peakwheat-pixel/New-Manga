"""AC2: prove the DTD/entity guard rejects XXE and Billion Laughs.

SEC-FMT-002 asks that an XML parser refuse external entity resolution and
entity expansion. The guard lives in the validation tool, not in product
code, because src/ only WRITES ComicInfo.xml (ET.Element + tostring) and
never parses one - see verification/SEC-FMT-IMPL-1/r1-xml-parsing-scope.md.

The guard is a plain substring check before the parser is reached:

    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        return False, "DTD/entity declarations are not accepted"

Both payload shapes below are refused by that check, so the parser never sees
them. That is the point: defusing before parsing beats configuring the parser,
because it does not depend on the parser's own entity settings.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_TOOLS = REPO / "test_assets" / "comic_golden_suite" / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

assets = pytest.importorskip("assets", reason="golden-suite tools not importable")


# A real XXE: the parser is asked to pull a local file into the document.
XXE = (
    b'<?xml version="1.0"?>'
    b'<!DOCTYPE r [<!ENTITY x SYSTEM "file:///C:/Windows/win.ini">]>'
    b"<r>&x;</r>"
)

# Billion Laughs: entity definitions that expand exponentially.
BILLION_LAUGHS = (
    b'<?xml version="1.0"?>'
    b"<!DOCTYPE lolz ["
    b'<!ENTITY lol "lol">'
    b'<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
    b'<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
    b"]>"
    b"<lolz>&lol3;</lolz>"
)

# A parameter-entity form, which some guards miss because they only look for
# the general-entity spelling.
PARAMETER_ENTITY = (
    b'<?xml version="1.0"?>'
    b'<!DOCTYPE r [<!ENTITY % p SYSTEM "http://example.invalid/x">%p;]>'
    b"<r/>"
)

LEGIT = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b"<ComicInfo><Series>Test Manga</Series><Pages><Page Image=\"0\"/></Pages></ComicInfo>"
)


@pytest.mark.parametrize(
    "label,payload",
    [
        ("external entity", XXE),
        ("billion laughs", BILLION_LAUGHS),
        ("parameter entity", PARAMETER_ENTITY),
    ],
)
def test_public_xml_valid_rejects_entity_payloads(label: str, payload: bytes) -> None:
    """Each payload must be reported invalid, not parsed."""
    ok, message = assets.public_xml_valid(payload, "ComicInfo.xml")
    assert ok is False, f"{label} was accepted"
    assert "DTD/entity declarations" in message, message


def test_public_xml_valid_accepts_legitimate_xml() -> None:
    """Control arm.

    Without this, a validator that rejected every document would satisfy the
    three rejections above while breaking every real import.
    """
    ok, message = assets.public_xml_valid(LEGIT, "ComicInfo.xml")
    assert ok is True, message


def test_public_xml_valid_rejects_malformed_xml() -> None:
    """Truncated XML is invalid, and must fail after the entity check passes."""
    ok, message = assets.public_xml_valid(b"<ComicInfo><Series>x</ComicInfo>", "ComicInfo.xml")
    assert ok is False
    assert "invalid" in message.lower()


def test_entity_check_runs_before_the_parser() -> None:
    """The guard must not depend on the parser refusing entities.

    A payload that is well-formed XML AND contains a DOCTYPE proves the
    rejection came from the substring check: ET.fromstring would parse this
    document happily, because it does not resolve external entities by
    default but it does not reject the declaration either.
    """
    well_formed_with_doctype = (
        b'<?xml version="1.0"?>'
        b'<!DOCTYPE r SYSTEM "about:invalid">'
        b"<r><a>1</a></r>"
    )
    ok, message = assets.public_xml_valid(well_formed_with_doctype, "ComicInfo.xml")
    assert ok is False
    assert "DTD/entity declarations" in message
