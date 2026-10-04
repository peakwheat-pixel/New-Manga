"""pytest 路径装配：把包父目录加进 sys.path（实验包不安装进 venv；仓库根直跑必需）。"""

import sys
from pathlib import Path

PKG_PARENT = Path(__file__).resolve().parents[1]
if str(PKG_PARENT) not in sys.path:
    sys.path.insert(0, str(PKG_PARENT))
