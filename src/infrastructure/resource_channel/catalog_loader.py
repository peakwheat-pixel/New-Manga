"""Offline catalog loader CLI (M2-RC2).

Seeds the Core/SQLite catalog authority from a launcher (the RC2 E2E runner)
or the product Core. This is the only sanctioned write path for catalog rows:
the WebView has no catalog command and the control bridge refuses host-supplied
paths, so a lab/launcher seeding this store is the whole catalog lifecycle in
the current slice.

Usage:
  python -m infrastructure.resource_channel.catalog_loader --db PATH \
      [--initialize-preview-namespace DERIVED_ROOT] \
      [--set RESOURCE_ID=REL_PATH[@SCOPE_CLASS]]... \
      [--remove RESOURCE_ID]... [--dump] [--count]

``@scope`` is optional and defaults to ``derived-read-only``. Every write is
validated by the store (servable scope class + rel-path gate), so a loader
mistake is a typed error, never a poisoned row.

M2-DERIVED-GC-2: ``--initialize-preview-namespace DERIVED_ROOT`` is the
trusted first-seed flag for isolated fixtures (design §2.3). It runs the
frozen narrow ``initialize_namespace`` against THIS loader's own new/empty
catalog and the given verified derived root, BEFORE any seed row is written;
without the flag an unbound catalog is refused (never auto-claimed), and a
failed initialization aborts the seed. A catalog that already carries rows or
a binding is never re-initialized by the flag (the store then serves the
bound namespace like any other participant).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from application.resource_channel.dto import TypedResourceChannelError
from infrastructure.resource_channel.catalog_store import (
    ResourceCatalogStore,
    initialize_namespace,
)

DEFAULT_SCOPE = "derived-read-only"


def _apply(store: ResourceCatalogStore, args: argparse.Namespace) -> int:
    for spec in args.set or []:
        resource_id, _, rest = spec.partition("=")
        if not resource_id or not rest:
            print(f"invalid --set spec (want RESOURCE_ID=REL_PATH[@SCOPE]): {spec!r}")
            return 2
        rel_path, _, scope = rest.partition("@")
        try:
            store.upsert(resource_id, scope or DEFAULT_SCOPE, rel_path)
        except TypedResourceChannelError as error:
            print(f"catalog upsert refused: {error.code}: {error.message}")
            return 2
    for resource_id in args.remove or []:
        store.remove(resource_id)
    if args.dump:
        print(
            json.dumps(
                {
                    entry.resource_id: {
                        "scope_class": entry.scope_class,
                        "rel_path": entry.rel_path,
                    }
                    for entry in store.entries()
                },
                indent=2,
            )
        )
    if args.count:
        print(f"catalog rows: {store.count()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", required=True, help="catalog SQLite database file")
    parser.add_argument(
        "--initialize-preview-namespace",
        metavar="DERIVED_ROOT",
        default=None,
        help=(
            "trusted fixture/seed initializer: first-bind THIS new/empty"
            " catalog to the given verified derived root before seeding"
            " (M2-DERIVED-GC-2; existing/unknown catalogs are refused)"
        ),
    )
    parser.add_argument(
        "--set",
        action="append",
        metavar="RESOURCE_ID=REL_PATH[@SCOPE_CLASS]",
        help="insert/replace one catalog row (repeatable)",
    )
    parser.add_argument(
        "--remove", action="append", metavar="RESOURCE_ID", help="remove one catalog row"
    )
    parser.add_argument("--dump", action="store_true", help="print the catalog as JSON")
    parser.add_argument("--count", action="store_true", help="print the catalog row count")
    args = parser.parse_args(argv)
    if args.initialize_preview_namespace:
        try:
            initialize_namespace(Path(args.db), Path(args.initialize_preview_namespace))
        except (TypedResourceChannelError, OSError) as error:
            print(f"preview namespace initialization refused: {error}")
            return 2
    try:
        store = ResourceCatalogStore(Path(args.db))
    except TypedResourceChannelError as error:
        print(f"catalog open refused: {error.code}: {error.message}")
        return 2
    try:
        return _apply(store, args)
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
