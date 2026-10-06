"""M2-PROD-SFX-PROBE-1 packaged sfx-detect probe — release-form evidence.

Independent probe (NOT part of the frozen M2-AC5 runner; the GATE 25-scenario
set stays untouched and is re-run separately as the no-regression face).

The frozen command surface (M2-IPC1: core.ping/ListBooks/core.shutdown, later
additively widened through core.detect / settings.* / set_region_type /
list_regions) has NO sfx-specific probe RPC and this Task deliberately does
NOT touch it. The evidence path is the FIFTH frozen entry exe shipped by
M2-PROD-SFX-PROBE-1: ``<install>/resources/core-sidecar/sfx_detect_probe.exe``
(dev form ``python -m bootstrap.sfx_detect_probe``) — one-shot, runs ONE
production ``SfxDetectionProvider.detect`` against the in-bundle v2b weights
INSIDE the frozen process and prints the audit JSON (the catalog_loader
standalone-entry precedent shape; zero IPC command-surface extension).

Scenarios:

  SP-P0  fifth entry installed: ``sfx_detect_probe.exe`` exists in the
         installed bundle (the build-sidecar sanity gate asserts the same
         five names at build time).
  SP-L1  frozen-process synthetic-page probe (structural smoke): the
         INSTALLED probe exe (purged PATH, no NEWMANGA_* env intervention)
         runs the builtin synthetic page -> EXIT=0, the ``SFX_PROBE_JSON``
         line parses, the three-key EP provenance (device/sfx_ep/
         sfx_ep_fallback) is present, and the in-bundle weights sha256
         equals the production pin. The synthetic page is OUTSIDE the
         training distribution — its candidate count is RECORDED, never
         asserted (a zero here is registered, not a silent pass and not a
         failure).
  SP-L2  frozen-process REAL-page probe (the AC2 evidence face): the same
         exe with ``--page`` pointing at the v2b anchor page K07_R123 (the
         M2-SFX-T4-SWITCH anchor, best sfx conf 0.9047) -> EXIT=0 AND
         candidates > 0 AND the three keys present. Expected release form:
         device=dml with NO sfx_ep_fallback; a wrapper-level CPU fallback,
         when observed, is recorded verbatim and per the Task contract is
         registered honestly WITHOUT failing the probe. The page image is
         read from the gitignored task-envs tree — never copied into the
         repository (weights/page-image zero-commit discipline); only the
         path + sha256 are recorded.
  SP-L3  existing command surface zero-change smoke: the INSTALLED
         core_service.exe still serves core.ping -> ready and
         core.shutdown -> stopped over stdio (the full 25-scenario GATE
         re-run is the authoritative no-regression face; this is the
         probe-runner-local cross-check).

Usage (from the repository root):
  python verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py \
      --install-dir <NSIS install dir> \
      [--real-page <png>] [--out <results.json>] [--raw-subdir <name>] \
      [--installer-sha256 <hex>] [--build-head <sha>] [--build-venv-note <note>]

Results JSON defaults to packaged-sfx-detect-probe-results.json next to this
script; raw stdout/stderr logs land in raw/ (--raw-subdir reroutes them to
raw/<name>/ so a re-run never overwrites the original evidence). The gate
fails closed: any FAIL fails the probe; SP-L2 with a missing real page is
recorded as SKIP (NOT_RUN evidence), not a failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path(__file__).resolve().parent / "packaged-sfx-detect-probe-results.json"
RAW_DIR = Path(__file__).resolve().parent / "raw"

PROBE_EXE_REL = Path("resources") / "core-sidecar" / "sfx_detect_probe.exe"
CORE_SERVICE_EXE_REL = Path("resources") / "core-sidecar" / "core_service.exe"
BUNDLE_WEIGHTS_REL = (
    Path("resources") / "core-sidecar" / "models" / "detector" / "yolo11s-seg.onnx"
)

#: The production weights pin (M2-SFX-T4-SWITCH v2b; verbatim from
#: src/infrastructure/providers/detection_sfx.py SFX_WEIGHTS_SHA256).
SFX_WEIGHTS_SHA256 = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)

#: The default real page: the M2-SFX-T4-SWITCH v2b anchor frame (highest-
#: confidence sfx detection of the M2-SFX-DETECT-EVAL sample; gitignored
#: task-envs tree).
DEFAULT_REAL_PAGE = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
)

JSON_MARKER = "SFX_PROBE_JSON: "
PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")


class Gate:
    def __init__(self) -> None:
        self.scenarios: list[dict] = []

    def record(self, scenario_id: str, status: str, observed: dict) -> None:
        self.scenarios.append({"id": scenario_id, "status": status, "observed": observed})
        print(f"  [{status}] {scenario_id}: {json.dumps(observed, sort_keys=True)[:300]}")

    def pass_or(self, condition: bool, scenario_id: str, observed: dict) -> None:
        self.record(scenario_id, "PASS" if condition else "FAIL", observed)

    @property
    def verdict(self) -> str:
        statuses = {entry["status"] for entry in self.scenarios}
        if not self.scenarios or "FAIL" in statuses:
            return "FAIL"
        return "PASS"


def log(section: str) -> None:
    print(f"\n=== {section} ===")


def purged_env() -> tuple[dict[str, str], list[str]]:
    """Runner-equivalent clean-start env: python-free PATH, M2RC1_* cleared,
    ALL NEWMANGA_* cleared (the installed release form must run with zero
    env intervention — the production defaults ARE the evidence)."""
    removed = []
    kept = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        marker_hit = any(m.lower() in entry.lower() for m in PURGE_MARKERS)
        (removed if marker_hit else kept).append(entry)
    cleared_env_names = []
    env: dict[str, str] = {}
    for key, value in os.environ.items():
        if key.startswith(("M2RC1_", "M2RC2_", "M2AC1_TEST_MODE", "NEWMANGA_")):
            cleared_env_names.append(key)
            continue
        if key == "NEWMANGA_DATA_ROOT":
            cleared_env_names.append(key)
            continue
        env[key] = value
    env["PATH"] = os.pathsep.join(kept)
    env.setdefault("SYSTEMROOT", os.environ.get("SYSTEMROOT", "C:\\Windows"))
    return env, cleared_env_names


def parse_probe_json(text: str) -> dict | None:
    lines = [line for line in text.splitlines() if line.startswith(JSON_MARKER)]
    if len(lines) != 1:
        return None
    try:
        return json.loads(lines[0][len(JSON_MARKER):])
    except json.JSONDecodeError:
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_frozen(payload: dict | None) -> bool:
    """DSH r1 P2-3: "inside the frozen process" is a judged face, not just a
    recorded one — the probe JSON's ``python.frozen`` flag must be asserted."""
    return (payload or {}).get("python", {}).get("frozen") is True


