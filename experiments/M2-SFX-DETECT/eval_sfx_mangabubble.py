"""Run the two ONNX candidates over the primary SFX sample frames (AC3).

Candidates (license-gate findings registered in the eval report):

- ``chiqui7/yolo11-manga-seg`` @7f5f5c04 (HF tag: MIT) — classes
  ``{0: bubble, 1: panel, 2: sfx, 3: text}`` per ONNX metadata; the ONLY
  surveyed candidate with a dedicated SFX class. Ultralytics export
  metadata carries 'AGPL-3.0 License' — internal evaluation only; weight
  redistribution in the product is a user/legal ruling item.
- ``Kiuyha/Manga-Bubble-YOLO`` @fb64650 (HF tag: apache-2.0) — ONNX
  metadata names ``{0: text}`` — SINGLE text class, NO SFX class: the
  "detect-then-tag-SFX" premise fails at the class surface. Evaluated as
  a text-detector reference (does its text class land on SFX pixels?).
  Same Ultralytics AGPL metadata caveat.

Minimal dependency-free inference (onnxruntime + numpy + PIL only; no
ultralytics package): letterbox preprocess per each model's metadata
imgsz, postprocess:
- yolo26n (end2end): output (1, 300, 6) = [x1, y1, x2, y2, score, cls] in
  letterboxed input pixels — map back, no NMS needed.
- yolo11s-seg: output0 (1, 40, N) = [xywh(4), cls(4), mask(32)]^T —
  sigmoid cls scores, conf filter, class-agnostic-free NMS (IoU 0.7),
  xywh -> xyxy, map back. Mask coefficients ignored (detection only).

Harvest threshold 0.25 (same protocol as the ogkalu baseline run);
``conf_ge_primary`` flags the 0.5 cut. Previews overlay: green=chiqui7
sfx-class, orange=chiqui7 text-class, blue=Kiuyha text-class.

Usage (from the worktree root):

  "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
      experiments/M2-SFX-DETECT/eval_sfx_mangabubble.py \
      --verdicts experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json \
      --chiqui7 "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx" \
      --kiuyha "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo26n.onnx" \
      --harvest-threshold 0.25 \
      --preview-dir "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/previews-onnx" \
      --out experiments/M2-SFX-DETECT/onnx-sfx-frames.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HARVEST_DEFAULT = 0.25
PRIMARY_THRESHOLD = 0.5
NMS_IOU = 0.7


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def letterbox(rgb: np.ndarray, size: int):
    """Resize keeping aspect ratio, pad with 114 gray to size x size."""
    h, w = rgb.shape[:2]
    scale = min(size / w, size / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    img = Image.fromarray(rgb).resize((nw, nh), Image.BILINEAR)
    canvas = Image.new("RGB", (size, size), (114, 114, 114))
    canvas.paste(img, (0, 0))
    arr = np.asarray(canvas, dtype=np.float32) / 255.0
    return np.ascontiguousarray(arr.transpose(2, 0, 1)[None]), scale


def map_back(box, scale: float):
    """Letterboxed input pixels -> source pixels."""
    return [
        float(box[0]) / scale,
        float(box[1]) / scale,
        float(box[2]) / scale,
        float(box[3]) / scale,
    ]


def nms(boxes, scores, iou_thr: float):
    order = np.argsort(scores)[::-1]
    keep = []
    for i in order:
        if all(
            _iou(boxes[i], boxes[k]) < iou_thr for k in keep
        ):
            keep.append(int(i))
    return keep


def _iou(a, b) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def run_chiqui7(session, inp, scale: float, conf_thr: float, names: dict):
    out = session.run(None, {"images": inp})[0]  # (1, 40, N)
    preds = out[0].T  # (N, 40)
    boxes_xywh = preds[:, :4]
    cls_scores = preds[:, 4:8]  # already post-sigmoid in this export (verified: raw range 0-0.956)
    cls_ids = cls_scores.argmax(axis=1)
    confs = cls_scores.max(axis=1)
    keep = confs >= conf_thr
    dets = []
    cand = []
    for i in np.where(keep)[0]:
        x, y, w, h = boxes_xywh[i]
        cand.append(([x - w / 2, y - h / 2, x + w / 2, y + h / 2], float(confs[i]), int(cls_ids[i])))
    for i in nms([c[0] for c in cand], np.array([c[1] for c in cand]), NMS_IOU):
        box, conf, cls_id = cand[i]
        dets.append(
            {
                "box_xyxy": [round(v, 1) for v in map_back(box, scale)],
                "conf": round(conf, 4),
                "cls": names[str(cls_id)],
                "conf_ge_primary": conf >= PRIMARY_THRESHOLD,
            }
        )
    return dets


def run_kiuyha(session, inp, scale: float, conf_thr: float, names: dict):
    out = session.run(None, {"images": inp})[0]  # (1, 300, 6), end2end
    dets = []
    for row in out[0]:
        x1, y1, x2, y2, conf, cls_id = row.tolist()
        if conf < conf_thr:
            continue
        dets.append(
            {
                "box_xyxy": [round(v, 1) for v in map_back([x1, y1, x2, y2], scale)],
                "conf": round(float(conf), 4),
                "cls": names[str(int(cls_id))],
                "conf_ge_primary": conf >= PRIMARY_THRESHOLD,
            }
        )
    return dets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verdicts", type=Path, required=True)
    parser.add_argument("--chiqui7", type=Path, required=True)
    parser.add_argument("--kiuyha", type=Path, required=True)
    parser.add_argument("--harvest-threshold", type=float, default=HARVEST_DEFAULT)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    import onnxruntime as ort

    sess_c = ort.InferenceSession(str(args.chiqui7), providers=["CPUExecutionProvider"])
    sess_k = ort.InferenceSession(str(args.kiuyha), providers=["CPUExecutionProvider"])
    names_c = {"0": "bubble", "1": "panel", "2": "sfx", "3": "text"}
    names_k = {"0": "text"}

    meta_c = sess_c.get_modelmeta().custom_metadata_map
    meta_k = sess_k.get_modelmeta().custom_metadata_map

    def parse_names(meta_names: str) -> dict:
        # R8 (DSH r1): the hardcoded class maps below are ASSERTED against
        # the ONNX metadata 'names' string so a silent class-surface drift
        # fails loudly instead of mislabeling detections.
        out = {}
        for part in meta_names.strip("{}").split(","):
            k, v = part.split(":")
            out[k.strip().strip("'")] = v.strip().strip("'")
        return out

    names_meta_c = parse_names(meta_c["names"])
    names_meta_k = parse_names(meta_k["names"])
    assert names_meta_c == names_c, f"chiqui7 names drift: {names_meta_c} != {names_c}"
    assert names_meta_k == names_k, f"kiuyha names drift: {names_meta_k} != {names_k}"

    payload_verdicts = json.loads(args.verdicts.read_text(encoding="utf-8"))
    frames = payload_verdicts["primary_frames"]
    regions = sorted({(r["case_id"], r["region_index"], None) for r in frames})
    # resolve image path from ogkalu detections payload (same regions)
    det_payload = json.loads(
        (args.verdicts.parent / "ogkalu-sfx-frames.json").read_text(encoding="utf-8")
    )
    img_by_region = {
        (r["case_id"], r["region_index"]): r["image"] for r in det_payload["regions"].values()
    }

    args.preview_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for case_id, region_index, _ in regions:
        image_path = img_by_region[(case_id, region_index)]
        img = Image.open(image_path).convert("RGB")
        rgb = np.asarray(img, dtype=np.uint8)
        inp_c, scale_c = letterbox(rgb, 1024)
        inp_k, scale_k = letterbox(rgb, 1280)
        dets_c = run_chiqui7(sess_c, inp_c, scale_c, args.harvest_threshold, names_c)
        dets_k = run_kiuyha(sess_k, inp_k, scale_k, args.harvest_threshold, names_k)
        key = f"{case_id}_R{region_index:03d}"
        results[key] = {
            "case_id": case_id,
            "region_index": region_index,
            "image": image_path,
            "chiqui7_yolo11s_seg": {
                "weights_sha256": sha256_file(args.chiqui7),
                "hf_revision": "7f5f5c0464f2eeb57282f16da760eb8828a8716a",
                "hf_license_tag": "mit",
                "onnx_metadata_names": meta_c["names"],
                "onnx_metadata_license": meta_c["license"],
                "onnx_metadata_imgsz": meta_c.get("imgsz"),
                "input_shape": list(inp_c.shape),
                "detections": dets_c,
            },
            "kiuyha_manga_bubble_yolo": {
                "weights_sha256": sha256_file(args.kiuyha),
                "hf_revision": "fb646500455e8a8a3a807fd27b855c8e4fc63766",
                "hf_license_tag": "apache-2.0",
                "onnx_metadata_names": meta_k["names"],
                "onnx_metadata_license": meta_k["license"],
                "onnx_metadata_imgsz": meta_k.get("imgsz"),
                "input_shape": list(inp_k.shape),
                "detections": dets_k,
            },
        }

        canvas = img.copy()
        draw = ImageDraw.Draw(canvas)
        for x in range(0, img.width, 100):
            draw.line([(x, 0), (x, img.height)], fill=(160, 160, 160), width=1)
            draw.text((x + 2, 2), str(x), fill=(60, 60, 60))
        for y in range(0, img.height, 100):
            draw.line([(0, y), (img.width, y)], fill=(160, 160, 160), width=1)
            draw.text((2, y + 2), str(y), fill=(60, 60, 60))
        for d in dets_c:
            color = (0, 170, 0) if d["cls"] == "sfx" else (255, 150, 0)
            x0, y0, x1, y1 = d["box_xyxy"]
            draw.rectangle([x0, y0, x1, y1], outline=color, width=2)
            draw.text((x0 + 2, max(0, y0 - 12)), f"C {d['conf']:.2f} {d['cls']}", fill=color)
        for d in dets_k:
            x0, y0, x1, y1 = d["box_xyxy"]
            draw.rectangle([x0, y0, x1, y1], outline=(30, 90, 220), width=2)
            draw.text((x0 + 2, max(0, y1 + 2)), f"K {d['conf']:.2f} {d['cls']}", fill=(30, 90, 220))
        canvas.save(args.preview_dir / f"onnx__{key}.png", format="PNG")

    payload = {
        "schema": "m2-sfx-detect/onnx-sfx-frames@1",
        "task": "M2-SFX-DETECT-EVAL",
        "harvest_threshold": args.harvest_threshold,
        "primary_threshold": PRIMARY_THRESHOLD,
        "nms_iou": NMS_IOU,
        "inference_note": (
            "onnxruntime CPU, letterbox per metadata imgsz (chiqui7=1024, "
            "kiuyha=1280; recorded per-region as onnx_metadata_imgsz + "
            "input_shape); no ultralytics package; chiqui7 output0 class "
            "scores are post-sigmoid in this export (verified empirically, "
            "no activation applied); detection-only (mask coefficients "
            "ignored); preview colors: green=chiqui7 sfx, orange=chiqui7 "
            "text/bubble/panel, blue=kiuyha text. PREPROCESSING "
            "DEVIATIONS vs the Ultralytics pretrained pipeline (R8 "
            "disclosure): letterbox pads top-left instead of centered; "
            "PIL BILINEAR instead of cv2 INTER_LINEAR; NMS is "
            "class-agnostic IoU 0.7 instead of Ultralytics default "
            "class-aware; coordinate mapping itself is self-consistent "
            "(top-left pad <-> divide by scale)"
        ),
        "license_gate_findings": {
            "chiqui7": {
                "hf_license_tag": "mit",
                "onnx_metadata_license": meta_c["license"],
                "names": meta_c["names"],
                "risk": (
                    "Ultralytics weights-license claim (AGPL-3.0 metadata) "
                    "vs HF MIT tag conflict; internal evaluation only, "
                    "production bundling = user/legal ruling item"
                ),
            },
            "kiuyha": {
                "hf_license_tag": "apache-2.0",
                "onnx_metadata_license": meta_k["license"],
                "names": meta_k["names"],
                "risk": (
                    "single 'text' class — NO SFX class (premise fails); "
                    "Ultralytics AGPL metadata vs apache-2.0 tag conflict; "
                    "manga109-s conduction satisfiable (attribution)"
                ),
            },
        },
        "n_regions": len(results),
        "regions": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    n_c = sum(
        1 for r in results.values() for d in r["chiqui7_yolo11s_seg"]["detections"] if d["cls"] == "sfx"
    )
    n_k = sum(len(r["kiuyha_manga_bubble_yolo"]["detections"]) for r in results.values())
    print(
        f"onnx eval done: regions={len(results)} chiqui7_sfx_dets={n_c} "
        f"kiuyha_text_dets={n_k} -> {args.out}"
    )
    print(f"previews -> {args.preview_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
