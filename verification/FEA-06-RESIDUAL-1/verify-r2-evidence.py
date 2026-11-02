"""只读检查 R2-005 当前快照、57 条 skip 与历史字节保全。仓库根目录运行。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = "ff9da7dcf8eb70333a8165d7c83106156a3107af"
HEAD = "8b39b1398"
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "verification/FEA-06-RESIDUAL-1"


def blob(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


manifest = json.loads((EVIDENCE / "r2-history-manifest.json").read_text(encoding="utf-8"))
for entry in manifest["files"]:
    data = (ROOT / entry["path"]).read_bytes()
    original = data[:entry["length"]] if entry["mode"] == "prefix" else data
    assert len(original) == entry["length"]
    assert hashlib.sha256(original).hexdigest() == entry["sha256"], entry["path"]
print(f"RAW_BYTES_ASSERT={len(manifest['files'])}/{len(manifest['files'])}；旧文件/前缀逐字节保留")


log = (EVIDENCE / "impl-r2-rework-verification.log").read_text(encoding="utf-8-sig")
assert f"TESTED_HEAD={HEAD}" in log
assert "TOTAL=1233 passed / 0 failed / 57 skipped" in log
for marker in ("BUILD_EXIT=0", "TEST_EXIT=0", "CHECK_EXIT=0", "PINS_EXIT=0"):
    assert marker in log, marker
actual_skips = set(re.findall(r"\s(NewManga\.[\w.]+) \[SKIP\]", log))
reason_rows = re.findall(r"^(NewManga\.[\w.]+) \| SKIPPED \| reason: needs sidecar fixture[^\n]+", log, re.M)
assert len(actual_skips) == len(reason_rows) == 57
assert actual_skips == set(reason_rows)
print("SKIP_ASSERT=57/57；每条实际 SKIP 均有完整名称与逐条原因")

for name in ("ac-coverage.md", "item-status.md", "component-state-matrix.md", "batch-b-verification.log"):
    data = (EVIDENCE / name).read_bytes()
    old = blob(f"verification/FEA-06-RESIDUAL-1/{name}")
    # These historical files used CRLF in the working tree and LF in Git. Preserve all old
    # content and line endings in place; normalize only for this repository-blob comparison.
    assert data.replace(b"\r\n", b"\n").startswith(old.replace(b"\r\n", b"\n")), name
    current = data.decode("utf-8-sig").split("## 当前快照（R2-005", 1)[1]
    assert HEAD in current and "1233/0/57" in current and "1213/0/57" in current, name
    assert "NOT_RUN" in current and "D-8" in current, name
    print(f"CURRENT_AND_HISTORY_ASSERT={name}: PASS")

frozen = [
    "verification/FEA-06-RESIDUAL-1/batch-a-verification.log",
    "verification/FEA-06-RESIDUAL-1/pre-review-verification.log",
    "verification/FEA-06-RESIDUAL-1/impl-r1-animation-verification.log",
    "doc/reviews/FEA-06-RESIDUAL-1-impl-r1.md",
    "doc/reviews/FEA-06-RESIDUAL-1-impl-r2.md",
]
for path in frozen:
    assert (ROOT / path).read_bytes().replace(b"\r\n", b"\n") == blob(path).replace(b"\r\n", b"\n"), path
for path in sorted((ROOT / "verification/FEA-06/screens").glob("*.png")):
    relative = path.relative_to(ROOT).as_posix()
    data = path.read_bytes()
    assert data == blob(relative), relative
    print(f"PNG_ASSERT={path.name}: {hashlib.sha256(data).hexdigest()}")
print("R2_005_ASSERT=PASS；EXIT=0")
