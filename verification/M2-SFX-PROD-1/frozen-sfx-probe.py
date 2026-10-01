"""M2-SFX-PROD-1 frozen SFX probe (AC7) — release-form evidence.

The NSIS-installed core_service.exe serves ``core.detect`` (protocol 1.1);
with M2-SFX-PROD-1 the SAME assembly wires the SFX parallel provider beside
the manga primary, so core.detect's passthrough now carries sfx candidates
whose anonymous ``sfx-<n>`` labels prove the whole frozen chain worked:
in-bundle yolo11s-seg.onnx found through the shared DETECT-2 lookup ->
sha256 pin gate -> onnxruntime session inside the frozen process -> eval-
caliber inference. The probe drives the REAL SFX frame K07_R123 (the
M2-SFX-DETECT-EVAL anchor, conf 0.9313) as a base64 PNG.

Scenarios:

  SF-1  frozen in-process REAL sfx inference: core.ping (ready) -> core.detect
        (K07_R123) -> candidates contain at least one ``sfx-`` label with
        conf >= 0.5 AND manga candidates (the parallel evidence); coordinate
        space page-global; elapsed_ms recorded (cold, in-process, includes
        onnxruntime load). The dev-side value: conf 0.9313, box (201, 1134,
        383, 1341) — asserted within tolerance.
  SF-2  NEWMANGA_SFX_DETECTION=off: the same install answers core.detect with
        ZERO sfx labels (the pre-SFX manga-only surface, byte-identical
        ruling) and stays alive.
  SF-3  broken sfx weights (NEWMANGA_SFX_WEIGHTS -> missing path): the typed
        sfx failure degrades — manga candidates STILL come back, the process
        stays alive, and stderr carries the ONE degradation line. The manga
        chain is the product core; the optional detector never takes it down.

Usage (from the repository root):
  python verification/M2-SFX-PROD-1/frozen-sfx-probe.py \
      --install-dir <NSIS install dir> [--python <interpreter>]

Results JSON lands next to this script (frozen-sfx-probe-results.json).
The gate fails closed: any FAIL fails the probe.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path(__file__).resolve().parent / "frozen-sfx-probe-results.json"

INSTALL_EXE_REL = Path("resources") / "core-sidecar" / "core_service.exe"

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_VERSION = {"major": 1, "minor": 1}

PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")

#: The M2-SFX-DETECT-EVAL anchor frame (highest-confidence sfx detection:
#: K07_R123 sfx conf 0.9313, box 201.1, 1134.0, 383.4, 1340.9).
REAL_FRAME = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
)
EXPECTED_CONF = 0.9313
EXPECTED_BOX = (201.1, 1134.0, 383.4, 1340.9)

DEGRADE_WARNING = "sfx detection degraded"


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


def frame_payload() -> tuple[str, int, int]:
    """K07_R123 as base64 PNG + declared dimensions."""
    from PIL import Image

    with Image.open(REAL_FRAME) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        buffer = io.BytesIO()
        rgb.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii"), width, height


class CoreProcess:
    """One stdio JSON-lines core_service.exe conversation."""

    def __init__(self, exe: Path, env: dict[str, str]) -> None:
        self.proc = subprocess.Popen(
            [str(exe)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self._request_id = 0

    def rpc(self, command: str, payload: dict) -> dict:
        self._request_id += 1
        request = {
            "protocol": PROTOCOL_NAME,
            "version": PROTOCOL_VERSION,
            "request_id": f"probe-{self._request_id}",
            "command": command,
            "payload": payload,
        }
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("core_service.exe closed stdout without a response")
        return json.loads(line)

    def stderr(self) -> str:
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        except Exception:
            pass
        return self.proc.stderr.read() or ""


def labels_of(response: dict) -> list[str]:
    result = response.get("result") or {}
    return [
        candidate.get("provider_label", "")
        for candidate in (result.get("candidates") or [])
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install-dir", required=True, type=Path)
    args = parser.parse_args()

    exe = args.install_dir / INSTALL_EXE_REL
    assert exe.is_file(), f"installed core_service.exe missing: {exe}"
    page_b64, width, height = frame_payload()

    gate = Gate()

    # ------------------------------------------------------------------
    log("SF-1 frozen in-process REAL sfx inference (default assembly, SFX on)")
    core = CoreProcess(exe, purged_env())
    ping = core.rpc("core.ping", {})
    ready = (ping.get("result") or {}).get("status") == "ready"
    detect = core.rpc(
        "core.detect",
        {"page": page_b64, "width": width, "height": height},
    )
    labels = labels_of(detect)
    sfx_labels = [label for label in labels if label.startswith("sfx-")]
    manga_labels = [label for label in labels if label.startswith("manga-")]
    result = detect.get("result") or {}
    best_sfx = None
    for candidate in result.get("candidates") or []:
        if str(candidate.get("provider_label", "")).startswith("sfx-"):
            confidence = candidate.get("confidence") or 0.0
            if best_sfx is None or confidence > best_sfx[0]:
                best_sfx = (confidence, candidate.get("polygon"))
    observed = {
        "ready": ready,
        "candidates": len(labels),
        "sfx_labels": sfx_labels,
        "manga_candidates": len(manga_labels),
        "best_sfx_conf": best_sfx[0] if best_sfx else None,
        "elapsed_ms": result.get("elapsed_ms"),
    }
    gate.pass_or(
        ready
        and bool(sfx_labels)
        and bool(manga_labels)
        and best_sfx is not None
        and abs(best_sfx[0] - EXPECTED_CONF) <= 0.01,
        "SF-1",
        observed,
    )
    if best_sfx is not None:
        polygon = best_sfx[1] or []
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        gate.pass_or(
            bool(xs)
            and abs(min(xs) - EXPECTED_BOX[0]) <= 2.0
            and abs(min(ys) - EXPECTED_BOX[1]) <= 2.0
            and abs(max(xs) - EXPECTED_BOX[2]) <= 2.0
            and abs(max(ys) - EXPECTED_BOX[3]) <= 2.0,
            "SF-1b",
            {"polygon_bbox": [min(xs), min(ys), max(xs), max(ys)] if xs else None,
             "expected": list(EXPECTED_BOX)},
        )
    stderr_1 = core.stderr()

    # ------------------------------------------------------------------
    log("SF-2 NEWMANGA_SFX_DETECTION=off -> manga-only surface (no sfx labels)")
    core = CoreProcess(exe, purged_env({"NEWMANGA_SFX_DETECTION": "off"}))
    ping = core.rpc("core.ping", {})
    detect = core.rpc(
        "core.detect",
        {"page": page_b64, "width": width, "height": height},
    )
    labels = labels_of(detect)
    sfx_labels = [label for label in labels if label.startswith("sfx-")]
    manga_labels = [label for label in labels if label.startswith("manga-")]
    gate.pass_or(
        (ping.get("result") or {}).get("status") == "ready"
        and not sfx_labels
        and bool(manga_labels),
        "SF-2",
        {"candidates": len(labels), "sfx_labels": sfx_labels,
         "manga_candidates": len(manga_labels)},
    )
    core.stderr()

    # ------------------------------------------------------------------
    log("SF-3 broken sfx weights -> typed degradation, manga chain lives on")
    core = CoreProcess(
        exe,
        purged_env(
            {
                "NEWMANGA_SFX_WEIGHTS": "G:/nonexistent/sfx/weights.onnx",
            }
        ),
    )
    ping = core.rpc("core.ping", {})
    detect = core.rpc(
        "core.detect",
        {"page": page_b64, "width": width, "height": height},
    )
    labels = labels_of(detect)
    manga_labels = [label for label in labels if label.startswith("manga-")]
    stderr_3 = core.stderr()
    gate.pass_or(
        (ping.get("result") or {}).get("status") == "ready"
        and bool(manga_labels)
        and DEGRADE_WARNING in stderr_3,
        "SF-3",
        {"ready": (ping.get("result") or {}).get("status"),
         "manga_candidates": len(manga_labels),
         "stderr_has_degradation": DEGRADE_WARNING in stderr_3},
    )

    verdict = gate.verdict
    payload = {
        "schema": "m2-sfx-prod-1/frozen-sfx-probe@1",
        "task": "M2-SFX-PROD-1",
        "install_dir": str(args.install_dir),
        "core_service_exe": str(exe),
        "probe_frame": str(REAL_FRAME),
        "expected_sfx_conf": EXPECTED_CONF,
        "scenarios": gate.scenarios,
        "verdict": verdict,
    }
    RESULTS_PATH.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    log(f"verdict: {verdict} -> {RESULTS_PATH}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
