"""M2-SFX-T4-SWITCH frozen-bundle v2b probe — release-channel evidence.

Companion of ``verification/M2-SFX-PROD-1/frozen-sfx-probe.py`` (same
CoreProcess/purged-env/protocol-1.1 shape, reused for the SWITCH release
form). Drives the PyInstaller onedir bundle built by
``packaging/m2ac5/build_sidecar.ps1`` with the NEW v2b pin:

  FV-1  frozen in-process REAL inference under the new pin: core.ping ready
        -> core.detect (K07_R123 frame, the M2-SFX-DETECT-EVAL anchor) ->
        protocol round trip with manga candidates AND the sfx provider
        loaded WITHOUT a sha-gate/degradation line on stderr. The sfx
        candidate set is recorded as observed (directional) — the PROD-1
        conf-0.9313 expectation was a chiqui7-era value and does NOT carry
        over to the v2b weights, so only chain health is asserted here.
  FV-2  NEWMANGA_SFX_DETECTION=off -> the pre-SFX manga-only surface
        (byte-identical ruling shape): no sfx labels, manga alive.
  FV-3  NEWMANGA_SFX_WEIGHTS -> missing path: the typed sfx degradation —
        manga candidates STILL come back, stderr carries the degradation
        line (the optional detector never takes the manga chain down).

The bundle weights file is asserted on-disk == the v2b pin before any
process starts (the build-sidecar copy is sha-verified; this re-checks it
independently). Exit 0 = verdict PASS.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = (
    REPO_ROOT / "verification" / "M2-SFX-T4-SWITCH" / "raw" / "frozen-v2b-probe-results.json"
)

BUNDLE_EXE = (
    REPO_ROOT
    / "apps/desktop/src-tauri/target/core-sidecar/core-sidecar/core_service.exe"
)
BUNDLE_SFX_ONNX = (
    REPO_ROOT
    / "apps/desktop/src-tauri/target/core-sidecar/core-sidecar/models/detector/yolo11s-seg.onnx"
)
V2B_SHA = "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"

REAL_FRAME = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
)

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_VERSION = {"major": 1, "minor": 1}
PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")
DEGRADE_MARKERS = ("sha256", "PROVIDER_FAILED", "sfx detection degraded")


def purged_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    kept = [
        entry
        for entry in os.environ.get("PATH", "").split(os.pathsep)
        if not any(m.lower() in entry.lower() for m in PURGE_MARKERS)
    ]
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
    from PIL import Image

    with Image.open(REAL_FRAME) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        buffer = io.BytesIO()
        rgb.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii"), width, height


class CoreProcess:
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
            "request_id": f"frozen-v2b-probe-{self._request_id}",
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
    assert BUNDLE_EXE.is_file(), f"bundle core_service.exe missing: {BUNDLE_EXE}"
    digest = hashlib.sha256(BUNDLE_SFX_ONNX.read_bytes()).hexdigest()
    assert digest == V2B_SHA, f"bundle sfx weights sha mismatch: {digest}"
    print(f"bundle weights sha256 == v2b pin: OK ({digest[:12]}…)", flush=True)

    page_b64, width, height = frame_payload()
    scenarios: list[dict] = []

    def record(scenario_id: str, status: str, observed: dict) -> None:
        scenarios.append({"id": scenario_id, "status": status, "observed": observed})
        print(f"  [{status}] {scenario_id}: {json.dumps(observed, sort_keys=True)[:300]}", flush=True)

    # ---- FV-1 --------------------------------------------------------------
    print("=== FV-1 frozen REAL inference under the v2b pin (SFX on) ===", flush=True)
    core = CoreProcess(BUNDLE_EXE, purged_env())
    ping = core.rpc("core.ping", {})
    ready = (ping.get("result") or {}).get("status") == "ready"
    detect = core.rpc("core.detect", {"page": page_b64, "width": width, "height": height})
    labels = labels_of(detect)
    sfx_labels = [label for label in labels if label.startswith("sfx-")]
    manga_labels = [label for label in labels if label.startswith("manga-")]
    stderr_1 = core.stderr()
    gate_lines = [line for line in stderr_1.splitlines() if any(m in line for m in ("sha256", "PROVIDER_FAILED"))]
    best_sfx_conf = None
    for candidate in (detect.get("result") or {}).get("candidates") or []:
        if str(candidate.get("provider_label", "")).startswith("sfx-"):
            confidence = candidate.get("confidence") or 0.0
            best_sfx_conf = confidence if best_sfx_conf is None else max(best_sfx_conf, confidence)
    record(
        "FV-1",
        "PASS" if ready and bool(manga_labels) and not gate_lines else "FAIL",
        {
            "ready": ready,
            "candidates": len(labels),
            "sfx_labels": sfx_labels,
            "best_sfx_conf": best_sfx_conf,
            "manga_candidates": len(manga_labels),
            "stderr_sha_or_provider_failed_lines": gate_lines,
            "elapsed_ms": (detect.get("result") or {}).get("elapsed_ms"),
        },
    )

    # ---- FV-2 --------------------------------------------------------------
    print("=== FV-2 NEWMANGA_SFX_DETECTION=off -> manga-only surface ===", flush=True)
    core = CoreProcess(BUNDLE_EXE, purged_env({"NEWMANGA_SFX_DETECTION": "off"}))
    ping = core.rpc("core.ping", {})
    detect = core.rpc("core.detect", {"page": page_b64, "width": width, "height": height})
    labels = labels_of(detect)
    sfx_labels = [label for label in labels if label.startswith("sfx-")]
    manga_labels = [label for label in labels if label.startswith("manga-")]
    core.stderr()
    record(
        "FV-2",
        "PASS" if (ping.get("result") or {}).get("status") == "ready" and not sfx_labels and bool(manga_labels) else "FAIL",
        {"candidates": len(labels), "sfx_labels": sfx_labels, "manga_candidates": len(manga_labels)},
    )

    # ---- FV-3 --------------------------------------------------------------
    print("=== FV-3 broken sfx weights -> typed degradation, manga chain lives ===", flush=True)
    core = CoreProcess(BUNDLE_EXE, purged_env({"NEWMANGA_SFX_WEIGHTS": r"Z:\definitely\missing\yolo11s-seg.onnx"}))
    ping = core.rpc("core.ping", {})
    detect = core.rpc("core.detect", {"page": page_b64, "width": width, "height": height})
    labels = labels_of(detect)
    sfx_labels = [label for label in labels if label.startswith("sfx-")]
    manga_labels = [label for label in labels if label.startswith("manga-")]
    stderr_3 = core.stderr()
    degraded = "sfx detection degraded" in stderr_3
    record(
        "FV-3",
        "PASS" if (ping.get("result") or {}).get("status") == "ready" and bool(manga_labels) and not sfx_labels and degraded else "FAIL",
        {"ready": (ping.get("result") or {}).get("status"), "manga_candidates": len(manga_labels), "sfx_labels": sfx_labels, "stderr_has_degradation": degraded},
    )

    verdict = "FAIL" if any(s["status"] == "FAIL" for s in scenarios) else "PASS"
    results = {
        "schema": "m2-sfx-t4-switch/frozen-v2b-probe@1",
        "task": "M2-SFX-T4-SWITCH",
        "bundle_exe": str(BUNDLE_EXE),
        "bundle_sfx_weights_sha256": digest,
        "probe_frame": str(REAL_FRAME),
        "scenarios": scenarios,
        "verdict": verdict,
    }
    RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"results -> {RESULTS_PATH}", flush=True)
    print(f"verdict: {verdict}", flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
