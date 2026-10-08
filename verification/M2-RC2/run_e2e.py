"""M2-RC2 end-to-end matrix runner (Task deliverable, RC2-AC1/AC2).

Exercises the REAL sidecar launch path and the hardened command surface:

  0. environment record (Python/Cargo/Node versions, WebView2 presence);
     a missing tool FAILS the gate (R2-06)
  1. synthetic lab preparation (asset/typical/boundary/oversize, scope roots)
  2. catalog seeding through the REAL loader entry point
     (``python -m infrastructure.resource_channel.catalog_loader``) into the
     Core/SQLite catalog store -- the launcher-side write path
  3. sidecar import isolation (headless subprocess loads the sidecar entry,
     captured module set is gated against the F-05 whitelist)
  4. PROBE phase: the built desktop runtime runs the full WebView matrix
     (RC1 resource-channel scenarios E-01..E-09 + RC2 hardened-surface
     scenarios D-01..D-03) and exits through probe_exit; the gate asserts
     the EXPECTED scenario SET (R2-05), and copies the discriminating
     artefacts (probe results JSON, sidecar module dumps) into raw/
  5. INTERACTIVE phase: the same runtime without M2RC1_PROBE_OUT. The gate
     (`interactive-production-surface`) verifies externally observable facts
     only -- the announced production allowlist, process liveness, absence
     of probe results; the in-page IP/IA matrix is NOT machine-verified
     (R2-03). A reader thread keeps draining stderr throughout.
  6. gate: every recorded scenario must be PASS (FAIL/MISSING/NOT_RUN are
     gate failures, the RC1 R-03 rule)

Run (from the repository root):
  python verification/M2-RC2/run_e2e.py --output-dir PATH [--exe PATH] [--skip-build]

Artifacts land in --output-dir and a fresh runner-owned %TEMP%/m2rc2-lab-* directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
RAW = Path(__file__).resolve().parent / "raw"
LAB = Path(os.environ.get("TEMP", ".")) / "m2rc2-lab"
BOUNDARY_BYTES = 256 * 1024 * 1024

sys.path.insert(0, str(REPO_ROOT / "tests" / "m2_resource_channel"))
from conftest import write_noise_png  # noqa: E402

#: F-05 isolation whitelist: the sidecar entry may load exactly these
#: project modules (mirrors tests/m2_resource_channel/test_sidecar_isolation.py).
SIDECAR_ALLOWED_PROJECT_MODULES = {
    "application",
    "application.resource_channel",
    "application.resource_channel.dto",
    "application.resource_channel.service",
    "infrastructure",
    "infrastructure.resource_channel",
    "infrastructure.resource_channel.catalog_store",
    "infrastructure.resource_channel.handle_resolver",
    "infrastructure.resource_channel.host_bridge",
    "infrastructure.resource_channel.scope",
}

# Note: document.title is NOT a reliable report channel here — Tauri's
# window.title() does not follow the page title on this stack, so the
# interactive phase is judged on observable behavior (self-close), not on the
# stderr title mirror.
def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(section: str) -> None:
    print(f"\n=== {section} ===")


def prepare_lab() -> dict:
    derived = LAB / "scope" / "derived"
    managed = LAB / "scope" / "managed"
    derived.mkdir(parents=True, exist_ok=True)
    managed.mkdir(parents=True, exist_ok=True)

    payload = write_noise_png(derived / "asset.png", 128, 128, seed=5101)
    typical = write_noise_png(derived / "typical.png", 1600, 2400, seed=5202)

    boundary = derived / "boundary.bin"
    with open(boundary, "wb") as handle:
        handle.truncate(BOUNDARY_BYTES)
    oversize = derived / "oversize.bin"
    with open(oversize, "wb") as handle:
        handle.truncate(BOUNDARY_BYTES + 1)

    manifest = {
        "lab": str(LAB),
        "fixtures": {
            "asset": {"sha256": sha256_hex(payload), "bytes": len(payload)},
            "typical": {"sha256": sha256_hex(typical), "bytes": len(typical)},
            "boundary": {
                "sha256": hashlib.sha256(b"\x00" * BOUNDARY_BYTES).hexdigest(),
                "bytes": BOUNDARY_BYTES,
            },
        },
    }
    (LAB / "fixtures.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"lab ready: {LAB}")
    return manifest


def seed_catalog() -> tuple[int, str]:
    """Seed the Core/SQLite catalog authority through the real loader CLI.

    M2-DERIVED-GC-2 (design §7): this runner's lab catalog is a brand-new
    fixture database, so the trusted first-bind flag runs against the
    already-prepared lab derived root (prepare_lab) BEFORE any row is
    written; without the flag the unbound catalog would be refused."""

    catalog_db = LAB / "catalog.sqlite"
    catalog_db.unlink(missing_ok=True)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "infrastructure.resource_channel.catalog_loader",
            "--db",
            str(catalog_db),
            "--initialize-preview-namespace",
            str(LAB / "scope" / "derived"),
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
        cwd=SRC_ROOT,
        timeout=120,
    )
    # R2-07: a trailing newline discipline -- the whole record is stripped
    # and closed with exactly ONE newline (an empty stderr inside the f-string
    # would otherwise leave a blank line at EOF, which `git diff --check`
    # flags and the review correctly called out).
    (RAW / "e2e-catalog-loader.log").write_text(
        (
            "$ python -m infrastructure.resource_channel.catalog_loader "
            f"--db {catalog_db} --set ... (5 rows)\n"
            f"exit={completed.returncode}\n"
            f"{completed.stdout}\n"
            f"{completed.stderr}"
        ).rstrip() + "\n",
        encoding="utf-8",
    )
    return completed.returncode, str(catalog_db)


def check_import_isolation() -> tuple[bool, str]:
    """Headless sidecar-entry import gate (F-05), recorded to raw/."""

    snippet = (
        "import sys, json; "
        "import infrastructure.resource_channel.host_bridge; "
        "print(json.dumps(sorted(m for m in sys.modules if m.startswith(('infrastructure', 'application', 'domain')))))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", snippet],
        capture_output=True,
        text=True,
        cwd=SRC_ROOT,
        timeout=120,
    )
    (RAW / "e2e-sidecar-import-isolation.log").write_text(
        (
            "$ python -c <import infrastructure.resource_channel.host_bridge; dump modules>\n"
            f"exit={completed.returncode}\n"
            f"{completed.stdout}\n"
            f"{completed.stderr}"
        ).rstrip() + "\n",
        encoding="utf-8",
    )
    if completed.returncode != 0:
        return False, f"sidecar import failed: {completed.stderr[-400:]}"
    modules = set(json.loads(completed.stdout.strip().splitlines()[-1]))
    forbidden = modules - SIDECAR_ALLOWED_PROJECT_MODULES
    if forbidden:
        return False, f"sidecar loaded unrelated project modules: {sorted(forbidden)}"
    missing = SIDECAR_ALLOWED_PROJECT_MODULES - modules
    if missing:
        print(f"  note (not a violation): expected modules absent from dump: {sorted(missing)}")
    return True, f"{len(modules)} project modules, all whitelisted"


def build_runtime(skip_build: bool) -> tuple[Path | None, int]:
    exe = REPO_ROOT / "apps" / "desktop" / "src-tauri" / "target" / "release" / "m2rc1-desktop.exe"
    if skip_build and exe.exists():
        return exe, 0
    completed = subprocess.run(
        ["cargo", "build", "--release", "--manifest-path",
         str(REPO_ROOT / "apps" / "desktop" / "src-tauri" / "Cargo.toml"), "--locked"],
        capture_output=True,
        text=True,
        timeout=900,
    )
    (RAW / "e2e-cargo-build.log").write_text(
        f"$ cargo build --release --manifest-path apps/desktop/src-tauri/Cargo.toml --locked\n"
        f"exit={completed.returncode}\n{completed.stdout}\n{completed.stderr[-4000:]}",
        encoding="utf-8",
    )
    return (exe if completed.returncode == 0 else None), completed.returncode


def runtime_env(out_path: Path, log_path: Path, catalog_db: str, probe: bool) -> dict:
    env = {
        **os.environ,
        "M2RC1_PYTHON": sys.executable,
        "M2RC1_SRC_ROOT": str(SRC_ROOT),
        "M2RC1_DERIVED_ROOT": str(LAB / "scope" / "derived"),
        "M2RC1_MANAGED_ROOT": str(LAB / "scope" / "managed"),
        "M2RC1_FIXTURES": str(LAB / "fixtures.json"),
        "M2RC2_CATALOG_DB": catalog_db,
        #: M2-IPC1 integration ruling (DSH r2 P2-2): the production phase now
        #: spawns `bootstrap.core_service`, which must not fall back to the
        #: real %LOCALAPPDATA% data root — pin it to the lab root.
        "NEWMANGA_DATA_ROOT": str(LAB / "data-root"),
        "M2RC2_MODULE_DUMP": str(LAB / ("sidecar-modules-probe.json" if probe else "sidecar-modules-interactive.json")),
        "WEBVIEW2_USER_DATA_FOLDER": str(LAB / "webview2-udd"),
    }
    if probe:
        env["M2RC1_PROBE_OUT"] = str(out_path)
        env["M2RC1_PROBE_LOG"] = str(log_path)
    else:
        env.pop("M2RC1_PROBE_OUT", None)
        env.pop("M2RC1_PROBE_LOG", None)
    return env


def run_probe_phase(exe: Path, catalog_db: str) -> tuple[int, dict | None]:
    out_path = LAB / "probe-results.json"
    log_path = LAB / "probe-runtime.log"
    for path in (out_path, log_path):
        path.unlink(missing_ok=True)
    shutil.rmtree(LAB / "webview2-udd", ignore_errors=True)

    start = time.time()
    proc = subprocess.Popen(
        [str(exe)], env=runtime_env(out_path, log_path, catalog_db, probe=True),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    output = b""
    try:
        output, _ = proc.communicate(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            output, _ = proc.communicate(timeout=15)
        except (subprocess.TimeoutExpired, ValueError):
            pass
        print("TIMEOUT: probe did not exit within 300 s (partial output below)")
    elapsed = time.time() - start
    if output:
        log_path.write_bytes(output)
        tail = output.decode("utf-8", errors="replace").splitlines()
        for line in tail[-20:]:
            print("  [runtime]", line)
    print(f"probe phase: exit_code={proc.returncode} elapsed={elapsed:.1f}s")

    results = None
    if out_path.exists():
        try:
            results = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("  probe results JSON unreadable")
    # R2-05: keep a copy of the discriminating artefacts in raw/ (the
    # interactive phase deliberately deletes the live probe-results file to
    # prove the write-command denial, so only the copy survives in-tree).
    for source in (
        out_path,
        LAB / "sidecar-modules-probe.json",
        LAB / "sidecar-modules-interactive.json",
    ):
        if source.exists():
            shutil.copy2(source, RAW / f"e2e-{source.name}")
    return proc.returncode, results


ALLOWLIST_RE = re.compile(r"\[m2rc2-allowlist\] (probe|production):(.*)")
#: M2-IPC1 integration ruling (2026-09-28, Codex proxy): the production
#: surface intentionally grows from 3 to 5 commands (core_ping,
#: library_list_books); this runner's expectations are maintained by the
#: M2-IPC1 integration, not by the Owner branch.
#: M2-SETTINGS-IPC-CHANNEL integration (2026-10-02, Codex proxy): 5 -> 7
#: (settings_get / settings_update_section, M2-C1 rev 1.3 §5.3); this
#: runner's expectations continue to be maintained by the integrating
#: slice, not by the Owner branch.
#: M2-REGION-RETYPE-CORE (2026-10-04, Owner ZCode): 7 -> 9
#: (set_region_type / list_regions, M2-C1 rev 1.4 §5.4) -- bypass sync done
#: by the Owner branch this time (the M2-SETTINGS-IPC-CHANNEL r1 R1 lesson:
#: the expectations must move in the same commit as the surface).
#: RC4 / page resolve / page navigation widen production to 15 commands;
#: keep exact ordered equality with the frozen main.rs production surface.
PRODUCTION_EXPECTED = [
    "issue_resource_url",
    "revoke_ref",
    "revoke_resource_refs",
    "core_ping",
    "library_list_books",
    "settings_get",
    "settings_update_section",
    "set_region_type",
    "list_regions",
    "list_region_revisions",
    "restore_region_revision",
    "rerender_page",
    "resolve_page_resource",
    "list_chapters",
    "list_chapter_pages",
]
#: M2-IPC1 ruling (DSH r2 P2-1 option B): test modes keep the frozen RC2
#: surface — the production-only IPC1 commands are absent from the probe
#: announcement, so it stays 7 and is pinned explicitly.
PROBE_EXPECTED = [
    "issue_resource_url",
    "revoke_ref",
    "revoke_resource_refs",
    "probe_config",
    "probe_write_results",
    "probe_exit",
    "probe_issue_url",
]

#: R2-05: the exact set of scenario ids the probe phase must report. The
#: gate asserts set equality -- an empty or partial results file is a gate
#: failure, not a pass.
EXPECTED_PROBE_IDS = [
    "E-00-probe-mode-detected",
    "E-01-issue-fetch-digest",
    "E-02-img-render",
    "E-03-unknown-id",
    "E-04-revoke-after-cached-fetch",
    "E-05-expired-ttl",
    "E-06-remount-fresh-references",
    "E-07-per-reference-first-byte-p95",
    "E-08-boundary-256mib",
    "E-09-over-limit-typed",
    "D-01-register-catalog-denied",
    "D-02-ttl-override-inert",
    "D-03-probe-issue-allowed-in-probe-mode",
]


def run_interactive_phase(exe: Path, catalog_db: str) -> tuple[bool, str]:
    """Production-surface facts, observed from the OUTSIDE.

    R2-03 disclosure: this phase does NOT machine-verify the in-page IP/IA
    matrix (that matrix cannot leave the page by design, and a white-screen
    page would pass this gate). The gate -- therefore named
    `interactive-production-surface`, not a deny-matrix check -- rests on
    externally observable facts only:

    - the host's stderr allowlist announcement (emitted at startup from the
      `command_allowlist` CONSTANT ARRAY -- one of THREE hand-maintained
      views of the command surface, see main.rs; R2-04) must be exactly the
      15 production commands in this mode;
    - the process must stay alive (an early death = probe_exit leak);
    - no probe results file may appear (a write = probe_write_results leak).

    A reader thread keeps draining the process output throughout the watch
    so any crash/panic text still lands in the log.
    """

    MIN_ALIVE_SECONDS = 10.0
    log_path = LAB / "interactive-runtime.log"
    shutil.rmtree(LAB / "webview2-udd", ignore_errors=True)
    # the deny matrix must never produce probe results in this mode
    out_path = LAB / "probe-results.json"
    out_path.unlink(missing_ok=True)

    start = time.time()
    proc = subprocess.Popen(
        [str(exe)], env=runtime_env(log_path, log_path, catalog_db, probe=False),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    tail: list[str] = []
    announcement: tuple[str, list[str]] | None = None
    assert proc.stdout is not None

    def _drain() -> None:
        for raw_line in proc.stdout:  # type: ignore[union-attr]
            tail.append(raw_line.decode("utf-8", errors="replace").rstrip())

    reader = threading.Thread(target=_drain, daemon=True)
    reader.start()
    deadline = time.time() + 60
    while time.time() < deadline and announcement is None:
        for text in tail:
            match = ALLOWLIST_RE.search(text)
            if match:
                announcement = (match.group(1), [c for c in match.group(2).split(",") if c])
                break
        if announcement is None:
            time.sleep(0.2)
    if announcement is None:
        proc.kill()
        proc.wait(timeout=30)
        reader.join(timeout=10)
        log_path.write_text("\n".join(tail), encoding="utf-8")
        return False, "host never announced its command allowlist (startup failed?)"
    # allow the page to boot and run its on-screen matrix while we watch for
    # an early death (probe_exit leak); the reader thread keeps the log alive
    while time.time() - start < MIN_ALIVE_SECONDS:
        if proc.poll() is not None:
            reader.join(timeout=10)
            log_path.write_text("\n".join(tail), encoding="utf-8")
            return False, (
                f"interactive runtime died after {time.time() - start:.1f}s: "
                "an exit command leaked onto the production surface"
            )
        time.sleep(0.5)
    early_death = proc.poll() is not None
    if not early_death:
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
    reader.join(timeout=10)
    elapsed = time.time() - start
    log_path.write_text(
        "\n".join(tail) + f"\n[runner] elapsed={elapsed:.1f}s alive_through_watch={not early_death}\n",
        encoding="utf-8",
    )

    wrote_probe_results = out_path.exists()
    mode, commands = announcement
    if mode != "production":
        return False, f"host announced mode {mode!r}, expected 'production'"
    if commands != PRODUCTION_EXPECTED:
        return False, (
            f"production allowlist mismatch: announced {commands}, "
            f"expected {PRODUCTION_EXPECTED}"
        )
    if early_death:
        return False, "process died during the liveness watch (probe_exit leak)"
    if wrote_probe_results:
        return False, "probe results file appeared in interactive mode (probe_write_results leak)"
    return True, (
        f"production allowlist exactly {PRODUCTION_EXPECTED}; process stayed alive "
        f"through the {MIN_ALIVE_SECONDS:.0f}s watch; no probe results written; "
        "the in-page IP/IA matrix itself is NOT machine-verified (R2-03)"
    )


def check_announcement(log_path: Path, expected_mode: str) -> tuple[bool, str]:
    """Verify the host's stderr allowlist announcement against the mode's
    expected command set (see ALLOWLIST_RE / *_EXPECTED)."""

    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False, f"{log_path.name} missing"
    match = ALLOWLIST_RE.search(text)
    if match is None:
        return False, f"no allowlist announcement in {log_path.name}"
    mode, commands = match.group(1), [c for c in match.group(2).split(",") if c]
    expected = PROBE_EXPECTED if expected_mode == "probe" else PRODUCTION_EXPECTED
    if mode != expected_mode:
        return False, f"announced mode {mode!r}, expected {expected_mode!r}"
    if commands != expected:
        return False, f"allowlist mismatch: announced {commands}, expected {expected}"
    return True, f"{mode} allowlist exactly {expected}"


def check_sidecar_dump(dump_path: Path, phase: str) -> tuple[bool, str]:
    if not dump_path.exists():
        return False, f"{phase}: sidecar module dump missing ({dump_path.name})"
    payload = json.loads(dump_path.read_text(encoding="utf-8"))
    modules = set(payload.get("modules", []))
    project = {m for m in modules if m.split(".")[0] in ("infrastructure", "application", "domain")}
    forbidden = project - SIDECAR_ALLOWED_PROJECT_MODULES
    if forbidden:
        return False, f"{phase}: sidecar loaded unrelated modules: {sorted(forbidden)}"
    return True, f"{phase}: {len(project)} project modules, all whitelisted"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", default=None, help="path to a prebuilt m2rc1-desktop.exe")
    # Each execution owns a fresh lab; --output-dir protects historical evidence.
    parser.add_argument("--skip-build", action="store_true", help="use the existing release build only")
    parser.add_argument("--output-dir", type=Path, required=True, help="isolated evidence directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    global RAW, LAB
    parser = build_parser()
    args = parser.parse_args(argv)
    RAW = args.output_dir.resolve()
    LAB = Path(tempfile.mkdtemp(prefix="m2rc2-lab-"))
    RAW.mkdir(parents=True, exist_ok=True)

    gate: dict[str, str] = {}

    log("0. environment")
    tools = {}
    missing = []
    for name, argv in (("python", [sys.executable, "--version"]), ("cargo", ["cargo", "--version"]),
                       ("rustc", ["rustc", "--version"]), ("node", ["node", "--version"]),
                       ("npm", ["npm", "--version"])):
        # R2-06: resolve through shutil.which so bare names like `npm`
        # resolve to npm.cmd on Windows; a tool that cannot be found or run
        # is recorded as UNAVAILABLE and FAILS the gate instead of being
        # silently PASSed.
        resolved = shutil.which(argv[0]) or shutil.which(argv[0] + ".cmd")
        if resolved is None:
            tools[name] = "UNAVAILABLE: not on PATH"
            missing.append(name)
            continue
        try:
            tools[name] = subprocess.run(
                [resolved] + argv[1:], capture_output=True, text=True, timeout=60
            ).stdout.strip()
        except (OSError, subprocess.TimeoutExpired) as error:
            tools[name] = f"UNAVAILABLE: {error}"
            missing.append(name)
    print(json.dumps(tools, indent=2))
    (RAW / "e2e-environment.json").write_text(json.dumps(tools, indent=2), encoding="utf-8")
    gate["environment"] = "FAIL" if missing else "PASS"
    if missing:
        print(f"environment gate FAIL: missing tools: {missing}")

    log("1. synthetic lab")
    manifest = prepare_lab()
    gate["lab"] = "PASS"

    log("2. catalog seeding (real loader entry point)")
    code, catalog_db = seed_catalog()
    gate["catalog-seeding"] = "PASS" if code == 0 else "FAIL"
    print(f"catalog loader exit={code} db={catalog_db}")
    if code != 0:
        print("cannot continue without a catalog authority")
        return 1

    log("3. sidecar import isolation (headless, F-05)")
    ok, detail = check_import_isolation()
    gate["sidecar-import-isolation"] = "PASS" if ok else "FAIL"
    print(f"{'PASS' if ok else 'FAIL'}: {detail}")

    log("4. desktop runtime build")
    exe = Path(args.exe) if args.exe else None
    if exe is None:
        exe, code = build_runtime(args.skip_build)
        print(f"cargo build exit={code}")
        if exe is None or not exe.exists():
            gate["runtime-build"] = "FAIL"
            return 1
    gate["runtime-build"] = "PASS"
    if not exe.exists():
        print(f"runtime exe missing: {exe}")
        gate["runtime-build"] = "FAIL"
        return 1
    print(f"exe: {exe}")

    log("5. PROBE phase (E2E matrix through the real sidecar)")
    exit_code, results = run_probe_phase(exe, catalog_db)
    reported: dict[str, str] = {}
    if results is not None:
        for record in results["results"]:
            reported[str(record.get("id", "?"))] = record.get("status", "MISSING")
            print(f"{record.get('id', '?'):42s} {record.get('status', 'MISSING')}")
    statuses: dict[str, int] = {}
    for status in reported.values():
        statuses[status] = statuses.get(status, 0) + 1
    print("summary:", statuses)
    # R2-05: assert the EXPECTED scenario SET, not just the status
    # distribution -- a missing, empty or partial results file cannot pass.
    expected_set = set(EXPECTED_PROBE_IDS)
    reported_set = set(reported)
    missing_ids = sorted(expected_set - reported_set)
    unexpected_ids = sorted(reported_set - expected_set)
    bad_ids = sorted(id_ for id_, status in reported.items() if status != "PASS")
    if missing_ids:
        print(f"missing scenario ids: {missing_ids}")
    if unexpected_ids:
        print(f"unexpected scenario ids: {unexpected_ids}")
    if bad_ids:
        print(f"non-PASS scenarios: {bad_ids}")
    gate["probe-phase"] = (
        "PASS"
        if (
            results is not None
            and exit_code == 0
            and not missing_ids
            and not unexpected_ids
            and not bad_ids
        )
        else "FAIL"
    )

    ok, detail = check_announcement(LAB / "probe-runtime.log", "probe")
    gate["probe-allowlist-announcement"] = "PASS" if ok else "FAIL"
    print(f"{'PASS' if ok else 'FAIL'}: {detail}")

    ok, detail = check_sidecar_dump(LAB / "sidecar-modules-probe.json", "probe")
    gate["sidecar-module-dump-probe"] = "PASS" if ok else "FAIL"
    print(f"{'PASS' if ok else 'FAIL'}: {detail}")

    log("6. INTERACTIVE phase (production-surface facts; the in-page IP/IA")
    log("   matrix is NOT machine-verified here — R2-03, see gate name)")
    ok, detail = run_interactive_phase(exe, catalog_db)
    gate["interactive-production-surface"] = "PASS" if ok else "FAIL"
    print(f"{'PASS' if ok else 'FAIL'}: {detail}")

    ok, detail = check_sidecar_dump(LAB / "sidecar-modules-interactive.json", "interactive")
    gate["sidecar-module-dump-interactive"] = "PASS" if ok else "FAIL"
    print(f"{'PASS' if ok else 'FAIL'}: {detail}")

    log("7. gate")
    failed = [name for name, status in gate.items() if status != "PASS"]
    for name, status in gate.items():
        print(f"{name:34s} {status}")
    (RAW / "e2e-gate.json").write_text(
        json.dumps(
            {
                "gate": gate,
                "failed": failed,
                "probe_statuses": statuses,
                "probe_missing_ids": missing_ids,
                "probe_unexpected_ids": unexpected_ids,
                "probe_non_pass_ids": bad_ids,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if failed:
        print(f"GATE FAIL: {failed}")
        return 1
    print("GATE PASS: all phases green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
