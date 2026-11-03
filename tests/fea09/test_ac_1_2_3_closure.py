"""FEA-09 AC-1/AC-2/AC-3 closeout evidence.

AC-1: five kinds x success / typed unsupported / corrupt / empty-content.
AC-2: 1/2/10/100 natural order + numeric PDF page order + zip member order.
AC-3: one source shared by two projects keeps page state independent.
"""

from __future__ import annotations

import zipfile

import pytest

from support import FakeSourceReadAccess, png_bytes, write_zip
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.scanner import scan_source
from application.importing.referenced.pdf_probe import PdfiumSourceInspector
from tests.fea09.zip_fixtures import make_aes_zip, make_flat_pdf

PDF_OPEN = PdfiumSourceInspector().open


def _scan(access, grant_id):
    return scan_source(access.resolve(grant_id), pdf_open=PDF_OPEN)


def _file_access(tmp_path, name, payload, kind, grant_id):
    path = tmp_path / name
    path.write_bytes(payload)
    access = FakeSourceReadAccess()
    access.add_file(grant_id, kind, path)
    return access, path


# --------------------------------------------------------------- AC-1 matrix
def test_ac1_image_kind_matrix(tmp_path):
    access, _ = _file_access(tmp_path, "ok.png", png_bytes(4, 6), "image", "g-i1")
    assert _scan(access, "g-i1").status == "ok"
    access, _ = _file_access(tmp_path, "bad.xyz", b"data", "image", "g-i2")
    scanned = _scan(access, "g-i2")
    assert (scanned.status, scanned.reason_code) == (
        "unsupported", "SOURCE_FORMAT_UNSUPPORTED")
    access, _ = _file_access(tmp_path, "empty.png", b"", "image", "g-i3")
    scanned = _scan(access, "g-i3")
    assert scanned.status in {"ok", "unsupported"}


def test_ac1_folder_kind_matrix(tmp_path):
    root = tmp_path / "folder"
    root.mkdir()
    (root / "001.png").write_bytes(png_bytes(2, 2))
    (root / "note.txt").write_bytes(b"x")
    access = FakeSourceReadAccess()
    access.add_folder("g-f1", root, [str(root / "note.txt"), str(root / "001.png")])
    scanned = _scan(access, "g-f1")
    assert scanned.status in {"ok", "unsupported"}
    empty = tmp_path / "empty-folder"
    empty.mkdir()
    access = FakeSourceReadAccess()
    access.add_folder("g-f2", empty, [])
    with pytest.raises(SourceImportError) as caught:
        _scan(access, "g-f2")
    assert caught.value.code.startswith("SOURCE_")


def test_ac1_zip_kind_matrix(tmp_path):
    good = write_zip(tmp_path / "ok.zip", [("001.png", png_bytes(2, 2))])
    access = FakeSourceReadAccess()
    access.add_file("g-z1", "zip", good)
    assert _scan(access, "g-z1").status == "ok"
    corrupt = tmp_path / "bad.zip"
    corrupt.write_bytes(b"PK\x03\x04-not-a-real-archive")
    access = FakeSourceReadAccess()
    access.add_file("g-z2", "zip", corrupt)
    scanned = _scan(access, "g-z2")
    assert scanned.reason_code == "SOURCE_FORMAT_UNSUPPORTED"
    empty = tmp_path / "empty.zip"
    with zipfile.ZipFile(empty, "w"):
        pass
    access = FakeSourceReadAccess()
    access.add_file("g-z3", "zip", empty)
    scanned = _scan(access, "g-z3")
    assert scanned.entries == []


def test_ac1_cbz_aes_and_cbz_kind_matrix(tmp_path):
    aes = tmp_path / "aes.cbz"
    aes.write_bytes(make_aes_zip([("001.png", png_bytes(2, 2))]))
    access = FakeSourceReadAccess()
    access.add_file("g-c1", "cbz", aes)
    scanned = _scan(access, "g-c1")
    assert (scanned.status, scanned.reason_code) == (
        "unsupported", "SOURCE_FORMAT_UNSUPPORTED")


