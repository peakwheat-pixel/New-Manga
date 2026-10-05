"""M2-SFX-T4-SWITCH AC3/AC4: SHA-gate reverse verification and rollback drill.

Two independent process modes (the pin is a module constant consumed ONLY by
``_build_engine``'s sha comparison, so a fresh process importing the module
against the CURRENT src state IS the "production pin" being exercised):

``--mode ac3`` (run AFTER the src pin switch commit — the production pin is
  then 944e8114…):
  1. the FOREIGN weights (the previous production chiqui7 ONNX, d87389af…)
     must be refused by the SHA gate with the typed PROVIDER_FAILED
     (T0/V2/export-smoke assertion shape: ``gate fired or abort``);
  2. the NEW production weights (v2b, 944e8114…) must build through the full
     ``_build_engine`` chain (file probe -> sha -> runtime import -> session
     -> names/imgsz metadata assertion).
  Exit 0 only when both hold.

``--mode ac4`` (rollback drill — run while the src pin is TEMPORARILY
  restored to d87389af… in the working tree, uncommitted):
  the previous production weights (chiqui7 ONNX, read-only, never modified)
  must build through the full ``_build_engine`` chain under the restored pin
  — the rollback path is proven real, not paper. Exit 0 = rollback viable.

Assertion shape follows ``experiments/M2-SFX-TRAIN-V2/export_smoke_v2.py``
(sha_gate.fired / sha_gate.ok records). No output fabrication: every record
carries the observed values. venv: M2-SFX-FINETUNE-gpu-py312 (onnxruntime
ready; the same venv T3's evaluation used).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RAW_OUT = REPO / "verification" / "M2-SFX-T4-SWITCH" / "raw"

CHIQUI7_ONNX = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx")
CHIQUI7_SHA = "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"
V2B_DEPLOY_ONNX = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx")
V2B_SHA = "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"

EXPECTED_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=["ac3", "ac4"])
    args = parser.parse_args()

    import infrastructure.providers.detection_sfx as dsfx
    from ports.providers.errors import ProviderError

    records: dict = {
        "task": "M2-SFX-T4-SWITCH",
        "mode": args.mode,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "production_pin_as_imported": dsfx.SFX_WEIGHTS_SHA256,
        "expected_class_map": {str(k): v for k, v in EXPECTED_CLASS_MAP.items()},
    }

    if args.mode == "ac3":
        # precondition: the src pin IS the new v2b value
        if dsfx.SFX_WEIGHTS_SHA256 != V2B_SHA:
            print(
                f"FATAL: imported production pin {dsfx.SFX_WEIGHTS_SHA256} != "
                f"new v2b pin {V2B_SHA} — AC3 must run after the pin switch",
                file=sys.stderr,
            )
            return 2
        # 1. foreign weights refused (typed PROVIDER_FAILED)
        gate = {"weights": str(CHIQUI7_ONNX), "weights_sha256": CHIQUI7_SHA}
        try:
            dsfx._build_engine(CHIQUI7_ONNX)
            gate.update({"fired": False})
        except ProviderError as error:
            gate.update({
                "fired": True,
                "error_code": error.error_code,
                "message_head": str(error)[:200],
            })
        records["sha_gate_foreign_chiqui7"] = gate
        if not gate.get("fired") or gate.get("error_code") != "PROVIDER_FAILED":
            print("FATAL: SHA gate did NOT fire on the foreign (chiqui7) weights — supply-chain gate broken", file=sys.stderr)
            (RAW_OUT / "pin-switch-verify.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            return 1
        print("sha_gate.fired (foreign chiqui7 under new v2b pin): PROVIDER_FAILED", flush=True)
        # 2. new production weights build through the full chain
        try:
            session, imgsz, imgsz_source, imgsz_raw = dsfx._build_engine(V2B_DEPLOY_ONNX)
        except Exception as error:  # noqa: BLE001
            records["v2b_build"] = {"ok": False, "error": f"{type(error).__name__}: {error}"}
            (RAW_OUT / "pin-switch-verify.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"FATAL: v2b build failed: {error}", file=sys.stderr)
            return 1
        records["v2b_build"] = {
            "ok": True,
            "weights": str(V2B_DEPLOY_ONNX),
            "weights_sha256": V2B_SHA,
            "imgsz": imgsz,
            "imgsz_source": imgsz_source,
            "imgsz_metadata_raw": imgsz_raw,
        }
        print(f"v2b build_engine.ok imgsz={imgsz} source={imgsz_source}", flush=True)
        ok = records["v2b_build"]["ok"] and imgsz_source == "metadata_parsed"
        (RAW_OUT / "pin-switch-verify.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        print("AC3:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    # ---- ac4: rollback drill (src pin temporarily restored to chiqui7) -----
    if dsfx.SFX_WEIGHTS_SHA256 != CHIQUI7_SHA:
        print(
            f"FATAL: imported production pin {dsfx.SFX_WEIGHTS_SHA256} != "
            f"restored chiqui7 pin {CHIQUI7_SHA} — AC4 must run with the pin "
            "temporarily restored in the working tree (uncommitted)",
            file=sys.stderr,
        )
        return 2
    if not CHIQUI7_ONNX.is_file():
        print(f"FATAL: chiqui7 weights missing: {CHIQUI7_ONNX}", file=sys.stderr)
        return 2
    try:
        session, imgsz, imgsz_source, imgsz_raw = dsfx._build_engine(CHIQUI7_ONNX)
    except Exception as error:  # noqa: BLE001
        records["rollback_build"] = {"ok": False, "error": f"{type(error).__name__}: {error}"}
        (RAW_OUT / "rollback-drill.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"FATAL: rollback build failed: {error}", file=sys.stderr)
        return 1
    records["rollback_build"] = {
        "ok": True,
        "weights": str(CHIQUI7_ONNX),
        "weights_sha256_verified_by_gate": CHIQUI7_SHA,
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "imgsz_metadata_raw": imgsz_raw,
        "note": "chiqui7 weights file read-only throughout — never modified/deleted",
    }
    print(f"rollback build_engine.ok imgsz={imgsz} source={imgsz_source} EXIT=0 semantics", flush=True)
    (RAW_OUT / "rollback-drill.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AC4:", "PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
