"""FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A) discrimination driver.

Applies deliberate break points to the SHIPPED implementation, runs ONE target
test per break and requires it to turn RED (exit != 0).  Every file is restored
byte-for-byte afterwards (sha256 checked) and each target is re-run to prove the
restored tree is GREEN again.

Breaks:
* B1 — apply face: the C-17 apply refresh call is disabled          (AC-LS4-3)
* B2 — import page unit: the page-unit refresh is not passed        (AC-LS4-2)
* B3 — import skip: the D-2 whole-source-skip refresh is disabled   (AC-LS4-3/D-2)
* B4 — a second inline ``UPDATE source_locations`` is restored      (AC-LS4-1)
* B5 — the same-registry generation monotonic guard is removed      (AC-LS4-5)
* B6 — the physical identity guard is removed                       (AC-LS4-4)
* B7 — the ``is_current = 1`` guard is removed                      (AC-LS4-4)

Usage (repo root):
  C:/Python314/python.exe verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/discrimination.py
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PYTHON = "C:/Python314/python.exe"
EVIDENCE = (
    REPO / "verification" / "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1"
    / "logs" / "discrimination.log"
)

SERVICE = "src/application/sources/service.py"
RUNTIME = "src/application/importing/referenced/runtime.py"
LIBRARY = "src/infrastructure/sqlite/library.py"

RELINK = "tests/fea11/test_source_relink.py"
IMPORT = "tests/fea09/test_import_source.py"
SYNC = "tests/fea09/test_source_sync_operations.py"

APPLY_REFRESH_BLOCK = (
    "        if auth_refresh is not None:\n"
    "            # The ONE implementation lives in the repository; this call runs\n"
    "            # inside the caller's BEGIN IMMEDIATE unit (no extra transaction).\n"
    "            self._repository.refresh_source_location_auth(**auth_refresh)\n"
)

BREAKS = [
    {
        "id": "B1",
        "what": "apply 面刷新调用被禁用（relink/resync 同身份不再刷新）",
        "file": SERVICE,
        "old": APPLY_REFRESH_BLOCK,
        "new": (
            "        if False:  # DISCRIMINATION BREAK B1: apply-path refresh disabled\n"
            "            self._repository.refresh_source_location_auth(**auth_refresh)\n"
        ),
        "target": SYNC + "::test_resync_same_identity_refreshes_the_location_auth",
    },
    {
        "id": "B2",
        "what": "import 页单元不再携带刷新（重导入新项目不刷新）",
        "file": RUNTIME,
        "old": "                        auth_refresh=auth_refresh if first_page else None,\n",
        "new": "                        auth_refresh=None,  # DISCRIMINATION BREAK B2\n",
        "target": IMPORT
        + "::test_reimport_into_another_project_refreshes_location_auth_in_place",
    },
    {
        "id": "B3",
        "what": "整源 skip 的 D-2 条件刷新被删除",
        "file": RUNTIME,
        "old": (
            "            # grant refreshes nothing; no page/version/binding write happens).\n"
            "            self._refresh_skipped_source_auth(source)\n"
        ),
        "new": (
            "            # grant refreshes nothing; no page/version/binding write happens).\n"
            "            # DISCRIMINATION BREAK B3: D-2 skip refresh removed.\n"
        ),
        "target": IMPORT + "::test_whole_source_skip_refreshes_location_auth_once",
    },
    {
        "id": "B4",
        "what": "恢复第二份内联 UPDATE source_locations（单点实现被破坏）",
        "file": SERVICE,
        "old": APPLY_REFRESH_BLOCK,
        "new": APPLY_REFRESH_BLOCK + (
            "        _legacy_location = store.get_source_location_current("
            "body[\"source_id\"])\n"
            "        if _legacy_location is not None and grant is not None:\n"
            "            store._conn.execute(\n"
            "                \"UPDATE source_locations SET registry_id = ?,\"\n"
            "                \" authorization_generation = ?, last_verified_at = ?\"\n"
            "                \" WHERE location_id = ?\",\n"
            "                (grant.registry_id, int(grant.generation), now,\n"
            "                 _legacy_location[\"location_id\"]),\n"
            "            )  # DISCRIMINATION BREAK B4: second inline SQL copy\n"
        ),
        "target": RELINK + "::test_refresh_source_location_auth_is_the_single_implementation",
    },
    {
        "id": "B5",
        "what": "同 registry generation 单调守卫被移除（允许代次回退）",
        "file": LIBRARY,
        "old": '            " AND (registry_id <> ? OR authorization_generation <= ?)"\n',
        "new": (
            '            " AND (registry_id <> ? OR ? >= 0)"'
            "  # DISCRIMINATION BREAK B5: monotonic guard removed\n"
        ),
        "target": RELINK
        + "::test_refresh_source_location_auth_fail_closed_guards",
    },
    {
        "id": "B6",
        "what": "物理身份三键守卫被移除（identity 不符也刷新）",
        "file": LIBRARY,
        "old": '            " AND volume_serial = ? AND file_id = ? AND is_current = 1"\n',
        "new": (
            '            " AND ? IS NOT NULL AND ? IS NOT NULL AND is_current = 1"'
            "  # DISCRIMINATION BREAK B6: identity guard removed\n"
        ),
        "target": RELINK
        + "::test_refresh_source_location_auth_fail_closed_guards",
    },
    {
        "id": "B7",
        "what": "is_current 守卫被移除（已 supersede 的旧行也可被刷新）",
        "file": LIBRARY,
        "old": '            " AND volume_serial = ? AND file_id = ? AND is_current = 1"\n',
        "new": (
            '            " AND volume_serial = ? AND file_id = ?"'
            "  # DISCRIMINATION BREAK B7: is_current guard removed\n"
        ),
        "target": RELINK
        + "::test_refresh_source_location_auth_fail_closed_guards",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_pytest(target: str) -> tuple[int, str]:
    completed = subprocess.run(
        [PYTHON, "-m", "pytest", target, "-q", "-p", "no:warnings", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip().splitlines()[-3:]


def main() -> int:
    lines: list[str] = []
    stamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def log(message: str) -> None:
        print(message)
        lines.append(message)

    log(f"[{stamp}] FEA-11-L-S4 discrimination start (repo={REPO})")
    results = []
    ok = True
    for case in BREAKS:
        path = REPO / case["file"]
        original = path.read_bytes()
        original_sha = hashlib.sha256(original).hexdigest()
        text = original.decode("utf-8")
        normalized = text.replace("\r\n", "\n")
        if normalized.count(case["old"]) != 1:
            log(
                f"case={case['id']} SETUP_FAIL "
                f"old-occurrences={normalized.count(case['old'])}"
            )
            ok = False
            break
        eol = "\r\n" if text.count("\r\n") * 2 >= text.count("\n") else "\n"
        mutated = normalized.replace(case["old"], case["new"]).replace("\n", eol)
        path.write_bytes(mutated.encode("utf-8"))
        try:
            red_code, red_tail = _run_pytest(case["target"])
        finally:
            path.write_bytes(original)
        restored_sha = _sha256(path)
        restored = restored_sha == original_sha
        if red_code == 0:
            status = "NOT_RED"
            ok = False
        elif not restored:
            status = "RESTORE_FAIL"
            ok = False
        else:
            green_code, _green_tail = _run_pytest(case["target"])
            status = "RED_AS_EXPECTED" if green_code == 0 else "RESTORE_RED"
            if green_code != 0:
                ok = False
        results.append((case["id"], status))
        log(
            f"case={case['id']} what={case['what']} file={case['file']} "
            f"target={case['target']} break_exit={red_code} "
            f"restore_sha256={'MATCH' if restored else 'MISMATCH'} status={status}"
        )
        for tail in red_tail:
            log(f"  break-out: {tail}")

    # Final tree cleanliness for the mutated sources: byte-identical to HEAD.
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", SERVICE, RUNTIME, LIBRARY],
        cwd=str(REPO), capture_output=True, text=True,
    ).stdout.strip()
    log(f"restored_tree_git_status={dirty or 'CLEAN'}")
    if dirty:
        ok = False
    verdict = "PASS" if ok else "FAIL"
    log(
        f"result={verdict} breaks={len(results)} "
        f"statuses={','.join(status for _id, status in results)}"
    )
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