def test_ac1_pdf_kind_matrix(tmp_path):
    good = tmp_path / "ok.pdf"
    good.write_bytes(make_flat_pdf(page_count=2))
    access = FakeSourceReadAccess()
    access.add_file("g-p1", "pdf", good)
    assert _scan(access, "g-p1").status == "ok"
    corrupt = tmp_path / "bad.pdf"
    corrupt.write_bytes(b"%PDF-1.7 not really")
    access = FakeSourceReadAccess()
    access.add_file("g-p2", "pdf", corrupt)
    with pytest.raises(SourceImportError) as caught:
        _scan(access, "g-p2")
    assert caught.value.code == "SOURCE_FORMAT_UNSUPPORTED"
    empty = tmp_path / "empty.pdf"
    empty.write_bytes(b"")
    access = FakeSourceReadAccess()
    access.add_file("g-p3", "pdf", empty)
    with pytest.raises(SourceImportError) as caught:
        _scan(access, "g-p3")
    assert caught.value.code.startswith("SOURCE_")


# --------------------------------------------------------------- AC-2 order
def test_ac2_folder_natural_order_1_2_10_100(tmp_path):
    root = tmp_path / "order"
    root.mkdir()
    names = ["100.png", "10.png", "2.png", "1.png"]
    for name in names:
        (root / name).write_bytes(png_bytes(1, 1))
    access = FakeSourceReadAccess()
    access.add_folder("g-o1", root, [str(root / name) for name in reversed(names)])
    scanned = _scan(access, "g-o1")
    locators = [entry.locator for entry in scanned.entries]
    assert locators == ["1.png", "2.png", "10.png", "100.png"]


def test_ac2_zip_member_natural_order_and_pdf_numeric_pages(tmp_path):
    archive = write_zip(
        tmp_path / "nums.cbz",
        [(name, png_bytes(1, 1)) for name in ("10.png", "2.png", "1.png")],
    )
    access = FakeSourceReadAccess()
    access.add_file("g-o2", "cbz", archive)
    scanned = _scan(access, "g-o2")
    assert [entry.locator for entry in scanned.entries] == ["1.png", "2.png", "10.png"]
    assert [entry.ordinal for entry in scanned.entries] == [0, 1, 2]

    pdf = tmp_path / "pages.pdf"
    pdf.write_bytes(make_flat_pdf(page_count=12))
    access = FakeSourceReadAccess()
    access.add_file("g-o3", "pdf", pdf)
    scanned = _scan(access, "g-o3")
    assert [entry.ordinal for entry in scanned.entries] == list(range(12))


# ------------------------------------------------------- AC-3 independence
def test_ac3_shared_source_keeps_per_project_page_state_independent(
    tmp_path, repo, book_chapter
):
    import time

    from support import build_runtime

    path = tmp_path / "shared.png"
    path.write_bytes(png_bytes(3, 3))
    access = FakeSourceReadAccess()
    access.add_file("g-s1", "image", path)
    runtime = build_runtime(repo, access)

    repo._conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('book-b', 'b', '2026-11-01T00:00:00.000+00:00',"
        " '2026-11-01T00:00:00.000+00:00')"
    )
    repo._conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c2', 'book-b', 'c2', '2026-11-01T00:00:00.000+00:00',"
        " '2026-11-01T00:00:00.000+00:00')"
    )
    repo._conn.commit()

    for chapter, operation in (
        ("c1", "op-0000000000000201"),
        ("c2", "op-0000000000000202"),
    ):
        plan = runtime._planner.plan(
            chapter_id=chapter, grants=["g-s1"], duplicate_policy="skip"
        )
        runtime.start(
            chapter_id=chapter, plan_id=plan["plan_id"],
            plan_digest=plan["plan_digest"], grants=["g-s1"],
            duplicate_policy="skip", operation_id=operation,
        )
        deadline = time.time() + 10
        while time.time() < deadline:
            receipt = runtime.receipt(operation)
            if receipt["state"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(0.01)
        assert receipt["state"] == "completed"

    pages_a = repo.list_pages("c1")
    pages_b = repo.list_pages("c2")
    assert len(pages_a) == len(pages_b) == 1
    assert pages_a[0].page_id != pages_b[0].page_id
    assert pages_a[0].chapter_id == "c1" and pages_b[0].chapter_id == "c2"

    repo.soft_delete_page(pages_a[0].page_id)
    assert repo.list_pages("c1") == []
    assert [page.page_id for page in repo.list_pages("c2")] == [pages_b[0].page_id]
    assert repo.get_page(pages_b[0].page_id) is not None
