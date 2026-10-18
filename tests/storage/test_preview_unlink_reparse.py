"""AC5 (N-004): preview cleanup must never follow a link to its destination.

The pre-fix code did ``(root / rel_path).resolve()`` and then checked the
*resolved* target for a reparse point.  A catalog entry pointing at a junction
therefore resolved to an ordinary file that passed containment, passed
``is_file()`` and passed the reparse check, so the unlink deleted the
destination - a file the tampered entry never legitimately referred to.

These tests are the injection the hardening task asks for: a junction is placed
where the real code does its check, and the protected destination must survive.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from infrastructure.sqlite.library import unlink_preview_without_following


@pytest.fixture()
def derived(tmp_path: Path) -> Path:
    root = tmp_path / "derived"
    (root / "previews").mkdir(parents=True)
    return root


def test_removes_a_plain_catalogued_preview(derived: Path) -> None:
    """The happy path still deletes: the fix must not turn into a no-op."""
    target = derived / "previews" / "keep.png"
    target.write_bytes(b"PREVIEW")

    assert unlink_preview_without_following("previews/keep.png", derived) is True
    assert not target.exists()


def test_refuses_a_junction_and_spares_the_destination(tmp_path: Path) -> None:
    """A root-internal junction resolves back inside the root.

    Containment alone therefore passes, ``is_file()`` passes on the resolved
    destination, and the destination's own ``lstat`` shows an ordinary file - so
    the pre-fix order deleted it.  Walking the raw path must refuse instead.
    """
    if sys.platform != "win32":
        pytest.skip("directory junctions are a Windows reparse-point facility")

    root = tmp_path / "derived"
    (root / "previews").mkdir(parents=True)

    protected = root / "protected" / "secret.png"
    protected.parent.mkdir(parents=True)
    protected.write_bytes(b"PROTECTED ORIGINAL")

    # previews/link -> ../protected, so "previews/link/secret.png" resolves to
    # the protected file while staying inside the derived root.
    # mklink /J needs no privileges on NTFS; os.symlink would.
    made = subprocess.run(
        [
            "cmd",
            "/c",
            "mklink",
            "/J",
            str(root / "previews" / "link"),
            str(protected.parent),
        ],
        capture_output=True,  # no text: mklink output is GBK on this box
    )
    assert made.returncode == 0, made.stderr

    removed = unlink_preview_without_following("previews/link/secret.png", root)

    assert removed is False, "the junction was traversed instead of refused"
    assert protected.is_file(), (
        "the root-internal junction was followed and the protected destination deleted"
    )


def test_refuses_absolute_and_traversing_paths(derived: Path) -> None:
    outside = derived.parent / "outside.png"
    outside.write_bytes(b"OUTSIDE")

    assert unlink_preview_without_following(str(outside), derived) is False
    assert outside.is_file()
    assert unlink_preview_without_following("../outside.png", derived) is False
    assert outside.is_file()
    assert unlink_preview_without_following("previews/./outside.png", derived) is False
    assert outside.is_file()


def test_refuses_drive_relative_and_alternate_data_stream_paths(derived: Path) -> None:
    """F-003 (Codex R1): two Windows bypasses of the absolute-path guard.

    "C:evil.png" is drive-RELATIVE, so Path.is_absolute() is False and it slipped
    past the guard entirely.  A colon also opens an alternate data stream, so
    "preview.png:stream" addresses a different file than the catalog row claims.
    """
    # Drive-relative: refused although is_absolute() is False on Windows.
    assert unlink_preview_without_following("C:evil.png", derived) is False

    # Alternate data stream on a real file: refuse, and leave the file alone.
    real = derived / "page-original-p1.png"
    real.write_bytes(b"preview")
    assert (
        unlink_preview_without_following("page-original-p1.png:ads", derived) is False
    )
    assert real.is_file(), "the real preview must survive an ADS-shaped request"

    # The happy path still works, so the new guard did not break deletion.
    assert unlink_preview_without_following("page-original-p1.png", derived) is True
    assert not real.exists()