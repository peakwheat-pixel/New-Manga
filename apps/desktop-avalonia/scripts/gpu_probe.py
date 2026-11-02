#!/usr/bin/env python3
"""GPU-ORT-PROBE-1: emit the packaged device-probe JSON.

The release closure is torch-free and ships ``onnxruntime-directml``, so the
device probe authority is ``onnxruntime.get_available_providers()`` (see
``infrastructure.devices.manager``). This helper runs inside the build
environment (where ONNX Runtime is installed) and prints the JSON that
``package.ps1`` records in the package's ``VERSION.json`` under ``devices``; the
Avalonia settings page renders it, so a packaged build shows "DirectML 可用".

Usage:
  python gpu_probe.py            # print JSON
  python gpu_probe.py --out f    # also write JSON to ``f``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)

    sys.path.insert(0, str(SRC_ROOT))
    from infrastructure.devices.manager import probe_snapshot  # noqa: PLC0415

    payload = probe_snapshot()
    payload["ac"] = "AC1/AC2"
    payload["source"] = (
        "build-environment probe: onnxruntime.get_available_providers() "
        "+ Windows display-adapter registry supplement"
    )
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
