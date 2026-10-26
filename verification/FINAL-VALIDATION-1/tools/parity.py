"""CORE-SLIM-2 parity harness: torch reference vs the ONNX Runtime chains.

Runs the SAME production adapters on the same 10 INFER-BASELINE-EP-1 fixture
pages and compares:

  detection  torch ``MangaDetectionProvider`` (transformers RT-DETR-v2, CPU)
             vs ``MangaDetectionOnnxProvider`` (shipped fixed-shape ONNX graph)
             -> per-page candidate counts, pre-merge text-box counts and IoU
             matching of the emitted RegionCandidate polygons (that is the
             product contract, not the raw model tensors).

  OCR        torch encoder/decoder greedy loop (the INFER baseline's verified
             reference, kha-white/manga-ocr-base weights) vs the product
             ``MangaOcrOnnxProvider`` engine on the SAME page image
             -> exact text equality per page (both sides apply the tokenizer's
             skip_special_tokens semantics).

Runs in the dedicated build venv (needs torch + transformers for the
reference side, onnxruntime for the product side):

  G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe parity.py
"""

from __future__ import annotations

import io
import json
import os
import statistics
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

FIXTURES = Path(
    os.environ.get(
        "CORE_SLIM_FIXTURES",
        r"G:\CODEX\New Manga.workspace\task-envs\INFER-BASELINE-EP-1\fixtures\pages10",
    )
)
ONNX_MODELS = Path(
    os.environ.get(
        "CORE_SLIM_MODELS",
        r"G:\CODEX\New Manga.workspace\task-envs\CORE-SLIM-2\models",
    )
)
TORCH_DETECTOR = Path(
    os.environ.get(
        "CORE_SLIM_TORCH_DETECTOR",
        r"G:\CODEX\New Manga.workspace\worktrees\CORE-SLIM-1\apps\desktop\src-tauri\target\core-sidecar\core-sidecar\models\detector\ogkalu-comic-text-and-bubble-detector",
    )
)
TORCH_OCR = Path(
    os.environ.get(
        "CORE_SLIM_TORCH_OCR",
        r"G:\CODEX\New Manga.workspace\task-envs\INFER-BASELINE-EP-1\models\manga-ocr-base",
    )
)
ONNX_OCR = ONNX_MODELS / "ocr" / "manga-ocr-onnx"


def _iou(a, b) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def _poly_bbox(polygon):
    xs = [x for x, _ in polygon]
    ys = [y for _, y in polygon]
    return (min(xs), min(ys), max(xs), max(ys))


def _match(ref_boxes, got_boxes, threshold: float = 0.5) -> dict:
    used: set[int] = set()
    matched = 0
    ious: list[float] = []
    for ref in ref_boxes:
        best, best_iou = None, 0.0
        for index, got in enumerate(got_boxes):
            if index in used:
                continue
            overlap = _iou(ref, got)
            if overlap > best_iou:
                best, best_iou = index, overlap
        if best is not None and best_iou >= threshold:
            used.add(best)
            matched += 1
            ious.append(best_iou)
    recall = matched / len(ref_boxes) if ref_boxes else None
    precision = matched / len(got_boxes) if got_boxes else None
    return {
        "refCount": len(ref_boxes),
        "gotCount": len(got_boxes),
        "matched": matched,
        "recall": recall,
        "precision": precision,
        "meanIoU": round(statistics.mean(ious), 4) if ious else None,
    }


class _MangaOcrTorchReference:
    """INFER-BASELINE-EP-1's verified greedy-loop reference implementation."""

    def __init__(self, weights_dir: Path, vocab_path: Path, device: str = "cpu") -> None:
        import numpy as np
        import torch
        from transformers import VisionEncoderDecoderModel

        self.np = np
        self.torch = torch
        self.model = VisionEncoderDecoderModel.from_pretrained(
            str(weights_dir), local_files_only=True
        )
        self.model.eval()
        self.vocab = vocab_path.read_text(encoding="utf-8").splitlines()
        self.start_id, self.eos_id, self.max_len = 2, 3, 24
        self.special = {"[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"}

    def __call__(self, image) -> str:
        np, torch = self.np, self.torch
        from PIL import Image as _PILImage

        resampling = getattr(_PILImage, "Resampling", _PILImage)
        resized = image.convert("RGB").resize((224, 224), resampling.BILINEAR)
        array = np.asarray(resized, dtype=np.float32) / 255.0
        array = (array - 0.5) / 0.5
        x = torch.from_numpy(np.ascontiguousarray(array.transpose(2, 0, 1)[None]))
        with torch.no_grad():
            hidden = self.model.encoder(pixel_values=x).last_hidden_state
            ids = [self.start_id]
            for _ in range(self.max_len):
                inp = torch.tensor([ids], dtype=torch.long)
                logits = self.model.decoder(
                    input_ids=inp, encoder_hidden_states=hidden
                ).logits
                nxt = int(logits[0, -1].argmax().item())
                if nxt == self.eos_id:
                    break
                ids.append(nxt)
        return "".join(
            self.vocab[token]
            for token in ids[1:]
            if 0 <= token < len(self.vocab) and self.vocab[token] not in self.special
        )


