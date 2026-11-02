"""AC4: pin the long-path capability so a future change cannot silently lose it.

SEC-FMT-004 asks that a path over 260 characters can still be read and
written. It frames the fix as "enable the Windows \\\\?\\ long-path prefix",
and this project does not do that - there is no prefix adder and no
longPathAware declaration.

It passes anyway, because Python 3.6+ uses the wide-character Win32 APIs on
Windows, so pathlib never meets the 260-character limit the requirement
assumes. That was measured, not inferred: see
verification/SEC-FMT-IMPL-1/sfx004-long-path-repro.md, where the full
ManagedFileStorage lifecycle passed at a 434-character path.

The gap this file closes is regression, not function: today's capability rests
on an implicit property of the interpreter and the libraries underneath it.
If either changes, nothing would notice. These tests notice.
"""

from __future__ import annotations

import os

import pytest

from infrastructure.filesystem.managed_storage import ManagedFileStorage

#: The threshold SEC-FMT-004 names. A root below this cannot exercise the case.
_LONG = 260
#: Comfortably above it, without approaching any filesystem node limit.
_ROOT_TARGET = 300


def _deep_root(tmp_path, target_len: int = _ROOT_TARGET) -> str:
    """Build a directory chain whose absolute path exceeds target_len."""
    deep = str(tmp_path)
    index = 0
    while len(deep) < target_len and index < 40:
        deep = os.path.join(deep, "segment" + str(index).zfill(3) + "x" * 12)
        index += 1
    os.makedirs(deep, exist_ok=True)
    return deep


def _relative_path() -> str:
    """A realistic managed-layout path, long enough to matter."""
    return (
        "books/" + "b" * 60 + "/chapters/" + "c" * 40 + "/images/r1.png"
    )


def test_long_root_exceeds_the_threshold(tmp_path) -> None:
    """Guard the guard: if the root is not actually long, the rest is vacuous."""
    root = _deep_root(tmp_path)
    assert len(root) > _LONG, f"root is only {len(root)} chars"


def test_full_lifecycle_on_a_long_path(tmp_path) -> None:
    """write_temp -> verify -> publish -> read -> remove, all over 260 chars."""
    root = _deep_root(tmp_path)
    storage = ManagedFileStorage(root)
    storage.ensure_layout()

    relative = _relative_path()
    absolute = storage.absolute_path(relative)
    assert len(absolute) > _LONG, f"full path is only {len(absolute)} chars"

    payload = b"long-path-payload" * 64
    handle = storage.write_temp(payload)
    storage.verify_temp(handle)
    storage.publish(handle, relative)

    assert os.path.exists(absolute), "published file missing at the long path"
    with open(absolute, "rb") as stream:
        assert stream.read() == payload

    storage.remove_managed(relative)
    assert not os.path.exists(absolute), "remove_managed left the file behind"


def test_ensure_layout_works_on_a_long_root(tmp_path) -> None:
    """Layout creation is the first thing every run does; it must not be the
    place where a long root fails."""
    root = _deep_root(tmp_path)
    assert len(root) > _LONG
    ManagedFileStorage(root).ensure_layout()


@pytest.mark.parametrize("target", [270, 350, 430])
def test_capability_holds_across_several_lengths(tmp_path, target: int) -> None:
    """Do not pin a single length.

    A capability that works at 300 and breaks at 430 is worse than one that
    fails at 300, because the first only shows up in a user's real library.
    """
    root = _deep_root(tmp_path, target)
    assert len(root) >= target
    storage = ManagedFileStorage(root)
    storage.ensure_layout()

    relative = _relative_path()
    absolute = storage.absolute_path(relative)
    handle = storage.write_temp(b"x" * 256)
    storage.publish(handle, relative)
    assert os.path.exists(absolute)
    with open(absolute, "rb") as stream:
        assert len(stream.read()) == 256
