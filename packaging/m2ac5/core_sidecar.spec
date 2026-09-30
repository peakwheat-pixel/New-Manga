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

M2-PROD-DETECT-2 DSH r1 R3 review-fix: transformers reaching the graph used
to be an ACCIDENT of torch's internal optional imports — the src tree only
mentions transformers as a string (the manga provider resolves it through
importlib at detect time), so modulegraph never tracks it directly; it entered
the PYZ because torch/onnx/_internal/exporter/_input_observer.py and
torch/testing/_internal/common_distributed.py happen to import it inside
functions. A torch/dependency bump that drops those two optional imports would
silently shrink the closure (build stays green, release-form detect degrades
to PROVIDER_DEPENDENCY_MISSING). The ML hiddenimports below make the closure
EXPLICIT, and the per-entry closure assertion right after each Analysis fails
the build if the graph did not actually collect them.
"""

import os
import shutil

from PyInstaller.config import CONF

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
# packaging/m2ac5 -> packaging -> repo root
REPO_ROOT = os.path.abspath(os.path.join(SPEC_DIR, "..", ".."))
SRC_ROOT = os.path.join(REPO_ROOT, "src")

#: (entry script stem, exe name, is_ml_entry) — exe names are the stable
#: identifiers the Rust host resolves under `resources/core-sidecar/` in
#: packaged mode. Only the production library entry (core_service) carries
#: the detect chain, so only its Analysis pins the ML hiddenimports and gets
#: the ML closure assertion (the other three entries keep their released
#: stdlib+repo closure — do not widen them).
ENTRIES = [
    ("entry_host_bridge", "host_bridge", False),
    ("entry_core_service", "core_service", True),
    ("entry_acceptance_bridge", "acceptance_bridge", False),
    ("entry_catalog_loader", "catalog_loader", False),
]

#: DSH r1 R3 review-fix (N3, DSH r2): the detect chain resolves transformers
#: and its RT-DETR model modules DYNAMICALLY (transformers' own _LazyModule —
#: `RTDetrV2ForObjectDetection` resolves through transformers.models.rt_detr_v2,
#: which modulegraph cannot be trusted to pull in on its own), so all three
#: names are pinned here; the assertion below fails the build if any of them
#: is missing from the analyzed graph.
ML_HIDDENIMPORTS = [
    "transformers",
    "transformers.models.rt_detr",
    "transformers.models.rt_detr_v2",
]


def _archive_warn_file(exe_name: str) -> None:
    """DSH r1 R1 review-fix: PyInstaller writes ONE shared warn file
    (CONF['warnfile'], fixed name `warn-<spec>.txt`) and every Analysis
    OVERWRITES it — without this copy only the LAST entry's warn file
    (catalog_loader, which carries no ML) would survive, which is exactly
    how the r1 evidence ended up anchored to the wrong closure. Each
    Analysis writes the shared file inside its own assemble step, so the
    copy right after `Analysis(...)` returns archives THAT entry's warnings
    under `warn-archive/warn-<exe>.txt` next to the shared file."""
    warn_src = CONF.get("warnfile")
    if not warn_src or not os.path.isfile(warn_src):
        # Incremental (non --clean) reruns may skip re-analysis entirely and
        # never write the shared file; archiving is best-effort in that case.
        print(f"warn-archive: no warn file written for {exe_name} (skipped)")
        return
    archive_dir = os.path.join(os.path.dirname(warn_src), "warn-archive")
    os.makedirs(archive_dir, exist_ok=True)
    warn_dst = os.path.join(archive_dir, f"warn-{exe_name}.txt")
    shutil.copy(warn_src, warn_dst)
    print(f"warn-archive: {warn_src} -> {warn_dst}")


def _assert_ml_closure(analysis, exe_name: str) -> None:
    """DSH r1 R3 review-fix: fail the BUILD (not the release) if the ML
    runtime is not actually in the analyzed graph. `analysis.pure` is the
    TOC of pure-Python modules that will land in this entry's PYZ."""
    pure_names = {entry[0] for entry in analysis.pure}
    missing = [m for m in ML_HIDDENIMPORTS if m not in pure_names]
    if missing:
        raise SystemExit(
            f"ML closure assertion FAILED for {exe_name}: {missing} not "
            "collected into the PYZ — the release-form detect chain would "
            "silently degrade to PROVIDER_DEPENDENCY_MISSING. Do NOT relax "
            "this check; fix the hiddenimports/analysis instead."
        )
    print(
        f"closure assertion: {exe_name} PYZ carries "
        + ", ".join(ML_HIDDENIMPORTS)
        + f" ({len(pure_names)} pure modules)"
    )

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
for stem, name, is_ml_entry in ENTRIES:
    a = Analysis(
        [os.path.join(SPEC_DIR, "entries", stem + ".py")],
        pathex=[SRC_ROOT],
        binaries=[],
        datas=[],
        hiddenimports=list(ML_HIDDENIMPORTS) if is_ml_entry else [],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=EXCLUDED,
        noarchive=False,
        optimize=1,
    )
    # DSH r1 R1: archive THIS entry's warn file before the next Analysis
    # overwrites the shared file (see _archive_warn_file).
    _archive_warn_file(name)
    if is_ml_entry:
        _assert_ml_closure(a, name)
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
