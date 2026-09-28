"""M2-AC1 end-to-end acceptance gate (doc/tasks/M2-AC1.md, AC6).

Runs the REAL desktop loop twice over two independent samples:

    launch -> Mock/Local pipeline -> SQLite save -> process exit
    relaunch (same data root, new PIDs) -> restore -> Reader 2 pages
    -> PNG export -> digest comparison

Every scenario is judged from OUTSIDE the app: the results files written by
the test-mode-only command surface, the process exit codes, the recorded
PIDs, the stderr command-surface announcement and the exported PNG bytes.
The gate fails closed: any missing scenario, FAIL or NOT_RUN verdict fails
the gate; an unusable environment is BLOCKED, never PASS.

Usage (from the repository root):
    python verification/M2-AC1/run_e2e.py [--skip-build] [--exe <path>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
FRONTEND_ROOT = REPO_ROOT / "apps" / "desktop" / "frontend"
TAURI_ROOT = REPO_ROOT / "apps" / "desktop" / "src-tauri"
DEFAULT_EXE = TAURI_ROOT / "target" / "release" / "m2rc1-desktop.exe"

RUN_TIMEOUT_SECONDS = 300
SAMPLES = ("sample-a", "sample-b")
LAUNCHES = ("run1", "run2")

ANNOUNCE_AC1_PREFIX = "[m2ac1-allowlist] ac1:"
EXPECTED_AC1_ALLOWLIST = (
    "issue_resource_url,revoke_ref,revoke_resource_refs,ac1_request,ac1_write_results,ac1_exit"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Gate:
    """Fail-closed evidence collector."""

    def __init__(self) -> None:
        self.scenarios: list[dict] = []

    def record(self, scenario_id: str, status: str, observed) -> None:
        self.scenarios.append(
            {"id": scenario_id, "status": status, "observed": observed}
        )
        print(f"  [{status}] {scenario_id}: {json.dumps(observed, sort_keys=True)[:200]}")

    def pass_or(self, condition: bool, scenario_id: str, observed) -> None:
        self.record(scenario_id, "PASS" if condition else "FAIL", observed)

    @property
    def verdict(self) -> str:
        statuses = {entry["status"] for entry in self.scenarios}
        if not self.scenarios or "FAIL" in statuses:
            return "FAIL"
        if "NOT_RUN" in statuses:
            return "FAIL"
        return "PASS"


def resolve_tool(name: str) -> str | None:
    """Resolve an executable through PATH (Windows npm/cmd shims included)."""
    return shutil.which(name)


def record_environment(gate: Gate) -> bool:
    print("[0] environment")
    tools = ("python", "cargo", "rustc", "node", "npm")
    usable = True
    for name in tools:
        resolved = resolve_tool(name)
        gate.pass_or(resolved is not None, f"EVN-{name}-resolved", {"path": resolved})
        if resolved is None:
            usable = False
            continue
        version_flag = "--version"
        try:
            completed = subprocess.run(
                [resolved, version_flag],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            version = (completed.stdout or completed.stderr).strip().splitlines()
            gate.pass_or(completed.returncode == 0, f"EVN-{name}", {"version": version[:1]})
            usable = usable and completed.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as error:
            gate.record(f"EVN-{name}", "NOT_RUN", {"error": str(error)})
            usable = False
    return usable


def build_frontend(gate: Gate) -> bool:
    print("[2a] frontend build (npm run build)")
    npm = resolve_tool("npm")
    if npm is None:
        gate.record("BLD-frontend", "NOT_RUN", {"error": "npm not on PATH"})
        return False
    completed = subprocess.run(
        [npm, "run", "build"],
        cwd=FRONTEND_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    (Path(log_dir) / "build-frontend.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    gate.pass_or(completed.returncode == 0, "BLD-frontend", {"exit": completed.returncode})
    return completed.returncode == 0


def build_host(gate: Gate, exe: Path) -> bool:
    print("[2b] host build (cargo build --release --locked)")
    cargo = resolve_tool("cargo")
    if cargo is None:
        gate.record("BLD-cargo", "NOT_RUN", {"error": "cargo not on PATH"})
        return False
    completed = subprocess.run(
        [cargo, "build", "--release", "--locked"],
        cwd=TAURI_ROOT,
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    (Path(log_dir) / "build-cargo.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    gate.pass_or(completed.returncode == 0, "BLD-cargo", {"exit": completed.returncode})
    gate.pass_or(exe.is_file(), "BLD-exe-present", {"exe": str(exe)})
    return completed.returncode == 0 and exe.is_file()


def launch_env(lab_root: Path, sample: str, results_name: str, venv_python: str) -> dict:
    root = lab_root / sample / "root"
    return {
        **os.environ,
        "M2AC1_TEST_MODE": "1",
        "NEWMANGA_DATA_ROOT": str(root),
        "M2RC2_CATALOG_DB": str(root / "catalog.sqlite"),
        "M2RC1_PYTHON": venv_python,
        "M2RC1_SRC_ROOT": str(SRC_ROOT),
        "M2RC1_DERIVED_ROOT": str(root / "scope" / "derived"),
        "M2RC1_MANAGED_ROOT": str(root / "managed"),
        "M2AC1_RESULTS_OUT": str(lab_root / sample / results_name),
    }


def run_launch(exe: Path, env: dict, log_path: Path) -> tuple[int, str | None, str, int]:
    """One real desktop launch; returns (exit_code, announced_allowlist, stderr_tail, desktop_pid)."""
    announced = None
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [str(exe)],
            cwd=str(REPO_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        desktop_pid = process.pid
        deadline = time.monotonic() + RUN_TIMEOUT_SECONDS
        for line in process.stdout:  # type: ignore[union-attr]
            log.write(line)
            log.flush()
            if announced is None and line.startswith(ANNOUNCE_AC1_PREFIX):
                announced = line.removeprefix(ANNOUNCE_AC1_PREFIX).strip()
            if time.monotonic() > deadline:
                process.kill()
                log.write(f"\n[TIMEOUT after {RUN_TIMEOUT_SECONDS}s]\n")
                break
        code = process.wait(timeout=60)
    return code, announced, log_path.read_text(encoding="utf-8")[-2000:], desktop_pid


def read_results(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def run_sample(gate: Gate, exe: Path, lab_root: Path, sample: str, venv_python: str) -> dict | None:
    """Both launches for one sample; returns the sample evidence or None."""
    print(f"[3] sample {sample}")
    sample_root = lab_root / sample
    (sample_root / "root").mkdir(parents=True, exist_ok=True)
    evidence: dict = {"sample": sample, "launches": {}}

    for launch in LAUNCHES:
        results_path = sample_root / f"{launch}.json"
        if results_path.exists():
            results_path.unlink()
        env = launch_env(lab_root, sample, f"{launch}.json", venv_python)
        code, announced, tail, desktop_pid = run_launch(
            exe, env, sample_root / f"{launch}.stderr.log"
        )
        results = read_results(results_path)
        gate.pass_or(
            announced == EXPECTED_AC1_ALLOWLIST,
            f"{sample}-{launch}-allowlist-announcement",
            {"announced": announced},
        )
        gate.pass_or(code == 0, f"{sample}-{launch}-exit-code", {"exit": code, "tail": tail[-400:]})
        gate.pass_or(
            results is not None and results.get("phase") == launch,
            f"{sample}-{launch}-results-phase",
            {"phase": (results or {}).get("phase")},
        )
        if results is None:
            return None
        results["desktop_pid"] = desktop_pid
        evidence["launches"][launch] = {"exit": code, "results": results}

    run1 = evidence["launches"]["run1"]["results"]
    run2 = evidence["launches"]["run2"]["results"]

    # AC3: a real restart — both the desktop process and the Core sidecar
    # came back as NEW OS processes
    gate.pass_or(
        run1.get("desktop_pid") != run2.get("desktop_pid"),
        f"{sample}-restart-desktop-pid-differs",
        {"run1": run1.get("desktop_pid"), "run2": run2.get("desktop_pid")},
    )
    gate.pass_or(
        run1.get("core_pid") != run2.get("core_pid"),
        f"{sample}-restart-core-pid-differs",
        {"run1": run1.get("core_pid"), "run2": run2.get("core_pid")},
    )

    # AC1/AC2: the pipeline run saved a complete, re-readable result
    saved = run1.get("saved") or {}
    gate.pass_or(
        saved.get("run_status") == "completed" and len(saved.get("pages") or []) == 2,
        f"{sample}-saved-summary",
        {"run_status": saved.get("run_status"), "pages": len(saved.get("pages") or [])},
    )
    gate.pass_or(
        saved.get("providers")
        == {"ocr": "m2ac1-mock-ocr", "translate": "m2ac1-mock-translate"},
        f"{sample}-mock-local-providers",
        {"providers": saved.get("providers")},
    )

    # AC4: the restored Reader displayed the same bytes that were saved
    saved_by_index = {page["index"]: page["sha256"] for page in saved.get("pages") or []}
    viewed = run2.get("viewed") or []
    gate.pass_or(
        len(viewed) == 2
        and all(
            entry.get("sha256") == saved_by_index.get(entry.get("index"))
            and entry.get("naturalWidth", 0) > 0
            for entry in viewed
        ),
        f"{sample}-reader-pages-match-saved",
        {
            "viewed": [
                {"index": entry.get("index"), "sha": (entry.get("sha256") or "")[:12]}
                for entry in viewed
            ]
        },
    )

    # AC5: the exported PNG is non-empty, decodable and is the Reader's page
    exported = run2.get("exported") or {}
    export_file = sample_root / "root" / "exports" / str(exported.get("output_path") or "")
    gate.pass_or(
        bool(exported.get("sha256"))
        and export_file.is_file()
        and export_file.stat().st_size > 0
        and sha256_file(export_file) == exported.get("sha256")
        and exported.get("sha256") == saved_by_index.get(exported.get("page_index")),
        f"{sample}-export-png",
        {
            "size": export_file.stat().st_size if export_file.is_file() else 0,
            "sha": (exported.get("sha256") or "")[:12],
        },
    )
    return evidence


def main() -> int:
    global log_dir
    parser = argparse.ArgumentParser(description="M2-AC1 end-to-end acceptance gate")
    parser.add_argument("--skip-build", action="store_true", help="reuse the existing builds")
    parser.add_argument("--exe", default=str(DEFAULT_EXE), help="desktop exe to launch")
    args = parser.parse_args()
    exe = Path(args.exe)

    lab_root = Path(tempfile.mkdtemp(prefix="m2ac1-e2e-"))
    log_dir = lab_root / "raw"
    log_dir.mkdir(parents=True, exist_ok=True)
    print(f"lab: {lab_root}")

    gate = Gate()
    env_usable = record_environment(gate)
    if not env_usable:
        gate.record("E2E-gate", "BLOCKED", {"reason": "toolchain incomplete; environment unusable"})
        write_gate(gate, lab_root)
        return 2
    if not args.skip_build:
        if not build_frontend(gate) or not build_host(gate, exe):
            gate.record("E2E-gate", "BLOCKED", {"reason": "build failed"})
            write_gate(gate, lab_root)
            return 2
    if not exe.is_file():
        gate.record("E2E-gate", "BLOCKED", {"reason": f"missing exe: {exe}"})
        write_gate(gate, lab_root)
        return 2

    print("[1] lab ready (two isolated data roots, no user data)")

    venv_python = sys.executable
    samples = {}
    for sample in SAMPLES:
        evidence = run_sample(gate, exe, lab_root, sample, venv_python)
        if evidence is not None:
            samples[sample] = evidence

    # AC1/AC6: two independent deterministic runs must agree
    if len(samples) == len(SAMPLES):
        summary_a = samples["sample-a"]["launches"]["run1"]["results"].get("saved")
        summary_b = samples["sample-b"]["launches"]["run1"]["results"].get("saved")
        gate.pass_or(
            summary_a == summary_b,
            "independent-samples-identical-summaries",
            {
                "sample-a": [page["sha256"][:12] for page in (summary_a or {}).get("pages", [])],
                "sample-b": [page["sha256"][:12] for page in (summary_b or {}).get("pages", [])],
            },
        )

    verdict = gate.verdict
    gate.record("E2E-gate", verdict if verdict != "FAIL" else "FAIL", {})
    write_gate(gate, lab_root)
    print(f"GATE {verdict}  evidence: {lab_root}")
    return 0 if verdict == "PASS" else 1


def write_gate(gate: Gate, lab_root: Path) -> None:
    payload = {
        "task": "M2-AC1",
        "verdict": gate.verdict,
        "scenarios": gate.scenarios,
        "lab": str(lab_root),
    }
    (lab_root / "raw" / "e2e-gate.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    raise SystemExit(main())
