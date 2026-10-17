from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[3]
isolation = Path(sys.argv[1]).resolve()
sys.dont_write_bytecode = True
approved = (Path(os.environ["TEMP"]) / "feat-import-multi-r1").resolve()
if isolation != approved:
    raise SystemExit("refusing namespace rebind outside the approved TEMP isolation root")

catalog = isolation / "catalog/catalog.sqlite"
derived = isolation / "derived"
lock = derived / ".preview-lifecycle.lock"
if not catalog.is_file() or not derived.is_dir() or any(derived.iterdir()):
    raise SystemExit("isolated catalog is missing or derived directory is not initially empty")

sys.path.insert(0, str(repo / "src"))
from infrastructure.resource_channel.handle_resolver import resolve_namespace_identity  # noqa: E402

catalog_root, catalog_identity = resolve_namespace_identity(catalog)
derived_root, derived_identity = resolve_namespace_identity(derived)
connection = sqlite3.connect(catalog)
try:
    rows = connection.execute("SELECT protocol_version FROM preview_namespace WHERE singleton = 1").fetchall()
    if len(rows) != 1 or rows[0][0] != 1:
        raise SystemExit("isolated catalog does not contain one protocol-v1 namespace binding")
    connection.execute("BEGIN IMMEDIATE")
    cursor = connection.execute(
        "UPDATE preview_namespace SET derived_root = ?, derived_identity_volume = ?, "
        "derived_identity_index = ?, catalog_root = ?, catalog_identity_volume = ?, "
        "catalog_identity_index = ? WHERE singleton = 1",
        (derived_root, derived_identity[0], derived_identity[1], catalog_root, catalog_identity[0], catalog_identity[1]),
    )
    if cursor.rowcount != 1:
        raise SystemExit("isolated namespace update did not affect exactly one row")
    connection.commit()
finally:
    connection.close()

binding = {
    "protocol_version": 1,
    "derived_root": derived_root,
    "derived_identity": list(derived_identity),
    "catalog_root": catalog_root,
    "catalog_identity": list(catalog_identity),
}
lock.write_text(json.dumps(binding, sort_keys=True) + "\n", encoding="utf-8")

connection = sqlite3.connect(f"file:{catalog.as_posix()}?mode=ro", uri=True)
try:
    stored = connection.execute(
        "SELECT protocol_version, derived_root, derived_identity_volume, derived_identity_index, "
        "catalog_root, catalog_identity_volume, catalog_identity_index FROM preview_namespace WHERE singleton = 1"
    ).fetchone()
finally:
    connection.close()
expected = (1, derived_root, derived_identity[0], derived_identity[1], catalog_root, catalog_identity[0], catalog_identity[1])
if stored != expected or json.loads(lock.read_text(encoding="utf-8")) != binding:
    raise SystemExit("isolated catalog/lock binding verification failed")

result = {"protocol_version": 1, "isolation_root": "%TEMP%\\feat-import-multi-r1", "source_catalog_modified": False, "rebind": "PASS"}
out = Path(__file__).with_name("gui-run-r1") / "namespace-rebind.json"
if out.exists():
    raise SystemExit("refusing to overwrite namespace rebind evidence")
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("isolated_namespace_rebind=PASS source_catalog_untouched=true")
