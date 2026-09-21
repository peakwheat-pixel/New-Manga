#!/usr/bin/env bash
# 修前判别探针 runner：日志带 shell/venv/env 头 + EXIT（§6.12 口径）
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="/g/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
REPO="$(cd "$DIR/../.." && pwd)"   # verification/TASK-057/pre-fix-probes -> repo root
cd "$REPO"

head_line() {
  cat <<HDR
=== tree:   $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)（修前形态：本切片代码改动前）
=== shell:  Git Bash (MSYS) / win32
=== venv:   TASK-012-py312 ($("$PY" --version 2>&1))
=== env:    PYTHONDONTWRITEBYTECODE=1, QT_QPA_PLATFORM 未设（产品边界口径）
=== date:   $(date '+%Y-%m-%dT%H:%M:%S%z')
HDR
}

run_one() {
  local probe="$1" log="$2"; shift 2
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

export PYTHONDONTWRITEBYTECODE=1
run_one probe_q008_truthy.py pre-fix-q008-truthy-run2.log \
  "$PY" -m pytest "$DIR/probe_q008_truthy.py" -q -s -p no:cacheprovider
run_one probe_r004_latch.py pre-fix-r004-latch-run1.log \
  "$PY" "$DIR/probe_r004_latch.py"
