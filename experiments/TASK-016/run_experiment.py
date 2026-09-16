"""Run or honestly block the TASK-016 OCR/detection route experiment.

Default mode is a no-download capability probe. ``--run-models`` is explicit:
it may invoke an already-installed local model or an already-configured
OpenAI-compatible endpoint, but it never installs dependencies or downloads
weights. Every result carries enough fields to distinguish quality evidence
from a missing prerequisite.

Revision notes (TASK-016 review findings):

* **R-001** — detector candidates are first-class ``CANDIDATES`` entries with
  ``stage``/``metadata_status``; they are probed and failed explicitly, and the
  report carries a ``verification_matrix`` stating what evidence exists per
  candidate stage (and what still needs a scope decision).
* **R-003** — every ``version``/``license`` value is prefixed ``UNVERIFIED`` and
  carries ``metadata_status: "UNVERIFIED"``; no version or licence is asserted
  that was not confirmed online.
* **R-004** — one sentinel ``MODEL_SHA256_UNAVAILABLE`` covers every record
  without a real model digest; a sample hash is never written to
  ``model_sha256``.

Preserved from a concurrent author's revision in this worktree: the manga-ocr
recognition path crops the Region polygon before recognition instead of feeding
the whole sample image.
"""

from __future__ import annotations

import argparse
import base64
import ctypes
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any
from urllib import request

from protocol import map_region_result, order_results, validate_route_configuration


ROOT = Path(__file__).resolve().parent

#: R-004: the one and only sentinel for "no real model digest available".
MODEL_SHA256_UNAVAILABLE = "NOT_AVAILABLE"

#: R-003: prefix applied to every unverified version/licence string.
UNVERIFIED = "UNVERIFIED"

#: R-002: routes this experiment may fall back to. Empty by default — nothing is
#: configured, therefore every fallback is BLOCKED.
CONFIGURED_ROUTES: set[str] = set()

CANDIDATES: dict[str, dict[str, Any]] = {
    "manga-ocr": {
        "candidate": "manga-ocr",
        "stage": "recognition",
        "metadata_status": "UNVERIFIED",
        "version": f"{UNVERIFIED} — claimed 0.1.16 (not confirmed online)",
        "model_ref": f"{UNVERIFIED} — kha-white/manga-ocr",
        "license": f"{UNVERIFIED} — repository claims Apache-2.0; model-weight terms unchecked",
        "requires": ["manga_ocr", "Pillow", "torch", "transformers"],
        "capability": "Japanese recognition on an existing Region crop; no detector output",
    },
    "paddleocr-korean": {
        "candidate": "PaddleOCR + PP-OCRv5 Korean",
        "stage": "detection+recognition",
        "metadata_status": "UNVERIFIED",
        "version": f"{UNVERIFIED} — claimed PaddleOCR 3.7.0 / korean_PP-OCRv5_mobile_rec",
        "model_ref": f"{UNVERIFIED} — korean_PP-OCRv5_mobile_rec",
        "license": f"{UNVERIFIED} — code claims Apache-2.0; model-weight terms must be checked",
        "requires": ["paddleocr", "paddlepaddle"],
        "capability": "Detection + Korean/English recognition",
    },
    "openai-compatible-vision": {
        "candidate": "Vision model behind an OpenAI-compatible endpoint",
        "stage": "detection+recognition",
        "metadata_status": "UNVERIFIED",
        "version": f"{UNVERIFIED} — candidate family only; no endpoint claimed",
        "model_ref": f"{UNVERIFIED} — operator-supplied model id",
        "license": f"{UNVERIFIED} — depends on the operator's endpoint and model",
        "requires": ["TASK016_OPENAI_BASE_URL or OPENAI_BASE_URL", "TASK016_OPENAI_MODEL or OPENAI_MODEL"],
        "capability": "Vision recognition/detection with a JSON polygon request",
    },
    # ---------------- R-001: detector candidates ----------------
    "detector-dbnet": {
        "candidate": "DBNet (documented as the default detector)",
        "stage": "detection",
        "metadata_status": "UNVERIFIED",
        "version": f"{UNVERIFIED} — documented as 'default' (DBNet ResNet34) with no pinned version",
        "model_ref": f"{UNVERIFIED} — no weight file available in this environment",
        "license": f"{UNVERIFIED} — detector weights not obtained",
        "requires": ["onnxruntime"],
        "capability": "Text detection (polygon/bbox) as an OCR prerequisite",
        "documented_in": "doc/01_FUNCTIONAL_ARCHITECTURE.md:255 — historical reference; detector/registry.py is NOT in this repository",
    },
    "detector-ctd": {
        "candidate": "CTD",
        "stage": "detection",
        "metadata_status": "UNVERIFIED",
        "version": f"{UNVERIFIED} — named in docs, no version pinned",
        "model_ref": f"{UNVERIFIED} — no weight file available in this environment",
        "license": f"{UNVERIFIED} — detector weights not obtained",
        "requires": ["onnxruntime"],
        "capability": "Text detection (polygon/bbox) as an OCR prerequisite",
        "documented_in": "doc/01_FUNCTIONAL_ARCHITECTURE.md:255 / doc/02_TECHNICAL_ARCHITECTURE_.md:24",
    },
    "detector-yolo": {
        "candidate": "YOLO family (yolo / saber_yolo / aux_yolo)",
        "stage": "detection",
        "metadata_status": "UNVERIFIED",
        "version": f"{UNVERIFIED} — names only; the referenced registry is not in this repository",
        "model_ref": f"{UNVERIFIED} — no weight file and no in-repo implementation source",
        "license": f"{UNVERIFIED} — upstream terms unknown; requires a scope decision",
        "requires": ["onnxruntime"],
        "capability": "Text detection (polygon/bbox) as an OCR prerequisite",
        "documented_in": "doc/01_FUNCTIONAL_ARCHITECTURE.md:255 — explicitly '本仓库无此文件'",
    },
}

