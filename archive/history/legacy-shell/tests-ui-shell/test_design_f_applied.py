"""T2.1.1: Design F is applied to the shipped QML, and stays applied.

``test_design_tokens.py`` proves the token singleton equals the contract.
This file proves the pages actually read from it, which is the part that can
regress silently: one pasted ``#hex`` inside a delegate, or one Label that
falls back to the platform's black, and the design is broken in a place the
parity tests cannot see.

Three surfaces are guarded:

* static  - no color literal and no numeric font size outside ``theme/``;
* runtime - every text item in the real ``Main.qml`` tree resolves to a
  contract color, which also proves the window palette reaches the Labels
  that have no explicit binding;
* contrast - the §7.2 text-on-ground pairs, including the accepted/completed
  badges, clear 4.5:1 in both modes.
"""

from __future__ import annotations

import json
import re

import helpers  # noqa: F401  (sys.path injection; SRC_ROOT below)
from fakes import InMemoryLibraryRepository, StubImporter

import pytest

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QColor
from PySide6.QtQml import QQmlComponent, QQmlEngine

QML_ROOT = helpers.SRC_ROOT / "ui" / "qml"
MAIN_QML = QML_ROOT / "Main.qml"
CONTRACT_TOKENS = helpers.SRC_ROOT.parent / "doc" / "design" / "tokens-cand-f.json"

# theme/ is the one directory allowed to name a color: it is the transcription
# of doc/design/tokens-cand-f.json, and the parity test binds it to the JSON.
TOKEN_SOURCE = QML_ROOT / "theme" / "Tokens.qml"

HEX_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b")
# "transparent" is not a design color -- it is the absence of one, and the
# region Canvas needs it to stay click-through.
NAMED_COLOR = re.compile(r"""[:=]\s*["'](white|black|red|blue|green|gray|grey)["']""")
NUMERIC_FONT_SIZE = re.compile(r"font\.pixelSize:\s*\d")
PALETTE_ROLE = re.compile(r"^\s*palette\.([A-Za-z]+):", re.M)
NUMERIC_CELL = re.compile(r"cell(?:Width|Height):\s*\d")
THEME_IMPORT = re.compile(r'^import "\.\./theme"$|^import "theme"$', re.M)
# §7.2 keeps st-ok / st-warn for dots, borders and painted graphics, and ships
# st-ok-t / st-warn-t as the text forms -- the audit table pairs the badge and
# panel rows with the *-t tokens. Handing a label the dot token is off-contract
# even when it happens to clear 4.5:1, and it is invisible to every contrast
# check, so it needs its own rule. QML object literals put the binding
# mid-line, so this reads per line and excuses the paint/border contexts.
DOT_TOKEN = re.compile(r"Tokens\.(?:stOk|stWarn)(?![A-Za-z])")
GRAPHIC_CONTEXT = re.compile(r"strokeStyle|fillStyle|border")

# The nine roles Main.qml and ExportWindow.qml must declare. Qt's QML palette
# has no palette.light.* / palette.dark.* grouping (assigning one is a load
# error), so both windows write the same flat roles.
WINDOW_ROLES = {
    "window", "windowText", "base", "button", "buttonText",
    "highlight", "highlightedText", "text", "placeholderText",
    "toolTipBase", "toolTipText",
}

# §7.2 "文字令牌 × 实际承载面". ``soft`` composits over ``ground`` the way the
# contract's own audit does: *-soft is an rgba over the panel, never a solid.
CONTRAST_PAIRS = [
    # (label, foreground token, translucent badge token or None, ground token)
    ("ink/panel",           "ink",           None,          "bg-panel"),
    ("ink-2/panel",         "ink-2",         None,          "bg-panel"),
    ("ink-3/panel",         "ink-3",         None,          "bg-panel"),
    ("ink-3/page",          "ink-3",         None,          "bg-page"),
    ("ink-2/inset",         "ink-2",         None,          "bg-inset"),
    ("accent-text/panel",   "accent-text",   None,          "bg-panel"),
    ("on-accent/accent",    "on-accent",     None,          "accent"),
    ("st-run/panel",        "st-run",        None,          "bg-panel"),
    ("st-ok/panel",         "st-ok-t",       None,          "bg-panel"),
    ("st-warn/panel",       "st-warn-t",     None,          "bg-panel"),
    ("st-fail/panel",       "st-fail",       None,          "bg-panel"),
    ("st-lock/panel",       "st-lock",       None,          "bg-panel"),
    ("st-block/panel",      "st-block",      None,          "bg-panel"),
    ("st-skip-direct",      "st-skip",       None,          "bg-panel"),
    ("badge-run",           "st-run",        "run-soft",    "bg-panel"),
    ("badge-ok",            "st-ok-t",       "ok-soft",     "bg-panel"),
    ("badge-warn",          "st-warn-t",     "warn-soft",   "bg-panel"),
    ("badge-fail",          "st-fail",       "fail-soft",   "bg-panel"),
    ("badge-skip",          "ink-2",         "skip-soft",   "bg-panel"),
    ("badge-lock",          "st-lock",       "lock-soft",   "bg-panel"),
    ("badge-block",         "st-block",      "block-soft",  "bg-panel"),
    ("accepted",            "accent-text",   "accent-soft", "bg-panel"),
    ("selected-row",        "ink",           "accent-soft", "bg-panel"),
    ("selected-row-inset",  "ink-2",         "accent-soft", "bg-raised"),
]

