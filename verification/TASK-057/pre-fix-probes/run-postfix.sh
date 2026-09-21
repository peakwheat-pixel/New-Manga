#!/usr/bin/env bash
# 修后判别探针复跑：同一探针在修后树的分支翻转 = 判别力成立（§6.12）
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="/g/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
REPO="$(cd "$DIR/../.." && pwd)"
cd "$REPO"
export PYTHONDONTWRITEBYTECODE=1

head_line() {
  cat <<HDR
=== tree:   $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)（修后形态：本切片代码改动已落地）
=== shell:  Git Bash (MSYS) / win32
=== venv:   TASK-012-py312 ($("$PY" --version 2>&1))
=== env:    PYTHONDONTWRITEBYTECODE=1, QT_QPA_PLATFORM 未设（产品边界口径）
=== date:   $(date '+%Y-%m-%dT%H:%M:%S%z')
HDR
}

run_one() {
  local log="$1"; shift
  {
    head_line
    echo "=== cmd:    $*"
    echo "---"
    "$@" 2>&1
    local rc=$?
    echo "---"
    echo "EXIT=$rc"
  } > "$DIR/$log"
  echo "$log: EXIT=$(tail -1 "$DIR/$log" | cut -d= -f2)"
}

run_one post-fix-q008-truthy-run1.log \
  "$PY" -m pytest "$DIR/probe_q008_truthy.py" -q -s -p no:cacheprovider
run_one post-fix-r004-latch-run1.log \
  "$PY" "$DIR/probe_r004_latch.py"
