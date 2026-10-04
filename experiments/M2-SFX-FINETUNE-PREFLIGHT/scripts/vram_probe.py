"""M2-SFX-FINETUNE-PREFLIGHT AC3：显存摸底（yolo11s-seg @imgsz=1024，batch 2/4/8 各 20 iter）。

设计（AC1-③ 联动）：
- 数据 = Ultralytics 官方 coco8-seg（8 train + 4 val，自动下载），标签类 id %4 重映射为
  chiqui7 四类名 {0:bubble, 1:panel, 2:sfx, 3:text} —— 冒烟只测显存/速度/导出链兼容性，
  不产生任何精度结论；
- 四类名数据集使训练产物 best.pt 天然带 nc=4 head（官方 COCO 80 类基座换头微调），
  供 AC4 导出链直接对齐生产 SFX_CLASS_MAP 断言；
- 每档 batch 通过复制 coco8 训练图（b2=5x/40 张、b4=10x/80 张、b8=20x/160 张）
  使 epoch 恰为 20 iter；
- 峰值显存 = torch.cuda.max_memory_reserved/allocated（训练前 reset）；
  it/s = on_train_batch_end 回调逐 iter 时间戳（排除首个 warmup iter 后取中位）。

零 src；运行于 task-envs/M2-SFX-FINETUNE-gpu-py312（外部树），产物不进 git。
"""

from __future__ import annotations

import json
import os
import shutil
import statistics
import time
from pathlib import Path

os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7890")
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7890")

ENVS = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312")
WEIGHTS = ENVS / "weights" / "yolo11s-seg.pt"
RUNS = ENVS / "runs" / "vram-probe"
DATA_ROOT = ENVS / "datasets"
RAW_OUT = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode"
    "/verification/M2-SFX-FINETUNE-PREFLIGHT/raw"
)

CLASS_NAMES = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
BATCH_REPEAT = {2: 20, 4: 40, 8: 80}  # coco8-seg train=4 张 → repeat 后每 epoch 恰 20 iter
IMGSZ = 1024


def ensure_coco8_seg() -> Path:
    """下载（走代理）并解压 Ultralytics 官方 coco8-seg（8 train + 4 val）。"""
    import urllib.request
    import zipfile

    src = DATA_ROOT / "coco8-seg"
    if (src / "images" / "train").is_dir():
        return src
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    zip_path = DATA_ROOT / "coco8-seg.zip"
    if not zip_path.is_file():
        proxy = urllib.request.ProxyHandler(
            {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        )
        opener = urllib.request.build_opener(proxy)
        print("[data] downloading coco8-seg.zip ...")
        with opener.open(
            "https://ultralytics.com/assets/coco8-seg.zip", timeout=180
        ) as response, zip_path.open("wb") as out:
            out.write(response.read())
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(DATA_ROOT)
    assert (src / "images" / "train").is_dir(), f"coco8-seg extract failed: {src}"
    return src


def build_split_dataset(batch: int) -> Path:
    """把 coco8-seg 训练集复制 REPEAT 份并重映射标签为四类，返回 dataset.yaml 路径。"""
    src = ensure_coco8_seg()
    repeat = BATCH_REPEAT[batch]
    dst = DATA_ROOT / f"sfx-smoke-4cls-b{batch}"
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "images" / "train").mkdir(parents=True)
    (dst / "labels" / "train").mkdir(parents=True)
    # train 与 val 统一走复制+重映射（val=False 不评估，但 ultralytics 仍会构建
    # val cache——无效标签会在 init 期炸 RuntimeError）
    count = 0
    for split in ("train", "val"):
        (dst / "images" / split).mkdir(parents=True, exist_ok=True)
        (dst / "labels" / split).mkdir(parents=True, exist_ok=True)
        for img in sorted((src / "images" / split).iterdir()):
            stem = img.stem
            lbl = src / "labels" / split / f"{stem}.txt"
            lines = [
                " ".join(part for part in line.split())
                for line in lbl.read_text().splitlines()
                if line.strip()
            ]
            for k in range(repeat):
                shutil.copy(img, dst / "images" / split / f"{stem}_r{k}{img.suffix}")
                remapped = []
                for line in lines:
                    parts = line.split()
                    parts[0] = str(int(parts[0]) % 4)  # 80 类 → chiqui7 四类 id
                    remapped.append(" ".join(parts))
                (dst / "labels" / split / f"{stem}_r{k}.txt").write_text(
                    "\n".join(remapped), encoding="utf-8"
                )
                if split == "train":
                    count += 1
    names_block = "\n".join(f"  {i}: {n}" for i, n in CLASS_NAMES.items())
    (dst / "dataset.yaml").write_text(
        f"path: {dst.as_posix()}\ntrain: images/train\nval: images/val\n\n"
        f"names:\n{names_block}\n",
        encoding="utf-8",
    )
    print(f"[data] b{batch}: {count} train images (repeat x{repeat}), labels remapped to 4 classes")
    return dst / "dataset.yaml"


def probe_batch(batch: int) -> dict:
    import torch
    from ultralytics import YOLO

    yaml_path = build_split_dataset(batch)

    iter_ends: list[float] = []

    def on_train_batch_end(trainer) -> None:
        iter_ends.append(time.perf_counter())

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    model = YOLO(str(WEIGHTS))
    model.add_callback("on_train_batch_end", on_train_batch_end)
    t0 = time.perf_counter()
    model.train(
        data=str(yaml_path),
        epochs=1,
        imgsz=IMGSZ,
        batch=batch,
        device=0,
        workers=2,
        val=False,
        plots=False,
        exist_ok=True,
        project=str(RUNS),
        name=f"b{batch}",
        verbose=True,
    )
    wall = time.perf_counter() - t0

    peak_reserved = torch.cuda.max_memory_reserved() / 2**20
    peak_allocated = torch.cuda.max_memory_allocated() / 2**20
    deltas = [
        iter_ends[i] - iter_ends[i - 1] for i in range(1, len(iter_ends))
    ]  # 排除首个 iter（含 cudnn/cublas warmup）
    med = statistics.median(deltas) if deltas else float("nan")
    result = {
        "batch": batch,
        "imgsz": IMGSZ,
        "iters_recorded": len(iter_ends),
        "per_iter_median_s": round(med, 4),
        "it_s": round(1.0 / med, 2) if deltas else None,
        "per_iter_all_median_s": round(
            statistics.median(
                [iter_ends[i] - iter_ends[i - 1] for i in range(1, len(iter_ends))]
            )
            if len(iter_ends) > 1
            else float("nan"),
            4,
        ),
        "peak_vram_reserved_MiB": round(peak_reserved, 1),
        "peak_vram_allocated_MiB": round(peak_allocated, 1),
        "epoch_wall_s": round(wall, 1),
        "amp": True,
    }
    print("[probe] " + json.dumps(result))
    return result


def main() -> None:
    import torch

    assert torch.cuda.is_available(), "CUDA 不可用：本脚本必须在 GPU venv 运行"
    print(
        "[env] torch",
        torch.__version__,
        "cuda",
        torch.version.cuda,
        torch.cuda.get_device_name(0),
        "vram_total_MiB",
        round(torch.cuda.get_device_properties(0).total_memory / 2**20, 1),
    )
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    all_results = []
    for batch in (2, 4, 8):
        result = probe_batch(batch)
        all_results.append(result)
        (RAW_OUT / f"vram_probe_b{batch}.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    (RAW_OUT / "vram_probe_summary.json").write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[done] summary ->", RAW_OUT / "vram_probe_summary.json")


if __name__ == "__main__":
    main()