def run_frozen_probe(exe: Path, args: list[str], env: dict[str, str], timeout: int) -> tuple[int, str, str, int]:
    started = time.perf_counter()
    proc = subprocess.run(
        [str(exe), *args],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return proc.returncode, proc.stdout, proc.stderr, elapsed_ms


def stdio_ping_shutdown(exe: Path, env: dict[str, str], timeout: int = 240) -> tuple[int, dict, dict, str]:
    """One stdio JSON-lines round trip against the INSTALLED core_service.exe:
    core.ping then core.shutdown (the M2-IPC1 frozen face, unchanged)."""
    def envelope(request_id: str, command: str) -> str:
        # minor=3 matches the frozen PROTOCOL_MINOR (DSH r1 P4-3): this is a
        # smoke of the EXISTING command face, so it speaks the frozen form
        # rather than a minimal envelope.
        return json.dumps(
            {
                "protocol": "new-manga.core",
                "version": {"major": 1, "minor": 3},
                "request_id": request_id,
                "command": command,
                "payload": {},
            }
        )

    proc = subprocess.Popen(
        [str(exe)],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        out, err = proc.communicate(
            (
                envelope("r1", "core.ping") + "\n" + envelope("r2", "core.shutdown") + "\n"
            ).encode("utf-8"),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=15)
    text = out.decode("utf-8", errors="replace")
    err_text = err.decode("utf-8", errors="replace")
    responses: dict[str, dict] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = value.get("request_id")
        if rid:
            responses[rid] = value
    return proc.returncode, responses.get("r1", {}), responses.get("r2", {}), (text + "--- stderr ---\n" + err_text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--real-page", type=Path, default=DEFAULT_REAL_PAGE)
    parser.add_argument("--out", type=Path, default=RESULTS_PATH)
    parser.add_argument(
        "--build-venv-note",
        default="",
        help="free-form note recorded into the results JSON (e.g. the build venv id)",
    )
    # DSH r1 P3-5: caller-supplied provenance for the evidence — record the
    # installer artifact and build HEAD the caller passes in (the runner does
    # not measure or verify them; cross-check against the GATE CS-E2 measured
    # installer sha256).
    parser.add_argument(
        "--installer-sha256",
        default="",
        help="sha256 of the NSIS installer under test (recorded into the results JSON)",
    )
    parser.add_argument(
        "--build-head",
        default="",
        help="repository HEAD the sidecar bundle was built from (recorded into the results JSON)",
    )
    # DSH r1 r1fix re-run support: keep the original raw/ evidence intact.
    parser.add_argument(
        "--raw-subdir",
        default="",
        help="reroute raw logs to raw/<name>/ instead of overwriting raw/",
    )
    args = parser.parse_args()

    install_dir = args.install_dir.resolve()
    probe_exe = install_dir / PROBE_EXE_REL
    core_service_exe = install_dir / CORE_SERVICE_EXE_REL
    bundle_weights = install_dir / BUNDLE_WEIGHTS_REL
    gate = Gate()
    raw_dir = RAW_DIR / args.raw_subdir if args.raw_subdir else RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)
    env, cleared_env_names = purged_env()

    print(f"install dir: {install_dir}")
    print(f"probe exe: {probe_exe} (exists={probe_exe.is_file()})")
    print(f"bundle weights: {bundle_weights} (exists={bundle_weights.is_file()})")
    print(f"real page: {args.real_page} (exists={args.real_page.is_file()})")
    print(f"cleared env names ({len(cleared_env_names)}): {sorted(cleared_env_names)}")

    # -- SP-P0: the fifth frozen entry is installed --------------------------
    log("SP-P0: fifth frozen entry installed (sfx_detect_probe.exe)")
    gate.pass_or(
        probe_exe.is_file() and core_service_exe.is_file() and bundle_weights.is_file(),
        "SP-P0-probe-entry-installed",
        {
            "probe_exe": str(probe_exe),
            "probe_exe_exists": probe_exe.is_file(),
            "core_service_exists": core_service_exe.is_file(),
            "in_bundle_weights_exist": bundle_weights.is_file(),
        },
    )

    # -- SP-L1: frozen-process synthetic-page probe (structural smoke) -------
    log("SP-L1: frozen-process probe on the builtin synthetic page (purged PATH)")
    exit_code, stdout, stderr, wall_ms = run_frozen_probe(
        probe_exe, ["--label", "synthetic"], env, timeout=300
    )
    (raw_dir / "sp-l1-synthetic.log").write_text(
        f"$ <install>\\{PROBE_EXE_REL.as_posix()} --label synthetic (purged PATH, all NEWMANGA_* cleared)\n"
        f"exit={exit_code} wall_ms={wall_ms}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}",
        encoding="utf-8",
    )
    payload = parse_probe_json(stdout)
    result = (payload or {}).get("result") or {}
    weights = (payload or {}).get("weights") or {}
    three_keys_present = (
        result.get("device") is not None
        and result.get("sfx_ep") is not None
        and payload is not None
        and "sfx_ep_fallback" in result
    )
    observed_l1 = {
        "exit": exit_code,
        "json_parsed": payload is not None,
        "frozen_in_process": is_frozen(payload),
        "n_candidates": result.get("n_candidates"),
        "device": result.get("device"),
        "sfx_ep": result.get("sfx_ep"),
        "sfx_ep_fallback": result.get("sfx_ep_fallback"),
        "elapsed_ms": result.get("elapsed_ms"),
        "wall_ms": wall_ms,
        "weights_resolved_from": weights.get("resolved_from"),
        "weights_sha256_matches_pin": weights.get("sha256") == SFX_WEIGHTS_SHA256,
        "synthetic_zero_candidates_note": (
            "synthetic page is outside the training distribution — the count "
            "is recorded, never asserted here (the real-page scenario is the "
            "candidate-count evidence face)"
            if result.get("n_candidates") == 0
            else None
        ),
    }
    gate.pass_or(
        exit_code == 0
        and payload is not None
        and three_keys_present
        and is_frozen(payload)
        and weights.get("sha256") == SFX_WEIGHTS_SHA256,
        "SP-L1-frozen-synthetic-probe",
        observed_l1,
    )

    # -- SP-L2: frozen-process REAL-page probe (the AC2 evidence face) -------
    log("SP-L2: frozen-process probe on the v2b anchor page (K07_R123)")
    if not args.real_page.is_file():
        gate.record(
            "SP-L2-frozen-real-page-probe",
            "SKIP",
            {
                "reason": "real page not present on this machine (NOT_RUN evidence)",
                "real_page": str(args.real_page),
            },
        )
    else:
        exit_code, stdout, stderr, wall_ms = run_frozen_probe(
            probe_exe,
            ["--page", str(args.real_page), "--label", "injected-real-page"],
            env,
            timeout=600,
        )
        (raw_dir / "sp-l2-real-page.log").write_text(
            f"$ <install>\\{PROBE_EXE_REL.as_posix()} --page {args.real_page} (purged PATH, all NEWMANGA_* cleared)\n"
            f"exit={exit_code} wall_ms={wall_ms}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}",
            encoding="utf-8",
        )
        payload = parse_probe_json(stdout)
        result = (payload or {}).get("result") or {}
        page = (payload or {}).get("page") or {}
        weights = (payload or {}).get("weights") or {}
        fallback = result.get("sfx_ep_fallback")
        observed_l2 = {
            "exit": exit_code,
            "json_parsed": payload is not None,
            "frozen_in_process": is_frozen(payload),
            "real_page": str(args.real_page),
            "page_sha256": page.get("sha256"),
            "page_sha256_domain_note": (
                "page.sha256 = decoded rgb24 PIXEL-BUFFER hash (probe face); "
                "page_file_sha256 = the PNG FILE hash (anchor-file face, DSH r1 P4-8)"
            ),
            "page_file_sha256": sha256_file(args.real_page),
            "n_candidates": result.get("n_candidates"),
            "confidences_max": max(result.get("confidences") or [None]),
            "device": result.get("device"),
            "sfx_ep": result.get("sfx_ep"),
            "sfx_ep_fallback": fallback,
            "elapsed_ms": result.get("elapsed_ms"),
            "wall_ms": wall_ms,
            "sfx_route": (result.get("options") or {}).get("sfx_route"),
            "imgsz": (result.get("options") or {}).get("imgsz"),
            "weights_sha256_matches_pin": weights.get("sha256") == SFX_WEIGHTS_SHA256,
            "expected_form": "device=dml, no sfx_ep_fallback; wrapper fallback recorded honestly without failing",
        }
        # AC2 face: real inference INSIDE the frozen process with candidates.
        # The EP form is recorded, not asserted: device=dml without fallback
        # is the expectation, but a wrapper-level CPU fallback is registered
        # honestly (Task contract) — never a silent pass, never a false fail.
        # DSH r1 P2-3: "frozen" and the weights pin are JUDGED here (they were
        # previously only recorded), so a probe accidentally pointed at a
        # non-frozen form or re-pinned weights cannot still PASS.
        gate.pass_or(
            exit_code == 0
            and payload is not None
            and is_frozen(payload)
            and (result.get("n_candidates") or 0) > 0
            and result.get("device") is not None
            and result.get("sfx_ep") is not None
            and "sfx_ep_fallback" in result
            and weights.get("sha256") == SFX_WEIGHTS_SHA256,
            "SP-L2-frozen-real-page-probe",
            observed_l2,
        )

    # -- SP-L3: existing frozen command surface zero-change smoke ------------
    log("SP-L3: existing command surface smoke (installed core_service.exe, stdio)")
    exit_code, ping, shutdown, raw = stdio_ping_shutdown(core_service_exe, env)
    (raw_dir / "sp-l3-core-service-ping.log").write_text(
        f"$ <install>\\{CORE_SERVICE_EXE_REL.as_posix()} (purged PATH)\nexit={exit_code}\n{raw}",
        encoding="utf-8",
    )
    gate.pass_or(
        exit_code == 0
        and (ping.get("result") or {}).get("status") == "ready"
        and (shutdown.get("result") or {}).get("status") == "stopped",
        "SP-L3-existing-command-surface-smoke",
        {
            "exit": exit_code,
            "ping_status": (ping.get("result") or {}).get("status"),
            "shutdown_status": (shutdown.get("result") or {}).get("status"),
        },
    )

    results = {
        "gate": "m2-prod-sfx-probe-1-packaged-sfx-detect-probe",
        "install_dir": str(install_dir),
        "verdict": gate.verdict,
        "build_venv_note": args.build_venv_note,
        "installer_sha256": args.installer_sha256,
        "build_head": args.build_head,
        "boundary_note": (
            "The frozen-process sfx detect evidence path is the fifth frozen "
            "entry exe (sfx_detect_probe.exe — one production "
            "SfxDetectionProvider.detect inside the frozen process); the "
            "frozen stdio command surface and every contract DTO are "
            "untouched (catalog_loader standalone-entry precedent shape). "
            "The GATE 25-scenario set stays untouched and is re-run "
            "separately as the no-regression face."
        ),
        "scenarios": gate.scenarios,
    }
    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nPROBE: {gate.verdict} -> {args.out}")
    return 0 if gate.verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
