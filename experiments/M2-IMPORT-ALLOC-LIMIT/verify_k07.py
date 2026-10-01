"""K07 real-file verification for M2-IMPORT-ALLOC-LIMIT (AC3).

Runs the TA3-B2 F2 rejects (K07/K09/K10 webtoon long-strips) through the
*production* import channel:

    ImportImagesUseCase
      -> QtImageDecoder            (src/infrastructure/importing.py, the only
                                    QImageReader use site, now asserting
                                    _ALLOCATION_LIMIT_MIB = 2047 before every
                                    decode)
      -> ManagedCopyStoreAdapter   (verbatim original bytes into a throwaway
                                    managed tree under %TEMP%)
      -> in-memory ImportPageSink

and logs, per case, the committed page dimensions / managed ref and the
decoded MiB — the exact fields TA3-B2 could not obtain when Qt's built-in
256 MiB default rejected these files at import (F2). (r1 R4: domain Page
carries no mime field, so none is claimed here.)

A control pass repeats the raw decode at Qt's built-in default (256 MiB) to
archive the original F2 failure verbatim, upgrading the TA3-B2 "inferred"
F2 caliber to first-hand evidence (AC4). Since r1 R2/R3 the control pass
also archives, per case, the Qt categorized stderr line
(``QImageIOHandler: Rejecting image as it exceeds the current allocation
limit of 256 megabytes``) captured at OS level, the header-declared MiB,
and a positive arm: the *same* raw reader read of the *same* bytes at 2047
MiB must succeed — so inside the control pass the allocation limit is the
only variable between reject and accept.

Read-only on the assets: source files are only read, never written
(D07 §37). Run with the main venv from the repo root:

    PYTHONPATH=src python experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py \
        --out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]

# TA3-B2 F2 rejects (experiments/M2-TA3-B/case-selection.json), resolved
# against the primary checkout's test_assets (not worktree-local).
CASES = {
    "K07": Path(
        r"G:\CODEX\New Manga\test_assets\comic_golden_suite"
        r"\韩漫_KO\01_real_webtoon_cleaned_dataset\K07_641253_141\base.png"
    ),
    "K09": Path(
        r"G:\CODEX\New Manga\test_assets\comic_golden_suite"
        r"\韩漫_KO\01_real_webtoon_cleaned_dataset\K09_717481_124\base.png"
    ),
    "K10": Path(
        r"G:\CODEX\New Manga\test_assets\comic_golden_suite"
        r"\韩漫_KO\01_real_webtoon_cleaned_dataset\K10_730656_11\base.png"
    ),
}

_MIB = 1024 * 1024


@dataclass
class MemorySink:
    """Minimal production-shaped ImportPageSink (no DB in this experiment)."""

    pages: list = field(default_factory=list)

    def existing_source_hashes(self, chapter_id: str) -> set[str]:
        del chapter_id
        return set()

    def max_source_order(self, chapter_id: str) -> int:
        del chapter_id
        return len(self.pages)

    def add_page(self, page) -> None:
        self.pages.append(page)


@contextmanager
def _capture_native_stderr(sink: list[str]):
    """Capture OS-level stderr (fd 2) into ``sink[0]``.

    Qt categorized logging (``qt.imageio``: "QImageIOHandler: Rejecting
    image as it exceeds the current allocation limit ...") is emitted by the
    native layer straight to fd 2, bypassing Python's ``sys.stderr``, so a
    dup2-level redirect is required to archive it (dsh r1 R2).
    """
    with tempfile.TemporaryFile(mode="w+b") as tmp:
        saved = os.dup(2)
        try:
            sys.stderr.flush()
            os.dup2(tmp.fileno(), 2)
            yield
        finally:
            sys.stderr.flush()
            os.dup2(saved, 2)
            os.close(saved)
        tmp.seek(0)
        sink.append(tmp.read().decode("utf-8", errors="replace").strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="write JSON evidence here")
    args = parser.parse_args()

    import PySide6
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice, qVersion
    from PySide6.QtGui import QImageReader

    from application.importing.images.service import ImportImagesUseCase
    from application.importing.images.ports import ImportSource
    from infrastructure.filesystem.managed_storage import ManagedFileStorage
    from infrastructure.importing import QtImageDecoder, ManagedCopyStoreAdapter, _ALLOCATION_LIMIT_MIB

    missing = [case for case, path in CASES.items() if not path.is_file()]
    if missing:
        print(f"FATAL: missing real assets: {missing}", file=sys.stderr)
        return 2

    results = {"schema_version": 2, "task": "M2-IMPORT-ALLOC-LIMIT", "cases": {}}
    # r1 R2: environment section so the evidence is attributable to a stack.
    results["env"] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "pyside6": PySide6.__version__,
        "qt": qVersion(),
        "allocation_limit_mib": _ALLOCATION_LIMIT_MIB,
    }

    # ---- production channel at the fixed limit -------------------------
    for case, path in CASES.items():
        with tempfile.TemporaryDirectory(prefix=f"alloc-limit-{case}-") as managed_root:
            storage = ManagedFileStorage(Path(managed_root))
            storage.ensure_layout()
            sink = MemorySink()
            use_case = ImportImagesUseCase(
                decoder=QtImageDecoder(),
                copy_store=ManagedCopyStoreAdapter(storage, lambda chapter_id: f"verify-{case.lower()}"),
                sink=sink,
            )
            report = use_case.import_files(
                f"chapter-{case.lower()}",
                [ImportSource(filename=path.name, data_provider=path.read_bytes)],
            )
            entry: dict = {
                "path": str(path),
                "source_size_bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "allocation_limit_mib": _ALLOCATION_LIMIT_MIB,
                "imported": [],
                "failed": [
                    {"filename": f.filename, "reason": f.reason, "detail": f.detail}
                    for f in report.failed
                ],
            }
            for imported in report.imported:
                page = imported.page
                entry["imported"].append(
                    {
                        "filename": imported.filename,
                        "width": page.width,
                        "height": page.height,
                        "source_size_bytes": page.source_size_bytes,
                        "managed_original_ref": page.managed_original_ref,
                    }
                )
            if entry["imported"]:
                # r1 R2: per-case decoded MiB (width * height * 4 B RGBA).
                first = entry["imported"][0]
                entry["decoded_mib"] = round(
                    first["width"] * first["height"] * 4 / _MIB, 1
                )
            results["cases"][case] = entry
            ok = bool(entry["imported"]) and not entry["failed"]
            status = "OK " if ok else "FAIL"
            if entry["imported"]:
                p = entry["imported"][0]
                print(
                    f"[{status}] {case}: {p['width']}x{p['height']} "
                    f"({entry['source_size_bytes']} bytes on disk, "
                    f"~{entry['decoded_mib']} MiB decoded) -> {p['managed_original_ref']}"
                )
            else:
                print(f"[{status}] {case}: {entry['failed']}")

    # ---- control: Qt built-in default reproduces F2 verbatim -----------
    # NOTE: this deliberately does NOT go through QtImageDecoder — the
    # fixed decoder re-asserts 2047 MiB before every read, which would mask
    # the 256 MiB default. The raw QImageReader read below is exactly the
    # pre-fix code path that produced the TA3-B2 F2 failures.
    #
    # r1 R3: each control case now also carries a positive arm — the same
    # raw reader reading the same bytes at 2047 MiB must succeed, so within
    # the control pass the allocation limit is the only variable.
    control: dict = {}
    for case, path in CASES.items():
        data = path.read_bytes()

        native_stderr: list[str] = []
        QImageReader.setAllocationLimit(256)  # the unfixed Qt default (F2)
        buffer = QBuffer()
        buffer.setData(QByteArray(data))
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        reader = QImageReader(buffer)
        declared = reader.size()  # header-declared size, before any read
        with _capture_native_stderr(native_stderr):
            image = reader.read()

        if image.isNull():
            case_control: dict = {
                "rejected": True,
                "detail": reader.errorString(),
                "declared_mib": round(declared.width() * declared.height() * 4 / _MIB, 1),
                "native_stderr": native_stderr[0],
            }
            print(f"[CTRL] {case}: rejected at 256 MiB limit, errorString={case_control['detail']!r}")
        else:
            case_control = {
                "rejected": False,
                "native_stderr": native_stderr[0],
            }
            print(f"[CTRL] {case}: unexpectedly decoded at 256 MiB limit")

        # positive arm (r1 R3): same raw reader, same bytes, limit 2047.
        QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)
        buffer_ok = QBuffer()
        buffer_ok.setData(QByteArray(data))
        buffer_ok.open(QIODevice.OpenModeFlag.ReadOnly)
        reader_ok = QImageReader(buffer_ok)
        image_ok = reader_ok.read()
        if image_ok.isNull():
            case_control["at_2047_same_reader_same_bytes"] = {
                "decoded": False,
                "detail": reader_ok.errorString(),
            }
            print(f"[CTRL+] {case}: UNEXPECTEDLY rejected at {_ALLOCATION_LIMIT_MIB} MiB")
        else:
            case_control["at_2047_same_reader_same_bytes"] = {
                "decoded": True,
                "width": image_ok.width(),
                "height": image_ok.height(),
            }
            print(
                f"[CTRL+] {case}: decoded at {_ALLOCATION_LIMIT_MIB} MiB "
                f"({image_ok.width()}x{image_ok.height()}) — limit is the only variable"
            )

        control[case] = case_control

    results["control_qt_default_256"] = control

    # restore the fixed bound so the process cannot leak the lower default
    QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)

    passed = all(
        entry["imported"] and not entry["failed"]
        for entry in results["cases"].values()
    ) and all(
        v["rejected"] and v["at_2047_same_reader_same_bytes"]["decoded"]
        for v in results["control_qt_default_256"].values()
    )
    results["verdict"] = "PASS" if passed else "FAIL"

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"evidence written: {args.out}")

    print(f"verdict: {results['verdict']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
