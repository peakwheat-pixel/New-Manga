"""R6 P1-A probe: publish cleanup must not delete through a repointed directory.

R6 reproduced an outside delete through publish_original's exception cleanup and read
outside bytes. Reading the file, the same four lines appear twice - publish and
publish_original - so the fix covers both. R6's probe was run in its own sandbox and is
not in this repository, so this is the regression case for the site.

How the race is won: the cleanup path is only reached when publishing fails, so the
probe makes it fail deterministically by pointing managed_file at a missing file. The
hook then fires on the call the cleanup is about to make and swaps the directory for a
junction to an outside tree, which is exactly the window between deciding which path to
delete and deleting it.

injection_fired is reported separately, so a hook that never fires cannot be read as a
defended attack. Fixtures are under the workspace.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1")
sys.path.insert(0, str(REPO / "src"))

import infrastructure.filesystem.win_unlink as w  # noqa: E402
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402

WS = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1\verification\P09-MANAGED-READ-ROOT-TRUST-1\_scratch\p1-publish")
if WS.exists():
    for child in WS.iterdir():
        if child.is_dir() and child.is_symlink():
            child.unlink()
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

derived_root = WS / "derived"
(derived_root / "pages").mkdir(parents=True)
target = derived_root / "pages" / "page-original-p1.png"
target.write_bytes(b"INSIDE")

outside = WS / "outside"
outside.mkdir(parents=True)
victim = outside / "page-original-p1.png"
victim.write_bytes(b"OUTSIDE - must survive")


class _Catalog:
    def upsert(self, *a, **k):
        return None

    def register_preview_with_origin(self, *a, **k):
        return None


publisher = RenderPreviewPublisher(derived_root, _Catalog())
print("derived_root       =", derived_root)
print("target             = pages/page-original-p1.png")

injected: list[str] = []
DIAG: list[str] = []
orig_open = w.unlink_by_handle


def hooked_unlink(root, segments):  # type: ignore[no-untyped-def]
    if not injected and segments and segments[-1] == "page-original-p1.png":
        injected.append(str(segments))
        pages = Path(root) / "pages"
        shutil.rmtree(pages)
        proc = subprocess.run(["cmd", "/c", "mklink", "/J", str(pages), str(outside)],
                              capture_output=True, text=True)
        if proc.returncode != 0 or not pages.is_dir():
            raise SystemExit("INJECTION FAILED (junction): %s" % (proc.stdout or proc.stderr))
        if not (pages / "page-original-p1.png").is_file():
            raise SystemExit("INJECTION FAILED: junction does not expose the outside file")
    return orig_open(root, segments)


# The old implementation deleted by path, so hooking only unlink_by_handle would
# never fire against it and the probe could not be shown to discriminate.  Both are
# wrapped: whichever route the code takes, the injection gets its window.
orig_path_unlink = Path.unlink


def hooked_path_unlink(self, *a, **k):  # type: ignore[no-untyped-def]
    global DIAG
    DIAG.append('path.unlink called with %s' % self)
    if not injected and self.name == 'page-original-p1.png':
        try:
            rel = self.relative_to(derived_root)
        except ValueError:
            rel = None
        if rel is not None:
            hooked_unlink(derived_root, [p for p in rel.parts if p])
    return orig_path_unlink(self, *a, **k)


Path.unlink = hooked_path_unlink  # type: ignore[assignment]
w.unlink_by_handle = hooked_unlink  # type: ignore[assignment]
# The publisher imported the name directly, so patch it there too.
import infrastructure.resource_channel.render_preview as rp  # noqa: E402

rp.unlink_by_handle = hooked_unlink  # type: ignore[assignment]
try:
    outcome = "NO_EXCEPTION"
    try:
        # A missing source makes the publish fail, which is what triggers cleanup.
        publisher.publish_original(WS / "missing-source.png", "page-original-p1", ".png")
    except Exception as error:  # noqa: BLE001 - the failure is what we want
        outcome = type(error).__name__
finally:
    w.unlink_by_handle = orig_open  # type: ignore[assignment]
    rp.unlink_by_handle = orig_open  # type: ignore[assignment]
    Path.unlink = orig_path_unlink  # type: ignore[assignment]

survived = victim.is_file()
for line in DIAG:
    print("  diag:", line)
print("injection_fired    =", bool(injected))
print("publish outcome    =", outcome, "(failure is expected: it triggers cleanup)")
print("outside_survived   =", survived)
if not injected:
    print("RESULT             = INCONCLUSIVE (cleanup chain never ran)")
else:
    print("RESULT             =", "SAFE" if survived else "VULNERABLE")
