"""M2-SFX-TRAIN-V2 AC2 训练 V2（A/B 双版）：基座 yolo11s-seg + train-v2 数据集微调。

沿 V1 train_v1.py（experiments/M2-SFX-TRAIN-V1/，只读蓝本）模式复制适配。
口径沿 V1/T0（合同 AC2）：imgsz=1024 / batch=8 / epochs=150 / patience=30 /
seed=20261004 / device=0 / workers=2 / AMP 默认开；数据=train-v2 dataset
（names 双通道校验已由 AC1 守住）。

A 版：基座 = Ultralytics 官方 yolo11s-seg.pt（AGPL，用户许可降权备案覆盖）
  sha256=1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3（先验门）。
B 版：基座 = anonimkaq4/manga-page-element-segmentation 的 yolo11s-seg .pt @1024
  （HF；T0 preflight-report.md:69,129 指路的 manga 域近基座；许可 `other` 未审计——
  仅作替代初始化，类别面 0:frame/1:speech_bubble/2:character 无 sfx，换头 nc=4 由
  ultralytics train() 自动处理并留痕日志；sha 无先验，下载后实测登记）。

失败纪律（沿 V1）：显存 OOM → batch 减半重试一次并登记；依赖缺失 → venv pip
install 并登记。runs 落 training_data/sfx-v1/train-v2/runs/{v2a,v2b}/（repo
gitignored）；本脚本 stdout 即训练全程日志（调用方重定向 verification/
M2-SFX-TRAIN-V2/raw/train-v2{a,b}-log.txt）。末行输出 TRAIN_RESULT_JSON{...}。

用法：
  python train_v2.py --variant a
  python train_v2.py --variant b --base-pt <path.pt> [--base-sha256 <sha>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = REPO_ROOT / "training_data" / "sfx-v1" / "train-v2" / "dataset" / "dataset.yaml"
RUNS_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "train-v2" / "runs"

BASE_A = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/weights/yolo11s-seg.pt")
BASE_A_SHA256 = "1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3"

EPOCHS = 150
PATIENCE = 30
SEED = 20261004
IMGSZ = 1024
BATCH = 8  # OOM 纪律：减半重试一次
WORKERS = 2
DEVICE = 0


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=["a", "b"])
    parser.add_argument("--base-pt", default=None,
                        help="B 版基座 .pt 路径（A 版忽略，用内置官方权重）")
    parser.add_argument("--base-sha256", default=None,
                        help="B 版基座 sha256 先验（可选；不符即 refuse，缺省仅登记实测）")
    args = parser.parse_args()

    if args.variant == "a":
        base_pt, run_name, base_id = BASE_A, "v2a", "official-yolo11s-seg-coco"
        expected_sha: str | None = BASE_A_SHA256
    else:
        if not args.base_pt:
            raise SystemExit("B 版需 --base-pt 指向 anonimkaq4 yolo11s-seg .pt（T0 preflight:69）")
        base_pt = Path(args.base_pt)
        if not base_pt.is_file():
            raise SystemExit(f"B 版基座不在盘: {base_pt}")
        run_name, base_id = "v2b", f"anonimkaq4/manga-page-element-segmentation ({base_pt.name})"
        expected_sha = args.base_sha256

    t0 = time.perf_counter()
    # 基座供应链自检：有先验即断言（不符 refuse，fail-fast）；无先验（B 版下载件）登记实测
    base_digest = sha256_file(base_pt)
    if expected_sha and base_digest != expected_sha:
        raise SystemExit(f"基座 sha256 失配: {base_digest} != {expected_sha}")
    note = "sha256 先验匹配" if expected_sha else "sha256 无先验，下载件实测登记"
    print(f"[train-v2{args.variant}] base ok: {base_pt} sha256={base_digest} "
          f"size={base_pt.stat().st_size} ({note})", flush=True)

    import torch  # noqa: F401  (先确认 CUDA 再进 ultralytics)
    from ultralytics import YOLO

    if not torch.cuda.is_available():
        raise SystemExit("torch.cuda.is_available()=False；AC2 合同要求单 GPU device=0")
    print(f"[train-v2{args.variant}] device: {torch.cuda.get_device_name(0)} "
          f"({torch.cuda.get_device_properties(0).total_memory / 2**20:.0f} MiB)", flush=True)

    def _train(batch: int):
        model = YOLO(str(base_pt))
        kwargs = dict(
            data=str(DATA_YAML),
            epochs=EPOCHS,
            patience=PATIENCE,
            imgsz=IMGSZ,
            batch=batch,
            seed=SEED,
            device=DEVICE,
            workers=WORKERS,
            project=str(RUNS_DIR),
            name=run_name,
            exist_ok=False,
            verbose=True,
        )
        print(f"[train-v2{args.variant}] train kwargs: {json.dumps(kwargs)}", flush=True)
        return model, model.train(**kwargs)

    try:
        model, _ = _train(BATCH)
        batch_used = BATCH
    except Exception as e:  # OOM 纪律：batch 减半重试一次
        msg = f"{type(e).__name__}: {e}"
        print(f"[train-v2{args.variant}] train failed with {msg}", flush=True)
        if "out of memory" not in msg.lower():
            raise
        batch_used = BATCH // 2
        print(f"[train-v2{args.variant}] OOM → batch 减半重试: batch={batch_used}", flush=True)
        stale = RUNS_DIR / run_name
        if stale.exists():
            import shutil
            shutil.rmtree(stale)
        t0 = time.perf_counter()
        model, _ = _train(batch_used)

    train_sec = time.perf_counter() - t0
    run_dir = Path(model.trainer.save_dir)
    csv_path = run_dir / "results.csv"
    best_pt = run_dir / "weights" / "best.pt"
    last_pt = run_dir / "weights" / "last.pt"

    csv_lines = csv_path.read_text(encoding="utf-8").strip().splitlines()
    header = [c.strip() for c in csv_lines[0].split(",")]
    last_row = [c.strip() for c in csv_lines[-1].split(",")]
    last_metrics = dict(zip(header, last_row))

    def fitness(row: dict) -> float:
        try:
            return 0.9 * float(row.get("metrics/mAP50-95(B)", 0)) + 0.1 * float(row.get("metrics/mAP50(B)", 0))
        except ValueError:
            return 0.0

    rows = [dict(zip(header, [c.strip() for c in ln.split(",")])) for ln in csv_lines[1:]]
    best_row = max(rows, key=fitness)

    out = {
        "variant": f"v2{args.variant}",
        "base": base_id,
        "base_sha256": base_digest,
        "run_dir": str(run_dir),
        "batch_used": batch_used,
        "requested_epochs": EPOCHS,
        "patience": PATIENCE,
        "actual_epochs": len(rows),
        "early_stopped": len(rows) < EPOCHS,
        "train_sec": round(train_sec, 1),
        "last_epoch_metrics": last_metrics,
        "best_epoch": best_row.get("epoch"),
        "best_epoch_metrics": best_row,
        "best_pt_sha256": sha256_file(best_pt) if best_pt.is_file() else None,
        "best_pt_size": best_pt.stat().st_size if best_pt.is_file() else None,
        "last_pt_sha256": sha256_file(last_pt) if last_pt.is_file() else None,
    }
    print("TRAIN_RESULT_JSON" + json.dumps(out, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
