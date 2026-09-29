"""M2-AC5 frozen entry for ``python -m bootstrap.core_service``.

Thin wrapper so PyInstaller can freeze the production library sidecar entry
(see entry_host_bridge.py for the rationale). Build tooling only.
"""

from bootstrap.core_service import main

if __name__ == "__main__":
    raise SystemExit(main())
