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

and logs, per case, the committed page dimensions / mime / managed ref —
the exact fields TA3-B2 could not obtain when Qt's built-in 256 MiB default
rejected these files at import (F2).

A control pass repeats the raw decode at Qt's built-in default (256 MiB) to
archive the original F2 failure verbatim, upgrading the TA3-B2 "inferred"
F2 caliber to first-hand evidence (AC4).

Read-only on the assets: source files are only read, never written
(D07 §37). Run with the main venv from the repo root:

    PYTHONPATH=src python experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py \
        --out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="write JSON evidence here")
    args = parser.parse_args()

    from PySide6.QtGui import QImageReader

    from application.importing.images.service import ImportImagesUseCase
    from application.importing.images.ports import ImportSource
    from infrastructure.filesystem.managed_storage import ManagedFileStorage
    from infrastructure.importing import QtImageDecoder, ManagedCopyStoreAdapter, _ALLOCATION_LIMIT_MIB

    missing = [case for case, path in CASES.items() if not path.is_file()]
    if missing:
        print(f"FATAL: missing real assets: {missing}", file=sys.stderr)
        return 2

    results = {"schema_version": 1, "task": "M2-IMPORT-ALLOC-LIMIT", "cases": {}}

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
            results["cases"][case] = entry
            ok = bool(entry["imported"]) and not entry["failed"]
            status = "OK " if ok else "FAIL"
            if entry["imported"]:
                p = entry["imported"][0]
                print(
                    f"[{status}] {case}: {p['width']}x{p['height']} "
                    f"({entry['source_size_bytes']} bytes on disk) -> {p['managed_original_ref']}"
                )
            else:
                print(f"[{status}] {case}: {entry['failed']}")

    # ---- control: Qt built-in default reproduces F2 verbatim -----------
    # NOTE: this deliberately does NOT go through QtImageDecoder — the
    # fixed decoder re-asserts 2047 MiB before every read, which would mask
    # the 256 MiB default. The raw QImageReader read below is exactly the
    # pre-fix code path that produced the TA3-B2 F2 failures.
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice

    results["control_qt_default_256"] = {}
    for case, path in CASES.items():
        QImageReader.setAllocationLimit(256)  # the unfixed Qt default (F2)
        buffer = QBuffer()
        buffer.setData(QByteArray(path.read_bytes()))
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        reader = QImageReader(buffer)
        image = reader.read()
        if image.isNull():
            detail = reader.errorString()
            results["control_qt_default_256"][case] = {
                "rejected": True,
                "detail": detail,
            }
            print(f"[CTRL] {case}: rejected at 256 MiB limit, errorString={detail!r}")
        else:
            results["control_qt_default_256"][case] = {"rejected": False}
            print(f"[CTRL] {case}: unexpectedly decoded at 256 MiB limit")

    # restore the fixed bound so the process cannot leak the lower default
    QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)

    passed = all(
        entry["imported"] and not entry["failed"]
        for entry in results["cases"].values()
    ) and all(v["rejected"] for v in results["control_qt_default_256"].values())
    results["verdict"] = "PASS" if passed else "FAIL"

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"evidence written: {args.out}")

    print(f"verdict: {results['verdict']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
