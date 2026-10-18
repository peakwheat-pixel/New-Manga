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
