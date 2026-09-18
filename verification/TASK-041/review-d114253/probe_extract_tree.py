import os, sys, tempfile
from pathlib import Path
TESTDIR = r"G:\CODEX\New Manga.worktrees\TASK-041-zcode\tests\import_formats"
sys.path.insert(0, TESTDIR)
sys.path.insert(0, r"G:\CODEX\New Manga.worktrees\TASK-041-zcode\src")
from test_mobi_import import picture_mobi, _make_jpeg, text_only_mobi
import mobi as mobibind
data = picture_mobi([_make_jpeg(8,6,(255,0,0)), _make_jpeg(9,7,(0,255,0))])
src = os.path.join(tempfile.mkdtemp(prefix="nm041probe"), "probe.mobi")
Path(src).write_bytes(data)
tempdir, out = mobibind.extract(src)
print("tempdir:", tempdir)
print("returned:", os.path.relpath(out, tempdir))
for root, dirs, files in os.walk(tempdir):
    rel = os.path.relpath(root, tempdir)
    print("DIR", rel, "->", sorted(files))
