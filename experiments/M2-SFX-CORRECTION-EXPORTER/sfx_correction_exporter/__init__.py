"""sfx_correction_exporter：纠错样本导出器（M2-SFX-CORRECTION-EXPORTER / T5c）。

revision 链类型纠错识别（AC1）→ T1a schema 样本（AC2）→ 资格判定（AC3）→
manifest+YOLO seg 双形态导出（AC4）。零 src 修改；SQLite 只读；依赖零新增
（stdlib + 既有 PIL + 复用 T1a sfx_data_infra）。
"""

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.1.0"

TASK_ID = "M2-SFX-CORRECTION-EXPORTER"

# 路径装配（实验包不安装进 venv；与 tests/conftest.py 同规则，CLI 直跑也需要）。
# _PKG_DIR = <root>/experiments/M2-SFX-CORRECTION-EXPORTER/sfx_correction_exporter
#            → parents[2] = 仓库根
_PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = _PKG_DIR.parents[2]
T1A_DIR = REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA"
SRC_DIR = REPO_ROOT / "src"

for _p in (str(_PKG_DIR.parent), str(T1A_DIR), str(REPO_ROOT), str(SRC_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
