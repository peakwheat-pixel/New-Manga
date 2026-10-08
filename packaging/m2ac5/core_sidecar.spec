# -*- mode: python ; coding: utf-8 -*-
"""M2-AC5 Core sidecar — PyInstaller spec (build tooling only).

One onedir bundle (`core-sidecar/`) holding FIVE frozen entry exes that share
a single `_internal` dependency directory (PyInstaller 6 layout):

    host_bridge.exe          <- `-m infrastructure.resource_channel.host_bridge`
    core_service.exe         <- `-m bootstrap.core_service`  (production library)
    acceptance_bridge.exe    <- `-m bootstrap.acceptance_bridge` (M2-AC1 test mode)
    catalog_loader.exe       <- `-m infrastructure.resource_channel.catalog_loader`
                                (launcher-side seeding tool; a packaged
                                clean-start env has no system Python to run
                                the dev `python -m` seeding step with)
    sfx_detect_probe.exe     <- `-m bootstrap.sfx_detect_probe`
                                (M2-PROD-SFX-PROBE-1: one-shot frozen-process
                                SFX-detect probe — NOT an IPC command, the
                                catalog_loader standalone-entry precedent
                                shape; runs one production
                                SfxDetectionProvider.detect against the
                                in-bundle v2b weights and prints the audit
                                JSON)

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
import sys

from PyInstaller.config import CONF

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
# packaging/m2ac5 -> packaging -> repo root
REPO_ROOT = os.path.abspath(os.path.join(SPEC_DIR, "..", ".."))
SRC_ROOT = os.path.join(REPO_ROOT, "src")

#: (entry script stem, exe name, is_ml_entry) — exe names are the stable
#: identifiers the Rust host resolves under `resources/core-sidecar/` in
#: packaged mode. Only the production library entry (core_service) carries
#: the detect chain, so only its Analysis pins the ML hiddenimports and gets
#: the ML closure assertion. The other entries take no ML
#: hiddenimports/assertion of their own; note the sfx probe's PYZ
#: nonetheless carries the ML closure transitively (detection_doctr static
#: import followed by modulegraph — see the ENTRIES comment below).
ENTRIES = [
    ("entry_host_bridge", "host_bridge", False),
    ("entry_core_service", "core_service", True),
    ("entry_acceptance_bridge", "acceptance_bridge", False),
    ("entry_catalog_loader", "catalog_loader", False),
    # M2-PROD-SFX-PROBE-1: the one-shot SFX-detect probe (frozen-process
    # evidence, NOT an IPC command — catalog_loader precedent shape).
    # Closure reality (DSH r1 P2-1, corrected from the original "onnxruntime
    # only" claim): the probe imports the production SfxDetectionProvider,
    # whose module graph runs detection_sfx -> detection_manga ->
    # detection_doctr, and detection_doctr carries a function-body-static
    # `from doctr.models import detection_predictor` that modulegraph DOES
    # follow — so this entry's PYZ ships a SECOND torch/transformers/doctr
    # closure (~8455 pure modules, ~64.76 MiB exe), not an onnxruntime-only
    # face. Accepted deliberately (integration ruling on the DSH r1 menu):
    # (a) accept the duplication (zero-risk, revert = drop this line);
    # (b) a one-shot CLI mode on core_service.exe (0 B) was rejected — it
    #     forks the production entry's startup behaviour;
    # (c) slimming the probe import face (breaking the static doctr import)
    #     is a product-src refactor left to a future slice.
    # It still gets its own hiddenimports + its own closure assertion below
    # instead of the ML entry treatment.
    ("entry_sfx_detect_probe", "sfx_detect_probe", False),
]

#: M2-PROD-SFX-PROBE-1: the probe entry's own closure pins — onnxruntime is
#: resolved through importlib at detect time (modulegraph never tracks it),
#: so it is pinned explicitly; the assertion below fails the BUILD if the
#: graph did not collect the engine binaries. Scope note (DSH r1 P2-1): this
#: asserts the onnxruntime ENGINE is present — it does NOT mean the probe PYZ
#: is onnxruntime-only (it carries a second torch/transformers/doctr closure
#: via the detection_doctr static import, see the ENTRIES comment above).
SFX_PROBE_ENTRY = "entry_sfx_detect_probe"
SFX_PROBE_HIDDENIMPORTS = [
    "onnxruntime",
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
    # M2-SFX-PROD-1: the standalone SFX provider resolves onnxruntime through
    # importlib at detect time (same lazy pattern as transformers), so
    # modulegraph never tracks it — pin it explicitly or the frozen sfx chain
    # would silently degrade to PROVIDER_DEPENDENCY_MISSING.
    "onnxruntime",
]

#: M2-PROD-DETECT-3 (frozen in-process detect evidence): torchvision 0.29's
#: C++ ops live in stable-ABI extensions (`_C_stable` / `image_stable`) that
#: load DYNAMICALLY through `torchvision.extension._load_library` — and the
#: stock hook-torchvision still pins the pre-0.29 name `torchvision._C`, so
#: the real binaries NEVER reached the closure: the first frozen in-process
#: detect (this Task's AC4 probe) failed with
#: `RuntimeError: operator torchvision::nms does not exist` wrapped by
#: transformers' _LazyModule as "Could not import module
#: 'RTDetrImageProcessor'". `RTDetrImageProcessor` imports
#: `torchvision.transforms.v2.functional`, whose import finishes the
#: torchvision init and hits the missing ops. Pin the two stable-ABI
#: extensions here (EXTENSION modules land in a.binaries, not a.pure —
#: hence the separate binaries assertion below).
ML_BINARY_IMPORT_MODULES = [
    "torchvision._C_stable",
    "torchvision.image_stable",
]

#: What the binaries assertion looks for: the dotted module names as they
#: appear as EXTENSION TOC entries inside the `torchvision/` bundle dir.
ML_BINARY_IMPORTS = [
    "torchvision/_C_stable.pyd",
    "torchvision/image_stable.pyd",
]

#: M2-SFX-PROD-1 / M2-SFX-GPU-EP-1: the onnxruntime C-extension pair plus —
#: since the GPU deployment ruling (2026-10-06) — the DirectML runtime DLL.
#: The dependency is onnxruntime-directml==1.24.4 (same import name ``onnxruntime``,
#: same pyd name; the directml wheel additionally bundles ``DirectML.dll``
#: beside the pyd in onnxruntime/capi/, and the DmlExecutionProvider session
#: cannot initialize without it). The pyd pull-in is what the assertion below
#: checks; the DLLs ship beside it in onnxruntime/capi/. The check is the SFX
#: counterpart of the torchvision binaries assertion: build venv has the
#: runtime but a shrink here must fail the BUILD, not the release detect.
SFX_BINARY_IMPORTS = [
    "onnxruntime_pybind11_state.pyd",
    "DirectML.dll",
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
    TOC of pure-Python modules that will land in this entry's PYZ;
    `analysis.binaries` carries the EXTENSION modules (M2-PROD-DETECT-3:
    torchvision's stable-ABI .pyd pair, see ML_BINARY_IMPORTS)."""
    pure_names = {entry[0] for entry in analysis.pure}
    missing = [m for m in ML_HIDDENIMPORTS if m not in pure_names]
    if missing:
        raise SystemExit(
            f"ML closure assertion FAILED for {exe_name}: {missing} not "
            "collected into the PYZ — the release-form detect chain would "
            "silently degrade to PROVIDER_DEPENDENCY_MISSING. Do NOT relax "
            "this check; fix the hiddenimports/analysis instead."
        )
    binary_names = {entry[0].replace("\\", "/") for entry in analysis.binaries}
    missing_binaries = [
        m for m in ML_BINARY_IMPORTS if not any(
            name == m or name.endswith("/" + m) for name in binary_names
        )
    ]
    # M2-SFX-PROD-1: the onnxruntime C-extension rides the same assertion —
    # a closure that lost it would break the frozen sfx detect chain only.
    missing_binaries += [
        m for m in SFX_BINARY_IMPORTS if not any(
            name == m or name.endswith("/" + m) for name in binary_names
        )
    ]
    if missing_binaries:
        raise SystemExit(
            f"ML closure assertion FAILED for {exe_name}: extension(s) "
            f"{missing_binaries} not collected into the bundle binaries — "
            "the frozen detect chain would fail at model load with the "
            "missing torchvision C++ ops (or the missing onnxruntime "
            "engine). Do NOT relax this check; fix the hiddenimports/"
            "analysis instead."
        )
    print(
        f"closure assertion: {exe_name} PYZ carries "
        + ", ".join(ML_HIDDENIMPORTS)
        + f" ({len(pure_names)} pure modules) + extensions "
        + ", ".join(ML_BINARY_IMPORTS + SFX_BINARY_IMPORTS)
    )

