"""Reviewer-side probes for TASK-045 (Codex, non-author review of 1171bc5).

Section A (no QML): re-derives the F-4 property from scratch. The page is
written by this script with its own stdlib PNG encoder; every row encodes its
own page index, and the stitched tile rows are compared against the page as
decoded by Qt itself -- not against the pattern function, so a self-consistent
mistake cannot pass.

Section B (QML): measures the *production trigger* for tile materialisation.
The author test asserts the sources are dropped on a page turn and then calls
vm.requestTiles() by hand; this probe never calls it, so what it reports is
what the shipped QML does on its own (the only trigger in ReaderView.qml is
onContentYChanged).

Run:  TASK045_WORKTREE=<branch worktree> python reviewer_probe.py
Env:  TASK045_BASE_SRC=<optional base src tree> to also run section A against
      the pre-fix implementation (discriminance).
"""

import os
import struct
import sys
import tempfile
import time
import zlib
from pathlib import Path

WT = os.environ.get("TASK045_WORKTREE", r"G:\CODEX\New Manga.worktrees\TASK-045-deepseek")
SRC = os.environ.get("TASK045_SRC", str(Path(WT) / "src"))
sys.path.insert(0, SRC)
sys.path.insert(0, str(Path(WT) / "tests" / "reading_export"))

WIDTH, HEIGHT = 60, 1200
TILE, OVERLAP = 500, 40


def row_bytes(y, width=WIDTH):
    value = (y * 7 + 3) % 251
    return bytes([value, (value * 3) % 251, (value * 11) % 251]) * width


def encode_png(rows, width, height):
    raw = b"".join(b"\x00" + row for row in rows)

    def chunk(tag, payload):
        body = tag + payload
        return (
            struct.pack(">I", len(payload))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 0))
        + chunk(b"IEND", b"")
    )


def write_probe_page(path):
    path.write_bytes(encode_png([row_bytes(y) for y in range(HEIGHT)], WIDTH, HEIGHT))


def qt_rows(path_or_bytes):
    from PySide6.QtGui import QImage

    image = QImage()
    if isinstance(path_or_bytes, (bytes, bytearray)):
        assert image.loadFromData(bytes(path_or_bytes))
    else:
        assert image.load(str(path_or_bytes))
    image = image.convertToFormat(QImage.Format.Format_RGB32)
    bits = bytes(image.constBits())
    stride = image.bytesPerLine()
    width = image.width() * 4
    return [bits[y * stride : y * stride + width] for y in range(image.height())]


def section_a(tmp, label):
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    source = Path(tmp) / "probe_page.png"
    write_probe_page(source)
    rasterizer = TiledPageRasterizer(
        source, cache_dir=Path(tmp) / "tiles", tile_height=TILE, overlap=OVERLAP
    )
    page_rows = qt_rows(source)
    assert len(page_rows) == HEIGHT, f"encoder sanity: {len(page_rows)} != {HEIGHT}"
    assert page_rows[1] != page_rows[2], "encoder sanity: rows must differ"
    print(f"[{label}] page={rasterizer.page_size} tiles={rasterizer.grid.tile_count}")

    stitched = []
    bad_height = []
    bad_rows = []
    for tile in rasterizer.grid.tiles:
        rows = qt_rows(rasterizer.tile_file(tile.index))
        if len(rows) != tile.content_height:
            bad_height.append((tile.index, len(rows), tile.content_height))
        expected = page_rows[tile.content_top : tile.content_bottom]
        if rows != expected:
            bad_rows.append(tile.index)
        stitched.extend(rows)
    heights = [tile.content_height for tile in rasterizer.grid.tiles]
    print(f"[{label}] declared content heights: {heights}")
    print(f"[{label}] tile-file height mismatches: {bad_height}")
    print(f"[{label}] tiles whose rows != their page rows: {bad_rows}")
    print(f"[{label}] stitched rows == whole page: {stitched == page_rows} "
          f"({len(stitched)} vs {len(page_rows)} rows)")
    return not bad_height and not bad_rows and stitched == page_rows


def find_by_name(root, name):
    from PySide6.QtCore import QObject

    if root.objectName() == name:
        return root
    for child in root.findChildren(QObject):
        if child.objectName() == name:
            return child
    return None


def served_sources(host):
    got = []
    if host is None:
        return got
    for item in host.childItems():
        source = item.property("source")
        if source is None:
            continue
        text = source.toString() if hasattr(source, "toString") else str(source)
        if text:
            got.append(Path(text.replace("file:///", "")).name)
    return got


