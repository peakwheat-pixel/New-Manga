"""M2-D1 audit probe P6: are the two Qt-free UI modules reachable without Qt?

`src/ui/models/tasks/projection.py` and `src/ui/viewmodels/workbench/region_canvas.py`
are reported as Qt-free by source reading. The tree-wide probe (P5) nevertheless
fails for both module *names*, because importing `ui.models.tasks` /
`ui.viewmodels.workbench` runs their package `__init__.py`, which re-exports
Qt-backed siblings.

This probe separates the two questions:
  A) import by module name   -> follows the package __init__ chain
  B) import by file path     -> loads the single file, skipping the package __init__

READ-ONLY: no files are written; run with `python -B` so no __pycache__ appears.
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path

TARGETS = (
    "ui/models/tasks/projection.py",
    "ui/viewmodels/workbench/region_canvas.py",
)


def main() -> int:
    src_root = Path(__file__).resolve().parents[3] / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))
    print("probe=ui_qtfree_bridge_probe")
    print(f"python={sys.version.split()[0]} ({sys.executable})")
    print(f"src_root={src_root}")
    print(f"qt_available={importlib.util.find_spec('PySide6') is not None}")
    print("-" * 60)

    for rel in TARGETS:
        module_name = rel[:-3].replace("/", ".")
        print(f"### target={rel}")

        # A) by module name (package __init__ chain runs)
        try:
            importlib.import_module(module_name)
        except BaseException as error:  # noqa: BLE001
            print(f"A_by_module_name=FAIL {type(error).__name__}: {error}")
        else:
            print("A_by_module_name=OK")

        # B) by file path (no package __init__)
        path = src_root / rel
        spec = importlib.util.spec_from_file_location(
            "m2d1_probe_" + module_name.replace(".", "_"), path
        )
        if spec is None or spec.loader is None:
            print("B_by_file_path=FAIL (no spec)")
            continue
        module = importlib.util.module_from_spec(spec)
        # Register before exec: dataclasses (3.12+) resolves cls.__module__ via
        # sys.modules, so an unregistered synthetic module raises AttributeError.
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException as error:  # noqa: BLE001
            print(f"B_by_file_path=FAIL {type(error).__name__}: {error}")
            traceback.print_exc()
        else:
            public = sorted(
                name
                for name in vars(module)
                if not name.startswith("_") and name not in {"annotations"}
            )
            print(f"B_by_file_path=OK exported={public[:12]}")
    print("-" * 60)
    print("probe_completed=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
