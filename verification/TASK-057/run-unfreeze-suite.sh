#!/usr/bin/env bash
# TASK-057 解冻切片全量测试 runner：日志带 shell/venv/env 头 + EXIT（§6.12 口径）
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="/g/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
REPO="$(cd "$DIR/../.." && pwd)"
cd "$REPO"
export PYTHONDONTWRITEBYTECODE=1

for n in 1 2 3; do
  LOG="$DIR/unfreeze-full-suite-run$n.log"
  {
    echo "=== tree:   $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)（TASK-057 解冻切片交付树）"
    echo "=== shell:  Git Bash (MSYS) / win32"
    echo "=== venv:   TASK-012-py312 ($("$PY" --version 2>&1))"
    echo "=== env:    PYTHONDONTWRITEBYTECODE=1, QT_QPA_PLATFORM 未设（产品边界口径）"
    echo "=== date:   $(date '+%Y-%m-%dT%H:%M:%S%z')"
    echo "=== cmd:    $PY -m pytest tests -q -p no:cacheprovider -rs"
    echo "---"
    "$PY" -m pytest tests -q -p no:cacheprovider -rs
    rc=$?
    echo "---"
    echo "EXIT=$rc"
  } > "$LOG"
  echo "run$n: $(grep -E '^[0-9]+ (passed|collected)|passed|failed' "$LOG" | tail -1) EXIT=$(tail -1 "$LOG")"
done
