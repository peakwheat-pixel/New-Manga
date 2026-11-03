"""FEA-09 AC-1/AC-2: five-kind scanning, safety checks, ordering."""

from __future__ import annotations

import io
import zipfile

import pytest

from support import (
    DEFAULT_BUDGET,
    FakeSourceReadAccess,
    capture_facts,
    png_bytes,
    write_zip,
)
from tests.fea09.zip_fixtures import make_aes_zip, make_flat_pdf, make_zipcrypto_zip
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import SourceReadBudget
from application.importing.referenced.scanner import scan_source
from application.importing.referenced.pdf_probe import PdfiumSourceInspector

PDF_OPEN = PdfiumSourceInspector().open


def _sha(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------- image
def test_scan_single_image_ok(tmp_path):
    payload = png_bytes(5, 7, (0, 128, 255))
    path = tmp_path / "cover.png"
    path.write_bytes(payload)
    access = FakeSourceReadAccess()
    access.add_file("g-image-0000000001", "image", path)

    scanned = scan_source(access.resolve("g-image-0000000001"), pdf_open=PDF_OPEN)

    assert scanned.status == "ok"
    assert scanned.source_kind == "image"
    assert scanned.container_digest == _sha(payload)
    assert len(scanned.entries) == 1
    entry = scanned.entries[0]
    assert entry.locator == "cover.png"
    assert entry.ordinal == 0
    assert entry.content_digest == _sha(payload)
    assert entry.content_digest_kind == "encoded"


def test_scan_image_unsupported_suffix_typed(tmp_path):
    path = tmp_path / "note.txt"
    path.write_bytes(b"not an image")
    access = FakeSourceReadAccess()
    access.add_file("g-image-0000000002", "image", path)

    scanned = scan_source(access.resolve("g-image-0000000002"), pdf_open=PDF_OPEN)

    assert scanned.status == "unsupported"
    assert scanned.reason_code == "SOURCE_FORMAT_UNSUPPORTED"
    assert scanned.entries == []


def test_scan_image_corrupt_bytes(tmp_path):
    path = tmp_path / "broken.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n-not-really-png")
    access = FakeSourceReadAccess()
    access.add_file("g-image-0000000003", "image", path)

    scanned = scan_source(access.resolve("g-image-0000000003"), pdf_open=PDF_OPEN)

    # Scan-level the bytes verify against grant facts; corruption is an
    # entry-level decode failure at start time, not a scan failure.
    assert scanned.status == "ok"


def test_scan_image_identity_drift(tmp_path):
    payload = png_bytes()
    path = tmp_path / "a.png"
    path.write_bytes(payload)
    access = FakeSourceReadAccess()
    access.add_file("g-image-0000000004", "image", path)
    path.write_bytes(png_bytes(9, 9, (1, 2, 3)))  # same file, new content

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-image-0000000004"), pdf_open=PDF_OPEN)
    assert caught.value.code == "FILE_IDENTITY_CHANGED"


# -------------------------------------------------------------------- folder
def _folder(tmp_path, name="folder"):
    root = tmp_path / name
    root.mkdir()
    return root


def test_scan_folder_natural_order_and_unsupported(tmp_path):
    root = _folder(tmp_path)
    files = {}
    for name in ["1.png", "2.png", "10.png", "100.png", "nested/a3.png"]:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        files[name] = png_bytes(3, 3)
        target.write_bytes(files[name])
    (root / "nested" / "skip.txt").write_bytes(b"note")
    members = [
        root / "1.png", root / "2.png", root / "10.png", root / "100.png",
        root / "nested" / "a3.png", root / "nested" / "skip.txt",
    ]
    access = FakeSourceReadAccess()
    access.add_folder("g-folder-0000000001", root, members)

    scanned = scan_source(access.resolve("g-folder-0000000001"), pdf_open=PDF_OPEN)

    assert scanned.status == "ok"
    assert [e.locator for e in scanned.entries] == [
        "1.png", "2.png", "10.png", "100.png", "nested/a3.png", "nested/skip.txt",
    ]
    assert scanned.entries[5].content_digest is None  # txt: unsupported member
    for entry in scanned.entries[:5]:
        assert entry.content_digest == _sha(files[entry.locator])


def test_scan_folder_member_escapes_root_denied(tmp_path):
    root = _folder(tmp_path, "inside")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.png").write_bytes(png_bytes())
    access = FakeSourceReadAccess()
    access.add_folder("g-folder-0000000002", root, [outside / "x.png"])

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-folder-0000000002"), pdf_open=PDF_OPEN)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


