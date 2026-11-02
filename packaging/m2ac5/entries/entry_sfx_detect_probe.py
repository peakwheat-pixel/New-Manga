"""M2-AC5 frozen entry for ``python -m bootstrap.sfx_detect_probe``.

M2-PROD-SFX-PROBE-1: one-shot packaged SFX-detect probe — runs ONE
production ``SfxDetectionProvider.detect`` against the in-bundle v2b weights
inside the frozen process and prints the audit JSON (candidates / elapsed /
device-sfx_ep-sfx_ep_fallback three-key provenance). NOT part of the frozen
stdio command surface (the core_service dispatch table is untouched); a
standalone frozen entry exe, the catalog_loader precedent shape. Thin wrapper
so PyInstaller can freeze the entry (see entry_host_bridge.py for the
rationale). Build tooling only.
"""

from bootstrap.sfx_detect_probe import main

if __name__ == "__main__":
    raise SystemExit(main())
