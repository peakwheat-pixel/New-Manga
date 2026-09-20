#!/usr/bin/env bash
# Qoder non-author re-review runner (TASK-057 round 2).
# Usage: run.sh <label> <tree> <cmd...>   -> writes verification/.../review-29546f7/<label>.log
set -u
LAB="$1"; TREE="$2"; shift 2
OUT="G:/CODEX/New Manga.worktrees/TASK-057-qoder-review/verification/TASK-057/review-29546f7/${LAB}.log"
PY="/g/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONIOENCODING=utf-8
unset QT_QPA_PLATFORM
{
  echo "=== label:  $LAB"
  echo "=== tree:   $TREE @ $(git -C "$TREE" rev-parse --short HEAD) [$(git -C "$TREE" rev-parse --abbrev-ref HEAD)]"
  echo "=== shell:  Git Bash (MSYS) / win32"
  echo "=== venv:   TASK-012-py312 (Python 3.12.3 CPython AMD64)"
  echo "=== env:    PYTHONDONTWRITEBYTECODE=1, QT_QPA_PLATFORM unset, PYTHONIOENCODING=utf-8"
  echo "=== date:   $(date -Iseconds)"
  echo "=== cmd:    $*"
  echo "---"
} > "$OUT"
( cd "$TREE" && "$@" ) >> "$OUT" 2>&1
EC=$?
echo "EXIT=$EC" >> "$OUT"
echo "EXIT=$EC  (log: $OUT)"
tail -6 "$OUT"
