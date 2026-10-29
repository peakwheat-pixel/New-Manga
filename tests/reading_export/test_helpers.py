"""Unit tests for the reading_export diagnostic helpers (TASK-037).

The helpers guard QML property reads against deleted C++ objects. The
numeric-wait contract added for TASK-036 R-01 (``safe_number``) is checked
here without a Qt stack: a placeholder string must never reach a numeric
comparison, and ``safe_number`` must keep such comparisons numeric so the
bounded wait keeps failing until the real assertion reports with full
diagnostics.
"""

from reading_export_helpers import safe_number, safe_property


class DeletedObject:
    """Stands in for a PySide6 wrapper whose C++ object is already gone."""

    def property(self, name):
        raise RuntimeError("Internal C++ object already deleted")


class Properties:
    """Fixed property bag; only ``property(name)`` is on the helper path."""

    def __init__(self, **values):
        self._values = values

    def property(self, name):
        return self._values[name]


def test_safe_property_placeholder_stays_a_string():
    value = safe_property(DeletedObject(), "contentY")
    assert isinstance(value, str) and "unavailable" in value


def test_safe_property_none_object_stays_none():
    assert safe_property(None, "contentY") is None


def test_safe_number_falls_back_to_default_when_object_deleted():
    assert safe_number(DeletedObject(), "contentY") == 0.0
    assert safe_number(DeletedObject(), "contentY", default=5.0) == 5.0


def test_safe_number_falls_back_to_default_for_none_or_non_numeric():
    assert safe_number(None, "contentY") == 0.0
    assert safe_number(Properties(contentY=None), "contentY") == 0.0
    assert safe_number(
        Properties(contentY="<unavailable: Internal C++ object already deleted>"),
        "contentY",
    ) == 0.0


def test_safe_number_reads_numeric_properties_as_is():
    assert safe_number(Properties(contentY=240.0), "contentY") == 240.0
    assert safe_number(Properties(height=800), "height") == 800
    assert safe_number(Properties(contentY=0), "contentY", default=99.0) == 0


def test_numeric_wait_condition_stays_numeric_with_deleted_object():
    """The TASK-036 R-01 regression shape: ``(safe_property(...) or 0) > 0``
    evaluated ``str > int`` and raised ``TypeError`` when the placeholder
    reached the comparison. With ``safe_number`` the same shape compares
    numbers and simply stays False, so the wait — not a crash — drives the
    failure reporting."""
    assert not (safe_number(DeletedObject(), "contentHeight") > 0)
    assert not (
        safe_number(DeletedObject(), "contentHeight")
        - safe_number(DeletedObject(), "height")
        >= 240.0
    )
