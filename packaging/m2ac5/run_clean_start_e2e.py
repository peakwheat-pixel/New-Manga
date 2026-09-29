"""M2-AC5 packaged clean-start acceptance runner (AC3/AC4, host simulation).

Drives the NSIS-installed desktop runtime through its three startup modes in
an environment that provably has NO system Python on PATH and NO M2RC1_*
source-tree env:

  0. environment record + PATH purge assertion (``python`` must NOT resolve)
  1. NSIS silent install into a space-free temp dir (``/S /D=...``)
  2. PROBE mode: launcher-side catalog seeding through the packaged
     catalog_loader.exe (the frozen equivalent of the dev runners'
     ``python -m infrastructure.resource_channel.catalog_loader``), then the
     full WebView resource-channel matrix; gate = probe results JSON verdicts
  3. AC1 test mode: the deterministic acceptance loop (pipeline -> SQLite ->
     restart -> restore -> reader -> PNG export); gate = results JSON verdicts
  4. PRODUCTION mode: real window, %APPDATA% userData layout assertions,
     graceful close, sidecar reaping assertion
  5. AC4: install-dir write-diff (hash before/after all runs), user source
     files byte-identical, no surviving sidecar/python processes

Scope note (frozen at release): this is the LOCAL host-simulation route
(python purged from PATH + M2RC1_* cleared); a truly clean Windows machine is
M2 Release Gate scope and stays explicitly NOT_RUN here.

The RUNNER may use the dev venv Python (acceptance tooling); every spawned
instance of the app runs under the purged environment. Usage:

    python packaging/m2ac5/run_clean_start_e2e.py [--installer <path>]

Artifacts land in verification/M2-AC5/raw/ (via stdout redirection) and the
lab temp dir. The gate fails closed: FAIL/MISSING verdicts fail the run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
RAW = Path(__file__).resolve().parent.parent.parent / "verification" / "M2-AC5" / "raw"
DEFAULT_INSTALLER = (
    REPO_ROOT
    / "apps"
    / "desktop"
    / "src-tauri"
    / "target"
    / "release"
    / "bundle"
    / "nsis"
    / "m2rc1-desktop_0.1.0_x64-setup.exe"
)
INSTALLED_EXE_NAME = "m2rc1-desktop.exe"
SIDECAR_EXES = (
    "host_bridge.exe",
    "core_service.exe",
    "acceptance_bridge.exe",
    "catalog_loader.exe",
)
USER_ROOT = Path(os.environ.get("APPDATA", "")) / "com.newmanga.m2rc1.desktop"

ANNOUNCE_PRODUCTION = "[m2rc2-allowlist] production:"
LAUNCH_TIMEOUT = 240

sys.path.insert(0, str(REPO_ROOT / "tests" / "m2_resource_channel"))
from conftest import write_noise_png  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Gate:
    """Fail-closed evidence collector (same shape as the RC2/AC1 runners)."""

    def __init__(self) -> None:
        self.scenarios: list[dict] = []

    def record(self, scenario_id: str, status: str, observed) -> None:
        self.scenarios.append({"id": scenario_id, "status": status, "observed": observed})
        print(f"  [{status}] {scenario_id}: {json.dumps(observed, sort_keys=True)[:220]}")

    def pass_or(self, condition: bool, scenario_id: str, observed) -> None:
        self.record(scenario_id, "PASS" if condition else "FAIL", observed)

    @property
    def verdict(self) -> str:
        statuses = {entry["status"] for entry in self.scenarios}
        if not self.scenarios or "FAIL" in statuses:
            return "FAIL"
        return "PASS"


def log(section: str) -> None:
    print(f"\n=== {section} ===")


# --------------------------------------------------------------------------
# 0. environment: purge Python from PATH, clear the dev env contract
# --------------------------------------------------------------------------

PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")


def purged_environment(lab: Path) -> tuple[dict, list[str]]:
    """Build the clean-start env: python-free PATH + no M2RC1_* contract."""
    removed = []
    kept = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        marker_hit = any(marker.lower() in entry.lower() for marker in PURGE_MARKERS)
        (removed if marker_hit else kept).append(entry)
    cleared_keys = [
        key
        for key in os.environ
        if key.startswith("M2RC1_") or key.startswith("M2RC2_") or key in ("M2AC1_TEST_MODE", "NEWMANGA_DATA_ROOT", "M2RC1_PACKAGED")
    ]
    env = {key: value for key, value in os.environ.items() if key not in cleared_keys}
    env["PATH"] = os.pathsep.join(kept)
    env.setdefault("SYSTEMROOT", os.environ.get("SYSTEMROOT", "C:\\Windows"))
    env.setdefault("TEMP", str(lab / "tmp"))
    env.setdefault("TMP", str(lab / "tmp"))
    (lab / "tmp").mkdir(parents=True, exist_ok=True)
    return env, removed


def assert_no_python_on_path(env: dict) -> tuple[bool, str]:
    """The purge assertion: under the purged PATH, `python` must not resolve."""
    probe = subprocess.run(
        ["where", "python"],
        env=env,
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        timeout=30,
    )
    if probe.returncode == 0:
        return False, f"python still resolves under purged PATH: {probe.stdout.strip()}"
    # also prove the packaged exes themselves are independent of any python:
    # list what IS resolvable for the record
    where_py_exes = subprocess.run(
        ["where", "host_bridge.exe"], env=env, capture_output=True, text=True, timeout=30
    )
    return True, (
        "python not on purged PATH (where exit="
        f"{probe.returncode}); host_bridge.exe resolves: {where_py_exes.returncode == 0}"
    )


# --------------------------------------------------------------------------
# 1. NSIS silent install
# --------------------------------------------------------------------------

def dir_tree_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hashes[str(path.relative_to(root)).lower()] = sha256_file(path)
    return hashes


def silent_install(installer: Path, target: Path, env: dict) -> tuple[bool, str]:
    if target.exists():
        subprocess.run(["taskkill", "/F", "/IM", INSTALLED_EXE_NAME], capture_output=True)
        time.sleep(1)
        import shutil

        shutil.rmtree(target, ignore_errors=True)
    # NSIS /S = silent; /D=<dir> must be the LAST argument and unquoted.
    # The NSIS setup exe is a GUI-subsystem process: wait for the installer
    # process itself, then poll for the payload to be fully on disk.
    proc = subprocess.Popen(
        [str(installer), "/S", f"/D={target}"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        proc.wait(timeout=600)
    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "installer timed out after 600 s"
    exe = target / INSTALLED_EXE_NAME
    deadline = time.time() + 60
    while time.time() < deadline and not exe.is_file():
        time.sleep(1)
    if not exe.is_file():
        return False, f"installed exe missing after wait: {exe}"
    missing = [name for name in SIDECAR_EXES if not (target / "resources" / "core-sidecar" / name).is_file()]
    if missing:
        return False, f"sidecar exes missing after install: {missing}"
    return True, f"installed to {target} with resources/core-sidecar/{', '.join(SIDECAR_EXES)}"


# --------------------------------------------------------------------------
# lab preparation (probe fixtures) — mirrors the RC2 runner lab
# --------------------------------------------------------------------------

def prepare_probe_lab(lab: Path) -> dict:
    derived = lab / "probe" / "scope" / "derived"
    managed = lab / "probe" / "scope" / "managed"
    derived.mkdir(parents=True, exist_ok=True)
    managed.mkdir(parents=True, exist_ok=True)

    payload = write_noise_png(derived / "asset.png", 128, 128, seed=5101)
    typical = write_noise_png(derived / "typical.png", 1600, 2400, seed=5202)
    boundary = derived / "boundary.bin"
    with open(boundary, "wb") as handle:
        handle.truncate(256 * 1024 * 1024)
    oversize = derived / "oversize.bin"
    with open(oversize, "wb") as handle:
        handle.truncate(256 * 1024 * 1024 + 1)

    manifest = {
        "lab": str(lab),
        "fixtures": {
            "asset": {"sha256": sha256_hex(payload), "bytes": len(payload)},
            "typical": {"sha256": sha256_hex(typical), "bytes": len(typical)},
            "boundary": {
                "sha256": hashlib.sha256(b"\x00" * (256 * 1024 * 1024)).hexdigest(),
                "bytes": 256 * 1024 * 1024,
            },
        },
    }
    (lab / "probe" / "fixtures.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # pre-run source-file hashes for the AC4 zero-touch assertion
    (lab / "probe" / "source-hashes-before.json").write_text(
        json.dumps(
            {p.name: sha256_file(p) for p in sorted(derived.iterdir()) if p.is_file()},
            indent=2,
        ),
        encoding="utf-8",
    )
    return manifest


def seed_catalog_packaged(install_dir: Path, catalog_db: Path) -> tuple[bool, str]:
    """Launcher-side seeding through the packaged catalog_loader.exe."""
    loader = install_dir / "resources" / "core-sidecar" / "catalog_loader.exe"
    completed = subprocess.run(
        [
            str(loader),
            "--db",
            str(catalog_db),
            "--set",
            "res-probe=asset.png",
            "--set",
            "res-hot=typical.png",
            "--set",
            "res-boundary=boundary.bin",
            "--set",
            "res-oversize=oversize.bin",
            "--set",
            "res-cataloged=asset.png",
            "--dump",
        ],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        timeout=120,
    )
    if completed.returncode != 0:
        return False, f"catalog_loader exit={completed.returncode}: {completed.stderr[-400:]}"
    return True, "catalog seeded (5 rows) via packaged catalog_loader.exe"


# --------------------------------------------------------------------------
# launch plumbing
# --------------------------------------------------------------------------

def probe_env(env: dict, lab: Path) -> dict:
    out = dict(env)
    out["M2RC1_PACKAGED"] = "1"
    out["M2RC1_DERIVED_ROOT"] = str(lab / "probe" / "scope" / "derived")
    out["M2RC1_MANAGED_ROOT"] = str(lab / "probe" / "scope" / "managed")
    out["M2RC1_FIXTURES"] = str(lab / "probe" / "fixtures.json")
    out["M2RC2_CATALOG_DB"] = str(lab / "probe" / "catalog.sqlite")
    out["M2RC1_PROBE_OUT"] = str(lab / "probe" / "probe-results.json")
    out["M2RC1_PROBE_LOG"] = str(lab / "probe" / "probe-runtime.log")
    out["WEBVIEW2_USER_DATA_FOLDER"] = str(lab / "probe" / "webview2-udd")
    return out


def ac1_env(env: dict, lab: Path) -> dict:
    out = dict(env)
    out["M2RC1_PACKAGED"] = "1"
    out["M2AC1_TEST_MODE"] = "1"
    # launcher-side lab prep (same contract as the dev AC1 runner): explicit
    # M2RC1_* paths are prepared by the runner, NOT by the host
    root = lab / "ac1" / "root"
    (root / "scope" / "derived").mkdir(parents=True, exist_ok=True)
    (root / "managed").mkdir(parents=True, exist_ok=True)
    out["NEWMANGA_DATA_ROOT"] = str(root)
    out["M2RC2_CATALOG_DB"] = str(root / "catalog.sqlite")
    out["M2RC1_DERIVED_ROOT"] = str(root / "scope" / "derived")
    out["M2RC1_MANAGED_ROOT"] = str(root / "managed")
    out["M2AC1_RESULTS_OUT"] = str(lab / "ac1" / "results.json")
    out["WEBVIEW2_USER_DATA_FOLDER"] = str(lab / "ac1" / "webview2-udd")
    return out


def production_env(env: dict, lab: Path) -> dict:
    out = dict(env)
    out["M2RC1_PACKAGED"] = "1"
    out["WEBVIEW2_USER_DATA_FOLDER"] = str(lab / "production" / "webview2-udd")
    return out


def run_app(exe: Path, env: dict, timeout: int) -> tuple[int, str, int]:
    """Run the app to completion, streaming stderr into the captured output."""
    proc = subprocess.Popen(
        [str(exe)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    desktop_pid = proc.pid
    output = b""
    try:
        output, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            output, _ = proc.communicate(timeout=15)
        except (subprocess.TimeoutExpired, ValueError):
            pass
    return proc.returncode, output.decode("utf-8", errors="replace"), desktop_pid


def wait_for_file(path: Path, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.is_file():
            return True
        time.sleep(1)
    return path.is_file()


def list_processes(names: tuple[str, ...]) -> dict[str, int]:
    completed = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        timeout=60,
    )
    counts = {name: 0 for name in names}
    for line in completed.stdout.splitlines():
        for name in names:
            if line.lower().startswith(f'"{name.lower()}"'):
                counts[name] += 1
    return counts


# --------------------------------------------------------------------------
# phases
# --------------------------------------------------------------------------

def run_probe_phase(gate: Gate, exe: Path, env: dict, lab: Path) -> None:
    log("phase 2: PROBE mode (resource channel matrix, packaged sidecar)")
    results_path = lab / "probe" / "probe-results.json"
    results_path.unlink(missing_ok=True)
    code, output = run_app(exe, probe_env(env, lab), LAUNCH_TIMEOUT)[:2]
    (RAW / "cleanstart-probe-stdout.log").write_text(
        f"$ <installed>\\m2rc1-desktop.exe (purged PATH, no M2RC1_SRC_ROOT/PYTHON)\n"
        f"exit={code}\n{output}",
        encoding="utf-8",
    )
    gate.pass_or(
        wait_for_file(results_path, 20),
        "CS-P1-probe-results-written",
        {"path": str(results_path)},
    )
    if not results_path.is_file():
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    scenarios = results.get("results", [])
    ids = [entry.get("id") for entry in scenarios]
    fails = [entry["id"] for entry in scenarios if entry.get("status") != "PASS"]
    gate.pass_or(
        len(scenarios) >= 10 and not fails,
        "CS-P2-probe-scenarios-all-pass",
        {"count": len(scenarios), "failed": fails, "ids": ids},
    )
    # the digest self-check pins a REAL sidecar round trip (E-01 compares the
    # fetched bytes against the fixture manifest sha)
    e01 = next((entry for entry in scenarios if entry.get("id") == "E-01-issue-fetch-digest"), None)
    gate.pass_or(
        bool(e01) and e01.get("status") == "PASS",
        "CS-P3-sidecar-roundtrip-digest",
        {"e01": e01},
    )


def run_ac1_phase(gate: Gate, exe: Path, env: dict, lab: Path) -> None:
    """The frozen M2-AC1 loop: run1 (pipeline -> SQLite save -> exit) then a
    REAL relaunch (run2: restore -> reader -> PNG export -> digest compare).
    Both launches run the packaged exe under the purged environment."""
    log("phase 3: AC1 test mode (acceptance loop, packaged sidecar)")
    ac1_dir = lab / "ac1"
    root = ac1_dir / "root"
    (root / "scope" / "derived").mkdir(parents=True, exist_ok=True)
    (root / "managed").mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    pids: dict[str, tuple[int, int | None]] = {}
    for launch in ("run1", "run2"):
        results_path = ac1_dir / f"{launch}.json"
        results_path.unlink(missing_ok=True)
        launch_env = ac1_env(env, lab)
        launch_env["M2AC1_RESULTS_OUT"] = str(results_path)
        code, output, desktop_pid = run_app(exe, launch_env, LAUNCH_TIMEOUT)
        (RAW / f"cleanstart-ac1-{launch}-stdout.log").write_text(
            f"$ <installed>\\m2rc1-desktop.exe (M2AC1_TEST_MODE=1, launch={launch}, purged PATH)\n"
            f"exit={code}\n{output}",
            encoding="utf-8",
        )
        payload = None
        if results_path.is_file():
            try:
                payload = json.loads(results_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = None
        gate.pass_or(
            code == 0 and bool(payload) and payload.get("phase") == launch,
            f"CS-A1-{launch}-completed",
            {"exit": code, "phase": (payload or {}).get("phase")},
        )
        if payload is None:
            return
        core_pid = payload.get("core_pid")
        results[launch] = payload
        pids[launch] = (desktop_pid, int(core_pid) if core_pid else None)

    # AC3 semantics: a real restart — desktop AND core sidecar are new PIDs
    gate.pass_or(
        pids["run1"][0] != pids["run2"][0] and pids["run1"][1] != pids["run2"][1],
        "CS-A2-restart-new-pids",
        {"run1": pids["run1"], "run2": pids["run2"]},
    )

    run1, run2 = results["run1"], results["run2"]
    saved = run1.get("saved") or {}
    gate.pass_or(
        saved.get("run_status") == "completed" and len(saved.get("pages") or []) == 2
        and saved.get("providers") == {"ocr": "m2ac1-mock-ocr", "translate": "m2ac1-mock-translate"},
        "CS-A3-saved-summary-complete",
        {"run_status": saved.get("run_status"), "pages": len(saved.get("pages") or []),
         "providers": saved.get("providers")},
    )

    saved_by_index = {page["index"]: page["sha256"] for page in saved.get("pages") or []}
    viewed = run2.get("viewed") or []
    gate.pass_or(
        len(viewed) == 2
        and all(
            entry.get("sha256") == saved_by_index.get(entry.get("index"))
            and entry.get("naturalWidth", 0) > 0
            for entry in viewed
        ),
        "CS-A4-restored-reader-matches-saved",
        {"viewed": [{"index": e.get("index"), "sha": (e.get("sha256") or "")[:12]} for e in viewed]},
    )

    exported = run2.get("exported") or {}
    output_name = exported.get("output_path")
    export_file = root / "exports" / output_name if isinstance(output_name, str) else None
    gate.pass_or(
        bool(export_file and export_file.is_file() and export_file.stat().st_size > 0
             and sha256_file(export_file) == exported.get("sha256")
             and exported.get("sha256") == saved_by_index.get(exported.get("page_index"))),
        "CS-A5-export-png-digest-matches",
        {"size": export_file.stat().st_size if export_file and export_file.is_file() else 0,
         "sha": (exported.get("sha256") or "")[:12]},
    )


def run_production_phase(gate: Gate, exe: Path, env: dict, lab: Path) -> None:
    log("phase 4: PRODUCTION mode (real window, %APPDATA% userData)")
    for child in ("catalog", "derived", "managed", "data"):
        target = USER_ROOT / child
        if target.exists():
            import shutil

            shutil.rmtree(target, ignore_errors=True)
    catalog_sqlite = USER_ROOT / "catalog" / "catalog.sqlite"
    if catalog_sqlite.exists():
        catalog_sqlite.unlink()

    proc = subprocess.Popen(
        [str(exe)],
        env=production_env(env, lab),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # hold the real window open for at least 10 s (AC3: the app must START
    # and STAY alive with its sidecars), then close gracefully
    alive_deadline = time.time() + 10
    while time.time() < alive_deadline:
        time.sleep(1)
        if proc.poll() is not None:
            break
    alive = proc.poll() is None
    gate.pass_or(alive, "CS-R1-production-process-alive", {"poll": proc.poll()})
    user_dirs = {
        child: (USER_ROOT / child).is_dir() for child in ("catalog", "derived", "managed", "data")
    }
    gate.pass_or(
        all(user_dirs.values()) and catalog_sqlite.is_file(),
        "CS-R2-userdata-layout-created",
        {"dirs": user_dirs, "catalog.sqlite": catalog_sqlite.is_file(), "root": str(USER_ROOT)},
    )
    # graceful close (WM_CLOSE, no /F): lets the host drop the channels so the
    # sidecars receive `shutdown` and exit — the AC4 reaping precondition
    subprocess.run(["taskkill", "/PID", str(proc.pid)], capture_output=True)
    try:
        output_tail, _ = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        output_tail, _ = proc.communicate(timeout=15)
    text = output_tail.decode("utf-8", errors="replace")
    (RAW / "cleanstart-production-stdout.log").write_text(
        f"$ <installed>\\m2rc1-desktop.exe (production defaults; pid={proc.pid}; graceful close)\n"
        f"exit={proc.returncode}\n{text}",
        encoding="utf-8",
    )
    gate.pass_or(
        ANNOUNCE_PRODUCTION in text,
        "CS-R3-production-surface-announced",
        {"announcement": ANNOUNCE_PRODUCTION, "present": ANNOUNCE_PRODUCTION in text},
    )
    gate.pass_or(
        text.count("CORE_SPAWN_FAILED") == 0 and "Traceback" not in text,
        "CS-R4-no-spawn-failures-in-log",
        {"spawn_failed_mentions": text.count("CORE_SPAWN_FAILED")},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--installer", type=Path, default=DEFAULT_INSTALLER)
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    lab = Path(tempfile.mkdtemp(prefix="m2ac5-cleanstart-"))
    installer = args.installer
    gate = Gate()

    log("phase 0: environment record + PATH purge")
    env, removed = purged_environment(lab)
    purged_ok, purge_detail = assert_no_python_on_path(env)
    gate.pass_or(purged_ok, "CS-E1-python-purged-from-path", {"detail": purge_detail, "removed_entries": removed})
    gate.pass_or(
        installer.is_file(),
        "CS-E2-installer-present",
        {"installer": str(installer)},
    )
    if not installer.is_file() or not purged_ok:
        gate.record("CS-BLOCKED", "FAIL", {"reason": "installer missing or python purge failed"})
        print(f"\nGATE: {gate.verdict}")
        return 1

    install_dir = Path(tempfile.gettempdir()) / "m2ac5-cleanstart" / "install"

    log("phase 1: NSIS silent install")
    ok, detail = silent_install(installer, install_dir, env)
    gate.pass_or(ok, "CS-I1-silent-install", {"detail": detail})
    if not ok:
        print(f"\nGATE: {gate.verdict}")
        return 1
    install_hashes_before = dir_tree_hashes(install_dir)
    print(f"  install dir files: {len(install_hashes_before)}")

    exe = install_dir / INSTALLED_EXE_NAME
    manifest = prepare_probe_lab(lab)
    seed_ok, seed_detail = seed_catalog_packaged(install_dir, lab / "probe" / "catalog.sqlite")
    gate.pass_or(seed_ok, "CS-I2-catalog-seeded-packaged-loader", {"detail": seed_detail})

    run_probe_phase(gate, exe, env, lab)
    run_ac1_phase(gate, exe, env, lab)
    run_production_phase(gate, exe, env, lab)

    log("phase 5: AC4 zero-touch assertions")
    install_hashes_after = dir_tree_hashes(install_dir)
    changed = {
        key for key in set(install_hashes_before) | set(install_hashes_after)
        if install_hashes_before.get(key) != install_hashes_after.get(key)
    }
    gate.pass_or(not changed, "CS-Z1-install-dir-zero-write", {"changed_entries": sorted(changed)[:8]})

    before = json.loads((lab / "probe" / "source-hashes-before.json").read_text(encoding="utf-8"))
    after = {
        p.name: sha256_file(p)
        for p in sorted((lab / "probe" / "scope" / "derived").iterdir())
        if p.is_file()
    }
    gate.pass_or(before == after, "CS-Z2-user-source-files-byte-identical", {"files": len(after)})

    survivors = list_processes(
        ("host_bridge.exe", "core_service.exe", "acceptance_bridge.exe", "catalog_loader.exe", "python.exe")
    )
    # python.exe is a RECORD-ONLY count here: this host machine legitimately
    # runs unrelated python processes (the acceptance runner itself among
    # them); "no system Python" is proven by the CS-E1 purged-PATH assertion
    # plus the frozen exes serving every workflow above. The gate asserts the
    # four packaged sidecar exes are fully reaped.
    gate.pass_or(
        survivors["host_bridge.exe"] == 0
        and survivors["core_service.exe"] == 0
        and survivors["acceptance_bridge.exe"] == 0
        and survivors["catalog_loader.exe"] == 0,
        "CS-Z3-no-surviving-sidecar-processes",
        survivors,
    )

    log("gate")
    results = {
        "gate": "m2ac5-clean-start",
        "installer": str(installer),
        "install_dir": str(install_dir),
        "lab": str(lab),
        "verdict": gate.verdict,
        "scenarios": gate.scenarios,
    }
    (RAW / "cleanstart-gate.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nGATE: {gate.verdict}")
    return 0 if gate.verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
