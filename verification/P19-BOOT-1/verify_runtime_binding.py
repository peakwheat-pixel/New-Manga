from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_NAME = os.environ.get("P19_RUN_NAME", "runtime-final4")
assert Path(RUN_NAME).name == RUN_NAME, f"invalid P19_RUN_NAME: {RUN_NAME}"
RUN_ROOT = ROOT / RUN_NAME
APP_ROOT = RUN_ROOT / "appdata-roaming" / "com.newmanga.m2rc1.desktop"
CATALOG = APP_ROOT / "catalog" / "catalog.sqlite"
DERIVED = APP_ROOT / "derived"
LOCK = DERIVED / ".preview-lifecycle.lock"
SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC_ROOT))

from infrastructure.resource_channel.handle_resolver import (  # noqa: E402
    read_lock_binding_if_any,
    resolve_namespace_identity,
)


def main() -> None:
    assert CATALOG.is_file()
    assert LOCK.is_file() and LOCK.stat().st_size > 0
    assert set(path.name for path in DERIVED.iterdir()) == {LOCK.name}

    binding = read_lock_binding_if_any(str(DERIVED))
    assert binding is not None
    catalog_root, catalog_identity = resolve_namespace_identity(CATALOG)
    derived_root, derived_identity = resolve_namespace_identity(DERIVED)
    assert binding.catalog_root == catalog_root
    assert binding.catalog_identity == catalog_identity
    assert binding.derived_root == derived_root
    assert binding.derived_identity == derived_identity

    with sqlite3.connect(CATALOG.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        rows = connection.execute(
            "SELECT protocol_version, derived_root, derived_identity_volume,"
            " derived_identity_index, catalog_root, catalog_identity_volume,"
            " catalog_identity_index FROM preview_namespace"
        ).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row == (
        binding.protocol_version,
        binding.derived_root,
        binding.derived_identity[0],
        binding.derived_identity[1],
        binding.catalog_root,
        binding.catalog_identity[0],
        binding.catalog_identity[1],
    )

    result = {
        "scenario": "runtime binding after real application startup",
        "catalog": str(CATALOG.relative_to(RUN_ROOT)),
        "lock": str(LOCK.relative_to(RUN_ROOT)),
        "lock_bytes": LOCK.stat().st_size,
        "lock_json": json.loads(LOCK.read_text(encoding="utf-8")),
        "catalog_binding_rows": len(rows),
        "lock_and_catalog_binding_match": True,
        "catalog_and_derived_path_identity_match": True,
    }
    (ROOT / "runtime-binding-final.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
