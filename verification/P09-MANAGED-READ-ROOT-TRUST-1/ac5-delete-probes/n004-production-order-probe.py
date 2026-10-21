import os, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1\src")
ws = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1\verification\P09-MANAGED-READ-ROOT-TRUST-1\_scratch\n004-prod")
if ws.exists(): shutil.rmtree(ws, ignore_errors=True)
ws.mkdir(parents=True)
outside = ws / "outside"; (outside / "derived" / "pages").mkdir(parents=True)
(outside / "derived" / "pages" / "page-original.png").write_bytes(b"OUTSIDE - must survive")
trusted = ws / "trusted"
proc = subprocess.run(["cmd","/c","mklink","/J",str(trusted),str(outside)], capture_output=True, text=True)
assert proc.returncode == 0, proc.stdout + proc.stderr
assert trusted.is_dir(), "junction missing"
# 生产顺序：先把 junction 放好，再取 derived_root
derived_root = trusted / "derived"
from infrastructure.sqlite.library import unlink_preview_without_following
print("  derived_root       =", derived_root)
print("  resolve() would be =", derived_root.resolve())
returned = unlink_preview_without_following("pages/page-original.png", derived_root)
survived = (outside / "derived" / "pages" / "page-original.png").is_file()
print("  unlink_returned    =", returned)
print("  outside_survived   =", survived)
print("  RESULT             =", "SAFE" if survived else "VULNERABLE")
