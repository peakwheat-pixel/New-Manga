"""M2-PROD-DETECT-3 frozen detect probe (AC4) — release-form evidence.

This probe closes M2-PROD-DETECT-2 AC5's NOT_RUN sub-item ("frozen in-process
ML import/detect"): the INSTALLED core_service.exe now serves ``core.detect``
(protocol 1.1, M2-PROD-DETECT-3) and the probe drives it DIRECTLY — the real
transformers/RT-DETR-v2 stack loads inside the frozen process and inference
runs there (no out-of-closure driver, unlike the M2-PROD-DETECT-2 probe).

Scenarios (ruling 4 of the Task; three semantics + one recovery check):

  FD-1  frozen in-process REAL inference (the closed NOT_RUN item):
        NSIS-installed core_service.exe (purged PATH, stdio JSON-lines):
        core.ping (ready, protocol 1.1) -> core.detect (a synthetic comic
        page, base64 PNG + declared width/height) -> the assembled manga
        provider loads the INSTALLED in-bundle weights (three-file SHA-256
        pins enforced inside the provider BEFORE the model build — a
        successful detect therefore proves the pin gate passed) and runs the
        RT-DETR-v2 text detection in-process. Gate: EXIT=0, candidates > 0,
        anonymous manga-N labels, coordinate_space=page-global, elapsed_ms
        recorded (cold, in-process, includes the transformers load).
  FD-2  weights-less install fails closed typed (ruling 5 of DETECT-2):
        the models/ tree of the SAME install is renamed away -> core.detect
        answers error.code=PROVIDER_NOT_CONFIGURED (retryable=false) with ONE
        stderr assembly warning naming the probed candidates, and the process
        still serves core.ping (ready) — assembly never crashes.
  FD-2b recovery: models/ restored -> core.ping ready, warning gone
        (the DETECT-2 L2 counter-proof shape, re-proven on the 1.1 surface).
  FD-3  doctr backend switch-back semantics (ruling 3 of DETECT-2):
        NEWMANGA_DETECTOR_BACKEND=doctr -> the doctr weights intentionally
        ship OUT of the bundle -> core.detect answers the same typed
        PROVIDER_NOT_CONFIGURED, process stays alive.

Usage (from the repository root):
  python verification/M2-PROD-DETECT-3/frozen-detect-probe.py \
      --install-dir <NSIS install dir> [--python <interpreter>]

The install dir is expected to be the clean-start lab install (the GATE
runner's %TEMP%/m2ac5-cleanstart/install or an equivalent silent install).
Results JSON lands next to this script (frozen-detect-probe-results.json).
The gate fails closed: any FAIL fails the probe.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path(__file__).resolve().parent / "frozen-detect-probe-results.json"

INSTALL_EXE_REL = Path("resources") / "core-sidecar" / "core_service.exe"
MODELS_DIR_REL = Path("resources") / "core-sidecar" / "models"

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_VERSION = {"major": 1, "minor": 1}

PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")

ANNOUNCE_WARNING = "probed candidates"


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


def purged_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Runner-equivalent clean-start env: python-free PATH, M2RC1_* cleared."""
    kept = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not any(m.lower() in entry.lower() for m in PURGE_MARKERS):
            kept.append(entry)
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("M2RC1_", "M2RC2_")) and k not in ("M2AC1_TEST_MODE",)
    }
    env["PATH"] = os.pathsep.join(kept)
    env.setdefault("SYSTEMROOT", os.environ.get("SYSTEMROOT", "C:\\Windows"))
    if extra:
        env.update(extra)
    return env


def make_synthetic_page(path: Path) -> tuple[int, int]:
    """A white comic page with two black-bordered bubbles containing text
    (the same generator shape the M2-PROD-DETECT-2 probe used)."""
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


