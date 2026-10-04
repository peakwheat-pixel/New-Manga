"""M2-SFX-TRAIN-V1 AC3：best.pt → ONNX 导出 + 生产序列冒烟 + BJ17 真实推理演示（零 src）。

沿 T0 export_smoke.py（experiments/M2-SFX-FINETUNE-PREFLIGHT/scripts/export_smoke.py，
只读蓝本）模式复制适配。链路：

  1. AC2 产物 best.pt（train_v1/runs/train_v1/weights/best.pt，epoch 86）
     → YOLO.export(format="onnx", imgsz=1024) → 移入
     training_data/sfx-v1/train-v1/weights/best.onnx（ask 指定产物路径）；
  2. SHA 门先证在位：直接以生产 _build_engine 加载导出物，期待 ProviderError
     （sha 不匹配 pin=d87389af… —— 供应链门对任何外来权重生效）；
  3. 测试进程内把 detection_sfx.SFX_WEIGHTS_SHA256 重指向导出物实际 sha
     （src 零改动零落盘，仅运行时模块常量重指；重指后 _build_engine 其余全链——
     onnxruntime session、metadata names 类面断言（R8）、imgsz 列表解析（DSH r1 R4）
     ——按生产代码原样执行）；
  4. SfxDetectionProvider.detect 在合成 manga 页双档 conf（0.5 生产冻结+0.01 低门）
     结构断言 + (1,40,N) 输出张量探针；
  5. BJ17 页真实推理演示（vol05_p0167.png 2946×4167，conf 0.5/0.2 两档原始检出）
     → raw/bj17-demo.json。

EXIT=0 判定：上述每步断言全过。零 src；生产 pin 不改（重指仅进程内，退出即失效）。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BEST_PT = REPO / "training_data" / "sfx-v1" / "train-v1" / "runs" / "train_v1" / "weights" / "best.pt"
BEST_ONNX = REPO / "training_data" / "sfx-v1" / "train-v1" / "weights" / "best.onnx"
RAW_OUT = REPO / "verification" / "M2-SFX-TRAIN-V1" / "raw"
BJ17_PAGE = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/test_assets/comic_golden_suite"
    r"/日漫_JA/01_black_jack_official/vol05/pages/vol05_p0167.png"
)

STEPS: list[dict] = []


def log(step: str, **fields) -> None:
    entry = {"step": step, "t": round(time.perf_counter(), 3), **fields}
    STEPS.append(entry)
    print("[smoke-v1] " + json.dumps(entry, ensure_ascii=False), flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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

    assert BEST_PT.is_file(), f"missing AC2 artifact: {BEST_PT}"
    log("input", best_pt=str(BEST_PT), best_pt_sha256=sha256_file(BEST_PT))

    # -- 1. export -----------------------------------------------------------
    from ultralytics import YOLO

    model = YOLO(str(BEST_PT))
    log("export.start", imgsz=1024, format="onnx")
    exported = Path(model.export(format="onnx", imgsz=1024, device="cpu"))
    BEST_ONNX.parent.mkdir(parents=True, exist_ok=True)
    if BEST_ONNX.exists():
        BEST_ONNX.unlink()
    if exported.resolve() != BEST_ONNX.resolve():
        shutil.move(str(exported), BEST_ONNX)
    onnx_sha = sha256_file(BEST_ONNX)
    log("export.done", onnx=str(BEST_ONNX), size_bytes=BEST_ONNX.stat().st_size, sha256=onnx_sha)

    # -- 2. SHA gate must fire ----------------------------------------------
    gate_fired = False
    try:
        _build_engine(BEST_ONNX)
    except ProviderError as error:
        gate_fired = True
        log("sha_gate.fired", error_code=error.error_code, detail=str(error)[:160])
    assert gate_fired, "SHA gate did NOT fire on a foreign export — supply-chain gate broken"
    log("sha_gate.ok", production_pin=SFX_WEIGHTS_SHA256[:12], export_actual=onnx_sha[:12])

    # -- 3. in-process pin retarget (src untouched) + full production chain --
    dsfx.SFX_WEIGHTS_SHA256 = onnx_sha
    session, imgsz, imgsz_source, imgsz_raw = _build_engine(BEST_ONNX)
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

    # -- 4. provider.detect on a synthetic manga page (structure probe) ------
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
        page_id="export-smoke-v1",
        image_bytes=rgb.tobytes(),
        width=page_w,
        height=page_h,
    )
    results = {}
    for conf in (0.5, 0.01):
        provider = SfxDetectionProvider(weights_path=BEST_ONNX, conf_threshold=conf)
        result = provider.detect(request)
        options = dict(result.options)
        results[str(conf)] = {
            "candidates": len(result.candidates),
            "provider_id": result.provider_id,
            "coordinate_space": result.coordinate_space,
            "imgsz": options.get("imgsz"),
            "imgsz_source": options.get("imgsz_source"),
            "class_filter": options.get("class_filter"),
        }
        log(f"detect.conf_{conf}", **results[str(conf)])
        assert results[str(conf)]["imgsz_source"] == "metadata_parsed"

    inp = numpy.zeros((1, 3, 1024, 1024), dtype=numpy.float32)
    out = session.run(None, {"images": inp})[0]
    log("output_tensor", shape=list(out.shape), expect="1x40xN (4+4cls+32mask)")
    assert out.shape[1] == 40, f"output channel surface drifted: {out.shape}"

    # -- 5. BJ17 real-page inference demo ------------------------------------
    assert BJ17_PAGE.is_file(), f"BJ17 page missing: {BJ17_PAGE}"
    page = Image.open(BJ17_PAGE).convert("RGB")
    pw, ph = page.size
    bj17_rgb = numpy.asarray(page, dtype=numpy.uint8)
    bj17_request = DetectionRequest(
        page_id="BJ17-vol05_p0167",
        image_bytes=bj17_rgb.tobytes(),
        width=pw,
        height=ph,
    )
    bj17_demo = {"page": str(BJ17_PAGE), "width": pw, "height": ph, "sha256": sha256_file(BJ17_PAGE), "inference": {}}
    for conf in (0.5, 0.2):
        provider = SfxDetectionProvider(weights_path=BEST_ONNX, conf_threshold=conf)
        result = provider.detect(bj17_request)
        boxes = [
            {"xyxy": [c.polygon[0][0], c.polygon[0][1], c.polygon[2][0], c.polygon[2][1]],
             "conf": round(c.confidence, 4), "provider_label": c.provider_label}
            for c in result.candidates
        ]
        bj17_demo["inference"][str(conf)] = {
            "conf_threshold": conf, "n_candidates": len(boxes), "boxes": boxes,
            "elapsed_ms": result.elapsed_ms,
            "imgsz_source": dict(result.options).get("imgsz_source"),
        }
        log("bj17_demo", conf=conf, n_candidates=len(boxes))

    RAW_OUT.mkdir(parents=True, exist_ok=True)
    (RAW_OUT / "bj17-demo.json").write_text(
        json.dumps(bj17_demo, ensure_ascii=False, indent=1), encoding="utf-8")
    report = {
        "best_pt": str(BEST_PT),
        "onnx": str(BEST_ONNX),
        "onnx_sha256": onnx_sha,
        "steps": STEPS,
        "exit": 0,
    }
    (RAW_OUT / "export-smoke-v1.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[smoke-v1] EXIT=0 — full chain: best.pt -> onnx -> production sequence OK; BJ17 demo written", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
