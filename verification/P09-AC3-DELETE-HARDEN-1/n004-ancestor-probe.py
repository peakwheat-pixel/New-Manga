import os, shutil, subprocess, sys, tempfile
sys.path.insert(0, r"G:\CODEX\New Manga\src")
from pathlib import Path
import infrastructure.filesystem.win_unlink as w

WORKSPACE_TMP = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\n004-tmp")
WORKSPACE_TMP.mkdir(parents=True, exist_ok=True)
base = Path(tempfile.mkdtemp(dir=str(WORKSPACE_TMP))).resolve()
# 结构：base/trusted/derived/pages/page-original.png
trusted = base / "trusted"; derived = trusted / "derived"
(derived / "pages").mkdir(parents=True)
(derived / "pages" / "page-original.png").write_bytes(b"inside")
# 外部受害目录
outside = base / "outside"; (outside / "derived" / "pages").mkdir(parents=True)
(outside / "derived" / "pages" / "page-original.png").write_bytes(b"OUTSIDE - must survive")

orig_open_anchor = w._open_anchor
fired = []
def hooked(root):
    """Replace `trusted` with a junction to `outside` BEFORE the anchor walk."""
    if not fired:
        fired.append(root)
        shutil.rmtree(trusted)
        proc = subprocess.run(["cmd","/c","mklink","/J",str(trusted),str(outside)],
                              capture_output=True, text=True)
        # P2 (Codex R4): prove the injection actually happened.  Setting the flag
        # before mklink meant a failed link still looked like a defended attack -
        # the same "never ran reported as stopped" defect this suite exists to catch.
        if proc.returncode != 0 or not trusted.is_dir():
            raise SystemExit("INJECTION FAILED: junction not created: %s"
                             % (proc.stdout.strip() or proc.stderr.strip()))
        if not (trusted / "derived" / "pages" / "page-original.png").is_file():
            raise SystemExit("INJECTION FAILED: junction does not expose the outside file")
    return orig_open_anchor(root)

w._open_anchor = hooked
try:
    returned = w.unlink_by_handle(derived, ["pages", "page-original.png"])
finally:
    w._open_anchor = orig_open_anchor

survived = (outside / "derived" / "pages" / "page-original.png").is_file()
print("  injection_fired  =", bool(fired))
print("  unlink_returned  =", returned)
print("  outside_survived =", survived)
print("  RESULT           =", "SAFE" if survived else "VULNERABLE")
