"""T2.1.1: the F token singleton is the single source of UI color/geometry.

Design contract: doc/contracts/UI_UX_GUI_DESIGN.md §6C + §7 -- candidate F
"Graphite Atelier" is A's palette x B's geometry, dark theme by default, and
its authoritative values live in doc/design/tokens-cand-f.json.

These tests pin the QML seam to that JSON. The JSON, not the QML, is the source
of truth: a token that drifts here is a contract violation, and no page can be
audited against the design until the mapping is fixed.
"""

from __future__ import annotations

import json

import helpers  # noqa: F401  (sys.path injection; SRC_ROOT below)

import pytest

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtQml import QQmlComponent, QQmlEngine

QML_ROOT = helpers.SRC_ROOT / "ui" / "qml"
CONTRACT_TOKENS = helpers.SRC_ROOT.parent / "doc" / "design" / "tokens-cand-f.json"

# The probes live in shell/ so `"../theme"` resolves exactly the way a real
# page directory resolves it -- that relative hop is the load-bearing detail.
PROBE_QML = """
import QtQuick
import "../theme"
Item {
    objectName: "tokenProbe"
    Component.onCompleted: Tokens.mode = "%(mode)s"
    function value(name) { return Tokens.value(name) }
    function geometry(name) { return Tokens.geometry(name) }
    property color inkValue: Tokens.ink
    property int cardWidthValue: Tokens.cardW
}
"""

# No mode assignment at all: the default theme is an acceptance item, so it has
# to be observed without being told.
DEFAULT_PROBE_QML = """
import QtQuick
import "../theme"
Item {
    objectName: "defaultProbe"
    property color bgPage: Tokens.bgPage
    property string mode: Tokens.mode
}
"""


def load_qml(source: str):
    engine = QQmlEngine(None)
    component = QQmlComponent(engine)
    component.setData(
        source.encode(),
        QUrl.fromLocalFile(str(QML_ROOT / "shell" / "_DesignTokensProbe.qml")),
    )
    assert component.isReady(), [e.toString() for e in component.errors()]
    root = component.create()
    assert root is not None
    # The component owns what create() returned: once its Python wrapper is
    # collected the item dies with it, and reads then raise "already deleted".
    # Parking both on the item keeps the whole graph alive while a test holds
    # the root.
    root._qml_harness = (engine, component)
    return engine, root


@pytest.fixture()
def tokens():
    """Loader that keeps every engine/probe it creates for teardown."""
    created = []

    def load(mode: str):
        engine, probe = load_qml(PROBE_QML % {"mode": mode})
        created.extend((engine, probe))
        return probe

    yield load
    for item in created:
        item.deleteLater()


def contract() -> dict:
    return json.loads(CONTRACT_TOKENS.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True, scope="module")
def _gui(qapp):
    """A QQmlEngine needs the session QGuiApplication (tests/ui_shell/conftest).

    Without it Qt aborts during engine construction: the run dies with no
    report at all, which reads like a harness failure instead of a test
    failure. Every other QML test here takes qapp for the same reason.
    """
    return qapp


def argb(value) -> str:
    """Normalize a QML `color` read-back to #aarrggbb.

    PySide6 hands typed color properties back as QColor, whose str() is a repr
    rather than a color string, so it must never be re-parsed as text.
    """
    color = value if isinstance(value, QColor) else QColor(str(value))
    assert color.isValid(), f"not a color: {value!r}"
    return color.name(QColor.HexArgb).lower()


def test_theme_directory_exposes_a_tokens_singleton():
    # Without this hop every page would re-declare the palette by hand, which
    # is exactly the drift the token layer exists to prevent.
    engine, item = load_qml(
        'import QtQuick\nimport "../theme"\n'
        "Item { property color probe: Tokens.ink }"
    )
    assert argb(item.property("probe")) == argb(contract()["modes"]["dark"]["color"]["ink"])
    item.deleteLater()
    engine.deleteLater()


def test_default_theme_is_dark():
    # §3 table + §11: F is "暗色（亮色完整提供）". A wrong default is a visible
    # product defect, not a preference.
    engine, probe = load_qml(DEFAULT_PROBE_QML)
    assert probe.property("mode") == "dark"
    assert argb(probe.property("bgPage")) == argb(contract()["modes"]["dark"]["color"]["bg-page"])
    assert argb(probe.property("bgPage")) == argb("#1a1a1d")
    probe.deleteLater()
    engine.deleteLater()


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_every_color_token_matches_the_contract(tokens, mode):
    # Exact literal equality rather than parsed-color equality: the singleton
    # carries the contract's strings verbatim, so a reformatted or re-cased
    # value is drift the audit should surface.
    probe = tokens(mode)
    colors = contract()["modes"][mode]["color"]
    assert len(colors) == 42, f"{mode} palette shrank from 42 tokens"
    mismatches = {}
    for name, expected in colors.items():
        got = probe.value(name)
        if got is None or str(got) != expected:
            mismatches[name] = f"contract {expected!r} != Tokens {got!r}"
    assert not mismatches, f"{mode}: {mismatches}"


def test_geometry_tokens_match_the_contract(tokens):
    probe = tokens("dark")
    geometry = contract()["geometry"]
    assert len(geometry) == 21, "geometry surface must not shrink (DDR-10)"
    mismatches = {}
    for name, expected in geometry.items():
        got = int(probe.geometry(name))
        if got != int(str(expected).rstrip("px")):
            mismatches[name] = f"contract {expected} != Tokens {got}"
    assert not mismatches, mismatches


def test_bookshelf_card_width_is_the_accepted_158px(tokens):
    # ND-1/DDR-10: the accepted bookshelf geometry is B's 158px card, not A's
    # 132px. The contract records this as an acceptance item.
    probe = tokens("dark")
    assert contract()["geometry"]["card-w"] == "158px"
    assert int(probe.geometry("card-w")) == 158


def test_named_properties_delegate_to_the_lookup_surface(tokens):
    # Pages bind `Tokens.ink`, not `Tokens.value("ink")`, so the named surface
    # must agree with the map the parity test walks; otherwise a page could
    # read a stale literal while the audit reported green.
    probe = tokens("dark")
    assert argb(probe.property("inkValue")) == argb(
        contract()["modes"]["dark"]["color"]["ink"]
    )
    assert int(probe.property("cardWidthValue")) == 158


def test_shadow_tokens_stay_in_the_surface_as_text(tokens):
    # Shadows are not applied anywhere in production QML yet; they are exposed
    # so the 42-token surface is complete, and asserted as text instead of
    # being silently dropped from the set.
    probe = tokens("dark")
    assert str(probe.value("shadow")) == contract()["modes"]["dark"]["color"]["shadow"]
    assert "rgba" in str(probe.value("shadow-sm"))
