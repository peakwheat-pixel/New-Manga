# -*- mode: python ; coding: utf-8 -*-
"""M2-AC5 Core sidecar — PyInstaller spec (build tooling only).

One onedir bundle (`core-sidecar/`) holding FOUR frozen entry exes that share
a single `_internal` dependency directory (PyInstaller 6 layout):

    host_bridge.exe          <- `-m infrastructure.resource_channel.host_bridge`
    core_service.exe         <- `-m bootstrap.core_service`  (production library)
    acceptance_bridge.exe    <- `-m bootstrap.acceptance_bridge` (M2-AC1 test mode)
    catalog_loader.exe       <- `-m infrastructure.resource_channel.catalog_loader`
                                (launcher-side seeding tool; a packaged
                                clean-start env has no system Python to run
                                the dev `python -m` seeding step with)

Ruling recorded for M2-AC5 (risk item 1): the three sidecar channels plus the
seeding tool are covered by ONE onedir closure. Measured facts behind the
choice: the import closure of host_bridge / core_service / catalog_loader is
stdlib + in-repo packages only (verified 2026-09-29 with TASK-012-py312), but
`bootstrap.acceptance_bridge` — through its frozen `assemble_acceptance_core`
assembly, shared verbatim with tests/m2_acceptance — HARD-REQUIRES PySide6
(QGuiApplication + the production Qt imaging/rendering adapters). Excluding
Qt made acceptance_bridge.exe fail closed with ModuleNotFoundError at
startup, so the closure INCLUDES PySide6. That release-time note ("Qt-free")
held for the resource-channel and library sidecars only; the acceptance
bridge's Qt dependence is a frozen M2-AC1 fact, not a packaging choice.

Excluded below: build tooling only. M2-PROD-DETECT-2 (proxy ruling 2,
reversible): the heavy ML stack (torch/torchvision/doctr/transformers) is now
IN the build venv and IN the closure — the release-form detect chain ships
its runtime (the default manga backend lazy-imports torch/transformers on
first detect, so the frozen process must find them in `_internal`). pandas
and the build/test tooling stay excluded — a stray import of those must fail
at build analysis time with a visible warning, not ship silently.
"""

import os

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
# packaging/m2ac5 -> packaging -> repo root
REPO_ROOT = os.path.abspath(os.path.join(SPEC_DIR, "..", ".."))
SRC_ROOT = os.path.join(REPO_ROOT, "src")

#: (entry script stem, exe name) — exe names are the stable identifiers the
#: Rust host resolves under `resources/core-sidecar/` in packaged mode.
ENTRIES = [
    ("entry_host_bridge", "host_bridge"),
    ("entry_core_service", "core_service"),
    ("entry_acceptance_bridge", "acceptance_bridge"),
    ("entry_catalog_loader", "catalog_loader"),
]

EXCLUDED = [
    # M2-PROD-DETECT-2 (proxy ruling 2): the ML stack (torch/torchvision/
    # doctr + their transitive deps) is deliberately NOT excluded anymore —
    # it is installed into the build venv (requirements-build.txt, versions
    # verbatim from requirements.txt) and must ship inside the frozen closure
    # so the release-form detect chain works. Reverting = re-add the three
    # names here + drop the ML lines from requirements-build.txt.
    "pandas",
    # build/test tooling never belongs in the runtime closure
    "pytest",
    "setuptools",
    "distutils",
    "pip",
]

exes = []
all_binaries = []
all_datas = []
for stem, name in ENTRIES:
    a = Analysis(
        [os.path.join(SPEC_DIR, "entries", stem + ".py")],
        pathex=[SRC_ROOT],
        binaries=[],
        datas=[],
        hiddenimports=[],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=EXCLUDED,
        noarchive=False,
        optimize=1,
    )
    pyz = PYZ(a.pure)
    exes.append(
        EXE(
            pyz,
            a.scripts,
            exclude_binaries=True,
            name=name,
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=False,
            # M2-RG1 (AC2): console=True is FROZEN — the stdio JSON-lines
            # protocol depends on pipe semantics that PyInstaller windowed
            # mode would alter. Console-window suppression for packaged
            # launches is done host-side (Rust CREATE_NO_WINDOW on the spawn
            # sections + windows_subsystem="windows" for the app exe).
            console=True,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None,
        )
    )
    all_binaries.append(a.binaries)
    all_datas.append(a.datas)

coll = COLLECT(
    *exes,
    *all_binaries,
    *all_datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="core-sidecar",
)
