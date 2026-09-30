"""M2-PROD-DETECT-2 packaged detect probe (AC5) — release-form evidence.

Independent probe (NOT part of the frozen M2-AC5 runner). It verifies the
NSIS-installed release form's detect chain in FOUR layers / SIX scenarios
(DSH r1 R12: the count is 6 scenarios across 4 layers — the L2 layer has a
counter-proof plus its recovery, the L4 layer has a frozen-start scenario
plus an out-of-closure detect assertion):

  L1  frozen startup smoke + assembly end-to-end:
      the INSTALLED core_service.exe (purged PATH, stdio JSON-lines) serves
      core.ping -> status=ready. The production assembly runs at process
      start, so this also proves the frozen weights lookup selects the
      in-bundle copy (with the bundle weights missing, assembly degrades to
      a stderr warning + detect-time typed failure — see L2).
  L2  in-bundle weights resolution counter-proof (DSH r1 R5/R6 review-fix:
      the assembly-time fail-fast is GONE — a missing weights tree must NOT
      take the whole app down):
      temporarily rename the installed models/ tree away -> the frozen
      core_service.exe must STILL start and answer core.ping (status=ready)
      with ONE stderr warning line naming every probed candidate -> restore
      -> ping again AND the warning is gone (recovery).
  L3  real manga inference against the INSTALLED in-bundle weights:
      a synthetic comic page (white background + black bubbles + text, PIL)
      goes through the production adapter (validate -> frame pixels ->
      processor -> model -> post_process -> text-class filter -> frozen
      merge) with weights_dir pointed at the installed bundle copy and the
      build-venv interpreter (the SAME pinned ML stack that ships in the
      closure, versions verbatim from requirements-build.txt). Gate:
      EXIT=0 and text candidates > 0; elapsed_ms recorded.
      Boundary (honest): the inference itself runs OUTSIDE the frozen
      process — the frozen command surface is M2-IPC1-frozen to
      core.ping/ListBooks/core.shutdown with NO detect RPC, and this probe
      does not extend it. Frozen-process closure completeness is evidenced
      by L1 (startup), the per-entry PyInstaller warn archives (R1), the
      build-time ML closure assertion in the spec (R3) and the PYZ archive
      listing (transformers + rt_detr present).
  L4  doctr fail-closed in the release form (proxy ruling 3):
      (a) the INSTALLED core_service.exe with NEWMANGA_DETECTOR_BACKEND=doctr
      starts fine (an assembly-time error would violate ruling 3; after the
      R5/R6 review-fix a frozen doctr miss prints the same stderr warning as
      manga and keeps detect-time NOT_CONFIGURED). This scenario is a frozen
      STARTUP check only — detect semantics are covered by the unit tests
      and the out-of-closure detect assertion below (DSH r1 R4).
      (b) an out-of-closure detect with the doctr weights ABSENT (the
      designed release state): the production DoctrDetectionProvider raises
      the typed ProviderNotConfigured (error_code PROVIDER_NOT_CONFIGURED),
      never an untyped error — run under the build venv, reusing the L3
      driver shape.

Usage (from the repository root):
  python verification/M2-PROD-DETECT-2/packaged-detect-probe.py \
      --install-dir <NSIS install dir> \
      [--build-venv-python <python.exe>] [--src-root <repo>/src]

Results JSON lands next to this script (packaged-detect-probe-results.json).
The gate fails closed: any FAIL fails the probe.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path(__file__).resolve().parent / "packaged-detect-probe-results.json"

INSTALL_EXE_REL = Path("resources") / "core-sidecar" / "core_service.exe"
BUNDLE_WEIGHTS_REL = (
    Path("resources")
    / "core-sidecar"
    / "models"
    / "detector"
    / "ogkalu-comic-text-and-bubble-detector"
)
MANGA_MODEL_FILENAME = "model.safetensors"

PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")

ANNOUNCE_L2 = "probed candidates"


class Gate:
    def __init__(self) -> None:
        self.scenarios: list[dict] = []

    def record(self, scenario_id: str, status: str, observed: dict) -> None:
        self.scenarios.append({"id": scenario_id, "status": status, "observed": observed})
        print(f"  [{status}] {scenario_id}: {json.dumps(observed, sort_keys=True)[:260]}")

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


def purged_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Runner-equivalent clean-start env: python-free PATH, M2RC1_* cleared."""
    removed = []
    kept = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        marker_hit = any(m.lower() in entry.lower() for m in PURGE_MARKERS)
        (removed if marker_hit else kept).append(entry)
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("M2RC1_", "M2RC2_")) and k not in ("M2AC1_TEST_MODE", "NEWMANGA_DATA_ROOT")
    }
    env["PATH"] = os.pathsep.join(kept)
    env.setdefault("SYSTEMROOT", os.environ.get("SYSTEMROOT", "C:\\Windows"))
    if extra:
        env.update(extra)
    return env


