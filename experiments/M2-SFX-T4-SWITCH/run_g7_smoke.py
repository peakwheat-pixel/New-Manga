"""M2-SFX-T4-SWITCH AC1: G7 translation-chain deep-call smoke (v2b repoint).

Hard precondition of the switch (user ruling 2026-10-05, "三件都同意"): one
BJ06-type ``policy=translate`` end-to-end run at run_qualification depth with
the v2b weights **repointed in-process** (zero src changes, T3/V2 precedent:
``eval_gate_t3.py:505-520`` — ``dsfx.SFX_WEIGHTS_SHA256 = <sha>`` inside a
try/finally that restores the pin). The SHA gate is proven FIRST (under the
default production pin the foreign weights are refused with the typed
``PROVIDER_FAILED``), only then is the pin repointed and the full chain run.

Sibling pass ``--side chiqui7`` runs the SAME page with the SAME arguments on
the un-repointed production pin (the AC1 comparison arm: new-failure count
must be 0; box-set differences are directional evidence only).

The harness itself is the VERIFIED M2-SFX-E2E-MATERIAL blueprint
(``experiments/M2-TA3-B/run_qualification.py``, read-only — reused in-process
via ``main()``; its ``NEWMANGA_SFX_WEIGHTS`` handling is ``os.environ.setdefault``
so a pre-set env selects the weights file). The venv is the E2E-MATERIAL one
(``M2-TA3-B-ocr``: onnxruntime + PySide6 + manga_ocr all present).

Credential: ``TA3B_TRANSLATE_API_KEY`` enters via env only, read from the
Git-external key file (same mechanism as E2E-MATERIAL report §commands); the
harness's ``scrub_secrets`` keeps it out of every persisted record.

Exit codes: 0 = SHA-gate probe behaved as asserted AND the qualification run
returned 0; 2 = precondition/gate-probe failure (fail-closed, nothing runs).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
_TA3B = REPO / "experiments" / "M2-TA3-B"
sys.path.insert(0, str(_TA3B))

RAW_OUT = REPO / "verification" / "M2-SFX-T4-SWITCH" / "raw"
PIXEL_ROOT_BASE = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-T4-SWITCH")

V2B_ONNX = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1"
    r"/train-v2/weights/v2b/best.onnx"
)
V2B_SHA = "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
CHIQUI7_ONNX = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx")
CHIQUI7_SHA = "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"
KEY_FILE = Path(r"G:/CODEX/New Manga.task-envs/M2-TA3-B/deepseek.key")

SIDES = {
    "v2b": {"onnx": V2B_ONNX, "sha": V2B_SHA, "repoint": True},
    "chiqui7": {"onnx": CHIQUI7_ONNX, "sha": CHIQUI7_SHA, "repoint": False},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side", required=True, choices=sorted(SIDES))
    args = parser.parse_args()
    side = SIDES[args.side]

    import infrastructure.providers.detection_sfx as dsfx
    from ports.providers.errors import ProviderError

    meta: dict = {
        "task": "M2-SFX-T4-SWITCH",
        "ac": "AC1 G7 translation-chain deep-call smoke",
        "side": args.side,
        "weights_path": str(side["onnx"]),
        "weights_sha256_expected": side["sha"],
        "production_pin_at_start": dsfx.SFX_WEIGHTS_SHA256,
        "repoint": side["repoint"],
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha_gate_probe": {},
    }

    # ---- SHA gate probe (fail-closed BEFORE any repoint) -------------------
    # v2b arm: under the DEFAULT production pin the foreign weights must be
    # refused with the typed PROVIDER_FAILED — the switch candidate may only
    # run inside an explicit in-process repoint window. chiqui7 arm: the
    # production weights load fine under the production pin (control sanity).
    if side["repoint"]:
        if not V2B_ONNX.is_file():
            print(f"FATAL: v2b onnx missing: {V2B_ONNX}", file=sys.stderr)
            return 2
        if dsfx.SFX_WEIGHTS_SHA256 != CHIQUI7_SHA:
            print(
                f"FATAL: production pin is not the chiqui7 d87389af… baseline "
                f"({dsfx.SFX_WEIGHTS_SHA256}); the AC1 pre/post assertions are "
                "defined against that baseline — aborting",
                file=sys.stderr,
            )
            return 2
        try:
            dsfx._build_engine(V2B_ONNX)
            meta["sha_gate_probe"] = {"fired": False}
        except ProviderError as error:
            meta["sha_gate_probe"] = {
                "fired": True,
                "error_code": error.error_code,
                "message_head": str(error)[:200],
            }
        if not meta["sha_gate_probe"].get("fired") or meta["sha_gate_probe"].get("error_code") != "PROVIDER_FAILED":
            print(
                "FATAL: SHA gate did NOT refuse the foreign weights under the "
                "default pin (expected typed PROVIDER_FAILED) — fail-closed stop",
                file=sys.stderr,
            )
            (RAW_OUT / f"g7-smoke-{args.side}" / "summaries").mkdir(parents=True, exist_ok=True)
            (RAW_OUT / f"g7-smoke-{args.side}" / "harness-meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return 2
        print(f"[g7-smoke] sha_gate_probe: FIRED error_code={meta['sha_gate_probe']['error_code']}", flush=True)
    else:
        engine_probe = "not-probed-in-this-arm"
        try:
            dsfx._build_engine(side["onnx"])
            engine_probe = "loaded-ok"
        except Exception as error:  # noqa: BLE001 — recorded, then fail-closed
            engine_probe = f"{type(error).__name__}: {error}"
        meta["sha_gate_probe"] = {"chiqui7_control_build": engine_probe}
        if engine_probe != "loaded-ok":
            print(f"FATAL: chiqui7 control weights failed to build: {engine_probe}", file=sys.stderr)
            return 2
        print(f"[g7-smoke] chiqui7 control build: loaded-ok", flush=True)

    # ---- credential via env only (never printed, never persisted) ----------
    if not KEY_FILE.is_file():
        print(f"FATAL: key file missing: {KEY_FILE}", file=sys.stderr)
        return 2
    os.environ["TA3B_TRANSLATE_API_KEY"] = KEY_FILE.read_text(encoding="utf-8").strip()

    # ---- weights selection + in-process repoint window (T3 precedent) ------
    os.environ["NEWMANGA_SFX_WEIGHTS"] = str(side["onnx"])
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    import run_qualification

    out_dir = RAW_OUT / f"g7-smoke-{args.side}" / "summaries"
    pixel_root = PIXEL_ROOT_BASE / f"pixels-{args.side}"
    argv_backup = sys.argv
    rc: int | None = None
    pin_backup = dsfx.SFX_WEIGHTS_SHA256
    try:
        if side["repoint"]:
            dsfx.SFX_WEIGHTS_SHA256 = side["sha"]
            print(f"[g7-smoke] repoint window OPEN: SFX_WEIGHTS_SHA256 -> {side['sha'][:12]}…", flush=True)
        else:
            assert dsfx.SFX_WEIGHTS_SHA256 == CHIQUI7_SHA  # control arm: pin untouched
        sys.argv = [
            "run_qualification.py",
            "--case", "BJ06",
            "--sfx-policy", "translate",
            "--determinism-track", "remote",
            "--meter-translation",
            "--force",
            "--out-dir", str(out_dir),
            "--pixel-root", str(pixel_root),
        ]
        rc = run_qualification.main()
    finally:
        dsfx.SFX_WEIGHTS_SHA256 = pin_backup
        sys.argv = argv_backup
        meta["pin_restored_after_window"] = dsfx.SFX_WEIGHTS_SHA256 == CHIQUI7_SHA
        meta["run_qualification_exit_code"] = rc
        meta["out_dir"] = str(out_dir)
        meta["pixel_root"] = str(pixel_root)
        meta["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (RAW_OUT / f"g7-smoke-{args.side}").mkdir(parents=True, exist_ok=True)
        (RAW_OUT / f"g7-smoke-{args.side}" / "harness-meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[g7-smoke] repoint window CLOSED (pin restored={meta['pin_restored_after_window']})", flush=True)
        print(f"[g7-smoke] run_qualification exit code = {rc}", flush=True)

    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