def _assert_sfx_probe_closure(analysis, exe_name: str) -> None:
    """M2-PROD-SFX-PROBE-1: the SFX-probe counterpart of _assert_ml_closure —
    the probe entry must carry the onnxruntime runtime (pure module) AND the
    engine binaries (the pyd + DirectML.dll, SFX_BINARY_IMPORTS). A closure
    that lost them would fail the probe at model load, not the build — this
    assertion keeps that failure at BUILD time."""
    pure_names = {entry[0] for entry in analysis.pure}
    missing = [m for m in SFX_PROBE_HIDDENIMPORTS if m not in pure_names]
    if missing:
        raise SystemExit(
            f"SFX probe closure assertion FAILED for {exe_name}: {missing} not "
            "collected into the PYZ — the frozen sfx probe would degrade to "
            "PROVIDER_DEPENDENCY_MISSING. Do NOT relax this check; fix the "
            "hiddenimports/analysis instead."
        )
    binary_names = {entry[0].replace("\\", "/") for entry in analysis.binaries}
    missing_binaries = [
        m for m in SFX_BINARY_IMPORTS if not any(
            name == m or name.endswith("/" + m) for name in binary_names
        )
    ]
    if missing_binaries:
        raise SystemExit(
            f"SFX probe closure assertion FAILED for {exe_name}: extension(s) "
            f"{missing_binaries} not collected into the bundle binaries — "
            "the frozen sfx probe would fail at engine load. Do NOT relax "
            "this check; fix the hiddenimports/analysis instead."
        )
    print(
        f"closure assertion: {exe_name} PYZ carries "
        + ", ".join(SFX_PROBE_HIDDENIMPORTS)
        + f" ({len(pure_names)} pure modules) + extensions "
        + ", ".join(SFX_BINARY_IMPORTS)
    )


