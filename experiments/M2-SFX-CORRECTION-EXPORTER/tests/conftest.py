"""pytest 路径装配：实验包不安装进 venv（沿 T1a tests/conftest.py 先例）。

装配四个路径：
- 本实验包父目录（sfx_correction_exporter 可导入）；
- T1a 工具链包目录（sfx_data_infra 可导入——AC6 互操作复用其
  schema/atomicio/dedup/splits/hash，零复制）；
- 仓库根与仓库 src/（生产契约事实只读导入：SFX_CLASS_MAP 出自
  src/infrastructure/providers/detection_sfx.py:137；fixture 库 schema 出自
  src/infrastructure/sqlite/schema.py 的冻结 DDL）。
"""

from __future__ import annotations

import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PKG_DIR.parents[1]
T1A_DIR = REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA"
SRC_DIR = REPO_ROOT / "src"

for p in (str(PKG_DIR), str(T1A_DIR), str(REPO_ROOT), str(SRC_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)