@pytest.fixture(autouse=True, scope="module")
def _gui(qapp):
    """A QQmlEngine needs the session QGuiApplication (see test_design_tokens)."""
    return qapp


def page_sources():
    return sorted(
        path for path in QML_ROOT.rglob("*.qml") if path != TOKEN_SOURCE
    )


def argb(value) -> str:
    color = value if isinstance(value, QColor) else QColor(str(value))
    assert color.isValid(), f"not a color: {value!r}"
    return color.name(QColor.HexArgb).lower()


def contract() -> dict:
    return json.loads(CONTRACT_TOKENS.read_text(encoding="utf-8"))


PROBE_QML = """
import QtQuick
import "../theme"
Item {
    objectName: "contrastProbe"
    property string mode: "dark"
    function colorFor(name) {
        Tokens.mode = mode
        return Tokens.colorFor(name)
    }
}
"""


@pytest.fixture()
def probe(qapp):
    engine = QQmlEngine(None)
    component = QQmlComponent(engine)
    component.setData(
        PROBE_QML.encode(),
        QUrl.fromLocalFile(str(QML_ROOT / "shell" / "_DesignFAppliedProbe.qml")),
    )
    assert component.isReady(), [e.toString() for e in component.errors()]
    item = component.create()
    assert item is not None
    item._qml_harness = (engine, component)
    yield item
    item.deleteLater()
    engine.deleteLater()


def resolved(probe, mode: str, name: str) -> QColor:
    """The color QML itself would paint for ``name`` under ``mode``."""
    probe.setProperty("mode", mode)
    value = getattr(probe, "colorFor")(name)
    color = value if isinstance(value, QColor) else QColor(str(value))
    assert color.isValid(), f"Tokens.colorFor({name!r}) -> {value!r}"
    return color


def composite(badge: QColor, ground: QColor) -> QColor:
    """Alpha-blend an ``*-soft`` token over its carrier.

    The contract's audit mixes in straight sRGB like a browser does, so the
    same arithmetic is used here rather than a linear-light blend.
    """
    alpha = badge.alphaF()
    return QColor.fromRgb(
        round(badge.red() * alpha + ground.red() * (1 - alpha)),
        round(badge.green() * alpha + ground.green() * (1 - alpha)),
        round(badge.blue() * alpha + ground.blue() * (1 - alpha)),
    )


