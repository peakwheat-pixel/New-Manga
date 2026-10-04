"""subcommands-r3-run.log 中 bypass 断言 OK 的驱动脚本（r2 新-9：断言可核）。

用法：python _bypass_asserts_r3.py <副本 data_root>
在临时副本上跑过 summary/dedup/split 后执行，校验：
  - split 后 lock 含 challenge_single_bucket（lock 形状不漂移）
  - summary 重算摘要保留 dedup/train_builder 证据（不降级）
  - 摘要字体为基名（无路径分隔符）
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
c = json.loads((root / "manifest.full.json").read_text(encoding="utf-8"))
assert "challenge_single_bucket" in c["lock"], "split 后 lock 缺 challenge_single_bucket (r2 新-6)"
s = json.loads((root / "summary.bypass.json").read_text(encoding="utf-8"))
assert s["dedup"]["exact_pairs"] == 0 and "perceptual_pairs" in s["dedup"]
assert s["train_builder"]["excluded_negative_ids"], "summary 重算后必须保留排除负样本证据 (r2 新-1)"
assert all("/" not in f and "\\" not in f for f in s["synthetic_poc"]["fonts"]), "字体基名 (r2 新-2)"
print("bypass assertions OK")
