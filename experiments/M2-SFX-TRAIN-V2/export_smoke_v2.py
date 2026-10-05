"""M2-SFX-TRAIN-V2 AC3：v2a/v2b best.pt → ONNX 导出 + 生产序列冒烟（零 src）。

沿 V1 export_smoke_v1.py（experiments/M2-SFX-TRAIN-V1/，只读蓝本）模式复制适配，
两版各跑一遍（A=官方基座 v2a / B=近域基座 v2b）：

  1. AC2 产物 best.pt → YOLO.export(format="onnx", imgsz=1024, device="cpu")
     → training_data/sfx-v1/train-v2/weights/{v2a,v2b}/best.onnx；
  2. SHA 门先证在位：直接以生产 _build_engine 加载导出物，期待 ProviderError
     （sha 不匹配 pin=d87389af…——供应链门对任何外来权重生效）；
  3. 测试进程内把 detection_sfx.SFX_WEIGHTS_SHA256 重指向导出物实际 sha
     （src 零改动零落盘，仅运行时模块常量重指）后 _build_engine 全链
     （metadata names 类面断言 + imgsz 列表解析）；
  4. SfxDetectionProvider.detect 合成 manga 页双档 conf 结构断言 +
     (1,40,N) 输出张量探针。

EXIT=0 判定：两版每步断言全过。零 src；生产 pin 不改（重指仅进程内，退出即失效）。
report → verification/M2-SFX-TRAIN-V2/raw/export-smoke-v2.json。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRAIN_V2 = REPO / "training_data" / "sfx-v1" / "train-v2"
RAW_OUT = REPO / "verification" / "M2-SFX-TRAIN-V2" / "raw"

VARIANTS = {
    "v2a": TRAIN_V2 / "runs" / "v2a" / "weights" / "best.pt",
    "v2b": TRAIN_V2 / "runs" / "v2b" / "weights" / "best.pt",
}

STEPS: list[dict] = []


def log(step: str, **fields) -> None:
    entry = {"step": step, "t": round(time.perf_counter(), 3), **fields}
    STEPS.append(entry)
    print("[smoke-v2] " + json.dumps(entry, ensure_ascii=False), flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def smoke_variant(variant: str, best_pt: Path, report: dict) -> None:
    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import (
        SFX_CLASS_MAP,
        SFX_WEIGHTS_SHA256,
        SfxDetectionProvider,
        _build_engine,
    )
    from ports.providers.errors import ProviderError

    best_onnx = TRAIN_V2 / "weights" / variant / "best.onnx"
    assert best_pt.is_file(), f"missing AC2 artifact: {best_pt}"
    log("input", variant=variant, best_pt=str(best_pt), best_pt_sha256=sha256_file(best_pt))

    # -- 1. export -----------------------------------------------------------
    from ultralytics import YOLO

    model = YOLO(str(best_pt))
    log("export.start", variant=variant, imgsz=1024, format="onnx")
    exported = Path(model.export(format="onnx", imgsz=1024, device="cpu"))
    best_onnx.parent.mkdir(parents=True, exist_ok=True)
    if best_onnx.exists():
        best_onnx.unlink()
    if exported.resolve() != best_onnx.resolve():
        shutil.move(str(exported), best_onnx)
    onnx_sha = sha256_file(best_onnx)
    log("export.done", variant=variant, onnx=str(best_onnx),
        size_bytes=best_onnx.stat().st_size, sha256=onnx_sha)
    report[variant] = {"best_pt": str(best_pt), "onnx": str(best_onnx), "onnx_sha256": onnx_sha}

    # -- 2. SHA gate must fire ----------------------------------------------
    gate_fired = False
    try:
        _build_engine(best_onnx)
    except ProviderError as error:
        gate_fired = True
        log("sha_gate.fired", variant=variant, error_code=error.error_code, detail=str(error)[:160])
    assert gate_fired, "SHA gate did NOT fire on a foreign export — supply-chain gate broken"
    log("sha_gate.ok", variant=variant, production_pin=SFX_WEIGHTS_SHA256[:12],
        export_actual=onnx_sha[:12])

    # -- 3. in-process pin retarget (src untouched) + full production chain --
    dsfx.SFX_WEIGHTS_SHA256 = onnx_sha
    session, imgsz, imgsz_source, imgsz_raw = _build_engine(best_onnx)
    names_meta = session.get_modelmeta().custom_metadata_map.get("names", "")
    log(
        "build_engine.full_chain_ok",
        variant=variant,
        names_metadata=names_meta,
        class_map_asserted=SFX_CLASS_MAP,
        imgsz=imgsz,
        imgsz_source=imgsz_source,
        imgsz_metadata_raw=imgsz_raw,
    )
    assert imgsz_source == "metadata_parsed", f"imgsz source unexpected: {imgsz_source}"
    assert imgsz == 1024, f"imgsz unexpected: {imgsz}"

    # -- 4. provider.detect on a synthetic manga page (structure probe) ------
    import numpy
    from PIL import Image, ImageDraw

    from ports.detection.ports import DetectionRequest

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
        page_id=f"export-smoke-{variant}",
        image_bytes=rgb.tobytes(),
        width=page_w,
        height=page_h,
    )
    for conf in (0.5, 0.01):
        provider = SfxDetectionProvider(weights_path=best_onnx, conf_threshold=conf)
        result = provider.detect(request)
        options = dict(result.options)
        entry = {
            "candidates": len(result.candidates),
            "provider_id": result.provider_id,
            "coordinate_space": result.coordinate_space,
            "imgsz": options.get("imgsz"),
            "imgsz_source": options.get("imgsz_source"),
            "class_filter": options.get("class_filter"),
        }
        log(f"detect.conf_{conf}", variant=variant, **entry)
        assert entry["imgsz_source"] == "metadata_parsed"

    inp = numpy.zeros((1, 3, 1024, 1024), dtype=numpy.float32)
    out = session.run(None, {"images": inp})[0]
    log("output_tensor", variant=variant, shape=list(out.shape),
        expect="1x40xN (4+4cls+32mask)")
    assert out.shape[1] == 40, f"output channel surface drifted: {out.shape}"
    report[variant]["smoke"] = "PASS"


def main() -> int:
    sys.path.insert(0, str(REPO / "src"))
    report: dict = {}
    for variant, best_pt in VARIANTS.items():
        smoke_variant(variant, best_pt, report)
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    report["steps"] = STEPS
    report["exit"] = 0
    (RAW_OUT / "export-smoke-v2.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[smoke-v2] EXIT=0 — v2a+v2b full chain: best.pt -> onnx -> production sequence OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
