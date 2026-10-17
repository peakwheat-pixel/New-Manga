from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_NAME = os.environ.get("P19_RUN_NAME", "runtime")
assert Path(RUN_NAME).name == RUN_NAME, f"invalid run name: {RUN_NAME}"
RUN_ROOT = ROOT / RUN_NAME
SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.resource_channel.catalog_store import initialize_namespace
from infrastructure.resource_channel.handle_resolver import PREVIEW_NAMESPACE_LOCK_NAME


def main() -> None:
    assert not RUN_ROOT.exists() or not any(RUN_ROOT.iterdir()), f"refusing non-empty run root: {RUN_ROOT}"
    app_root = RUN_ROOT / "appdata-roaming" / "com.newmanga.m2rc1.desktop"
    derived_root = app_root / "derived"
    catalog_db = app_root / "catalog" / "catalog.sqlite"
    for path in (
        app_root / "data",
        derived_root,
        app_root / "managed",
        catalog_db.parent,
        RUN_ROOT / "appdata-local",
        RUN_ROOT / "tmp",
        RUN_ROOT / "webview2-udd",
    ):
        path.mkdir(parents=True, exist_ok=True)

    initialize_namespace(catalog_db, derived_root)
    with sqlite3.connect(catalog_db) as connection:
        connection.execute("DELETE FROM preview_namespace")
    (derived_root / PREVIEW_NAMESPACE_LOCK_NAME).unlink()

    assert catalog_db.is_file()
    assert not any(derived_root.iterdir())
    state = {
        "scenario": "catalog exists with empty derived root before real app launch",
        "catalog_db": str(catalog_db.relative_to(RUN_ROOT)),
        "catalog_bytes": catalog_db.stat().st_size,
        "catalog_sha256": hashlib.sha256(catalog_db.read_bytes()).hexdigest(),
        "derived_root": str(derived_root.relative_to(RUN_ROOT)),
        "derived_entries_before_launch": [],
        "construction": [
            "create an empty canonical catalog and binding through initialize_namespace",
            "delete only the preview_namespace row to model interrupted first bind",
            "remove the lock file and verify derived/ is empty",
        ],
        "root": str(RUN_ROOT),
    }
    (ROOT / f"partial-state-{RUN_NAME}.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
