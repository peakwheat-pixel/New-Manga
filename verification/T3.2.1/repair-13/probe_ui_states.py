"""REPAIR-13 UI state probe: drives the real production assembly through
the repaired bookshelf import path and captures per-page button-state
screenshots plus text/background color samples.

Covers (R13-AC1/AC2/AC3/AC4 local evidence; the Sandbox rerun remains a
separate AC5 gate):
- AC1: toolbar import button disabled with a visible hint while no
  chapter is selected; enabled after a real row click selects one; and
  zero QML TypeErrors on stderr.
- AC2: two fixed synthetic PNGs imported through
  bookshelfViewModel.importFilesFromUrls into the selected chapter;
  managed-copy files exist; fixture hashes unchanged.
- AC3: full-window grabs of all four top-level pages, the new-book
  dialog, the reader chapter picker and the export window; for each
  named button the sampled text/background colors and WCAG contrast.
- AC4: with pages present and the reader chapter active, the Export
  button opens the export window and startExport writes a ZIP with the
  two pages.

Run from the worktree root with the project venv:
  python verification/T3.2.1/repair-13/probe_ui_states.py --out-dir <dir>
Stdout carries the step log, the color table and PASS/FAIL lines; the
caller captures stderr separately (it must contain no QML TypeError on
the import path).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[2] / "src"
for entry in (str(SRC_ROOT),):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from PySide6.QtCore import QObject, QPoint, QUrl, Qt, QTimer  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage  # noqa: E402
from PySide6.QtQuick import QQuickItem, QQuickWindow  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from bootstrap.app import _shutdown_services, assemble_engine, assemble_services  # noqa: E402

FAILURES: list[str] = []
STEPS: list[str] = []


def step(message: str) -> None:
    print(f"[STEP] {message}", flush=True)


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""), flush=True)
    if not ok:
        FAILURES.append(name)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def click_qml_button(button: QObject) -> None:
    """Emit AbstractButton.clicked through QMetaMethod (same technique as
    tests/ui_shell/test_qml_shell.py::click_button)."""
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, "clicked() not found on button"
    meta.method(index).invoke(button)


def find_item(root: QObject, object_name: str) -> QQuickItem:
    listed = root.findChildren(QObject, object_name)
    if not listed:
        raise AssertionError(f"item not found: {object_name}")
    return listed[0]


def grab(window: QQuickWindow, path: Path) -> None:
    image = window.grabWindow()
    if image.isNull():
        raise AssertionError(f"grabWindow returned null for {path.name}")
    if not image.save(str(path)):
        raise AssertionError(f"failed to save {path.name}")
    STEPS.append(str(path))


# ---- WCAG contrast sampling -------------------------------------------

def _rel_luminance(color) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    r, g, b = channel(color.redF()), channel(color.greenF()), channel(color.blueF())
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2) -> float:
    l1, l2 = _rel_luminance(c1), _rel_luminance(c2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def sample_button(window: QQuickWindow, image: QImage, item: QQuickItem, label: str) -> None:
    """Report center/background color, brightest pixel (approx. text) and
    the WCAG ratio of text-vs-background inside the button bounds."""
    dsr = window.effectiveDevicePixelRatio()
    scene = item.mapToScene(QPoint(0, 0))
    x = int(scene.x() * dsr)
    y = int(scene.y() * dsr)
    w = max(2, int(item.width() * dsr))
    h = max(2, int(item.height() * dsr))
    w = min(w, image.width() - x)
    h = min(h, image.height() - y)
    if w <= 0 or h <= 0:
        print(f"[COLOR] {label}: bounds off-screen x={x} y={y}", flush=True)
        return
    center = image.pixelColor(x + w // 2, y + h // 2)
    brightest = center
    darkest = center
    for yy in range(y, y + h, max(1, h // 24)):
        for xx in range(x, x + w, max(1, w // 24)):
            pixel = image.pixelColor(xx, yy)
            if _rel_luminance(pixel) > _rel_luminance(brightest):
                brightest = pixel
            if _rel_luminance(pixel) < _rel_luminance(darkest):
                darkest = pixel
    text_candidate = (
        brightest if contrast(brightest, center) >= contrast(darkest, center) else darkest
    )
    ratio = contrast(text_candidate, center)
    def hexs(c) -> str:
        return f"#{c.red():02x}{c.green():02x}{c.blue():02x}"
    print(
        f"[COLOR] {label}: bg={hexs(center)} text≈{hexs(text_candidate)} "
        f"contrast={ratio:.2f}:1 enabled={item.isEnabled()}",
        flush=True,
    )


def grab_and_audit(window: QQuickWindow, path: Path, names: list[str], root: QObject) -> None:
    """Grab the window and sample the named buttons while this page is
    still the visible one (item visibility is live, the image is the
    just-captured frame)."""
    grab(window, path)
    image = QImage(str(path))
    if image.isNull():
        check(f"color audit image {path.name}", False, "unreadable")
        return
    print(f"[COLOR] ---- {path.name} ----", flush=True)
    for name in names:
        listed = root.findChildren(QObject, name)
        if not listed or not isinstance(listed[0], QQuickItem):
            print(f"[COLOR] {name}: not found on this page", flush=True)
            continue
        item = listed[0]
        if not item.isVisible():
            print(f"[COLOR] {name}: not visible (skipped)", flush=True)
            continue
        sample_button(window, image, item, name)


def audit_nav_rail(window: QQuickWindow, image: QImage) -> None:
    """Repeater delegates are not on the QObject tree; read them from the
    rail's visual children (same technique as tests/ui_shell)."""
    rail_items = window.findChildren(QObject, "navRail")
    if not rail_items:
        print("[COLOR] navRail: not found", flush=True)
        return
    rail = rail_items[0]
    buttons = [child for child in rail.childItems()
               if child.objectName().startswith("nav-")]
    for button in buttons:
        if button.isVisible():
            sample_button(window, image, button, button.objectName())
        else:
            print(f"[COLOR] {button.objectName()}: not visible (skipped)", flush=True)


