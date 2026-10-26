"""CORE-SLIM-1 / AC2+AC3 — measure one sidecar bundle and emit JSON + a table.

Usage:
    python measure_bundle.py --bundle <core-sidecar dir> --label after --out <json>

Measures the AC3 accounting unit: the whole bundle tree, minus ``models/``
(the "Core runtime, models excluded" budget unit), plus the per-entry exe sizes
and the closure composition. Also asserts the CORE-SLIM-1 packaging facts:
no Qt in the closure, pure modules stored as shared ``.pyc`` files (noarchive
dedup), and every capability engine still present in the bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ENTRY_EXES = [
    "host_bridge.exe",
    "core_service.exe",
    "acceptance_bridge.exe",
    "catalog_loader.exe",
    "sfx_detect_probe.exe",
]

#: capability engines that must stay inside the frozen closure (AC3 evidence:
#: a byte saving that removes one of these would be a capability loss).
#: Each entry is a capability -> acceptable on-disk locations (layout differs
#: between torch/torchvision wheel vintages).
REQUIRED_RUNTIME = {
    "onnxruntime (DirectML EP)": [
        "_internal/onnxruntime",
        "_internal/onnxruntime_pybind11_state.pyd",
    ],
    "Pillow (image decode/render)": ["_internal/PIL"],
    "pypdfium2 (PDF raster)": ["_internal/pypdfium2_raw"],
    "numpy": ["_internal/numpy"],
    "detector ONNX model": ["models/detector/rtdetr-v2-fixed.onnx"],
    "manga-ocr ONNX bundle": [
        "models/ocr/manga-ocr-onnx/encoder_model.onnx",
        "models/ocr/manga-ocr-onnx/decoder_model.onnx",
        "models/ocr/manga-ocr-onnx/vocab.txt",
    ],
}

#: CORE-SLIM-2 negative assertion: these must NOT appear anywhere in the
#: shipped bundle (the whole point of the ONNX migration). A hit means the
#: spec exclusions/closure assertion were bypassed.
FORBIDDEN_RUNTIME = [
    "_internal/torch",
    "_internal/torchvision",
    "_internal/transformers",
    "_internal/doctr",
    "_internal/cv2",
    "_internal/scipy",
    "_internal/h5py",
    "_internal/shapely",
]


def tree_bytes(path: Path) -> tuple[int, int]:
    total = 0
    count = 0
    for item in path.rglob("*"):
        if item.is_file():
            total += item.stat().st_size
            count += 1
    return total, count


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def measure(bundle: Path, label: str) -> dict:
    total, count = tree_bytes(bundle)
    models_bytes = tree_bytes(bundle / "models")[0] if (bundle / "models").is_dir() else 0
    internal = bundle / "_internal"
    internal_bytes = tree_bytes(internal)[0] if internal.is_dir() else 0
    python_bytes = tree_bytes(bundle / "python")[0] if (bundle / "python").is_dir() else 0

    exe_sizes = {}
    exe_hashes = {}
    for name in ENTRY_EXES:
        candidate = bundle / name
        if candidate.is_file():
            exe_sizes[name] = candidate.stat().st_size
            exe_hashes[name] = sha256(candidate)

    top: list[dict] = []
    if internal.is_dir():
        for child in internal.iterdir():
            if child.is_dir():
                size = tree_bytes(child)[0]
            else:
                size = child.stat().st_size
            top.append({"name": child.name, "bytes": size, "mb": round(size / 1048576, 1)})
    top.sort(key=lambda entry: -entry["bytes"])

    pyc_files = list(internal.rglob("*.pyc")) if internal.is_dir() else []
    qt_hits = [
        str(item.relative_to(bundle))
        for item in bundle.rglob("*")
        if item.is_file() and item.name.lower() in {
            "qt6core.dll", "qt6gui.dll", "qt6qml.dll", "pyside6.abi3.pyd", "shiboken6.abi3.pyd"
        }
    ]
    pyside_dirs = [
        str(item.relative_to(bundle)) for item in bundle.rglob("PySide6") if item.is_dir()
    ]

    forbidden_hits = []
    for relative in FORBIDDEN_RUNTIME:
        if (bundle / relative).exists():
            forbidden_hits.append(relative)

    missing_runtime = []
    for capability, candidates in REQUIRED_RUNTIME.items():
        if not any((bundle / rel).exists() for rel in candidates):
            missing_runtime.append(capability)

    return {
        "label": label,
        "bundle": str(bundle),
        "exists": bundle.is_dir(),
        "totalBytes": total,
        "totalMb": round(total / 1048576, 1),
        "fileCount": count,
        "modelsBytes": models_bytes,
        "modelsMb": round(models_bytes / 1048576, 1),
        "excludingModelsBytes": total - models_bytes,
        "excludingModelsMb": round((total - models_bytes) / 1048576, 1),
        "internalBytes": internal_bytes,
        "internalMb": round(internal_bytes / 1048576, 1),
        "pythonRuntimeMb": round(python_bytes / 1048576, 1),
        "exeSizes": exe_sizes,
        "exeMb": {name: round(size / 1048576, 2) for name, size in exe_sizes.items()},
        "exeSha256": exe_hashes,
        "internalTop": top[:14],
        "noarchivePycCount": len(pyc_files),
        "noarchivePycMb": round(sum(item.stat().st_size for item in pyc_files) / 1048576, 1),
        "qtArtifacts": qt_hits + pyside_dirs,
        "torchArtifacts": forbidden_hits,
        "missingRequiredRuntime": missing_runtime,
        "models": {
            "detector": str(bundle / "models" / "detector" / "rtdetr-v2-fixed.onnx"),
            "ocr": str(bundle / "models" / "ocr" / "manga-ocr-onnx"),
        },
        "modelFiles": sorted(
            str(item.relative_to(bundle)) for item in (bundle / "models").rglob("*") if item.is_file()
        ) if (bundle / "models").is_dir() else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = measure(Path(args.bundle), args.label)
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "label", "totalMb", "modelsMb", "excludingModelsMb", "fileCount",
        "noarchivePycCount", "qtArtifacts", "torchArtifacts",
        "missingRequiredRuntime", "modelFiles",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
