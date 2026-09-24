"""M2-D1 audit probe: import-surface probe for the Python Core trees.

READ-ONLY probe. It imports modules from src/domain, src/ports and
src/application to determine, at runtime, whether the Core import surface
requires PySide6/Qt. It never touches the real user data root: the caller
sets NEWMANGA_DATA_ROOT/LOCALAPPDATA to an isolated temporary directory and
runs this with ``python -B`` so no ``__pycache__`` is written into src/.

Usage (from the M2-D1 worktree root):

    python -B verification/M2-D1/probes/core_import_probe.py

Output: one line per module, then a summary. Exit code is 0 when the probe
itself completed; the verdict is in the printed summary, not the exit code.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import traceback
from pathlib import Path

TREES = ("domain", "ports", "application")

#: Extra trees probed only when named on the command line (e.g. infrastructure,
#: bootstrap). They are not part of the "Core" verdict but the same probe
#: records their import-time Qt blocking.
EXTRA_TREES = ("infrastructure", "bootstrap")


def module_names(src_root: Path, tree: str) -> list[str]:
    names: list[str] = []
    for path in sorted((src_root / tree).rglob("*.py")):
        rel = path.relative_to(src_root).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        names.append(".".join(parts))
    return names


def main() -> int:
    # <worktree>/verification/M2-D1/probes/<this file> -> parents[3] is the root
    src_root = Path(__file__).resolve().parents[3] / "src"
    requested = tuple(sys.argv[1:]) or TREES
    unknown = [t for t in requested if not (src_root / t).is_dir()]
    if unknown:
        print(f"probe_error=unknown_tree:{unknown}")
        return 2
    print(f"probe=core_import_probe")
    print(f"trees={list(requested)}")
    print(f"python={sys.version.split()[0]} ({sys.executable})")
    print(f"src_root={src_root}")
    print(f"sys.path_has_src={str(src_root) in sys.path}")
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))
    print(f"qt_available={importlib.util.find_spec('PySide6') is not None}")
    print("-" * 60)

    ok = 0
    failed: list[tuple[str, str, str]] = []
    for tree in requested:
        names = module_names(src_root, tree)
        print(f"### tree={tree} modules={len(names)}")
        for name in names:
            try:
                importlib.import_module(name)
            except BaseException as error:  # noqa: BLE001 - probe reports all
                reason = f"{type(error).__name__}: {error}"
                failed.append((tree, name, reason))
                print(f"FAIL {name} :: {reason}")
            else:
                ok += 1
                print(f"OK   {name}")
    print("-" * 60)
    print(f"imported_ok={ok}")
    print(f"imported_failed={len(failed)}")
    for tree, name, reason in failed:
        print(f"FAILED_MODULE tree={tree} module={name} reason={reason}")
    module_error = [f for f in failed if "ModuleNotFoundError" in f[2]]
    print(f"failures_due_to_missing_module={len(module_error)}")
    print("probe_completed=True")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(2)