def stdio_ping(exe: Path, env: dict[str, str], timeout: int = 240) -> tuple[int, dict, dict, str]:
    """One stdio JSON-lines round trip: core.ping then core.shutdown.

    Returns (exit, ping_response, shutdown_response, raw_text).
    """
    envelope = json.dumps(
        {
            "protocol": "new-manga.core",
            "version": {"major": 1, "minor": 0},
            "request_id": "r{i}",
            "command": "{cmd}",
            "payload": {},
        }
    )
    ping_req = envelope.replace("{i}", "1").replace("{cmd}", "core.ping")
    shutdown_req = envelope.replace("{i}", "2").replace("{cmd}", "core.shutdown")
    started = time.perf_counter()
    proc = subprocess.Popen(
        [str(exe)],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        out, err = proc.communicate(
            input=(ping_req + "\n" + shutdown_req + "\n").encode("utf-8"),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=15)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
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


# ---------------------------------------------------------------------------
# L3: real inference driver (runs under the build venv, PYTHONPATH=src)
# ---------------------------------------------------------------------------

L3_DRIVER = r'''
import json, sys, time
from pathlib import Path

src_root, weights_dir, page_path, out_path = sys.argv[1:5]
sys.path.insert(0, src_root)

import importlib.metadata as md
versions = {}
for dist in ("torch", "torchvision", "transformers", "safetensors", "python-doctr", "tokenizers"):
    try:
        versions[dist] = md.version(dist)
    except Exception:
        versions[dist] = None

from infrastructure.providers.detection_manga import MangaDetectionProvider
from ports.detection.ports import DetectionRequest

from PIL import Image
import io

# The production page_frame contract (same as the docTR adapter): the
# request carries a RAW pixel buffer (rgb24/rgb32), never an encoded file.
with Image.open(page_path) as im:
    rgb = im.convert("RGB")
    width, height = rgb.size
    frame = rgb.tobytes()

provider = MangaDetectionProvider(weights_dir=Path(weights_dir), device="cpu")
request = DetectionRequest(page_id="probe-page", image_bytes=frame, width=width, height=height)

# cold pass (engine build + weights load + one inference), then steady-state
# passes so the recorded latency separates one-off loading from per-page cost.
started = time.perf_counter()
result = provider.detect(request)
cold_ms = int((time.perf_counter() - started) * 1000)
warm_ms = []
for _ in range(3):
    started = time.perf_counter()
    result = provider.detect(request)
    warm_ms.append(int((time.perf_counter() - started) * 1000))
payload = {
    "exit": 0,
    "versions": versions,
    "provider_id": result.provider_id,
    "model": result.model,
    "n_candidates": len(result.candidates),
    "confidences": [c.confidence for c in result.candidates],
    "cold_elapsed_ms_incl_engine_build": cold_ms,
    "warm_elapsed_ms": warm_ms,
    "warm_avg_ms": sum(warm_ms) // len(warm_ms),
    "detect_reported_ms": result.elapsed_ms,
}
Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
'''


# ---------------------------------------------------------------------------
# L4(b): out-of-closure doctr detect driver (runs under the build venv,
# PYTHONPATH=src) — reuses the L3 driver shape (R4)
# ---------------------------------------------------------------------------

L4_DRIVER = r'''
import json, sys
from pathlib import Path

src_root, weights_path, out_path = sys.argv[1:4]
sys.path.insert(0, src_root)

import importlib.metadata as md
versions = {}
for dist in ("torch", "torchvision", "transformers", "safetensors", "python-doctr"):
    try:
        versions[dist] = md.version(dist)
    except Exception:
        versions[dist] = None

from infrastructure.providers.detection_doctr import DoctrDetectionProvider
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderNotConfigured

# A minimal 4x4 rgb24 frame: passes the pure-Python input validate gate so
# the failure lands on the WEIGHTS check (the thing under test), not on
# input validation.
frame = bytes(4 * 4 * 3)
request = DetectionRequest(page_id="probe-doctr-absent", image_bytes=frame, width=4, height=4)

provider = DoctrDetectionProvider(weights_path=Path(weights_path), device="cpu")
try:
    provider.detect(request)
    payload = {
        "exit": 1,
        "outcome": "no_error",
        "message": "detect did NOT fail closed on the absent doctr weights",
    }
except ProviderNotConfigured as error:
    payload = {
        "exit": 0,
        "outcome": "typed_not_configured",
        "error_code": getattr(error, "error_code", None),
        "provider_id": getattr(provider, "provider_id", None),
        "message_head": str(error)[:240],
    }
except Exception as error:  # noqa: BLE001 - any other shape is a FAIL
    payload = {
        "exit": 1,
        "outcome": "untyped_error",
        "error_class": type(error).__name__,
        "message_head": str(error)[:240],
    }
Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
'''


def make_synthetic_page(path: Path) -> tuple[int, int]:
    """A white comic page with two black-bordered bubbles containing text."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 900, 1300
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.load_default(size=64)
    except TypeError:  # Pillow < 10.1 fallback
        font = ImageFont.load_default()
    for (cx, cy, rx, ry, label) in (
        (300, 350, 220, 130, "HELLO"),
        (620, 800, 240, 150, "MANGA"),
    ):
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill="white", outline="black", width=8)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw / 2, cy - th / 2 - bbox[1]), label, fill="black", font=font)
    image.save(path, "PNG")
    return width, height


# ---------------------------------------------------------------------------
# layers
# ---------------------------------------------------------------------------


def run_l1(gate: Gate, exe: Path, env: dict, evidence_dir: Path) -> None:
    log("L1: frozen startup smoke + assembly end-to-end (installed core_service.exe)")
    exit_code, ping, shutdown, raw = stdio_ping(exe, env)
    (evidence_dir / "l1-frozen-ping.log").write_text(
        f"$ <install>\\{INSTALL_EXE_REL.as_posix()} (purged PATH)\nexit={exit_code}\n{raw}",
        encoding="utf-8",
    )
    result = ping.get("result") or {}
    gate.pass_or(
        ping.get("error") is None
        and result.get("status") == "ready"
        and shutdown.get("result", {}).get("status") == "stopped"
        and exit_code == 0,
        "PK-L1-frozen-startup-ping",
        {"exit": exit_code, "status": result.get("status"), "shutdown": shutdown.get("result")},
    )


def run_l2(gate: Gate, exe: Path, install_dir: Path, env: dict, evidence_dir: Path) -> None:
    log(
        "L2: in-bundle weights counter-proof (move away -> stderr warning + "
        "assembly still succeeds -> restore -> warning gone)"
    )
    models_dir = install_dir / "resources" / "core-sidecar" / "models"
    parked = install_dir / "resources" / "core-sidecar" / "models.probe-parked"
    if not models_dir.is_dir():
        gate.record("PK-L2-weights-absent-assembles-with-warning", "FAIL", {"reason": f"bundle weights tree missing: {models_dir}"})
        return
    try:
        models_dir.rename(parked)
        exit_code, ping, _shutdown, raw = stdio_ping(exe, env, timeout=120)
        (evidence_dir / "l2-frozen-weights-absent.log").write_text(
            f"$ core_service.exe with the bundle models/ tree moved away\nexit={exit_code}\n{raw}",
            encoding="utf-8",
        )
        # DSH r1 R5/R6 review-fix: a broken install (weights tree gone) must
        # NOT crash the assembly — one stderr diagnostic line (naming every
        # probed candidate), then the app still comes up ready; the detect
        # step fails closed NOT_CONFIGURED at its own time.
        gate.pass_or(
            exit_code == 0
            and (ping.get("result") or {}).get("status") == "ready"
            and ANNOUNCE_L2 in raw,
            "PK-L2-weights-absent-assembles-with-warning",
            {
                "exit": exit_code,
                "status": (ping.get("result") or {}).get("status"),
                "mentions_probed_candidates": ANNOUNCE_L2 in raw,
            },
        )
    finally:
        if parked.is_dir():
            parked.rename(models_dir)
    # recovery proof: weights back in place -> ready AND no warning
    exit_code, ping, _shutdown, raw = stdio_ping(exe, env)
    gate.pass_or(
        exit_code == 0
        and (ping.get("result") or {}).get("status") == "ready"
        and ANNOUNCE_L2 not in raw,
        "PK-L2-recovery-after-restore",
        {
            "exit": exit_code,
            "status": (ping.get("result") or {}).get("status"),
            "warning_gone": ANNOUNCE_L2 not in raw,
        },
    )


def run_l3(
    gate: Gate,
    install_dir: Path,
    build_venv_python: Path,
    src_root: Path,
    evidence_dir: Path,
) -> None:
    log("L3: real manga inference against the installed in-bundle weights")
    weights_dir = install_dir / BUNDLE_WEIGHTS_REL
    if not (weights_dir / MANGA_MODEL_FILENAME).is_file():
        gate.record("PK-L3-real-inference", "FAIL", {"reason": f"in-bundle weights missing: {weights_dir}"})
        return
    driver_path = evidence_dir / "l3-inference-driver.py"
    driver_path.write_text(L3_DRIVER, encoding="utf-8")
    page_path = evidence_dir / "l3-synthetic-page.png"
    make_synthetic_page(page_path)

    with tempfile.TemporaryDirectory(prefix="m2pd2-probe-") as tmp:
        out_path = Path(tmp) / "l3-result.json"
        proc = subprocess.run(
            [
                str(build_venv_python),
                str(driver_path),
                str(src_root),
                str(weights_dir),
                str(page_path),
                str(out_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        (evidence_dir / "l3-inference.log").write_text(
            f"$ build-venv python l3-inference-driver.py (weights_dir=INSTALLED bundle copy)\n"
            f"exit={proc.returncode}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}",
            encoding="utf-8",
        )
        payload = {}
        if out_path.is_file():
            try:
                payload = json.loads(out_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        gate.pass_or(
            proc.returncode == 0 and payload.get("n_candidates", 0) > 0,
            "PK-L3-real-inference",
            {
                "exit": proc.returncode,
                "n_candidates": payload.get("n_candidates"),
                "cold_elapsed_ms_incl_engine_build": payload.get("cold_elapsed_ms_incl_engine_build"),
                "warm_avg_ms": payload.get("warm_avg_ms"),
                "warm_elapsed_ms": payload.get("warm_elapsed_ms"),
                "versions": payload.get("versions"),
                "weights_dir": str(weights_dir),
                "stderr_tail": proc.stderr[-300:] if proc.returncode != 0 else "",
            },
        )


def run_l4(
    gate: Gate,
    exe: Path,
    env: dict,
    evidence_dir: Path,
    install_dir: Path,
    build_venv_python: Path,
    src_root: Path,
) -> None:
    log("L4: doctr fail-closed in the release form (ruling 3)")
    # (a) frozen STARTUP check only (DSH r1 R4/R12: the scenario name no
    # longer claims detect coverage): with NEWMANGA_DETECTOR_BACKEND=doctr
    # the frozen process must start — the doctr weights ship OUT of the
    # bundle ON PURPOSE, and after the R5/R6 review-fix a frozen miss prints
    # the same stderr warning as manga instead of any assembly-time error.
    doctr_env = dict(env)
    doctr_env["NEWMANGA_DETECTOR_BACKEND"] = "doctr"
    exit_code, ping, shutdown, raw = stdio_ping(exe, doctr_env)
    (evidence_dir / "l4-frozen-doctr-startup.log").write_text(
        f"$ core_service.exe with NEWMANGA_DETECTOR_BACKEND=doctr (purged PATH)\nexit={exit_code}\n{raw}",
        encoding="utf-8",
    )
    gate.pass_or(
        exit_code == 0
        and (ping.get("result") or {}).get("status") == "ready"
        and shutdown.get("result", {}).get("status") == "stopped",
        "PK-L4-doctr-starts-without-assembly-error",
        {
            "exit": exit_code,
            "status": (ping.get("result") or {}).get("status"),
            "warning_expected_state": "see raw log (stderr line if present)",
        },
    )
    # (b) out-of-closure DETECT assertion (DSH r1 R4): the doctr weights are
    # absent from the bundle by design (ruling 3), so the production provider
    # must raise the TYPED ProviderNotConfigured (error_code
    # PROVIDER_NOT_CONFIGURED) at detect time — never an untyped error.
    absent_weights = (
        install_dir
        / "resources"
        / "core-sidecar"
        / "models"
        / "detector"
        / "fast_base-688a8b34.pt"
    )
    if absent_weights.exists():
        gate.record(
            "PK-L4-doctr-detect-fail-closed-typed",
            "FAIL",
            {"reason": f"doctr weights unexpectedly IN the bundle: {absent_weights} (violates ruling 3)"},
        )
        return
    driver_path = evidence_dir / "l4-doctr-detect-driver.py"
    driver_path.write_text(L4_DRIVER, encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="m2pd2-probe-") as tmp:
        out_path = Path(tmp) / "l4-result.json"
        proc = subprocess.run(
            [
                str(build_venv_python),
                str(driver_path),
                str(src_root),
                str(absent_weights),
                str(out_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        (evidence_dir / "l4-doctr-detect.log").write_text(
            f"$ build-venv python l4-doctr-detect-driver.py (weights_path=absent in-bundle candidate)\n"
            f"exit={proc.returncode}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}",
            encoding="utf-8",
        )
        payload = {}
        if out_path.is_file():
            try:
                payload = json.loads(out_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        gate.pass_or(
            proc.returncode == 0
            and payload.get("outcome") == "typed_not_configured"
            and payload.get("error_code") == "PROVIDER_NOT_CONFIGURED",
            "PK-L4-doctr-detect-fail-closed-typed",
            {
                "driver_exit": proc.returncode,
                "outcome": payload.get("outcome"),
                "error_code": payload.get("error_code"),
                "provider_id": payload.get("provider_id"),
                "weights_path": str(absent_weights),
                "stderr_tail": proc.stderr[-300:] if proc.returncode != 0 else "",
            },
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument(
        "--build-venv-python",
        type=Path,
        default=Path("G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe"),
    )
    parser.add_argument("--src-root", type=Path, default=REPO_ROOT / "src")
    args = parser.parse_args()

    install_dir = args.install_dir.resolve()
    exe = install_dir / INSTALL_EXE_REL
    gate = Gate()

    print(f"install dir: {install_dir}")
    print(f"core_service.exe: {exe} (exists={exe.is_file()})")
    weights_dir = install_dir / BUNDLE_WEIGHTS_REL
    print(f"bundle weights: {weights_dir} (model present={(weights_dir / MANGA_MODEL_FILENAME).is_file()})")

    env = purged_env()
    evidence_dir = Path(__file__).resolve().parent / "raw"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    run_l1(gate, exe, env, evidence_dir)
    run_l2(gate, exe, install_dir, env, evidence_dir)
    run_l3(gate, install_dir, args.build_venv_python, args.src_root, evidence_dir)
    run_l4(gate, exe, env, evidence_dir, install_dir, args.build_venv_python, args.src_root)

    results = {
        "gate": "m2-prod-detect-2-packaged-detect-probe",
        "install_dir": str(install_dir),
        "verdict": gate.verdict,
        "scenario_count_note": "6 scenarios across 4 layers (L2 = counter-proof + recovery, L4 = frozen start + out-of-closure typed detect)",
        "scenarios": gate.scenarios,
        "boundary_note": (
            "L3 inference and the L4(b) detect assertion run OUTSIDE the frozen "
            "process: the frozen command surface is M2-IPC1-frozen (core.ping/"
            "ListBooks/core.shutdown) with no detect RPC — frozen in-process ML "
            "import/detect stays NOT_RUN until M2-IPC1 extends the command "
            "surface (DSH r1 R2: AC5 is PARTIAL). Closure completeness is "
            "evidenced by L1 startup, the per-entry warn archives (R1), the "
            "build-time ML closure assertion + PYZ listing (R3) and L2."
        ),
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nPROBE: {gate.verdict} -> {RESULTS_PATH}")
    return 0 if gate.verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
