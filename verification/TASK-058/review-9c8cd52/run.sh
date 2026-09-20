#!/usr/bin/env bash
# Qoder post-hoc reviewer runner (TASK-058). Every log carries the
# tree/shell/venv/env header and a trailing EXIT= line (协议 §6 第 12 条).
#
# Usage: run.sh <label> <tree> <cmd> [args...]
set -u
LAB="$1"; TREE="$2"; shift 2
OUT="G:/CODEX/New Manga.worktrees/TASK-058-qoder-review/verification/TASK-058/review-9c8cd52/${LAB}.log"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONIOENCODING=utf-8
unset QT_QPA_PLATFORM
{
  echo "=== label:  $LAB"
  echo "=== tree:   $TREE @ $(git -C "$TREE" rev-parse --short HEAD) [$(git -C "$TREE" rev-parse --abbrev-ref HEAD)]"
  echo "=== shell:  Git Bash (MSYS) / win32"
  echo "=== venv:   G:/CODEX/New Manga.task-envs/TASK-012-py312 (Python 3.12.3 CPython AMD64)"
  echo "=== env:    PYTHONDONTWRITEBYTECODE=1, PYTHONIOENCODING=utf-8, QT_QPA_PLATFORM unset"
  echo "=== date:   $(date -Iseconds)"
  echo "=== cmd:    $*"
  echo "---"
} > "$OUT"
( cd "$TREE" && "$@" ) >> "$OUT" 2>&1
EC=$?
echo "EXIT=$EC" >> "$OUT"
echo "EXIT=$EC -> $OUT"
tail -3 "$OUT"
