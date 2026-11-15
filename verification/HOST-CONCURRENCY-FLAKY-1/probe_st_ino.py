"""验证 FILE_IDENTITY_CHANGED 的 mask 缺口假设：
在 Windows 上取多个文件的 st_ino，看是否 > 2^53（_FILE_MASK = (1<<53)-1）。
同时打印 mask 前后的值，证明高 11 位是否真的被丢弃。
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

FILE_MASK = (1 << 53) - 1
VOLUME_MASK = 0xFFFFFFFF

print(f"_FILE_MASK   = {FILE_MASK}  (2^53-1 = {2**53-1})")
print(f"_VOLUME_MASK = 0x{VOLUME_MASK:X}\n")

# 准备一组真实存在的文件：本次测试用的 alpha.png 的临时副本 + 本进程产生的文件
samples: list[Path] = []

alpha = Path(r"G:\CODEX\New Manga\verification\CORE-SLIM-1\ac1\fixtures\alpha.png")
if alpha.exists():
    samples.append(alpha)

# 模拟 GrantIssuerTests 的夹具目录（同样的 %TEMP% + Guid 命名）
tmp = Path(tempfile.gettempdir())
probe_dir = tmp / ("grant-fixtures-probe-" + os.urandom(5).hex())
probe_dir.mkdir(parents=True, exist_ok=True)
payload = alpha.read_bytes() if alpha.exists() else b"\x89PNG\r\n\x1a\n" + b"\0" * 60
for i in range(6):
    p = probe_dir / f"page-{i+1:02d}.png"
    p.write_bytes(payload)
    samples.append(p)

print(f"{'path':<44} {'st_ino':>22} {'> 2^53?':>8} {'masked':>22} {'丢位?':>6}")
print("-" * 110)

overflow_count = 0
for p in samples:
    st = p.stat()
    ino = st.st_ino
    masked = ino & FILE_MASK
    over = ino > FILE_MASK
    if over:
        overflow_count += 1
    print(
        f"{p.name:<44} {ino:>22} {('YES' if over else 'no'):>8} "
        f"{masked:>22} {('YES' if ino != masked else 'no'):>6}"
    )

print()
print(f"样本总数 {len(samples)}，其中 st_ino > _FILE_MASK 的：{overflow_count}")
print()
if overflow_count:
    print("=> 假设成立：st_ino 确实超过 53 位，mask 会改变数值。")
    print("   Host 侧若按完整 64 位写入 grant，而 Python 侧比较前 mask，就会不等。")
else:
    print("=> 假设不成立（在本次样本上）：所有 st_ino 都 <= 2^53，mask 不改变数值。")
    print("   说明 FILE_IDENTITY_CHANGED 另有原因，需换方向继续查。")

# 同时打印 volume serial，确认 32 位截断是否也有影响
print("\nvolume serial (st_dev):")
for p in samples[:3]:
    st = p.stat()
    print(f"  {p.name}: st_dev={st.st_dev}  0x{st.st_dev & VOLUME_MASK:X}  "
          f"(mask 改变={st.st_dev != (st.st_dev & VOLUME_MASK)})")

# 清理探针目录
try:
    for f in probe_dir.iterdir():
        f.unlink()
    probe_dir.rmdir()
    print(f"\n已清理探针目录 {probe_dir}")
except OSError as exc:
    print(f"\n清理失败（不影响结论）: {exc}")
