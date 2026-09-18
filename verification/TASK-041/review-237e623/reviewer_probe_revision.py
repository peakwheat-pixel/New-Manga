"""Reviewer-side re-check of the TASK-041 revision (Codex, non-author).

Pins the semantics the first review demanded, from the reviewer side:

1. a tree carrying the extractor's non-page outputs (cover%05d, HDimage%05d)
   yields exactly the KF7 page images;
2. ordering is by the record number in the name (numeric, not lexicographic):
   image00009 before image00010;
3. a mirrored mobi8/ tree fails typed (KF8/AZW3 fail-closed), and so does a
   KF8-only tree;
4. names that do not fullmatch image%05d.<ext> are excluded rather than
   silently becoming pages.

Env: TASK041_WORKTREE (default the task worktree).
"""

import os
import sys
import tempfile
from pathlib import Path

WT = os.environ.get("TASK041_WORKTREE", r"G:\CODEX\New Manga.worktrees\TASK-041-zcode")
sys.path.insert(0, os.path.join(WT, "src"))
sys.path.insert(0, os.path.join(WT, "tests", "import_formats"))

from test_mobi_import import _make_jpeg, picture_mobi  # noqa: E402
from infrastructure.importing import MobiDocumentRaster  # noqa: E402
from application.importing.documents.ports import DocumentDecodeError  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
import mobi as binding  # noqa: E402

RED, GREEN, BLUE, WHITE = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)


def make_tree(image_names, *, mobi8=False, cover=True, hd=True):
    root = Path(tempfile.mkdtemp(prefix="nm041rev"))
    imgdir = root / "mobi7" / "Images"
    imgdir.mkdir(parents=True)
    (root / "mobi7" / "book.html").write_text("<html></html>", encoding="utf-8")
    for index, (name, colour, size) in enumerate(image_names):
        (imgdir / name).write_bytes(_make_jpeg(size[0], size[1], colour))
    if cover:
        (imgdir / "cover00001.jpeg").write_bytes(_make_jpeg(4, 4, WHITE))
    if hd:
        hddir = root / "HDImages"
        hddir.mkdir(parents=True)
        (hddir / "HDimage00004.jpeg").write_bytes(_make_jpeg(5, 5, BLUE))
    if mobi8:
        kf8 = root / "mobi8" / "OEBPS" / "Images"
        kf8.mkdir(parents=True)
        (kf8 / "image00002.jpeg").write_bytes(_make_jpeg(8, 6, RED))
    return root


def run(label, root):
    original = binding.extract
    binding.extract = lambda infile: (str(root), str(root / "mobi7" / "book.html"))
    try:
        handle = MobiDocumentRaster().open(picture_mobi([_make_jpeg(8, 6, RED)]))
        pages = []
        for index in range(handle.page_count):
            image = QImage()
            assert image.loadFromData(handle.render_page(index).png)
            colour = image.pixelColor(1, 1)
            pages.append((image.width(), image.height(),
                          (colour.red(), colour.green(), colour.blue())))
        handle.close()
        print(f"[{label}] pages={len(pages)} {pages}")
    except DocumentDecodeError as error:
        print(f"[{label}] typed failure reason={error.reason} detail={error.detail[:72]}")
    finally:
        binding.extract = original


H = (8, 6)
run("1 noise tree (cover+HD+images 02,03)",
    make_tree([("image00002.jpeg", RED, H), ("image00003.jpeg", GREEN, (9, 7))]))

run("2 numeric order (records 09 then 10)",
    make_tree([("image00010.jpeg", GREEN, (9, 7)), ("image00009.jpeg", RED, H)]))

run("3 mirrored mobi8 tree",
    make_tree([("image00002.jpeg", RED, H)], mobi8=True))

kf8_only = Path(tempfile.mkdtemp(prefix="nm041kf8"))
(kf8_only / "mobi8" / "OEBPS" / "Images").mkdir(parents=True)
(kf8_only / "mobi8" / "OEBPS" / "Images" / "image00002.jpeg").write_bytes(
    _make_jpeg(8, 6, RED))
run("4 KF8-only tree (no mobi7)", kf8_only)

run("5 non-conforming names excluded",
    make_tree([("image00002.jpeg", RED, H), ("image0002.jpeg", GREEN, H),
               ("image.jpeg", BLUE, H), ("imagenote00003.jpeg", GREEN, H)]))

run("6 same record, two extensions",
    make_tree([("image00002.jpeg", RED, H), ("image00002.png", GREEN, H)]))
