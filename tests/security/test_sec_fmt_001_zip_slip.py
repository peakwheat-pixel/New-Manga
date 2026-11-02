"""AC1: prove zip_parts rejects every Zip Slip shape it claims to reject.

SEC-FMT-001 asks that archive entries with illegal relative paths be
identified and discarded. The implementation lives in the validation tool
(test_assets/comic_golden_suite/tools/assets.py:zip_parts), because the
product only ever WRITES a zip - src/ has no namelist/infolist/extractall at
all (see verification/SEC-FMT-IMPL-1/guard-on-attack-path.md).

Each case below is one of the six shapes the guard is meant to stop. The
final test is the control arm: without it, a function that rejected
everything would pass all six.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_TOOLS = REPO / "test_assets" / "comic_golden_suite" / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

assets = pytest.importorskip("assets", reason="golden-suite tools not importable")


def _info(name: str) -> zipfile.ZipInfo:
    return zipfile.ZipInfo(filename=name)


class _RawInfo:
    """A ZipInfo look-alike that preserves the filename byte-for-byte.

    zipfile.ZipInfo(filename=...) silently truncates at a NUL byte:
    'images/evil\\x00.jpg' becomes 'images/evil'. So it cannot be used to
    prove the guard's NUL check works. This stand-in carries the raw string,
    which is what a hand-built or tampered archive could present to the
    parser.
    """

    __slots__ = ("filename",)

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def is_dir(self) -> bool:
        return self.filename.endswith("/")


# (case name, entry name) - every one must be rejected
ATTACKS = [
    ("parent traversal", "../../Windows/System32/evil.dll"),
    ("single traversal", "images/../../../evil.jpg"),
    ("absolute posix path", "/etc/passwd"),
    ("windows drive letter", "C:/Windows/evil.dll"),
    ("backslash separator", "images\\..\\..\\evil.jpg"),
    ("nul byte", "images/evil\x00.jpg"),
    ("dot segment", "images/./evil.jpg"),
    ("empty segment", "images//evil.jpg"),
]


@pytest.mark.parametrize("label,name", ATTACKS)
def test_zip_parts_rejects_attack(label: str, name: str) -> None:
    """Every shape must raise, not return a path."""
    with pytest.raises(ValueError, match="unsafe path in ZIP archive"):
        assets.zip_parts(_RawInfo(name))


def test_zip_parts_accepts_a_legitimate_entry() -> None:
    """Control arm: a real CBZ member must pass.

    Without this, the eight rejections above would also be satisfied by a
    guard that rejected every possible name.
    """
    parts = assets.zip_parts(_RawInfo("images/My Book/001.jpg"))
    assert parts == ("images", "My Book", "001.jpg")


def test_zip_parts_accepts_directory_entries() -> None:
    """A trailing slash on a directory entry is legitimate, not traversal."""
    parts = assets.zip_parts(_RawInfo("images/My Book/"))
    assert parts == ("images", "My Book")


def test_zipinfo_truncates_nul_so_the_stand_in_is_required() -> None:
    """Pin the reason _RawInfo exists.

    If a future zipfile stops truncating, this test fails and the stand-in can
    be replaced by a real ZipInfo - which is better evidence than a mock.
    """
    assert zipfile.ZipInfo(filename="images/evil\x00.jpg").filename == "images/evil"