def _is_within_dir(path_norm: str, root_norm: str) -> bool:
    """Check if path_norm is exactly root_norm or inside root_norm with boundary safety."""
    if path_norm == root_norm:
        return True
    sep = os.sep
    prefix = root_norm if root_norm.endswith(sep) else root_norm + sep
    return path_norm.startswith(prefix)


KNOWN_CONTAMINANT_SHA256 = (
    "39aec884c7124d673d75b38cca7b44ac1909d9633d8366a812a6e1c269d74bdf"
)


def _is_confirmed_contaminant(src_path: str, src_norm: str) -> bool:
    """
    R-004 fact-boundary fix:
    The ONLY confirmed contaminant source is the external poppler native toolchain
    icuuc.dll (SHA256: 39aec884c7124d673d75b38cca7b44ac1909d9633d8366a812a6e1c269d74bdf)
    harvested from host PATH. Never broadly match generic dependencies/native or codex-runtimes.
    """
    sep = os.sep
    poppler_bin_marker = f"{sep}poppler{sep}library{sep}bin"
    if poppler_bin_marker not in src_norm and "poppler" not in src_norm:
        return False
    if os.path.isfile(src_path):
        import hashlib
        try:
            with open(src_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest().lower() == KNOWN_CONTAMINANT_SHA256
        except Exception:
            return False
    return False


def _isolate_icu_closure(analysis, exe_name: str) -> None:
    """M2-PACKAGED-AC1-ICU-ISOLATION-FIX:
    Qt6Core.dll dynamically imports Windows System32 ICU (icuuc.dll) with
    unsuffixed exports (ucnv_*). When PyInstaller's bindepend analyzes Qt6Core,
    it can harvest an alien ICU78 from external native toolchains on host PATH
    (e.g. from poppler Library/bin). Packaging that alien ICU at the root of
    `_internal` causes DLL shadowing: Windows loads the bundled icuuc.dll ahead
    of System32, hitting WinError 127 because the alien ICU78 exports only `_78`
    suffixed symbols.

    Per AC-1 matrix and DSH r1 findings R-004 & R-005:
    1. Source-bounded isolation: inspect `entry[1]` (source path).
       - In-venv / in-repo ICU binaries are preserved (never globally deleted).
       - Confirmed alien toolchain ICU binaries (verified poppler SHA256)
         are isolated to prevent shadowing.
       - Unclassified external ICU candidates fail closed with explicit diagnostic evidence.
    2. Discriminative guard assertion: verify no confirmed alien toolchain ICU remains in binaries,
       and verify that if Qt6Core is present, no shadowing icuuc.dll exists in the bundle.
    """
    cleaned_binaries = []
    isolated = []
    preserved = []
    unclassified = []

    venv_prefix = os.path.normcase(os.path.abspath(sys.prefix))
    repo_root = os.path.normcase(os.path.abspath(REPO_ROOT))

    for entry in analysis.binaries:
        dest_name = entry[0].replace("\\", "/")
        dest_base = os.path.basename(dest_name).lower()
        src_path = entry[1]
        src_norm = os.path.normcase(os.path.abspath(src_path))

        is_icu_candidate = (
            dest_base.startswith("icuuc")
            or dest_base.startswith("icudt")
            or dest_base.startswith("icuin")
        )

        if not is_icu_candidate:
            cleaned_binaries.append(entry)
            continue

        # Candidate is an ICU binary. Inspect source path with boundary safety.
        is_in_venv_or_repo = (
            _is_within_dir(src_norm, venv_prefix) or _is_within_dir(src_norm, repo_root)
        )
        is_confirmed_alien = _is_confirmed_contaminant(src_path, src_norm)

        if is_in_venv_or_repo:
            preserved.append((dest_name, src_path))
            cleaned_binaries.append(entry)
        elif is_confirmed_alien:
            isolated.append((dest_name, src_path))
        else:
            unclassified.append((dest_name, src_path))

    if isolated:
        print(
            f"icu-isolation: isolated {len(isolated)} confirmed alien ICU binary entries for {exe_name}:"
        )
        for dest, src in isolated:
            print(f"  [SHADOW-PREVENTED] {dest} <- {src}")

    if preserved:
        print(
            f"icu-isolation: preserved {len(preserved)} legitimate in-venv/repo ICU binary entries for {exe_name}:"
        )
        for dest, src in preserved:
            print(f"  [ICU-PRESERVED] {dest} <- {src}")

    if unclassified:
        paths = "\n".join(f"  {d} <- {s}" for d, s in unclassified)
        raise SystemExit(
            f"ICU isolation assertion FAILED for {exe_name}: found {len(unclassified)} unclassified external ICU binaries.\n"
            f"Task policy forbids unclassified removal or silent shadowing. Aborting build:\n{paths}"
        )

    analysis.binaries = cleaned_binaries

    # Discriminative guard assertions (R-005):
    # 1. Verify no confirmed alien contaminant leaked through
    for entry in analysis.binaries:
        src_norm = os.path.normcase(os.path.abspath(entry[1]))
        if _is_confirmed_contaminant(entry[1], src_norm):
            raise SystemExit(
                f"ICU isolation guard FAILED for {exe_name}: confirmed alien contaminant {entry[0]} leaked through!"
            )

    # 2. If Qt6Core is bundled, verify no shadowing icuuc.dll is packaged that would collide with System32
    has_qt6core = any(
        os.path.basename(e[0].replace("\\", "/")).lower() == "qt6core.dll"
        for e in analysis.binaries
    )
    if has_qt6core:
        shadowing_entries = [
            e for e in analysis.binaries
            if os.path.basename(e[0].replace("\\", "/")).lower() == "icuuc.dll"
        ]
        if shadowing_entries:
            raise SystemExit(
                f"ICU isolation guard FAILED for {exe_name}: Qt6Core is present and shadowing icuuc.dll exists: "
                f"{[e[0] for e in shadowing_entries]}"
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
        hiddenimports=(
            list(ML_HIDDENIMPORTS) + list(ML_BINARY_IMPORT_MODULES)
        ) if is_ml_entry else (
            list(SFX_PROBE_HIDDENIMPORTS) if stem == SFX_PROBE_ENTRY else []
        ),
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
    if stem == SFX_PROBE_ENTRY:
        _assert_sfx_probe_closure(a, name)
    _isolate_icu_closure(a, name)
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

# M2-PACKAGED-AC1-ICU-ISOLATION-FIX (R-005): Final closure verification across all aggregated binaries before COLLECT
for entry_binaries in all_binaries:
    for dest_name, src_path, _ in entry_binaries:
        s_norm = os.path.normcase(os.path.abspath(src_path))
        if _is_confirmed_contaminant(src_path, s_norm):
            raise SystemExit(
                f"Final COLLECT closure assertion FAILED: confirmed alien contaminant {dest_name} (from {src_path}) leaked into bundle collection!"
            )

coll = COLLECT(
    *exes,
    *all_binaries,
    *all_datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="core-sidecar",
)
