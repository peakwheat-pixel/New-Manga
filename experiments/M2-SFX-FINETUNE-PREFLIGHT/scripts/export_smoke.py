"""M2-SFX-FINETUNE-PREFLIGHT AC4：训练格式 → ONNX 导出 → 生产推理序列全链冒烟。

链路（对照 src/infrastructure/providers/detection_sfx.py 生产序列）：
  1. AC3 摸底产物 best.pt（官方 yolo11s-seg.pt 基座 + 四类冒烟数据换头微调）
     → YOLO.export(format="onnx", imgsz=1024)；
  2. SHA-256 门验证：直接以生产 _build_engine 加载导出物，期待 ProviderError
     （sha 不匹配 pin —— 证明供应链门在位且对任何外来权重生效）；
  3. 测试进程内把 SFX_WEIGHTS_SHA256 重指向导出物实际 sha（**src 零改动**，
     仅运行时模块常量重指；重指后 _build_engine 的其余全链——onnxruntime
     session 构建、metadata names 类面断言（R8）、imgsz metadata 列表解析
     （DSH r1 R4）——按生产代码原样执行）；
  4. SfxDetectionProvider.detect 在程序合成 manga 页上跑两档 conf
     （0.5 生产默认 + 0.01 低门），检查 DetectionResult 结构、
     imgsz_source=metadata_parsed、输出张量形状 (1, 40, N) 与生产解析链。

EXIT=0 判定：上述每步断言全过。零 src；不产生精度结论。
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode")
ENVS = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312")
BEST_PT = ENVS / "runs" / "vram-probe" / "b2" / "weights" / "best.pt"
EXPORT_DIR = ENVS / "runs" / "export-smoke"
RAW_OUT = REPO / "verification" / "M2-SFX-FINETUNE-PREFLIGHT" / "raw"

STEPS: list[dict] = []


def log(step: str, **fields) -> None:
    entry = {"step": step, "t": round(time.perf_counter(), 3), **fields}
    STEPS.append(entry)
    print("[smoke] " + json.dumps(entry, ensure_ascii=False))


def main() -> int:
    sys.path.insert(0, str(REPO / "src"))
    import numpy
    from PIL import Image, ImageDraw

    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import (
        SFX_CLASS_MAP,
        SFX_WEIGHTS_SHA256,
        SfxDetectionProvider,
        _build_engine,
    )
    from ports.detection.ports import DetectionRequest
    from ports.providers.errors import ProviderError

    assert BEST_PT.is_file(), f"missing AC3 artifact: {BEST_PT}"
    log("input", best_pt=str(BEST_PT))

    # -- 1. export -----------------------------------------------------------
    from ultralytics import YOLO

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(BEST_PT))
    log("export.start", imgsz=1024, format="onnx")
    onnx_path = Path(model.export(format="onnx", imgsz=1024))
    onnx_sha = hashlib.sha256(onnx_path.read_bytes()).hexdigest()
    log(
        "export.done",
        onnx=str(onnx_path),
        size_bytes=onnx_path.stat().st_size,
        sha256=onnx_sha,
    )

    # -- 2. SHA gate must fire ----------------------------------------------
    gate_fired = False
    try:
        _build_engine(onnx_path)
    except ProviderError as error:
        gate_fired = True
        log("sha_gate.fired", error_code=error.error_code, detail=str(error)[:200])
    assert gate_fired, "SHA gate did NOT fire on a foreign export — supply-chain gate broken"
    log("sha_gate.ok", pinned=SFX_WEIGHTS_SHA256[:12], actual=onnx_sha[:12])

    # -- 3. in-process pin retarget (src untouched) + full production chain --
    dsfx.SFX_WEIGHTS_SHA256 = onnx_sha
    session, imgsz, imgsz_source, imgsz_raw = _build_engine(onnx_path)
    names_meta = session.get_modelmeta().custom_metadata_map.get("names", "")
    log(
        "build_engine.full_chain_ok",
        names_metadata=names_meta,
        class_map_asserted=SFX_CLASS_MAP,
        imgsz=imgsz,
        imgsz_source=imgsz_source,
        imgsz_metadata_raw=imgsz_raw,
    )
    assert imgsz_source == "metadata_parsed", f"imgsz source unexpected: {imgsz_source}"
    assert imgsz == 1024, f"imgsz unexpected: {imgsz}"

    # -- 4. provider.detect on a synthetic manga page ------------------------
    page_w, page_h = 1024, 1536
    image = Image.new("RGB", (page_w, page_h), (250, 250, 250))
    draw = ImageDraw.Draw(image)
    draw.line([(page_w // 2, 0), (page_w // 2, page_h)], fill=(0, 0, 0), width=6)
    draw.line([(0, page_h // 3), (page_w, page_h // 3)], fill=(0, 0, 0), width=6)
    for cx, cy, rx, ry in [(256, 200, 150, 100), (760, 700, 170, 120)]:
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(0, 0, 0), width=5)
    draw.polygon([(100, 1200), (200, 1100), (320, 1180), (260, 1300)], fill=(20, 20, 20))
    rgb = numpy.asarray(image, dtype=numpy.uint8)
    request = DetectionRequest(
        page_id="export-smoke",
        image_bytes=rgb.tobytes(),
        width=page_w,
        height=page_h,
    )

    results = {}
    for conf in (0.5, 0.01):
        provider = SfxDetectionProvider(weights_path=onnx_path, conf_threshold=conf)
        started = time.perf_counter()
        result = provider.detect(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        options = dict(result.options)
        results[str(conf)] = {
            "candidates": len(result.candidates),
            "elapsed_ms": elapsed_ms,
            "provider_id": result.provider_id,
            "coordinate_space": result.coordinate_space,
            "imgsz": options.get("imgsz"),
            "imgsz_source": options.get("imgsz_source"),
            "arch": options.get("arch"),
            "class_filter": options.get("class_filter"),
            "first_candidate": (
                {
                    "polygon": result.candidates[0].polygon,
                    "confidence": result.candidates[0].confidence,
                    "provider_label": result.candidates[0].provider_label,
                }
                if result.candidates
                else None
            ),
        }
        log(f"detect.conf_{conf}", **results[str(conf)])

    # output tensor shape probe (the (1, 40, N) production assumption)
    inp = numpy.zeros((1, 3, 1024, 1024), dtype=numpy.float32)
    out = session.run(None, {"images": inp})[0]
    log("output_tensor", shape=list(out.shape), expect="1x40xN (4+4cls+32mask)")
    assert out.shape[1] == 40, f"output channel surface drifted: {out.shape}"

    assert results["0.5"]["imgsz_source"] == "metadata_parsed"
    assert results["0.01"]["imgsz_source"] == "metadata_parsed"

    report = {
        "best_pt": str(BEST_PT),
        "onnx": str(onnx_path),
        "onnx_sha256": onnx_sha,
        "steps": STEPS,
        "exit": 0,
    }
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    (RAW_OUT / "export_smoke.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[smoke] EXIT=0 — full chain: .pt -> onnx -> production sequence OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