#: R-001: what evidence each candidate stage can produce in this environment.
VERIFICATION_MATRIX: tuple[dict[str, str], ...] = (
    {
        "stage": "detection",
        "candidates": "detector-dbnet, detector-ctd, detector-yolo",
        "geometric_protocol": "COVERED — tile_polygon_to_global / order_results (model-free)",
        "real_detection_run": "BLOCKED — no detector weights and no onnxruntime in this interpreter",
        "scope_decision_needed": "YOLO family has no in-repo implementation source (detector/registry.py absent)",
    },
    {
        "stage": "recognition",
        "candidates": "manga-ocr",
        "geometric_protocol": "COVERED — map_region_result preserves region_id and page-global coordinates",
        "real_recognition_run": "BLOCKED — dependency and weights unavailable",
        "scope_decision_needed": "none",
    },
    {
        "stage": "detection+recognition",
        "candidates": "paddleocr-korean, openai-compatible-vision",
        "geometric_protocol": "COVERED — same protocol helpers",
        "real_run": "BLOCKED — dependency/weights unavailable; no configured endpoint",
        "scope_decision_needed": "model-weight licence, and endpoint authorization",
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def _package_available(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def _memory_mb() -> float | None:
    """Best-effort current RSS on Windows without adding psutil."""
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    try:
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ok = ctypes.windll.psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(counters), counters.cb
        )
        return round(counters.WorkingSetSize / 1024 / 1024, 2) if ok else None
    except (AttributeError, OSError):
        return None


def _vram_mb() -> float | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        values = [float(line.strip()) for line in result.stdout.splitlines() if line.strip()]
        return max(values) if values else None
    except (FileNotFoundError, subprocess.SubprocessError, ValueError):
        return None


def _base_result(provider: str, sample: dict[str, Any], *, mode: str) -> dict[str, Any]:
    image = ROOT / "samples" / sample["path"]
    return {
        "provider": provider,
        "candidate": CANDIDATES[provider],
        "mode": mode,
        "sample_id": sample["sample_id"],
        "sample_sha256": sample["sha256"],
        "expected_regions": sample["regions"],
        "observed_regions": None,
        # R-004: only a real model run may replace this; a sample hash never may.
        "model_sha256": MODEL_SHA256_UNAVAILABLE,
        "recognition_errors": "NOT_RUN",
        "coordinate_order": "NOT_RUN",
        "fallback": "NOT_RUN",
        "metrics": {
            "latency_ms": None,
            "rss_before_mb": None,
            "rss_after_mb": None,
            "vram_before_mb": None,
            "vram_after_mb": None,
        },
        "image_path": str(image).replace("\\", "/"),
    }


def _blocked(result: dict[str, Any], reason: str) -> dict[str, Any]:
    result.update({"status": "BLOCKED", "reason": reason})
    # R-004: keep the single sentinel; never substitute the sample hash.
    result["model_sha256"] = MODEL_SHA256_UNAVAILABLE
    # R-002: nothing is configured and no route is named, so fallback stays BLOCKED.
    result["fallback"] = "BLOCKED: no explicitly configured and named fallback route"
    return result


def _normalize_json_text(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("provider response contains no JSON object")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("provider response JSON is not an object")
    return value


def _run_manga_ocr(result: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
    if not _package_available("manga_ocr"):
        return _blocked(result, "missing dependency: manga_ocr")
    if len(sample["regions"]) != 1:
        return _blocked(result, "recognition-only route requires one Region crop; detector output unavailable")
    try:
        from PIL import Image
        from manga_ocr import MangaOcr
    except Exception as error:
        return _blocked(result, f"provider import failed: {type(error).__name__}")
    image_path = ROOT / "samples" / sample["path"]
    started = time.perf_counter()
    result["metrics"]["rss_before_mb"] = _memory_mb()
    result["metrics"]["vram_before_mb"] = _vram_mb()
    try:
        with Image.open(image_path) as image:
            polygon = sample["regions"][0]["polygon"]
            box = (
                min(point[0] for point in polygon),
                min(point[1] for point in polygon),
                max(point[0] for point in polygon),
                max(point[1] for point in polygon),
            )
            text = str(MangaOcr()(image.crop(box)))
        result["observed_regions"] = [map_region_result(
            region_id=sample["regions"][0]["region_id"],
            text=text,
            polygon=sample["regions"][0]["polygon"],
            reading_order=0,
        )]
        result["status"] = "PASS"
        result["recognition_errors"] = (
            "NONE" if text == sample["regions"][0]["text"] else "TEXT_MISMATCH"
        )
        result["coordinate_order"] = "REGION_CROP_REFERENCE"
    except Exception as error:
        result = _blocked(result, f"inference failed: {type(error).__name__}: {error}")
        result["status"] = "FAIL"
    result["metrics"]["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    result["metrics"]["rss_after_mb"] = _memory_mb()
    result["metrics"]["vram_after_mb"] = _vram_mb()
    return result


def _as_mapping(value: Any) -> dict[str, Any]:
    if hasattr(value, "json"):
        value = value.json
    if callable(value):
        value = value()
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise ValueError("provider result is not a mapping")
    return value.get("res", value)


def _run_paddle(result: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
    missing = [name for name in ("paddleocr", "paddle") if not _package_available(name)]
    if missing:
        return _blocked(result, "missing dependency: " + ", ".join(missing))
    try:
        from paddleocr import PaddleOCR
    except Exception as error:
        return _blocked(result, f"provider import failed: {type(error).__name__}")
    started = time.perf_counter()
    result["metrics"]["rss_before_mb"] = _memory_mb()
    result["metrics"]["vram_before_mb"] = _vram_mb()
    try:
        ocr = PaddleOCR(
            lang="korean",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
        raw = next(iter(ocr.predict(str(ROOT / "samples" / sample["path"]))))
        data = _as_mapping(raw)
        texts = list(data.get("rec_texts", []))
        polygons = data.get("dt_polys", [])
        if hasattr(polygons, "tolist"):
            polygons = polygons.tolist()
        observed = []
        for index, text in enumerate(texts):
            polygon = polygons[index] if index < len(polygons) else []
            if not polygon:
                continue
            observed.append({
                "region_id": f"unmapped-{index}",
                "text": str(text),
                "polygon": polygon,
                "reading_order": index,
            })
        observed = order_results(observed)
        result["observed_regions"] = observed
        result["status"] = "PASS"
        result["recognition_errors"] = "NOT_AUTOMATICALLY_SCORED"
        result["coordinate_order"] = "PADDLE_PAGE_COORDINATES_ORDER_AS_RETURNED"
    except Exception as error:
        result["status"] = "FAIL"
        result["reason"] = f"inference failed: {type(error).__name__}: {error}"
    result["metrics"]["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    result["metrics"]["rss_after_mb"] = _memory_mb()
    result["metrics"]["vram_after_mb"] = _vram_mb()
    return result


def _run_openai_compatible(result: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
    base_url = os.environ.get("TASK016_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("TASK016_OPENAI_MODEL") or os.environ.get("OPENAI_MODEL")
    if not base_url or not model:
        return _blocked(result, "missing endpoint/model: TASK016_OPENAI_BASE_URL and TASK016_OPENAI_MODEL")
    image_path = ROOT / "samples" / sample["path"]
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    prompt = (
        "Read all visible text. Return JSON only: "
        '{"regions":[{"text":"...","polygon":[[x,y],...],"reading_order":0}]}. '
        "Coordinates must be page-global pixel coordinates. Do not invent RegionIDs."
    )
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + encoded}},
        ]}],
    }
    target = base_url.rstrip("/")
    if not target.endswith("/chat/completions"):
        target += "/chat/completions"
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("TASK016_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    started = time.perf_counter()
    result["metrics"]["rss_before_mb"] = _memory_mb()
    result["metrics"]["vram_before_mb"] = _vram_mb()
    try:
        req = request.Request(target, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with request.urlopen(req, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        value = _normalize_json_text(str(content))
        outputs = value.get("regions")
        if not isinstance(outputs, list):
            raise ValueError("response regions is not a list")
        result["observed_regions"] = [map_region_result(
            region_id=f"unmapped-{index}",
            text=str(item.get("text", "")),
            polygon=item["polygon"],
            reading_order=int(item.get("reading_order", index)),
        ) for index, item in enumerate(outputs)]
        result["status"] = "PASS"
        result["recognition_errors"] = "NOT_AUTOMATICALLY_SCORED"
        result["coordinate_order"] = "MODEL_JSON_PAGE_GLOBAL"
    except Exception as error:
        result["status"] = "FAIL"
        result["reason"] = f"request or schema failed: {type(error).__name__}: {error}"
    result["metrics"]["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    result["metrics"]["rss_after_mb"] = _memory_mb()
    result["metrics"]["vram_after_mb"] = _vram_mb()
    return result


def _run_detector(result: dict[str, Any], sample: dict[str, Any], provider: str) -> dict[str, Any]:
    """R-001: probe a detector candidate and fail explicitly.

    No detector box is ever fabricated: the historical ``detector/registry.py``
    is not part of this repository and no weight file is available here.
    """

    result["metrics"]["rss_before_mb"] = _memory_mb()
    result["metrics"]["vram_before_mb"] = _vram_mb()
    if not _package_available("onnxruntime"):
        return _blocked(
            result,
            "missing dependency: onnxruntime (detector runtime); no weight file present either",
        )
    return _blocked(
        result,
        f"no production detector implementation source for {provider!r}: the documented registry "
        "module is absent from this repository and no weight file was provided; "
        "a scope decision is required before this candidate can run",
    )


def _run_provider(provider: str, sample: dict[str, Any], mode: str) -> dict[str, Any]:
    result = _base_result(provider, sample, mode=mode)
    stage = CANDIDATES[provider]["stage"]
    if mode == "probe-only":
        if provider == "manga-ocr" and not _package_available("manga_ocr"):
            return _blocked(result, "missing dependency: manga_ocr")
        if provider == "paddleocr-korean" and not all(_package_available(name) for name in ("paddleocr", "paddle")):
            return _blocked(result, "missing dependency: paddleocr and/or paddle")
        if provider == "openai-compatible-vision" and not (
            (os.environ.get("TASK016_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL"))
            and (os.environ.get("TASK016_OPENAI_MODEL") or os.environ.get("OPENAI_MODEL"))
        ):
            return _blocked(result, "missing endpoint/model configuration")
        if stage == "detection":
            return _blocked(result, "probe-only: detector runtime/weights unavailable")
        return _blocked(result, "probe-only: real inference intentionally not invoked")
    if provider == "manga-ocr":
        return _run_manga_ocr(result, sample)
    if provider == "paddleocr-korean":
        return _run_paddle(result, sample)
    if provider == "openai-compatible-vision":
        return _run_openai_compatible(result, sample)
    return _run_detector(result, sample, provider)


def run(manifest_path: Path, output_path: Path, providers: list[str], run_models: bool) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mode = "model-run" if run_models else "probe-only"
    records = []
    for provider in providers:
        for sample in manifest["samples"]:
            records.append(_run_provider(provider, sample, mode))
    output = {
        "schema": "task016-experiment-result-v2",
        "manifest_sha256": _sha256(manifest_path),
        "mode": mode,
        "providers": providers,
        "model_sha256_sentinel": MODEL_SHA256_UNAVAILABLE,
        "fallback_configuration": validate_route_configuration(CONFIGURED_ROUTES),
        "verification_matrix": [dict(row) for row in VERIFICATION_MATRIX],
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(json.dumps({"output": str(output_path), "counts": counts}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "samples" / "manifest.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "probe.json")
    parser.add_argument("--provider", choices=[*CANDIDATES, "all"], default="all")
    parser.add_argument("--run-models", action="store_true", help="invoke installed/configured providers; never install/download")
    args = parser.parse_args()
    providers = list(CANDIDATES) if args.provider == "all" else [args.provider]
    run(args.manifest, args.output, providers, args.run_models)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
