"""M2-SFX-TRAIN-V1 AC2 训练 V1：官方 yolo11s-seg.pt 基座 + train-v1 数据集微调。

参数沿 T0 preflight 实测口径（verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md）：
- 基座 = Ultralytics 官方 yolo11s-seg.pt（AGPL，用户许可降权备案覆盖；T0 §2 A′ 路线）
  sha256=1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3（20,669,228 B）
- imgsz=1024（T0 §1.4 生产口径兼容实测）、batch=8（T0 §4.2 推荐：peak 7488MiB、吞吐 67 img/s）、
  workers=2（T0 摸底口径）、AMP 默认开
- epochs=150 + patience=30 早停（T2 合同 AC2）、seed=20261004 冻结（沿 R1/R2/AC1）、device=0 单 GPU、单次运行
- names 顺序逐字=SFX_CLASS_MAP 已由 AC1 dataset.yaml 双通道校验守住（T0 §2 硬约束）

失败纪律（T2 合同）：显存 OOM → batch 减半重试一次并登记；依赖缺失 → venv pip install 并登记。

run 产物落 training_data/sfx-v1/train-v1/runs/（repo gitignored）；本脚本 stdout 即训练
全程日志（由调用方重定向 verification/M2-SFX-TRAIN-V1/raw/train-log.txt）。
末行输出 TRAIN_RESULT_JSON{...} 结构化摘要行。
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = REPO_ROOT / "training_data" / "sfx-v1" / "train-v1" / "dataset" / "dataset.yaml"
RUNS_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "train-v1" / "runs"
BASE_PT = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/weights/yolo11s-seg.pt")
BASE_SHA256 = "1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3"

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
    t0 = time.perf_counter()
    # 基座供应链自检（T0 §8 登记 sha；不符即 refuse，fail-fast）
    base_digest = sha256_file(BASE_PT)
    if base_digest != BASE_SHA256:
        raise SystemExit(f"基座 sha256 失配: {base_digest} != {BASE_SHA256}")
    print(f"[train-v1] base ok: {BASE_PT} sha256={base_digest} size={BASE_PT.stat().st_size}", flush=True)

    import torch  # noqa: F401  (先确认 CUDA 再进 ultralytics)
    from ultralytics import YOLO

    if not torch.cuda.is_available():
        raise SystemExit("torch.cuda.is_available()=False；AC2 合同要求单 GPU device=0")
    print(f"[train-v1] device: {torch.cuda.get_device_name(0)} "
          f"({torch.cuda.get_device_properties(0).total_memory / 2**20:.0f} MiB)", flush=True)

    model = YOLO(str(BASE_PT))
    kwargs = dict(
        data=str(DATA_YAML),
        epochs=EPOCHS,
        patience=PATIENCE,
        imgsz=IMGSZ,
        batch=BATCH,
        seed=SEED,
        device=DEVICE,
        workers=WORKERS,
        project=str(RUNS_DIR),
        name="train_v1",
        exist_ok=False,
        verbose=True,
    )
    print(f"[train-v1] train kwargs: {json.dumps(kwargs)}", flush=True)
    try:
        results = model.train(**kwargs)
        batch_used = BATCH
    except Exception as e:  # OOM 纪律：batch 减半重试一次
        msg = f"{type(e).__name__}: {e}"
        print(f"[train-v1] train failed with {msg}", flush=True)
        if "out of memory" not in msg.lower():
            raise
        batch_used = BATCH // 2
        print(f"[train-v1] OOM → batch 减半重试: batch={batch_used}", flush=True)
        RUNS_DIR_exists = RUNS_DIR / "train_v1"
        if RUNS_DIR_exists.exists():
            import shutil
            shutil.rmtree(RUNS_DIR_exists)
        model = YOLO(str(BASE_PT))
        t0 = time.perf_counter()
        results = model.train(**{**kwargs, "batch": batch_used})

    train_sec = time.perf_counter() - t0
    run_dir = Path(model.trainer.save_dir)
    csv_path = run_dir / "results.csv"
    best_pt = run_dir / "weights" / "best.pt"
    last_pt = run_dir / "weights" / "last.pt"

    csv_lines = csv_path.read_text(encoding="utf-8").strip().splitlines()
    header = [c.strip() for c in csv_lines[0].split(",")]
    last_row = [c.strip() for c in csv_lines[-1].split(",")]
    last_metrics = dict(zip(header, last_row))
    # best epoch = fitness 最高行（ultralytics results.csv 按列对齐）
    def fitness(row: dict) -> float:
        try:
            return 0.9 * float(row.get("metrics/mAP50-95(B)", 0)) + 0.1 * float(row.get("metrics/mAP50(B)", 0))
        except ValueError:
            return 0.0
    rows = [dict(zip(header, [c.strip() for c in ln.split(",")])) for ln in csv_lines[1:]]
    best_row = max(rows, key=fitness)

    out = {
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
        "base_sha256": base_digest,
    }
    print("TRAIN_RESULT_JSON" + json.dumps(out, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