def pump(seconds, condition=None):
    from PySide6.QtGui import QGuiApplication

    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        QGuiApplication.processEvents()
        if condition is not None and condition():
            return True
        time.sleep(0.02)
    return False


def section_b(tmp):
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication, QImage, qRgb
    from PySide6.QtQml import QQmlComponent, QQmlEngine
    from PySide6.QtQuick import QQuickItem, QQuickWindow  # noqa: F401 - registers the item types so QML items wrap as QQuickItem

    from application.export import ExportService, JsonHistoryDocumentStore
    from application.reading import JsonProgressDocumentStore, ReaderPage
    from application.reading.service import ReadingService
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer
    from ui.viewmodels.reader.viewmodel import ReaderViewModel

    app = QGuiApplication.instance() or QGuiApplication([])
    pages = []
    for index in range(2):
        path = Path(tmp) / f"page_{index}.png"
        image = QImage(60, 1200, QImage.Format.Format_RGB32)
        image.fill(qRgb(120 + index * 60, 40, 40))
        assert image.save(str(path))
        pages.append(
            ReaderPage(
                page_id=f"p{index}",
                filename=path.name,
                original_path=str(path),
                text=f"第 {index} 页",
            )
        )

    class Catalog:
        def list_pages(self, chapter_id):
            return list(pages)

    reading = ReadingService(JsonProgressDocumentStore(Path(tmp) / "progress.json"))
    export_service = ExportService(JsonHistoryDocumentStore(Path(tmp) / "history.json"))

    def factory(path):
        return TiledPageRasterizer(
            path, cache_dir=Path(tmp) / "tile-cache", tile_height=600, overlap=32
        )

    vm = ReaderViewModel(
        reading, Catalog(), export_service=export_service, tile_factory=factory
    )
    engine = QQmlEngine()
    engine.rootContext().setContextProperty("readerViewModel", vm)
    qml_dir = Path(WT) / "src" / "ui" / "qml" / "reader"
    host_qml = (
        "import QtQuick\nimport QtQuick.Controls\n"
        "ApplicationWindow { objectName: \"probeWindow\"; width: 900; height: 700;"
        " ReaderView { anchors.fill: parent } }\n"
    )
    component = QQmlComponent(engine)
    component.setData(host_qml.encode(), QUrl.fromLocalFile(str(qml_dir / "host.qml")))
    if component.isError():
        raise RuntimeError(component.errorString())
    window = component.create()
    window._keep = component
    window.show()
    pump(1.5)

    root = find_by_name(window, "readerView")
    vm.openChapter("b", "c", "条漫", "webtoon", "vertical")
    pump(2.0, lambda: find_by_name(root, "readerWebtoonScroll") is not None)
    pump(2.0)
    host = find_by_name(root, "readerTilesHost")
    scroll = find_by_name(root, "readerWebtoonScroll")
    print(f"[B] tilesActive={vm.tilesActive} pagePixelWidth={vm.pagePixelWidth} "
          f"hostVisible={bool(host.property('visible')) if host else None}")
    fallback = find_by_name(root, "readerPage")
    def state(tag):
        print(f"    {tag}: hostVisualChildren={len(host.childItems())} (Repeater + its delegates) "
              f"sources={served_sources(host)} "
              f"wholePageImageVisible={fallback.property(chr(118)+chr(105)+chr(115)+chr(105)+chr(98)+chr(108)+chr(101))}")

    print("[B1] first open, no manual requestTiles")
    state("B1")

    scroll.setProperty("contentY", 13)
    pump(2.0)
    first = served_sources(host)
    print(f"[B2] after one scroll (contentY=13) -> {len(first)} source(s): {first}")

    vm.nextPage()
    pump(2.5)
    after_turn = served_sources(host)
    print(f"[B3] after nextPage, page={vm.pageNumber}, no manual request")
    state("B3")
    print(f"    B3 sources were {after_turn}")

    scroll.setProperty("contentY", 27)
    pump(2.5)
    second = served_sources(host)
    print(f"[B4] after a scroll on page 2 -> {len(second)} source(s): {second}")
    print(f"[B4] page-2 tiles differ from page-1 tiles: {second != first}")
    window.close()


def main():
    tmp = tempfile.mkdtemp(prefix="nm045probe")
    print(f"src tree = {SRC}")
    ok_a = section_a(tempfile.mkdtemp(prefix="nm045a"), "A")
    print(f"[A] F-4 property holds: {ok_a}")
    section_b(tempfile.mkdtemp(prefix="nm045b"))


if __name__ == "__main__":
    main()