# ---- main --------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=THIS_DIR / "screenshots")
    parser.add_argument("--scheme", choices=("early", "none"), default="early",
                        help="early: force the dark color scheme before any "
                             "control exists; none: rely on Main.qml only")
    options = parser.parse_args()
    out_dir = options.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    app = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
    if options.scheme == "early":
        app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
        print(f"[STEP] colorScheme forced dark before assembly: "
              f"{app.styleHints().colorScheme()}", flush=True)

    data_root = Path(tempfile.mkdtemp(prefix="repair13-probe-"))
    fixture_a = data_root / "fixture-page-a.png"
    fixture_b = data_root / "fixture-page-b.png"
    for path, rgb in ((fixture_a, (178, 52, 52)), (fixture_b, (44, 92, 178))):
        image = QImage(400, 600, QImage.Format_RGB32)
        image.fill(QColor(*rgb))
        image.save(str(path))
    hash_a_before, hash_b_before = sha256(fixture_a), sha256(fixture_b)
    step(f"fixtures: a={hash_a_before} b={hash_b_before}")

    services = assemble_services(data_root / "library.db", data_root / "managed")
    engine = assemble_engine(services)
    window = engine.rootObjects()[0]
    shelf = services.bookshelf
    navigation = services.navigation

    # -- AC1: empty shelf — import disabled with visible hint ------------
    QTest.qWait(400)
    grab_and_audit(window, out_dir / "01-bookshelf-empty.png", [
        "btnCreateBook", "btnImport", "importHint", "emptyCreateBook",
        "emptyImport", "searchField", "btnFavoritesFilter",
        "btnArchivedFilter", "btnSort", "btnViewMode",
    ], window)
    audit_nav_rail(window, QImage(str(out_dir / "01-bookshelf-empty.png")))
    btn_import = find_item(window, "btnImport")
    hint = find_item(window, "importHint")
    check("AC1 empty-shelf: import disabled", not btn_import.isEnabled())
    check("AC1 empty-shelf: hint visible", hint.isVisible() and hint.property("text") != "",
          str(hint.property("text")))

    # -- new-book dialog --------------------------------------------------
    dialog = find_item(window, "newBookDialog")
    dialog.open()
    QTest.qWait(300)
    grab(window, out_dir / "02-new-book-dialog.png")
    dialog.close()
    QTest.qWait(200)

    # -- create book + chapter -------------------------------------------
    book = shelf.createBook("探针作品", "probe-original")
    book_id = book["book_id"]
    chapter = shelf.createChapter(book_id, "第一章", "1")
    chapter_id = chapter["chapter_id"]
    shelf.selectBook(book_id)
    QTest.qWait(300)
    grab_and_audit(window, out_dir / "03-bookshelf-detail.png", [
        "btnImport", "btnCreateChapter", "btnEnterTranslation",
        "btnEnterReading", "detailFavorite", "detailArchived",
    ], window)

    # checked state (favorites filter) ------------------------------------
    shelf.setFavoritesOnly(True)
    QTest.qWait(200)
    grab(window, out_dir / "04-toolbar-checked.png")
    shelf.setFavoritesOnly(False)
    QTest.qWait(200)

    # -- AC1: select the chapter with a real row click --------------------
    list_view = find_item(window, "chapterListView")
    content = list_view.property("contentItem")
    delegates = [
        child for child in content.childItems()
        if child.metaObject().className().startswith("QQuickRectangle")
    ]
    check("AC1 chapter row exists", len(delegates) == 1, f"{len(delegates)} rows")
    if delegates:
        row = delegates[0]
        pos = row.mapToScene(QPoint(30, int(row.height() // 2))).toPoint()
        QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, pos)
        QTest.qWait(200)
    check("AC1 chapter-selected: import enabled", btn_import.isEnabled())
    check("AC1 chapter-selected: hint hidden", not hint.isVisible())
    grab(window, out_dir / "05-chapter-selected.png")

    # -- AC2: the import button actually opens the file picker -------------
    click_qml_button(btn_import)
    QTest.qWait(600)
    import_dialog = find_item(window, "importDialog")
    picker_visible = bool(import_dialog.property("visible"))
    check("AC2 import click opens the file picker", picker_visible)
    if picker_visible:
        # Dismiss the native picker; the two-fixture import itself is driven
        # through the viewmodel entry below (same handler the dialog's
        # accepted() signal invokes).
        import_dialog.close()
        QTest.qWait(400)
    grab(window, out_dir / "05b-import-picker-opened.png")

    # -- AC2: import two fixed PNGs through the viewmodel -----------------
    report = shelf.importFilesFromUrls(
        chapter_id,
        [QUrl.fromLocalFile(str(fixture_a)), QUrl.fromLocalFile(str(fixture_b))],
    )
    step(f"import report: {report}")
    check("AC2 imported == 2", report["imported"] == 2, str(report))
    managed_dir = data_root / "managed"
    managed_files = sorted(p for p in managed_dir.rglob("*") if p.is_file())
    check("AC2 managed copy has 2 files", len(managed_files) == 2,
          "; ".join(str(p.relative_to(managed_dir)) for p in managed_files))
    check("AC2 fixture A hash unchanged", sha256(fixture_a) == hash_a_before)
    check("AC2 fixture B hash unchanged", sha256(fixture_b) == hash_b_before)
    grab(window, out_dir / "06-pages-imported.png")

    # -- reader with the active chapter -----------------------------------
    shelf.enterReading(chapter_id)
    QTest.qWait(800)
    reader_export = find_item(window, "readerExportButton")
    check("AC4 reader: export enabled", reader_export.isEnabled())
    grab_and_audit(window, out_dir / "07-reader-active.png", [
        "readerPickChapter", "readerModeOriginal", "readerModeTranslated",
        "readerPreviousPage", "readerNextPage", "readerContinueLast",
        "readerRestart", "readerExportButton",
    ], window)

    # reader chapter picker dialog -----------------------------------------
    picker = window.findChildren(QObject, "readerChapterPicker")
    if picker:
        picker[0].open()
        QTest.qWait(400)
        grab(window, out_dir / "08-reader-chapter-picker.png")
        image08 = QImage(str(out_dir / "08-reader-chapter-picker.png"))
        print("[COLOR] ---- 08-reader-chapter-picker.png ----", flush=True)
        for name in ("chapterPickerBookList", "chapterPickerChapterList",
                     "chapterPickerCancel", "chapterPickerAccept"):
            # Two ChapterPicker instances exist (reader/workbench) with the
            # same inner objectNames — sample the visible one.
            candidates = [item for item in window.findChildren(QObject, name)
                          if isinstance(item, QQuickItem) and item.isVisible()]
            if candidates:
                sample_button(window, image08, candidates[0], name)
            else:
                print(f"[COLOR] {name}: not visible (skipped)", flush=True)
        picker[0].close()
        QTest.qWait(200)

    # -- AC4: export window + real ZIP export ------------------------------
    click_qml_button(reader_export)
    QTest.qWait(500)
    export_windows = window.findChildren(QQuickWindow)
    export_window = None
    for candidate in export_windows:
        if candidate is not window and candidate.objectName() == "exportWindow":
            export_window = candidate
            break
    check("AC4 export window opened", export_window is not None)
    if export_window is not None:
        grab(export_window, out_dir / "09-export-window.png")
        image09 = QImage(str(out_dir / "09-export-window.png"))
        print("[COLOR] ---- 09-export-window.png ----", flush=True)
        for name in ("exportMode", "exportFormat", "exportRunButton",
                     "exportCancelButton", "exportCloseButton"):
            listed = export_window.findChildren(QObject, name)
            if listed and isinstance(listed[0], QQuickItem) and listed[0].isVisible():
                sample_button(export_window, image09, listed[0], name)
            else:
                print(f"[COLOR] {name}: not visible (skipped)", flush=True)
        run_button = export_window.findChildren(QObject, "exportRunButton")[0]
        check("AC4 export run enabled", run_button.isEnabled())
        target = data_root / "export-out" / "probe-export.zip"
        target.parent.mkdir(parents=True, exist_ok=True)
        controller = services.reader.exportController
        controller.setOutputPath(str(target))
        controller.setFormat("zip")
        # The imported pages have original pixels only (no pipeline run in
        # this slice), so the default `translated` mode is stale-by-design
        # and policy `abort` refuses it. Export the original pages, which
        # is exactly what the reader toolbar shows (mode === "original").
        controller.setMode("original")
        controller.startExport()
        for _ in range(100):
            if not controller.running:
                break
            QTest.qWait(100)
        QTest.qWait(300)
        step(f"export statusMessage={controller.statusMessage!r} "
             f"running={controller.running}")
        step(f"export history={controller.history}")
        check("AC4 export file exists", target.is_file())
        if target.is_file():
            with zipfile.ZipFile(target) as archive:
                names = archive.namelist()
            check("AC4 export has 2 pages", len(names) == 2, str(names))
        grab(export_window, out_dir / "10-export-after.png")

    # -- workbench: the two imported pages are listed and selectable -------
    shelf.enterTranslation(chapter_id)
    QTest.qWait(600)
    page_list = find_item(window, "pageListView")
    page_content = page_list.property("contentItem")
    tiles = [
        child for child in page_content.childItems()
        if child.objectName().startswith("pageTile-")
    ]
    check("AC2 workbench lists 2 pages", len(tiles) == 2,
          f"{len(tiles)} tiles: {[t.objectName() for t in tiles]}")
    if tiles:
        center = QPoint(int(tiles[0].width() // 2), int(tiles[0].height() // 2))
        pos = tiles[0].mapToScene(center).toPoint()
        QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, pos)
        QTest.qWait(400)
        # Selection state lives in the workbench ViewModel's viewerPageId
        # (PageListPanel paints the selected tile from it), not in the
        # ListView currentIndex. The host overrides the panel's objectName.
        expected_id = tiles[0].objectName().replace("pageTile-", "", 1)
        viewer_page_id = find_item(window, "pageListPanelHost").property("viewerPageId")
        check("AC2 workbench first page selectable", viewer_page_id == expected_id,
              f"viewerPageId={viewer_page_id!r} expected {expected_id!r}")
    grab_and_audit(window, out_dir / "11-workbench.png", [
        "pageListPanel", "workbenchPickContext",
    ], window)
    audit_nav_rail(window, QImage(str(out_dir / "11-workbench.png")))
    navigation.navigate("settings")
    QTest.qWait(300)
    grab(window, out_dir / "12-settings.png")
    audit_nav_rail(window, QImage(str(out_dir / "12-settings.png")))
    navigation.navigate("bookshelf")
    QTest.qWait(300)

    # -- keyboard focus state ----------------------------------------------
    btn_create = find_item(window, "btnCreateBook")
    btn_create.forceActiveFocus(Qt.TabFocusReason)
    QTest.qWait(200)
    grab(window, out_dir / "13-focus-create-book.png")
    check("AC3 focus active on btnCreateBook", btn_create.hasActiveFocus())

    # -- shutdown -----------------------------------------------------------
    _shutdown_services(services)
    print("[DONE] failures: " + (", ".join(FAILURES) if FAILURES else "none"), flush=True)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
