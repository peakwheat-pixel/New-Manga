"""M2-AC5 frozen entry for ``python -m infrastructure.resource_channel.catalog_loader``.

The catalog loader is the launcher-side seeding write path for the Core/SQLite
catalog authority (dev runners invoke ``python -m ...catalog_loader`` before
starting the desktop runtime). A packaged clean-start environment has no
system Python, so the same seeding step needs a self-contained frozen exe.
It ships in the sidecar directory as the launcher-equivalent tool; the
production command surface does not change and the host never writes the
catalog itself (F-03 is preserved: seeding is a launcher-side CLI step).
"""

from infrastructure.resource_channel.catalog_loader import main

if __name__ == "__main__":
    raise SystemExit(main())
