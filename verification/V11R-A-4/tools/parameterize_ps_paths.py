"""V11R-A-4: parameterize hardcoded workspace/repo absolute paths in PowerShell scripts.

Replaces literals of the form
    'G:/CODEX/New Manga.workspace/<rel>'      (workspace, Windows or forward slashes)
    'G:/CODEX/New Manga/<rel>'                (repository)
with an expression that resolves in this order:
    1. NEWMANGA_WORKSPACE_ROOT / NEWMANGA_REPO_ROOT (explicit CI / operator override)
    2. a workspace sibling derived from $PSScriptRoot (<repo>/../<repo-name>.workspace)

The expression is valid in `param(...)` default values and in ordinary assignments. It never
depends on this machine's checkout location, so a clean clone works without edits.

Run: python verification/V11R-A-4/tools/parameterize_ps_paths.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[3]
TARGETS = [
    "apps/desktop-avalonia/scripts",
    "packaging",
]

# depth = number of parents from the script directory to the repository root
DEPTHS = {
    "apps/desktop-avalonia/scripts": 3,
    "packaging": 2,
}

WORKSPACE_RE = re.compile(r"""['"](?P<path>G:[\\/]CODEX[\\/]New Manga\.workspace[\\/](?P<rel>[^'"]+))['"]""")
REPO_RE = re.compile(r"""['"](?P<path>G:[\\/]CODEX[\\/]New Manga(?![.\\/]workspace)[\\/](?P<rel>[^'"]+))['"]""")
# Historical typo: some scripts pointed at "<repo>.task-envs/..." which never existed; the real
# operator tree is <workspace>/task-envs/.... Map it to the workspace expression (never a machine path).
BUILD_PYTHON_RE = re.compile(r"""['"](?P<path>G:[\\/]CODEX[\\/]New Manga\.task-envs[\\/](?P<rel>[^'"]*python\.exe))['"]""")
STALE_TASKENV_RE = re.compile(r"""['"](?P<path>G:[\\/]CODEX[\\/]New Manga\.task-envs[\\/](?P<rel>[^'"]+))['"]""")


def repo_expr(depth: int) -> str:
    expr = "$PSScriptRoot"
    for _ in range(depth):
        expr = f"(Split-Path {expr} -Parent)"
    return expr


def workspace_expr(depth: int, relative: str) -> str:
    repo = repo_expr(depth)
    rel = relative.replace("\\", "/")
    return (
        "$( $v11rRepo = " + repo + "; "
        "if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT '" + rel + "' } "
        "else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) '" + rel + "' } )"
    )


def repo_path_expr(depth: int, relative: str) -> str:
    repo = repo_expr(depth)
    rel = relative.replace("\\", "/")
    return (
        "$( if ($env:NEWMANGA_REPO_ROOT) { Join-Path $env:NEWMANGA_REPO_ROOT '" + rel + "' } "
        "else { Join-Path " + repo + " '" + rel + "' } )"
    )


def depth_for(path: Path) -> int | None:
    relative = path.relative_to(WORKTREE).as_posix()
    for prefix, depth in DEPTHS.items():
        if relative.startswith(prefix + "/"):
            return depth
    return None


def transform(text: str, depth: int) -> tuple[str, list[str]]:
    changes: list[str] = []

    def workspace_repl(match: re.Match) -> str:
        rel = match.group("rel")
        changes.append(f"workspace {match.group('path')} -> env/derived")
        return workspace_expr(depth, rel)

    def repo_repl(match: re.Match) -> str:
        rel = match.group("rel")
        changes.append(f"repo {match.group('path')} -> env/derived")
        return repo_path_expr(depth, rel)

    def build_python_repl(match: re.Match) -> str:
        changes.append(f"build-python {match.group('path')} -> env/python")
        return "$( if ($env:NEWMANGA_BUILD_PYTHON) { $env:NEWMANGA_BUILD_PYTHON } else { 'python' } )"

    def stale_taskenv_repl(match: re.Match) -> str:
        rel = match.group("rel")
        changes.append(f"stale-task-env {match.group('path')} -> workspace/{rel}")
        return workspace_expr(depth, rel)

    text = BUILD_PYTHON_RE.sub(build_python_repl, text)
    text = STALE_TASKENV_RE.sub(stale_taskenv_repl, text)
    text = WORKSPACE_RE.sub(workspace_repl, text)
    text = REPO_RE.sub(repo_repl, text)
    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total = 0
    for target in TARGETS:
        directory = WORKTREE / target
        for path in sorted(directory.rglob("*.ps1")):
            depth = depth_for(path)
            if depth is None:
                continue
            original = path.read_text(encoding="utf-8")
            updated, changes = transform(original, depth)
            if not changes:
                continue
            total += len(changes)
            print(f"{path.relative_to(WORKTREE).as_posix()}: {len(changes)} replacement(s)")
            for change in changes:
                print(f"  - {change}")
            if not args.dry_run:
                path.write_text(updated, encoding="utf-8")
    print(f"total replacements: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

