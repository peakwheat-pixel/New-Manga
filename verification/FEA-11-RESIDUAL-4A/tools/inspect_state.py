"""FEA-11-RESIDUAL-4A (AC-R3-2) evidence probe: read the isolated v8 library.

Read-only. Emits the binding/entry/rendition/page facts the .NET production
chain test asserts before and after the sync:

* every ``page_bindings`` row (the old binding's already-published
  ``verified_digest`` is the "old digest" that must stay immutable);
* the old version's ``source_entries`` content digests;
* the ``rendition_cache`` catalog keys (``page-rendition-*``): the legacy page
  key must never be (re)published by the sync;
* the page order and the source version/location rows.

Usage:
  python inspect_state.py --db D --out O --old-version sv1 --source-id s1
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--old-version", default="sv1")
    parser.add_argument("--source-id", default="s1")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    facts = {
        "bindings": [
            dict(row)
            for row in conn.execute(
                "SELECT binding_id, page_id, project_id, binding_version,"
                " accepted_source_version, entry_id, status, verified_digest,"
                " previous_binding_id, source_id"
                " FROM page_bindings ORDER BY page_id, binding_version"
            ).fetchall()
        ],
        "old_entries": [
            dict(row)
            for row in conn.execute(
                "SELECT entry_id, locator, content_digest FROM source_entries"
                " WHERE version_id = ? ORDER BY entry_id",
                (args.old_version,),
            ).fetchall()
        ],
        "renditions": [
            dict(row)
            for row in conn.execute(
                "SELECT cache_key, content_digest, rel_path FROM rendition_cache"
                " ORDER BY cache_key"
            ).fetchall()
        ],
        "pages": [
            dict(row)
            for row in conn.execute(
                "SELECT page_id, chapter_id, sort_order, source_order, source_hash"
                " FROM pages ORDER BY page_id"
            ).fetchall()
        ],
        "versions": [
            dict(row)
            for row in conn.execute(
                "SELECT version_id, content_digest FROM source_versions"
                " WHERE source_id = ? ORDER BY created_at",
                (args.source_id,),
            ).fetchall()
        ],
        "locations": [
            dict(row)
            for row in conn.execute(
                "SELECT location_id, is_current, content_digest"
                " FROM source_locations WHERE source_id = ? ORDER BY location_id",
                (args.source_id,),
            ).fetchall()
        ],
    }
    conn.close()
    args.out.write_text(json.dumps(facts, indent=1), encoding="utf-8")
    print(
        "FEA11_R4A_STATE_OK "
        + json.dumps(
            {
                "bindings": len(facts["bindings"]),
                "renditions": len(facts["renditions"]),
                "pages": len(facts["pages"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