def test_scan_folder_member_identity_drift(tmp_path):
    root = _folder(tmp_path, "drift")
    member = root / "a.png"
    member.write_bytes(png_bytes())
    access = FakeSourceReadAccess()
    access.add_folder("g-folder-0000000003", root, [member])
    member.write_bytes(png_bytes(8, 8))  # replaced after the grant

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-folder-0000000003"), pdf_open=PDF_OPEN)
    assert caught.value.code == "FILE_IDENTITY_CHANGED"


# ---------------------------------------------------------------- zip / cbz
def test_scan_zip_order_duplicate_members_digests(tmp_path):
    pages = {
        "001.png": png_bytes(2, 2, (255, 0, 0)),
        "002.png": png_bytes(2, 2, (0, 255, 0)),
        "010.png": png_bytes(2, 2, (0, 0, 255)),
        "dup/001.png": png_bytes(2, 2, (255, 0, 0)),  # duplicate content+name
    }
    path = write_zip(tmp_path / "book.zip", list(pages.items()))
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000001", "zip", path)

    scanned = scan_source(access.resolve("g-zip-0000000000001"), pdf_open=PDF_OPEN)

    assert scanned.status == "ok"
    assert [e.locator for e in scanned.entries] == [
        "001.png", "002.png", "010.png", "dup/001.png",
    ]
    # Independent occurrences: same name AND same content keep separate
    # entries with distinct ordinals (C-15 §3.2).
    assert scanned.entries[0].ordinal == 0
    assert scanned.entries[3].ordinal == 3
    # duplicate name + identical content, independent occurrence rows:
    assert scanned.entries[0].content_digest == scanned.entries[3].content_digest
    for entry in scanned.entries:
        assert entry.content_digest == _sha(pages[entry.locator])


def test_scan_cbz_unsupported_only_members(tmp_path):
    path = write_zip(tmp_path / "text.cbz", [("a.txt", b"x"), ("b.txt", b"y")])
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000001", "cbz", path)

    scanned = scan_source(access.resolve("g-cbz-0000000000001"), pdf_open=PDF_OPEN)

    assert scanned.status == "ok"  # container fine; members unsupported
    assert all(entry.content_digest is None for entry in scanned.entries)
    assert len(scanned.entries) == 2


def test_scan_zip_traversal_member_denied(tmp_path):
    path = write_zip(tmp_path / "evil.zip", [("../evil.png", b"ABCD")])
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000002", "zip", path)

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-zip-0000000000002"), pdf_open=PDF_OPEN)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


def test_scan_zip_absolute_member_denied(tmp_path):
    path = write_zip(tmp_path / "abs.zip", [("/abs/path.png", b"data")])
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000003", "zip", path)

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-zip-0000000000003"), pdf_open=PDF_OPEN)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


AES_FIXTURE_SHA256 = "437fe717fdfe74d52ba83475f9af836894101597ec23397054a251678274acc1"


def test_scan_zip_aes_typed_unsupported(tmp_path):
    """AES ZIP：预生成 fixture（SHA-256 见 FIXTURES.md）→ typed unsupported。"""
    import hashlib
    from pathlib import Path

    fixture = Path(__file__).parent / "fixtures" / "aes_member.zip"
    blob = fixture.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == AES_FIXTURE_SHA256
    path = tmp_path / "aes.zip"
    path.write_bytes(blob)
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000004", "zip", path)

    scanned = scan_source(access.resolve("g-zip-0000000000004"), pdf_open=PDF_OPEN)

    assert scanned.status == "unsupported"
    assert scanned.reason_code == "SOURCE_FORMAT_UNSUPPORTED"
    assert scanned.entries == []


def test_scan_zip_decompression_budget(tmp_path):
    pages = [(f"{i:03d}.png", png_bytes(6, 6)) for i in range(4)]
    path = write_zip(tmp_path / "big.zip", pages)
    access = FakeSourceReadAccess()
    access.add_file(
        "g-zip-0000000000005", "zip", path,
        budget=SourceReadBudget(max_bytes=8 << 20, max_decode_bytes=8, max_entries=1000),
    )

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-zip-0000000000005"), pdf_open=PDF_OPEN)
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"


def test_scan_zip_read_budget(tmp_path):
    path = write_zip(tmp_path / "cap.zip", [("a.png", png_bytes(4, 4))])
    access = FakeSourceReadAccess()
    access.add_file(
        "g-zip-0000000000006", "zip", path,
        budget=SourceReadBudget(max_bytes=4, max_decode_bytes=8 << 20, max_entries=1000),
    )

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-zip-0000000000006"), pdf_open=PDF_OPEN)
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"


def test_scan_zip_corrupt_container(tmp_path):
    path = tmp_path / "broken.zip"
    path.write_bytes(b"PK\x03\x04 definitely not a zip")
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000007", "zip", path)

    scanned = scan_source(access.resolve("g-zip-0000000000007"), pdf_open=PDF_OPEN)

    assert scanned.status == "error"
    assert scanned.reason_code == "SOURCE_FORMAT_UNSUPPORTED"