def main() -> int:
    from PIL import Image

    from infrastructure.providers.detection_manga import MangaDetectionProvider
    from infrastructure.providers.detection_manga_onnx import MangaDetectionOnnxProvider
    from infrastructure.providers.ocr_manga_onnx import MangaOcrOnnxProvider
    from ports.detection.ports import DetectionRequest
    from ports.ocr.ports import OcrRequest, SCRIPT_JAPANESE

    pages = sorted(FIXTURES.glob("*.jpg"))
    if not pages:
        print(json.dumps({"error": "no fixtures"}))
        return 2

    torch_detector = MangaDetectionProvider(weights_dir=TORCH_DETECTOR, device="cpu")
    onnx_detector_cpu = MangaDetectionOnnxProvider(
        weights_path=ONNX_MODELS / "detector" / "rtdetr-v2-fixed.onnx", device="cpu"
    )
    onnx_detector_dml = MangaDetectionOnnxProvider(
        weights_path=ONNX_MODELS / "detector" / "rtdetr-v2-fixed.onnx", device="dml"
    )
    torch_ocr = _MangaOcrTorchReference(TORCH_OCR, ONNX_OCR / "vocab.txt")
    onnx_ocr = MangaOcrOnnxProvider(weights_dir=ONNX_OCR)

    report: dict = {"pages": [], "summary": {}}
    det_torch_ms: list[float] = []
    det_onnx_cpu_ms: list[float] = []
    det_onnx_dml_ms: list[float] = []
    ocr_torch_ms: list[float] = []
    ocr_onnx_ms: list[float] = []

    for page in pages:
        image = Image.open(page).convert("RGB")
        payload = image.tobytes()
        width, height = image.size
        request = DetectionRequest(
            page_id=page.stem, image_bytes=payload, width=width, height=height
        )

        start = time.perf_counter()
        reference = torch_detector.detect(request)
        det_torch_ms.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter()
        cpu = onnx_detector_cpu.detect(request)
        det_onnx_cpu_ms.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter()
        dml = onnx_detector_dml.detect(request)
        det_onnx_dml_ms.append((time.perf_counter() - start) * 1000)

        ref_boxes = [_poly_bbox(candidate.polygon) for candidate in reference.candidates]
        cpu_boxes = [_poly_bbox(candidate.polygon) for candidate in cpu.candidates]
        dml_boxes = [_poly_bbox(candidate.polygon) for candidate in dml.candidates]

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        ocr_request = OcrRequest(
            page_id=page.stem,
            region_id="r1",
            image_bytes=buffer.getvalue(),
            script=SCRIPT_JAPANESE,
        )
        start = time.perf_counter()
        ref_text = torch_ocr(image)
        ocr_torch_ms.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter()
        onnx_text = onnx_ocr.recognize(ocr_request).text
        ocr_onnx_ms.append((time.perf_counter() - start) * 1000)

        report["pages"].append(
            {
                "page": page.name,
                "size": [width, height],
                "detection": {
                    "torch": {
                        "candidates": len(ref_boxes),
                        "preMerge": dict(reference.options).get("text_boxes_pre_merge"),
                    },
                    "onnxCpu": {
                        "candidates": len(cpu_boxes),
                        "preMerge": dict(cpu.options).get("text_boxes_pre_merge"),
                        "ep": dict(cpu.options).get("inference_ep"),
                    },
                    "onnxDml": {
                        "candidates": len(dml_boxes),
                        "preMerge": dict(dml.options).get("text_boxes_pre_merge"),
                        "ep": dict(dml.options).get("inference_ep"),
                    },
                    "onnxCpuVsTorch": _match(ref_boxes, cpu_boxes),
                    "onnxDmlVsTorch": _match(ref_boxes, dml_boxes),
                },
                "ocr": {
                    "torchText": ref_text,
                    "onnxText": onnx_text,
                    "exactMatch": ref_text == onnx_text,
                },
            }
        )

    def median(values: list[float]) -> float:
        return round(statistics.median(values), 2)

    pages_report = report["pages"]
    report["summary"] = {
        "pages": len(pages_report),
        "detection": {
            "torchMedianMs": median(det_torch_ms),
            "onnxCpuMedianMs": median(det_onnx_cpu_ms),
            "onnxDmlMedianMs": median(det_onnx_dml_ms),
            "candidateCountsEqualCpu": all(
                page["detection"]["torch"]["candidates"]
                == page["detection"]["onnxCpu"]["candidates"]
                for page in pages_report
            ),
            "preMergeCountsEqualCpu": all(
                page["detection"]["torch"]["preMerge"]
                == page["detection"]["onnxCpu"]["preMerge"]
                for page in pages_report
            ),
            "exactCandidateCountMatchDml": all(
                page["detection"]["torch"]["candidates"]
                == page["detection"]["onnxDml"]["candidates"]
                for page in pages_report
            ),
            "totalTorchCandidates": sum(
                page["detection"]["torch"]["candidates"] for page in pages_report
            ),
            "totalOnnxCandidates": sum(
                page["detection"]["onnxCpu"]["candidates"] for page in pages_report
            ),
            "meanRecallCpu": round(
                statistics.mean(
                    page["detection"]["onnxCpuVsTorch"]["recall"] or 0.0
                    for page in pages_report
                ),
                4,
            ),
            "meanIoUCpu": round(
                statistics.mean(
                    page["detection"]["onnxCpuVsTorch"]["meanIoU"] or 0.0
                    for page in pages_report
                ),
                4,
            ),
        },
        "ocr": {
            "torchMedianMs": median(ocr_torch_ms),
            "onnxMedianMs": median(ocr_onnx_ms),
            "exactMatchPages": sum(1 for page in pages_report if page["ocr"]["exactMatch"]),
            "pages": len(pages_report),
        },
    }
    output = Path(os.environ.get("CORE_SLIM_PARITY_OUT", str(REPO / "verification" / "CORE-SLIM-2" / "parity.json")))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print("wrote", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
