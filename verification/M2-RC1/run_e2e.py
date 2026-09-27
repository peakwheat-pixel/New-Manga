"""M2-RC1 end-to-end matrix runner.

Prepares the synthetic lab (asset.png + sparse 256 MiB boundary.bin + sparse
oversize.bin), spawns the built Tauri desktop runtime with the ?probe=1
evidence matrix, and reports the outcome.

Run (from the repository root, after `cargo build --release`):
  python verification/M2-RC1/run_e2e.py --exe <path-to-m2rc1-desktop.exe>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAB = Path(os.environ.get("TEMP", ".")) / "m2rc1-lab"
BOUNDARY_BYTES = 256 * 1024 * 1024


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare_lab() -> dict:
    derived = LAB / "scope" / "derived"
    managed = LAB / "scope" / "managed"
    derived.mkdir(parents=True, exist_ok=True)
    managed.mkdir(parents=True, exist_ok=True)

    # small asset: deterministic PNG-ish bytes (the channel is content-agnostic;
    # PNG magic kept so the <img> render scenario is meaningful)
    sys.path.insert(0, str(REPO_ROOT / "tests" / "m2_resource_channel"))
    from conftest import write_noise_png  # noqa: E402

    payload = write_noise_png(derived / "asset.png", 128, 128, seed=5101)
    # F-04: an 11,525,983 B "typical page" fixture for the T3 per-reference
    # first-byte P95 line (E-07)
    typical = write_noise_png(derived / "typical.png", 1600, 2400, seed=5202)

    # boundary (exactly 256 MiB) and oversize (+1) as sparse files
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
            "boundary": {"sha256": hashlib.sha256(b"\x00" * BOUNDARY_BYTES).hexdigest(), "bytes": BOUNDARY_BYTES},
        },
    }
    (LAB / "fixtures.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"lab ready: {LAB}")
    print(f"asset sha256: {manifest['fixtures']['asset']['sha256']}")
    return manifest


def run_probe(exe: Path, manifest: dict) -> tuple[int, Path | None, float]:
    out_path = LAB / "probe-results.json"
    log_path = LAB / "probe-runtime.log"
    udd = LAB / "webview2-udd"
    shutil.rmtree(udd, ignore_errors=True)
    for path in (out_path, log_path):
        if path.exists():
            path.unlink()

    env = {
        **os.environ,
        "M2RC1_PYTHON": sys.executable,
        "M2RC1_SRC_ROOT": str(REPO_ROOT / "src"),
        "M2RC1_DERIVED_ROOT": str(LAB / "scope" / "derived"),
        "M2RC1_MANAGED_ROOT": str(LAB / "scope" / "managed"),
        "M2RC1_FIXTURES": str(LAB / "fixtures.json"),
        "M2RC1_PROBE_OUT": str(out_path),
        "M2RC1_PROBE_LOG": str(log_path),
        "WEBVIEW2_USER_DATA_FOLDER": str(udd),
    }
    start = time.time()
    proc = subprocess.Popen(
        [str(exe)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = b""
    try:
        output, _ = proc.communicate(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
        # still collect whatever stderr/stdout the window produced
        try:
            output, _ = proc.communicate(timeout=15)
        except (subprocess.TimeoutExpired, ValueError):
            pass
        print("TIMEOUT: probe did not exit within 300 s (partial output below)")
    elapsed = time.time() - start
    if output:
        log_path.write_bytes(output)
        tail = output.decode("utf-8", errors="replace").splitlines()
        for line in tail[-25:]:
            print("  [runtime]", line)
    print(f"exit_code={proc.returncode} elapsed={elapsed:.1f}s")
    return proc.returncode, out_path if out_path.exists() else None, elapsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exe",
        default=str(
            REPO_ROOT / "apps" / "desktop" / "src-tauri" / "target" / "release" / "m2rc1-desktop.exe"
        ),
    )
    args = parser.parse_args()

    exe = Path(args.exe)
    if not exe.exists():
        print(f"runtime exe missing: {exe}")
        print("build first: cargo build --release --manifest-path apps/desktop/src-tauri/Cargo.toml")
        return 2

    manifest = prepare_lab()
    exit_code, results_path, _ = run_probe(exe, manifest)
    if results_path is None:
        print("no results produced")
        return 1

    results = json.loads(results_path.read_text(encoding="utf-8"))
    statuses: dict[str, int] = {}
    for record in results["results"]:
        status = record.get("status", "MISSING")
        statuses[status] = statuses.get(status, 0) + 1
        print(f"{record.get('id', '?'):40s} {status}")
    print("summary:", statuses)
    print(f"results: {results_path}")
    # R-03: NOT_RUN is a gate failure, not a pass — the runner must be able
    # to tell "scenario did not run" apart from "scenario passed"
    failed = (
        statuses.get("FAIL", 0)
        + statuses.get("MISSING", 0)
        + statuses.get("NOT_RUN", 0)
    )
    return 0 if exit_code == 0 and failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