def test_scan_zip_entry_budget(tmp_path):
    pages = [(f"{i:02d}.png", png_bytes(2, 2)) for i in range(5)]
    path = write_zip(tmp_path / "many.zip", pages)
    access = FakeSourceReadAccess()
    access.add_file(
        "g-zip-0000000000008", "zip", path,
        budget=SourceReadBudget(max_bytes=8 << 20, max_decode_bytes=8 << 20, max_entries=2),
    )

    with pytest.raises(SourceImportError) as caught:
        scan_source(access.resolve("g-zip-0000000000008"), pdf_open=PDF_OPEN)
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"


# ----------------------------------------------------------------------- pdf
def test_scan_pdf_page_identity_entries(tmp_path):
    pdf = make_flat_pdf(3)
    path = tmp_path / "doc.pdf"
    path.write_bytes(pdf)
    access = FakeSourceReadAccess()
    access.add_file("g-pdf-00000000000001", "pdf", path)

    scanned = scan_source(access.resolve("g-pdf-00000000000001"), pdf_open=PDF_OPEN)

    assert scanned.status == "ok"
    assert [e.locator for e in scanned.entries] == ["1", "2", "3"]
    assert [e.ordinal for e in scanned.entries] == [0, 1, 2]
    from application.importing.referenced.model import pdf_page_identity_digest

    for entry in scanned.entries:
        assert entry.content_digest == pdf_page_identity_digest(
            scanned.container_digest, entry.ordinal
        )
        assert entry.content_digest_kind == "page-identity"


def test_scan_pdf_encrypted_structural_only(tmp_path):
    class _EncryptedOpen:
        def __call__(self, data, password):
            raise SourceImportError(
                "SOURCE_PASSWORD_REQUIRED", "the pdf source requires a password"
            )

    pdf = make_flat_pdf(2)
    path = tmp_path / "secret.pdf"
    path.write_bytes(pdf)
    access = FakeSourceReadAccess()
    access.add_file("g-pdf-00000000000002", "pdf", path)

    scanned = scan_source(
        access.resolve("g-pdf-00000000000002"), pdf_open=_EncryptedOpen()
    )

    assert scanned.status == "encrypted"
    assert scanned.structural_only is True
    # No content digests before the password is confirmed (C-16 §3).
    assert all(entry.content_digest is None for entry in scanned.entries)
    # pypdfium2 cannot even count pages without the password: the page
    # count stays "unknown" in the encrypted preview (C-16 §3).
    assert scanned.entries == []


# ---------------------------------------------------------------- zipcrypto
def test_scan_zipcrypto_plans_encrypted_no_digests(tmp_path):
    blob = make_zipcrypto_zip(
        [("001.png", png_bytes(3, 3)), ("002.png", png_bytes(3, 3, (0, 255, 0)))],
        "s3cret",
    )
    path = tmp_path / "locked.cbz"
    path.write_bytes(blob)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000002", "cbz", path)

    scanned = scan_source(access.resolve("g-cbz-0000000000002"), pdf_open=PDF_OPEN)

    assert scanned.status == "encrypted"
    assert scanned.structural_only is True
    assert [e.locator for e in scanned.entries] == ["001.png", "002.png"]
    assert all(e.content_digest is None for e in scanned.entries)


def test_scan_zipcrypto_with_password_computes_digests(tmp_path):
    payload_a, payload_b = png_bytes(3, 3), png_bytes(3, 3, (9, 9, 9))
    blob = make_zipcrypto_zip(
        [("001.png", payload_a), ("002.png", payload_b)], "s3cret"
    )
    path = tmp_path / "locked2.cbz"
    path.write_bytes(blob)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000003", "cbz", path)

    scanned = scan_source(
        access.resolve("g-cbz-0000000000003"),
        pdf_open=PDF_OPEN,
        password=b"s3cret",
    )

    assert scanned.status == "ok"  # confirmed-password rescan decrypts
    assert [e.content_digest for e in scanned.entries] == [
        _sha(payload_a), _sha(payload_b),
    ]


def test_scan_zipcrypto_wrong_password_typed_invalid(tmp_path):
    blob = make_zipcrypto_zip([("001.png", png_bytes(3, 3))], "s3cret")
    path = tmp_path / "locked3.cbz"
    path.write_bytes(blob)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000004", "cbz", path)

    with pytest.raises(SourceImportError) as caught:
        scan_source(
            access.resolve("g-cbz-0000000000004"),
            pdf_open=PDF_OPEN,
            password=b"wr0ng",
        )
    assert caught.value.code == "SOURCE_PASSWORD_INVALID"