def luminance(color: QColor) -> float:
    def channel(value: int) -> float:
        ratio = value / 255
        return ratio / 12.92 if ratio <= 0.03928 else ((ratio + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color.red()) + 0.7152 * channel(color.green()) + 0.0722 * channel(color.blue())


def contrast_ratio(foreground: QColor, background: QColor) -> float:
    first, second = luminance(foreground), luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


# ----------------------------------------------------------------------
# static surface: no page may re-declare the design
# ----------------------------------------------------------------------


def test_no_page_re_declares_a_color_literal():
    offenders = {}
    for path in page_sources():
        hits = HEX_LITERAL.findall(path.read_text(encoding="utf-8"))
        if hits:
            offenders[str(path.relative_to(QML_ROOT))] = sorted(set(hits))
    assert not offenders, f"color literals outside theme/Tokens.qml: {offenders}"


def test_no_named_css_color_slips_past_the_tokens():
    offenders = {}
    for path in page_sources():
        text = path.read_text(encoding="utf-8")
        hits = {match.group(1) for match in NAMED_COLOR.finditer(text)}
        if hits:
            offenders[str(path.relative_to(QML_ROOT))] = sorted(hits)
    assert not offenders, f"named CSS colors in page QML: {offenders}"


def test_no_page_hardcodes_a_font_size():
    offenders = {}
    for path in page_sources():
        text = path.read_text(encoding="utf-8")
        hits = NUMERIC_FONT_SIZE.findall(text)
        if hits:
            offenders[str(path.relative_to(QML_ROOT))] = len(hits)
    assert not offenders, f"numeric font.pixelSize (use Tokens.fs*): {offenders}"


def test_no_label_paints_with_a_graphic_only_token():
    offenders = {}
    for path in page_sources():
        text = path.read_text(encoding="utf-8")
        hits = [line.strip()[:60] for line in text.splitlines()
                if DOT_TOKEN.search(line) and not GRAPHIC_CONTEXT.search(line)]
        if hits:
            offenders[str(path.relative_to(QML_ROOT))] = hits
    assert not offenders, (
        f"text bound to a dot token instead of its *-t text form: {offenders}"
    )


def test_nav_badge_uses_soft_status_ground_and_text_token():
    """Rail status badges must use the audited three-part status encoding."""
    badge = (QML_ROOT / "shell" / "NavBadge.qml").read_text(encoding="utf-8")
    assert "color: Tokens.runSoft" in badge
    assert "color: Tokens.stRun" in badge
    assert "color: Tokens.onAccent" not in badge


def test_the_bookshelf_grid_takes_its_cell_geometry_from_tokens():
    # ND-1 accepted B's 158px card. A re-added numeric cellWidth here would
    # silently undo the acceptance item this task exists to deliver.
    grid = (QML_ROOT / "bookshelf" / "BookGrid.qml").read_text(encoding="utf-8")
    assert "Tokens.cardW" in grid, "BookGrid must size cells from Tokens.cardW"
    assert not NUMERIC_CELL.search(grid), "cellWidth/cellHeight must not be numeric"


def test_every_file_that_reads_tokens_imports_the_module():
    offenders = []
    for path in page_sources():
        text = path.read_text(encoding="utf-8")
        if "Tokens." in text and not THEME_IMPORT.search(text):
            offenders.append(str(path.relative_to(QML_ROOT)))
    assert not offenders, f"uses Tokens.* without importing ../theme: {offenders}"


def test_both_top_level_windows_declare_the_same_palette_surface():
    # The reader's export window is a second Window: it inherits nothing from
    # Main.qml, so the two role lists have to be kept identical by hand.
    windows = {"Main.qml": MAIN_QML, "ExportWindow.qml": QML_ROOT / "windows" / "ExportWindow.qml"}
    declared = {
        name: {match.group(1) for match in PALETTE_ROLE.finditer(
            path.read_text(encoding="utf-8"))}
        for name, path in windows.items()
    }
    for name, roles in declared.items():
        assert roles == WINDOW_ROLES, f"{name} palette surface drifted: {sorted(roles)}"


# ----------------------------------------------------------------------
# contrast: the §7.2 pairs, in both modes, through the QML token layer
# ----------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["dark", "light"])
@pytest.mark.parametrize("label,fg,soft,ground", CONTRAST_PAIRS, ids=[p[0] for p in CONTRAST_PAIRS])
def test_shipped_text_ground_pairs_clear_45(probe, mode, label, fg, soft, ground):
    fg_color = resolved(probe, mode, fg)
    ground_color = resolved(probe, mode, ground)
    carrier = (
        composite(resolved(probe, mode, soft), ground_color) if soft else ground_color
    )
    ratio = contrast_ratio(fg_color, carrier)
    assert ratio >= 4.5, f"{mode} {label}: {fg} on {soft or ground} = {ratio:.2f}:1"


def test_accepted_and_completed_are_distinguishable_in_both_modes(probe):
    # The acceptance item names these two states specifically: a confirmed
    # Region must not read as a finished page, and neither may rely on color
    # alone being the only cue.
    for mode in ("dark", "light"):
        accepted_fg = resolved(probe, mode, "accent-text")
        completed_fg = resolved(probe, mode, "st-ok-t")
        accepted_bg = composite(resolved(probe, mode, "accent-soft"),
                                resolved(probe, mode, "bg-panel"))
        completed_bg = composite(resolved(probe, mode, "ok-soft"),
                                 resolved(probe, mode, "bg-panel"))
        assert argb(accepted_fg) != argb(completed_fg), f"{mode}: badge text collides"
        assert argb(accepted_bg) != argb(completed_bg), f"{mode}: badge ground collides"


# ----------------------------------------------------------------------
# runtime: the real Main.qml tree paints with token colors only
# ----------------------------------------------------------------------


@pytest.fixture()
def product_tree(qapp):
    """Main.qml with the assembly context properties, never shown."""
    from application.library.service import LibraryService
    from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel
    from ui.viewmodels.navigation.viewmodel import NavigationViewModel

    library = LibraryService(InMemoryLibraryRepository())
    nav_vm = NavigationViewModel()
    shelf_vm = BookshelfViewModel(
        library=library, importer=StubImporter(), navigation=nav_vm
    )
    shelf_vm.createBook("迷宫饭")

    engine = QQmlEngine(None)
    engine.rootContext().setContextProperty("navigationViewModel", nav_vm)
    engine.rootContext().setContextProperty("bookshelfViewModel", shelf_vm)
    component = QQmlComponent(engine)
    source = MAIN_QML.read_text(encoding="utf-8").replace(
        "visible: true", "visible: false", 1
    )
    component.setData(source.encode("utf-8"), QUrl.fromLocalFile(str(MAIN_QML)))
    assert component.isReady(), [e.toString() for e in component.errors()]
    window = component.create()
    assert window is not None, [e.toString() for e in component.errors()]
    window._qml_harness = (engine, component)
    qapp.processEvents()
    yield window
    window.deleteLater()
    engine.deleteLater()
    qapp.processEvents()


def text_items(window):
    """Every text-rendering item in the window, page-declared or style-made.

    A QML-declared type reports a ``_QMLTYPE_`` class name; anything starting
    with ``QQuick`` is a Control's internal (its IconLabel, its placeholder).
    Internals resolve their color through the control and may report it unset,
    so the two kinds are distinguished here rather than lumped together.
    """
    for item in window.findChildren(QObject):
        color = item.property("color")
        if isinstance(color, QColor) and isinstance(item.property("text"), str):
            declared = not item.metaObject().className().startswith("QQuick")
            yield item, color, declared


def test_every_text_in_the_product_tree_resolves_to_a_token(product_tree, probe):
    # This is the load-bearing check behind the dark default: an unstyled
    # Label paints #000000, and the only thing that saves it is the window
    # palette Main.qml binds. A dropped role shows up here, not as a crash.
    allowed = {argb(resolved(probe, "dark", name))
               for name in contract()["modes"]["dark"]["color"]}
    offenders = {}
    for item, color, declared in text_items(product_tree):
        key = item.objectName() or item.metaObject().className()
        if not color.isValid():
            # An unset color is a style internal resolving through its
            # control; a page-declared Label with no color is the black-on-dark
            # defect this test exists to catch.
            assert not declared, f"page text has no color at all: {key}"
            continue
        name = argb(color)
        if name not in allowed:
            offenders[key] = name
    assert not offenders, f"text drawn in a non-contract color: {offenders}"


@pytest.mark.parametrize(
    "object_name,property_name,expected",
    [
        ("navRail", "width", 68),             # rail-w
        ("bookshelfToolbar", "height", 52),   # tb-h
        ("bookDetailPanel", "width", 336),    # det-w
    ],
)
def test_accepted_geometry_is_live_in_the_product_tree(
    product_tree, object_name, property_name, expected
):
    # The workbench panels are asserted in tests/workbench, where a viewmodel
    # and a chapter context exist.
    found = [item for item in product_tree.findChildren(QObject)
             if item.objectName() == object_name]
    assert found, f"{object_name} missing from the loaded shell"
    assert int(found[0].property(property_name)) == expected, (
        f"{object_name}.{property_name} left the accepted geometry"
    )


def test_bookshelf_cells_are_the_accepted_158px_grid(product_tree):
    # DDR-10: the accepted card is B's 158px, which the pre-F grid never used
    # (it was a 168px cell). The cell is card-w plus the grid's own gutter, so
    # the assertion pins the card and lets the gutter stay local to the grid.
    views = [item for item in product_tree.findChildren(QObject)
             if item.objectName() == "bookGridView"]
    gutters = [item for item in product_tree.findChildren(QObject)
               if item.objectName() == "bookGrid"]
    assert views and gutters, "bookshelf grid missing from the loaded shell"
    gutter = int(gutters[0].property("cardGutter"))
    assert int(views[0].property("cellWidth")) == 158 + gutter * 2
