"""M2-AC5 frozen entry for ``python -m bootstrap.acceptance_bridge``.

Thin wrapper so PyInstaller can freeze the M2-AC1 acceptance sidecar entry
(see entry_host_bridge.py for the rationale). Build tooling only; the
acceptance bridge is spawned only in the explicit ``M2AC1_TEST_MODE=1``
startup configuration, exactly as before.
"""

from bootstrap.acceptance_bridge import main

if __name__ == "__main__":
    raise SystemExit(main())