class FrozenCoreSession:
    """One frozen core_service.exe process over stdio JSON-lines."""

    def __init__(self, exe: Path, env: dict[str, str], log_path: Path) -> None:
        self._log_path = log_path
        self._started = time.perf_counter()
        self._proc = subprocess.Popen(
            [str(exe)],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.stderr_text = ""

    def request(self, request_id: str, command: str, payload: dict | None = None) -> dict:
        line = json.dumps({
            "protocol": PROTOCOL_NAME,
            "version": PROTOCOL_VERSION,
            "request_id": request_id,
            "command": command,
            "payload": payload or {},
        })
        assert self._proc.stdin is not None
        self._proc.stdin.write((line + "\n").encode("utf-8"))
        self._proc.stdin.flush()
        assert self._proc.stdout is not None
        raw = self._proc.stdout.readline()
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def close(self, timeout: int = 30) -> int:
        try:
            self.request("bye", "core.shutdown")
        except Exception:
            pass
        try:
            self._proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._proc.kill()
        err = self._proc.stderr.read() if self._proc.stderr else b""
        self.stderr_text = err.decode("utf-8", errors="replace")
        # LF-normalized on purpose: frozen stderr arrives as CRLF, and the
        # evidence files must stay diff --check clean (repo hygiene precedent).
        clean_stderr = self.stderr_text.replace("\r\n", "\n").replace("\r", "\n")
        self._log_path.write_text(
            f"$ frozen core_service.exe session (wall {int((time.perf_counter() - self._started) * 1000)}ms)\n"
            f"exit={self._proc.returncode}\n--- stderr ---\n{clean_stderr}",
            encoding="utf-8",
            newline="\n",
        )
        return self._proc.returncode


def run_fd1(gate: Gate, exe: Path, install_dir: Path) -> None:
    log("FD-1: frozen in-process REAL inference (core.detect, in-bundle weights)")
    workdir = Path(__file__).resolve().parent / "raw"
    workdir.mkdir(parents=True, exist_ok=True)
    page_path = workdir / "fd1-synthetic-page.png"
    width, height = make_synthetic_page(page_path)
    page_b64 = base64.b64encode(page_path.read_bytes()).decode("ascii")

    env = purged_env({"NEWMANGA_DATA_ROOT": str(install_dir / "fd1-data-root")})
    os.makedirs(env["NEWMANGA_DATA_ROOT"], exist_ok=True)
    session = FrozenCoreSession(exe, env, workdir / "fd1-frozen-session.log")
    detect_resp: dict = {}
    ping_resp: dict = {}
    try:
        ping_resp = session.request("r1", "core.ping")
        detect_resp = session.request(
            "r2",
            "core.detect",
            {"page": page_b64, "width": width, "height": height},
        )
    finally:
        exit_code = session.close(timeout=60)
    result = detect_resp.get("result") or {}
    error = detect_resp.get("error")
    candidates = result.get("candidates") or []
    labels_ok = bool(candidates) and all(
        isinstance(c.get("provider_label"), str) and c["provider_label"].startswith("manga-")
        for c in candidates
    )
    geometry_ok = all(
        isinstance(c.get("polygon"), list) and len(c["polygon"]) >= 3
        and c.get("coordinate_space") == "page-global"
        for c in candidates
    )
    gate.pass_or(
        exit_code == 0
        and (ping_resp.get("result") or {}).get("status") == "ready"
        and (ping_resp.get("result") or {}).get("protocol_version") == PROTOCOL_VERSION
        # M2-SETTINGS-IPC-CHANNEL (2026-10-02): PROTOCOL_VERSION above pins
        # minor=1 — this probe is FROZEN HISTORICAL EVIDENCE of the
        # M2-PROD-DETECT-3 gate and is NOT re-run against later tips
        # (envelope minor bumped to 2 by M2-C1 rev 1.3 §5.3).
        and error is None
        and len(candidates) > 0
        and labels_ok
        and geometry_ok,
        "FD1-frozen-inprocess-real-detect",
        {
            "exit": exit_code,
            "ping_status": (ping_resp.get("result") or {}).get("status"),
            "protocol_version": (ping_resp.get("result") or {}).get("protocol_version"),
            "n_candidates": len(candidates),
            "labels": [c.get("provider_label") for c in candidates],
            "confidences": [c.get("confidence") for c in candidates],
            "elapsed_ms_incl_model_load": result.get("elapsed_ms"),
            "page": f"{width}x{height} PNG base64 ({len(page_b64)} chars)",
            "stderr_head": session.stderr_text[:200],
        },
    )


def run_fd2(gate: Gate, exe: Path, install_dir: Path) -> tuple[Path | None, Path | None]:
    """Weights-less install: typed NOT_CONFIGURED + assembly survives.
    Returns (models_dir, parked_dir) so the caller can restore on failure."""
    log("FD-2: weights-less install -> typed PROVIDER_NOT_CONFIGURED (assembly survives)")
    models_dir = install_dir / MODELS_DIR_REL
    parked = install_dir / "resources" / "core-sidecar" / "models.probe-parked"
    if not models_dir.is_dir():
        gate.record("FD2-weights-absent-typed-not-configured", "FAIL", {"reason": f"models tree missing: {models_dir}"})
        return None, None
    models_dir.rename(parked)
    workdir = Path(__file__).resolve().parent / "raw"
    env = purged_env({"NEWMANGA_DATA_ROOT": str(install_dir / "fd2-data-root")})
    os.makedirs(env["NEWMANGA_DATA_ROOT"], exist_ok=True)
    session = FrozenCoreSession(exe, env, workdir / "fd2-frozen-weights-absent.log")
    ping_resp: dict = {}
    detect_resp: dict = {}
    try:
        ping_resp = session.request("r1", "core.ping")
        # The exact synthetic page still validates at the REQUEST layer; the
        # failure must land on the WEIGHTS check, not on input validation.
        page_path = workdir / "fd1-synthetic-page.png"
        page_b64 = base64.b64encode(page_path.read_bytes()).decode("ascii")
        detect_resp = session.request(
            "r2", "core.detect", {"page": page_b64, "width": 900, "height": 1300}
        )
    finally:
        exit_code = session.close(timeout=60)
    error = detect_resp.get("error") or {}
    gate.pass_or(
        exit_code == 0
        and (ping_resp.get("result") or {}).get("status") == "ready"
        and error.get("code") == "PROVIDER_NOT_CONFIGURED"
        and error.get("retryable") is False
        and ANNOUNCE_WARNING in session.stderr_text,
        "FD2-weights-absent-typed-not-configured",
        {
            "exit": exit_code,
            "ping_status": (ping_resp.get("result") or {}).get("status"),
            "error_code": error.get("code"),
            "retryable": error.get("retryable"),
            "assembly_warning_present": ANNOUNCE_WARNING in session.stderr_text,
        },
    )
    return models_dir, parked


def run_fd2b(gate: Gate, exe: Path, install_dir: Path, parked: Path | None) -> None:
    if parked is None:
        gate.record("FD2b-recovery-after-restore", "FAIL", {"reason": "FD-2 did not park a models tree"})
        return
    log("FD-2b: recovery after weights restore (warning gone, still ready)")
    models_dir = install_dir / MODELS_DIR_REL
    try:
        parked.rename(models_dir)
    except OSError as error:
        gate.record("FD2b-recovery-after-restore", "FAIL", {"reason": f"restore failed: {error}"})
        return
    workdir = Path(__file__).resolve().parent / "raw"
    env = purged_env({"NEWMANGA_DATA_ROOT": str(install_dir / "fd2b-data-root")})
    os.makedirs(env["NEWMANGA_DATA_ROOT"], exist_ok=True)
    session = FrozenCoreSession(exe, env, workdir / "fd2b-frozen-recovery.log")
    ping_resp: dict = {}
    try:
        ping_resp = session.request("r1", "core.ping")
    finally:
        exit_code = session.close(timeout=60)
    gate.pass_or(
        exit_code == 0
        and (ping_resp.get("result") or {}).get("status") == "ready"
        and ANNOUNCE_WARNING not in session.stderr_text,
        "FD2b-recovery-after-restore",
        {
            "exit": exit_code,
            "ping_status": (ping_resp.get("result") or {}).get("status"),
            "warning_gone": ANNOUNCE_WARNING not in session.stderr_text,
        },
    )


def run_fd3(gate: Gate, exe: Path, install_dir: Path) -> None:
    log("FD-3: doctr backend switch-back -> typed PROVIDER_NOT_CONFIGURED (ruling 3)")
    # Counter-proof first: the doctr weights must NOT be in the bundle.
    stray = install_dir / MODELS_DIR_REL / "detector" / "fast_base-688a8b34.pt"
    if stray.exists():
        gate.record("FD3-doctr-backend-typed-not-configured", "FAIL", {"reason": f"doctr weights IN the bundle: {stray}"})
        return
    workdir = Path(__file__).resolve().parent / "raw"
    env = purged_env({
        "NEWMANGA_DETECTOR_BACKEND": "doctr",
        "NEWMANGA_DATA_ROOT": str(install_dir / "fd3-data-root"),
    })
    os.makedirs(env["NEWMANGA_DATA_ROOT"], exist_ok=True)
    session = FrozenCoreSession(exe, env, workdir / "fd3-frozen-doctr.log")
    ping_resp: dict = {}
    detect_resp: dict = {}
    try:
        ping_resp = session.request("r1", "core.ping")
        page_path = workdir / "fd1-synthetic-page.png"
        page_b64 = base64.b64encode(page_path.read_bytes()).decode("ascii")
        detect_resp = session.request(
            "r2", "core.detect", {"page": page_b64, "width": 900, "height": 1300}
        )
    finally:
        exit_code = session.close(timeout=60)
    error = detect_resp.get("error") or {}
    gate.pass_or(
        exit_code == 0
        and (ping_resp.get("result") or {}).get("status") == "ready"
        and error.get("code") == "PROVIDER_NOT_CONFIGURED"
        and error.get("retryable") is False,
        "FD3-doctr-backend-typed-not-configured",
        {
            "exit": exit_code,
            "ping_status": (ping_resp.get("result") or {}).get("status"),
            "error_code": error.get("code"),
            "retryable": error.get("retryable"),
            "message_head": (error.get("message") or "")[:160],
        },
    )


def restore_parked_models(models_dir: Path | None, parked: Path | None) -> None:
    """DSH r1 R17: never leave the install's models tree parked.

    FD-2 parks models/ as models.probe-parked and FD-2b restores it; if
    anything between (or inside) them raises, this finally-hook puts the
    tree back so the next probe run starts from a normal install."""
    if (
        models_dir is not None
        and parked is not None
        and parked.is_dir()
        and not models_dir.exists()
    ):
        parked.rename(models_dir)
        print(f"  [finally] restored parked models tree -> {models_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--install-dir", type=Path, required=True)
    args = parser.parse_args()

    install_dir = args.install_dir.resolve()
    exe = install_dir / INSTALL_EXE_REL
    gate = Gate()

    print(f"install dir: {install_dir}")
    print(f"core_service.exe: {exe} (exists={exe.is_file()})")
    weights = install_dir / MODELS_DIR_REL / "detector" / "ogkalu-comic-text-and-bubble-detector"
    print(f"in-bundle weights: {weights} (model present={(weights / 'model.safetensors').is_file()})")

    # The page generator imports PIL on the HOST side only — the inference
    # itself runs inside the frozen process (FD-1), which is the point.
    import PIL  # noqa: F401

    run_fd1(gate, exe, install_dir)
    # DSH r1 R17: FD-2/FD-2b rename+restore the install's models tree; the
    # finally-hook guarantees restoration even if a scenario raises.
    models_dir: Path | None = None
    parked: Path | None = None
    try:
        models_dir, parked = run_fd2(gate, exe, install_dir)
        run_fd2b(gate, exe, install_dir, parked)
        run_fd3(gate, exe, install_dir)
    finally:
        restore_parked_models(models_dir, parked)

    results = {
        "gate": "m2-prod-detect-3-frozen-detect-probe",
        "install_dir": str(install_dir),
        "verdict": gate.verdict,
        "scenario_count_note": (
            "4 scenarios across 3 semantics (ruling 4): FD-1 frozen in-process "
            "real inference (the closed DETECT-2 AC5 NOT_RUN item); FD-2 "
            "weights-absent typed NOT_CONFIGURED + FD-2b recovery (one "
            "semantics, two proofs); FD-3 doctr switch-back typed "
            "NOT_CONFIGURED."
        ),
        "scenarios": gate.scenarios,
        "boundary_note": (
            "All four scenarios run INSIDE the frozen process: the detect "
            "inference itself executes in core_service.exe (no out-of-closure "
            "driver). The host-side PIL usage is limited to generating the "
            "synthetic page bytes that travel through the 1.1 wire contract."
        ),
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8", newline="\n")
    print(f"\nPROBE: {gate.verdict} -> {RESULTS_PATH}")
    return 0 if gate.verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
