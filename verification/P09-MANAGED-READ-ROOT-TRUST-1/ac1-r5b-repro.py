"""P09-MANAGED-READ-ROOT-TRUST-1 / AC1：R5b 的读取路径复现（base vs 当前 worktree）。

复现内容（R5b P2 #3 原文）：
  「在 ``_checked_managed_path()`` 调用前，把 configured root 的祖先换成指向外部目录的
   junction。该方法**接受了外部路径**，随后**读取出 `outside bytes`**。」

本探针不改 checkout、不写仓库：先用 ``git archive <base_commit> src`` 把 **base 源码**
解到 ``G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/``（R-004：仓外
temp 目录，不用系统 `%TEMP%`），再分别在 base 与当前 worktree 的代码上运行同一个 driver：

  1. 以 ``live``（junction → ``real``）作为数据目录的**祖先**装配生产 Core；
  2. 写入合法的 managed 文件并做一次**合法读取**（证明探针不是一律失败）；
  3. ``os.rmdir(live)`` 去掉 junction，再 ``CreateJunction(payload, live)`` 把它重定向到
     外部镜像树（``payload/data/managed/...``，文件内容是 ``OUTSIDE`` 字节）；
  4. 调用被测 ``_checked_managed_path()``，若接受则读出字节。

判定：base 必须 VULNERABLE（读到 OUTSIDE），当前 worktree 必须 SAFE（typed 拒绝，
outside 字节未被读出）。任一不符 → exit 1。打印 ``injection_fired`` 与
``outside_bytes_served`` 分开，注入未触发绝不读作 SAFE。

运行：``C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py``
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
from pathlib import Path

BASE_COMMIT = "b8a1e519703f13af73b320dded117004b4bb189a"
REPO = Path(__file__).resolve().parents[2]
#: R-004: repository-adjacent scratch root, never the system %TEMP%.
SCRATCH_ROOT = Path("G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1")
DRIVER = r'''
from __future__ import annotations
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

SRC = os.environ["P09_SRC"]
sys.path.insert(0, SRC)

import _winapi  # noqa: E402

from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402

report = {"injection_fired": False, "legal_read_ok": False, "accepted": None,
          "outside_bytes_served": None, "error": None}
tmp = Path(tempfile.mkdtemp(prefix="ac1-driver-", dir=os.environ["P09_SCRATCH"]))
live = tmp / "live"
real = tmp / "real"
payload = tmp / "payload"
try:
    real.mkdir()
    _winapi.CreateJunction(str(real), str(live))
    core = assemble_production_core(live / "data")
    server = CoreServiceServer(core)
    managed = Path(core.storage.root)
    ref = "probe.png"
    inside = b"INSIDE - legal managed bytes"
    (managed / ref).write_bytes(inside)

    # --- legal read BEFORE any swap (AC2 control / probe discrimination) ---
    legal = server._checked_managed_path(str(managed / ref)).read_bytes()
    report["legal_read_ok"] = legal == inside

    # --- the R5b injection: repoint the configured root's ANCESTOR ---
    (payload / "data" / "managed").mkdir(parents=True)
    (payload / "data" / "managed" / ref).write_bytes(b"OUTSIDE - must not be read")
    os.rmdir(str(live))                      # removes the junction itself only
    _winapi.CreateJunction(str(payload), str(live))
    report["injection_fired"] = (managed / ref).resolve().parent == (payload / "data" / "managed").resolve()

    try:
        checked = server._checked_managed_path(str(managed / ref))
        report["accepted"] = True
        data = checked.read_bytes()
        report["outside_bytes_served"] = b"OUTSIDE" in data
    except Exception as error:  # noqa: BLE001
        report["accepted"] = False
        report["outside_bytes_served"] = False
        report["error"] = type(error).__name__
    core.conn.close()
finally:
    # Remove the junction/reparse point itself first: rmtree must never recurse
    # through it.  os.rmdir on a directory junction deletes only the link.
    try:
        if (tmp / "live").is_dir():
            os.rmdir(str(tmp / "live"))
    except OSError:
        pass
    shutil.rmtree(tmp, ignore_errors=True)

print("P09_AC1_RESULT " + json.dumps(report, sort_keys=True))
'''


def extract_base_src(destination: Path) -> Path:
    """git archive the base commit's src/ into destination (no checkout)."""
    archive = subprocess.run(
        ["git", "-C", str(REPO), "archive", "--format=tar", BASE_COMMIT, "src"],
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(destination)
    return destination / "src"


def run_variant(label: str, src: Path) -> dict:
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"ac1-{label}-", dir=str(SCRATCH_ROOT)))
    driver = scratch / "driver.py"
    driver.write_text(DRIVER, encoding="utf-8")
    env = dict(os.environ)
    env["P09_SRC"] = str(src)
    env["P09_SCRATCH"] = str(SCRATCH_ROOT)
    env["PYTHONPATH"] = str(src)
    env.pop("PYTHONSTARTUP", None)
    try:
        completed = subprocess.run(
            [sys.executable, str(driver)],
            cwd=str(scratch),
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    payload = None
    for line in completed.stdout.splitlines():
        if line.startswith("P09_AC1_RESULT "):
            payload = json.loads(line[len("P09_AC1_RESULT "):])
    if payload is None:
        raise SystemExit(
            f"{label}: driver produced no result\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    payload["exit"] = completed.returncode
    return payload


def verdict(row: dict) -> str:
    if not row["injection_fired"]:
        return "INCONCLUSIVE (injection never fired)"
    if not row["legal_read_ok"]:
        return "INCONCLUSIVE (legal read control failed)"
    if row["accepted"] and row["outside_bytes_served"]:
        return "VULNERABLE"
    if not row["accepted"] and not row["outside_bytes_served"]:
        return "SAFE"
    return "UNEXPECTED"


def main() -> int:
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="ac1-base-", dir=str(SCRATCH_ROOT)))
    try:
        base_src = extract_base_src(work)
        rows = []
        for label, src in (("base", base_src), ("current", REPO / "src")):
            row = run_variant(label, src)
            row["label"] = label
            row["verdict"] = verdict(row)
            rows.append(row)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print("P09-MANAGED-READ-ROOT-TRUST-1 / AC1 — R5b read-path reproduction")
    print(f"base_commit = {BASE_COMMIT}")
    print(f"repo        = {REPO}")
    print(f"scratch_root= {SCRATCH_ROOT}")
    for row in rows:
        print(
            f"  [{row['label']:<7}] injection_fired={row['injection_fired']!s:<5}"
            f" legal_read_ok={row['legal_read_ok']!s:<5}"
            f" accepted={row['accepted']!s:<5}"
            f" outside_bytes_served={row['outside_bytes_served']!s:<5}"
            f" error={row['error']} -> {row['verdict']}"
        )
    expected = {"base": "VULNERABLE", "current": "SAFE"}
    ok = all(row["verdict"] == expected[row["label"]] for row in rows)
    print("RESULT =", "PASS" if ok else "FAIL")
    if not ok:
        print("  expected base=VULNERABLE (R5b reproduction) and current=SAFE (fix effective)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
