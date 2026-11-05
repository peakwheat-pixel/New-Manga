"""FEA-12-DSIM-1: D-flow simulation slice — typed contract, simulated bin,
isolation/sentinel proof and static禁令 scans.

Mapping to the task card ACs:

- AC1 protocol + production default: structural protocol checks, the
  fail-closed default is typed-unavailable with zero file/journal/database
  operations, and no production file references the port (no Host/UI wiring).
- AC2 simulated implementation: the simulated bin only moves inside the
  isolated root, keeps an auditable manifest and journals attempt + receipt.
- AC3 failure semantics: an injected refusal keeps the original bytes and
  path, the result is typed per item, and a static AST scan proves neither
  module has a permanent-delete/database fallback ("D 失败不得降级 C").
- AC4 isolation: zero Windows recycle-bin API tokens in ``src/**`` and
  ``apps/**``; a runtime sentinel outside the isolated root is byte-identical
  before/after success *and* failure runs; the test sources themselves carry
  no app-data environment-variable names, real volume paths or real
  recycle-bin locations.

All fixtures are pytest ``tmp_path`` based; nothing here touches user data,
AppData, a real volume root or a real recycle bin.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance.recycle_gateway import (  # noqa: E402
    FAILURE_REASONS,
    ITEM_STATUSES,
    OriginalFileRecycleGateway,
    REASON_GATEWAY_UNAVAILABLE,
    REASON_INVALID_REQUEST,
    REASON_IN_USE,
    REASON_OUTSIDE_ISOLATED_ROOT,
    REASON_PATH_NOT_FOUND,
    REASON_RECYCLE_REJECTED,
    STATUS_FAILED,
    STATUS_MOVED,
    STATUS_NOT_STARTED,
    RecycleEntry,
    RecycleItemOutcome,
    RecycleJournal,
    RecycleOutcome,
    UnavailableOriginalFileRecycleGateway,
)
from infrastructure.filesystem.simulated_recycle_bin import (  # noqa: E402
    BIN_DIR_NAME,
    GATEWAY_NAME,
    JOURNAL_NAME,
    MANIFEST_FORMAT,
    MANIFEST_NAME,
    JsonLinesRecycleJournal,
    SimulatedRecycleBin,
    UnsafeIsolatedRootError,
)

APPLICATION_MODULE = SRC_ROOT / "application" / "maintenance" / "recycle_gateway.py"
SIMULATED_MODULE = (
    SRC_ROOT / "infrastructure" / "filesystem" / "simulated_recycle_bin.py"
)

#: Windows recycle-bin APIs / bindings that must never appear in production
#: source (SHFileOperation, IFileOperation, Shell32, Microsoft.VisualBasic,
#: Windows.Storage and their Python wrappers).
WINDOWS_RECYCLE_API_TOKENS: tuple[str, ...] = (
    "shfileoperation",
    "shfileopstruct",
    "ifileoperation",
    "ifileoperationprogresssink",
    "shell32",
    "microsoft.visualbasic",
    "windows.storage",
    "send2trash",
    "winshell",
    "win32com",
    "shell.application",
    "fof_allowundo",
)

SOURCE_SUFFIXES = {
    ".py",
    ".cs",
    ".csproj",
    ".props",
    ".targets",
    ".xaml",
    ".ps1",
}

_EXCLUDED_DIRS = {
    "bin",
    "obj",
    "target",
    "dist",
    "build",
    "__pycache__",
    ".git",
    ".vs",
    "node_modules",
    "testresults",
    ".pytest_cache",
    ".venv",
    "site-packages",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _same_path(left: str | Path, right: str | Path) -> bool:
    """Case/normalisation-insensitive same-path comparison (Windows)."""
    return os.path.normcase(os.path.abspath(str(left))) == os.path.normcase(
        os.path.abspath(str(right))
    )


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def _tree_snapshot(
    root: Path, *, exclude: Path | None = None
) -> dict[str, tuple[str, int, str]]:
    """Exact on-disk state of ``root``: relative path → (kind, size, sha256)."""
    snapshot: dict[str, tuple[str, int, str]] = {}
    for path in sorted(root.rglob("*")):
        if exclude is not None and (
            path == exclude or exclude in path.parents
        ):
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = ("dir", 0, "")
        else:
            snapshot[relative] = ("file", path.stat().st_size, _sha256_file(path))
    return snapshot


class _RecordingJournal:
    """In-memory ``RecycleJournal`` probe: proves a gateway never journals."""

    def __init__(self) -> None:
        self.attempts: list = []
        self.receipts: list = []

    def record_attempt(self, attempt) -> None:
        self.attempts.append(attempt)

    def record_receipt(self, receipt) -> None:
        self.receipts.append(receipt)


def _call_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            names.add(function.id)
        elif isinstance(function, ast.Attribute):
            names.add(function.attr)
    return names


def _imported_modules(tree: ast.Module) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _iter_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name for name in dirnames if name.lower() not in _EXCLUDED_DIRS
        ]
        for filename in filenames:
            if Path(filename).suffix.lower() in SOURCE_SUFFIXES:
                files.append(Path(current) / filename)
    return files


def _scan_tokens(text: str, tokens: tuple[str, ...]) -> list[tuple[str, str]]:
    lowered = text.lower()
    hits: list[tuple[str, str]] = []
    for token in tokens:
        if token in lowered:
            hits.append((token, "matched"))
    return hits


# ---------------------------------------------------------------------------
# AC1 — protocol, typed result and fail-closed production default
# ---------------------------------------------------------------------------


def test_protocol_is_structural_and_the_typed_vocabulary_is_closed(
    isolated_root: Path,
) -> None:
    assert isinstance(
        UnavailableOriginalFileRecycleGateway(), OriginalFileRecycleGateway
    )
    assert isinstance(SimulatedRecycleBin(isolated_root), OriginalFileRecycleGateway)
    assert isinstance(JsonLinesRecycleJournal(isolated_root), RecycleJournal)
    assert isinstance(_RecordingJournal(), RecycleJournal)

    signature = inspect.signature(OriginalFileRecycleGateway.move_to_recyclebin)
    assert list(signature.parameters) == ["self", "entries", "journal"]
    journal_parameter = signature.parameters["journal"]
    assert journal_parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert journal_parameter.default is inspect.Parameter.empty
    assert journal_parameter.annotation is not inspect.Parameter.empty

    # closed vocabulary: no free-form status or reason can be constructed
    assert ITEM_STATUSES == {STATUS_MOVED, STATUS_FAILED, STATUS_NOT_STARTED}
    assert REASON_IN_USE in FAILURE_REASONS
    with pytest.raises(ValueError):
        RecycleItemOutcome("req-1", "gone")
    with pytest.raises(ValueError):
        RecycleItemOutcome("req-1", STATUS_FAILED, "some_os_message")
    with pytest.raises(ValueError):
        RecycleItemOutcome("req-1", STATUS_MOVED, REASON_IN_USE)
    with pytest.raises(ValueError):
        RecycleEntry("", str(isolated_root / "x.png"))
    with pytest.raises(ValueError):
        RecycleEntry("req-1", "")


def test_production_default_is_typed_unavailable_with_zero_side_effects(
    isolated_root: Path,
) -> None:
    target = _write(
        isolated_root / "selections" / "art.png", b"USER ORIGINAL BYTES"
    )
    missing = isolated_root / "selections" / "not-there.png"
    before = _tree_snapshot(isolated_root)
    recorder = _RecordingJournal()

    outcome = UnavailableOriginalFileRecycleGateway().move_to_recyclebin(
        [
            RecycleEntry("req-1", str(target)),
            RecycleEntry("req-2", str(missing)),
        ],
        journal=recorder,
    )

    assert outcome.gateway == "unavailable"
    assert outcome.operation_id == ""
    assert (outcome.moved, outcome.failed, outcome.not_started) == (0, 0, 2)
    assert not outcome.complete
    assert outcome.has_failures
    assert [item.status for item in outcome.items] == [STATUS_NOT_STARTED] * 2
    assert {item.reason for item in outcome.items} == {
        REASON_GATEWAY_UNAVAILABLE
    }

    # zero side effects — no filesystem change, no journal write, no bin
    assert _tree_snapshot(isolated_root) == before
    assert target.read_bytes() == b"USER ORIGINAL BYTES"
    assert recorder.attempts == [] and recorder.receipts == []
    assert not (isolated_root / BIN_DIR_NAME).exists()
    assert not (isolated_root / JOURNAL_NAME).exists()

    # safe projection: statuses and reasons only, never a path
    projected = json.dumps(outcome.to_dict())
    assert str(isolated_root) not in projected
    assert "art.png" not in projected


def test_no_production_file_references_the_d_flow_port() -> None:
    """AC1 "no Host/UI wiring": only the port module and the additive
    ``maintenance`` package export may mention these names."""
    port_references: set[str] = set()
    simulated_references: set[str] = set()
    for root in (SRC_ROOT, REPO_ROOT / "apps"):
        for path in _iter_source_files(root):
            text = path.read_text(encoding="utf-8", errors="replace")
            relative = path.relative_to(REPO_ROOT).as_posix()
            if "OriginalFileRecycleGateway" in text:
                port_references.add(relative)
            if "SimulatedRecycleBin" in text:
                simulated_references.add(relative)
    assert port_references == {
        "src/application/maintenance/recycle_gateway.py",
        "src/application/maintenance/__init__.py",
        # the simulation module mentions the port by name in its docstring to
        # document which contract it implements; it is the test double, not a
        # production wiring point (it is never imported by src/apps code)
        "src/infrastructure/filesystem/simulated_recycle_bin.py",
    }
    assert simulated_references == {
        # both are docstring cross-references between the port and its test
        # double; no production module mentions or imports either name
        "src/application/maintenance/recycle_gateway.py",
        "src/infrastructure/filesystem/simulated_recycle_bin.py",
    }


# ---------------------------------------------------------------------------
# AC2 — simulated implementation inside the isolated root, auditable manifest
# ---------------------------------------------------------------------------


def test_simulated_move_is_auditable_and_keeps_original_path_semantics(
    isolated_root: Path,
) -> None:
    file_source = _write(
        isolated_root / "user-sources" / "page-01.png", b"PAGE ONE"
    )
    folder_source = isolated_root / "user-sources" / "chapter-02"
    _write(folder_source / "page-02.png", b"PAGE TWO")
    _write(folder_source / "page-03.png", b"PAGE THREE")
    journal = JsonLinesRecycleJournal(isolated_root)
    simulated = SimulatedRecycleBin(
        isolated_root, clock=lambda: "2026-11-05T00:00:00.000000+00:00"
    )

    outcome = simulated.move_to_recyclebin(
        [
            RecycleEntry("req-file", str(file_source)),
            RecycleEntry("req-folder", str(folder_source)),
        ],
        journal=journal,
    )

    assert outcome.gateway == GATEWAY_NAME
    assert outcome.complete and outcome.moved == 2
    assert {item.status for item in outcome.items} == {STATUS_MOVED}
    assert {item.reason for item in outcome.items} == {""}
    assert outcome.operation_id

    # original-path semantics: the exact selection is gone from its place, the
    # moved copy lives under the simulated bin and still holds the same bytes
    assert not file_source.exists()
    assert not folder_source.exists()
    entries = {entry.request_id: entry for entry in simulated.list_entries()}
    assert set(entries) == {"req-file", "req-folder"}
    file_entry = entries["req-file"]
    assert _same_path(file_entry.original_path, file_source)
    assert file_entry.kind == "file"
    assert file_entry.size_bytes == len(b"PAGE ONE")
    assert file_entry.sha256 == hashlib.sha256(b"PAGE ONE").hexdigest()
    assert file_entry.moved_at == "2026-11-05T00:00:00.000000+00:00"
    stored_file = Path(file_entry.stored_path)
    assert stored_file.read_bytes() == b"PAGE ONE"
    assert _same_path(stored_file.parent, simulated.bin_dir)
    folder_entry = entries["req-folder"]
    assert folder_entry.kind == "directory"
    stored_folder = Path(folder_entry.stored_path)
    assert stored_folder.is_dir()
    assert (stored_folder / "page-02.png").read_bytes() == b"PAGE TWO"
    assert (stored_folder / "page-03.png").read_bytes() == b"PAGE THREE"
    for entry in entries.values():
        assert _same_path(Path(entry.stored_path).parent, simulated.bin_dir)

    # the manifest itself is a self-describing, valid JSON file inside the root
    assert _same_path(
        simulated.manifest_path,
        isolated_root / BIN_DIR_NAME / MANIFEST_NAME,
    )
    manifest = simulated.read_manifest()
    assert manifest["format"] == MANIFEST_FORMAT
    assert json.loads(
        simulated.manifest_path.read_text(encoding="utf-8")
    ) == manifest

    # SC-34 journal: attempt first (exact paths), receipt after verification
    records = journal.read_records()
    assert [record["record_type"] for record in records] == [
        "attempt",
        "receipt",
    ]
    attempt, receipt = records
    assert attempt["operation_id"] == receipt["operation_id"] == outcome.operation_id
    assert {
        entry["path"] for entry in attempt["entries"]
    } == {str(file_source), str(folder_source)}
    assert [item["status"] for item in receipt["items"]] == [
        STATUS_MOVED,
        STATUS_MOVED,
    ]


def test_empty_selection_is_an_empty_typed_outcome(isolated_root: Path) -> None:
    journal = JsonLinesRecycleJournal(isolated_root)
    outcome = SimulatedRecycleBin(isolated_root).move_to_recyclebin(
        [], journal=journal
    )
    assert outcome.items == ()
    assert (outcome.moved, outcome.failed, outcome.not_started) == (0, 0, 0)
    assert not outcome.complete
    assert not (isolated_root / BIN_DIR_NAME).exists()
    # the attempt/receipt pair is still journalled (auditable no-op)
    assert [record["record_type"] for record in journal.read_records()] == [
        "attempt",
        "receipt",
    ]


def test_simulated_bin_refuses_non_isolated_roots(tmp_path: Path) -> None:
    with pytest.raises(UnsafeIsolatedRootError, match="already exist"):
        SimulatedRecycleBin(tmp_path / "does-not-exist")
    with pytest.raises(UnsafeIsolatedRootError, match="recycle-bin"):
        real_looking = tmp_path / ("$Recycle" + ".Bin")
        real_looking.mkdir()
        SimulatedRecycleBin(real_looking)
    not_a_directory = tmp_path / "a-file.txt"
    not_a_directory.write_text("not a root", encoding="utf-8")
    with pytest.raises(UnsafeIsolatedRootError, match="directory"):
        SimulatedRecycleBin(not_a_directory)


# ---------------------------------------------------------------------------
# AC3 — failure semantics: original preserved, typed per item, no C fallback
# ---------------------------------------------------------------------------


def test_failure_injection_keeps_original_bytes_and_never_deletes(
    isolated_root: Path,
) -> None:
    moved_source = _write(
        isolated_root / "user-sources" / "good.png", b"GOOD ORIGINAL"
    )
    refused_source = _write(
        isolated_root / "user-sources" / "locked.png", b"LOCKED ORIGINAL"
    )

    def inject(entry: RecycleEntry) -> str | None:
        if entry.request_id == "req-locked":
            return REASON_IN_USE
        return None

    journal = JsonLinesRecycleJournal(isolated_root)
    simulated = SimulatedRecycleBin(isolated_root, failure_injector=inject)
    before = _tree_snapshot(isolated_root)

    outcome = simulated.move_to_recyclebin(
        [
            RecycleEntry("req-good", str(moved_source)),
            RecycleEntry("req-locked", str(refused_source)),
        ],
        journal=journal,
    )

    assert (outcome.moved, outcome.failed, outcome.not_started) == (1, 1, 0)
    good_item, locked_item = outcome.items
    assert (good_item.status, good_item.reason) == (STATUS_MOVED, "")
    assert (locked_item.status, locked_item.reason) == (
        STATUS_FAILED,
        REASON_IN_USE,
    )
    # the failed item keeps its original file and bytes — not deleted
    assert refused_source.exists()
    assert refused_source.read_bytes() == b"LOCKED ORIGINAL"
    # only the good item entered the bin; the failed one was never catalogued
    assert [entry.request_id for entry in simulated.list_entries()] == [
        "req-good"
    ]
    # nothing else left its place: the only removed path is the moved item
    after = _tree_snapshot(isolated_root)
    assert set(before) - set(after) == {"user-sources/good.png"}
    assert after["user-sources/locked.png"] == before["user-sources/locked.png"]
    # journal receipt carries the typed failure reason
    receipt = journal.read_records()[-1]
    assert receipt["record_type"] == "receipt"
    reasons = {
        item["request_id"]: item["reason"] for item in receipt["items"]
    }
    assert reasons["req-locked"] == REASON_IN_USE


def test_d_failure_cannot_degrade_to_permanent_delete__static_ast() -> None:
    """Static proof that neither D-flow module can fall back to a permanent
    delete or a database delete: no destructive calls, no DB/OS-process
    imports, and the application port imports no infrastructure at all."""
    destructive_calls = {
        "unlink",
        "rmtree",
        "rmdir",
        "remove",
        "remove_managed",
        "purge_pages",
        "purge_batch",
        "permanently_delete",
        "Popen",
        "system",
    }
    forbidden_modules = (
        "sqlite3",
        "subprocess",
        "ctypes",
        "winreg",
        "pythoncom",
        "win32",
        "send2trash",
        "winshell",
        "shell",
    )
    for module_path in (APPLICATION_MODULE, SIMULATED_MODULE):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        calls = _call_names(tree)
        assert calls & destructive_calls == set(), (
            f"{module_path.name} has a destructive fallback call: "
            f"{sorted(calls & destructive_calls)}"
        )
        imported = _imported_modules(tree)
        for prefix in forbidden_modules:
            assert not any(
                name == prefix or name.startswith(prefix + ".")
                for name in imported
            ), f"{module_path.name} imports forbidden module {prefix!r}"
    # the application port is infrastructure-free (layer rule)
    application_imports = _imported_modules(
        ast.parse(APPLICATION_MODULE.read_text(encoding="utf-8"))
    )
    assert not any(
        name.startswith(("infrastructure", "bootstrap", "ports"))
        for name in application_imports
    )
    # the fail-closed production default performs zero file operations
    mutating_calls = {
        "open",
        "mkdir",
        "replace",
        "rename",
        "write_text",
        "write_bytes",
        "unlink",
        "rmtree",
        "rmdir",
        "remove",
        "system",
        "Popen",
    }
    production_calls = _call_names(
        ast.parse(APPLICATION_MODULE.read_text(encoding="utf-8"))
    )
    assert production_calls & mutating_calls == set()


def test_missing_selection_is_a_typed_failure_without_side_effects(
    isolated_root: Path,
) -> None:
    journal = JsonLinesRecycleJournal(isolated_root)
    simulated = SimulatedRecycleBin(isolated_root)
    outcome = simulated.move_to_recyclebin(
        [RecycleEntry("req-missing", str(isolated_root / "not-there.png"))],
        journal=journal,
    )
    item = outcome.items[0]
    assert (item.status, item.reason) == (STATUS_FAILED, REASON_PATH_NOT_FOUND)
    assert outcome.complete is False
    assert simulated.list_entries() == ()
    assert not (isolated_root / BIN_DIR_NAME).exists()


# ---------------------------------------------------------------------------
# AC4 — confinement, static scan, runtime sentinel, no real path literals
# ---------------------------------------------------------------------------


def test_paths_outside_the_isolated_root_are_refused(
    isolated_root: Path, outside_tree: Path
) -> None:
    sentinel = outside_tree / "user-sources" / "chapter-01.png"
    before = _tree_snapshot(outside_tree)
    journal = JsonLinesRecycleJournal(isolated_root)
    simulated = SimulatedRecycleBin(isolated_root)
    traversal = isolated_root / ".." / "outside-root" / "user-sources" / "chapter-01.png"

    outcome = simulated.move_to_recyclebin(
        [
            RecycleEntry("req-outside", str(sentinel)),
            RecycleEntry("req-traversal", str(traversal)),
            RecycleEntry("req-relative", "user-sources/page-01.png"),
        ],
        journal=journal,
    )

    assert [item.status for item in outcome.items] == [STATUS_FAILED] * 3
    assert outcome.items[0].reason == REASON_OUTSIDE_ISOLATED_ROOT
    assert outcome.items[1].reason == REASON_OUTSIDE_ISOLATED_ROOT
    assert outcome.items[2].reason == REASON_INVALID_REQUEST
    # zero effect outside the isolated root and nothing entered the bin
    assert _tree_snapshot(outside_tree) == before
    assert sentinel.read_bytes() == b"ORIGINAL PIXELS 01"
    assert simulated.list_entries() == ()
    assert not (isolated_root / BIN_DIR_NAME).exists()


def test_runtime_sentinel_outside_isolated_root_never_changes(
    isolated_root: Path, outside_tree: Path, tmp_path: Path
) -> None:
    """Success and failure runs must leave every path outside the isolated
    root byte-identical (runtime sentinel, not a static claim)."""
    outside_before = _tree_snapshot(tmp_path, exclude=isolated_root)

    success_target = _write(
        isolated_root / "user-sources" / "one.png", b"ONE"
    )
    SimulatedRecycleBin(isolated_root).move_to_recyclebin(
        [RecycleEntry("req-1", str(success_target))],
        journal=JsonLinesRecycleJournal(isolated_root),
    )

    refused_target = _write(
        isolated_root / "user-sources" / "two.png", b"TWO"
    )
    SimulatedRecycleBin(
        isolated_root,
        failure_injector=lambda entry: REASON_RECYCLE_REJECTED,
    ).move_to_recyclebin(
        [RecycleEntry("req-2", str(refused_target))],
        journal=JsonLinesRecycleJournal(isolated_root),
    )

    outside_after = _tree_snapshot(tmp_path, exclude=isolated_root)
    assert outside_after == outside_before
    assert _tree_snapshot(outside_tree) == {
        "notes.txt": outside_before["outside-root/notes.txt"],
        "user-sources": outside_before["outside-root/user-sources"],
        "user-sources/chapter-01.png": outside_before[
            "outside-root/user-sources/chapter-01.png"
        ],
        "user-sources/chapter-02.png": outside_before[
            "outside-root/user-sources/chapter-02.png"
        ],
    }
    # the refused item is still exactly where it was
    assert refused_target.read_bytes() == b"TWO"


def test_static_scan_finds_no_windows_recycle_bin_api() -> None:
    scanned: list[Path] = []
    hits: list[str] = []
    for root in (SRC_ROOT, REPO_ROOT / "apps"):
        for path in _iter_source_files(root):
            scanned.append(path)
            text = path.read_text(encoding="utf-8", errors="replace")
            for token, _ in _scan_tokens(text, WINDOWS_RECYCLE_API_TOKENS):
                hits.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {token}")
    assert len(scanned) > 100, f"scan is suspiciously small: {len(scanned)}"
    assert hits == [], (
        "Windows recycle-bin API reference found in production source "
        "(grep -rIni -E 'SHFileOperation|IFileOperation|Shell32|"
        "Microsoft.VisualBasic|Windows.Storage|send2trash|winshell|win32com|"
        "Shell.Application|FOF_ALLOWUNDO' src apps): " + "; ".join(hits)
    )
    # non-vacuous: the scanner does detect a synthetic occurrence
    synthetic = "shell32" + "." + "SHFileOperation" + "W("
    assert _scan_tokens(synthetic, WINDOWS_RECYCLE_API_TOKENS)


def test_test_sources_reference_no_real_path_literals() -> None:
    """The tests must build every path from ``tmp_path``; no environment
    variable, real volume path or real recycle-bin location may appear."""
    # fragments keep the forbidden literals out of this file while still
    # letting the detector be checked against synthetic samples below
    env_appdata = "%" + "APPDATA" + "%"
    env_local_appdata = "%" + "LOCALAPPDATA" + "%"
    env_userprofile = "%" + "USERPROFILE" + "%"
    powershell_appdata = "$" + "env:" + "APPDATA"
    real_recycle_bin = "$Recycle" + ".Bin"
    drive_path = re.compile(
        "(?<![A-Za-z0-9_])" + "[A-Za-z]" + ":" + r"[\\/]"
    )
    needles = {
        "environment variable (roaming app data)": env_appdata,
        "environment variable (local app data)": env_local_appdata,
        "environment variable (user profile)": env_userprofile,
        "PowerShell roaming app-data variable": powershell_appdata,
        "real recycle-bin folder": real_recycle_bin,
    }

    test_files = sorted(Path(__file__).resolve().parent.glob("*.py"))
    assert len(test_files) >= 2
    problems: list[str] = []
    for path in test_files:
        text = path.read_text(encoding="utf-8")
        for label, needle in needles.items():
            if needle in text:
                problems.append(f"{path.name}: {label}")
        for match in drive_path.finditer(text):
            problems.append(f"{path.name}: volume path {match.group(0)!r}")
    assert problems == []

    # non-vacuity: every detector fires on a synthetic sample
    samples = [
        "%" + "APPDATA" + "%",
        "%" + "LOCALAPPDATA" + "%",
        "%" + "USERPROFILE" + "%",
        "$" + "env:" + "APPDATA",
        "$Recycle" + ".Bin",
        "Q" + ":" + "\\" + "drive",
    ]
    for label, needle in needles.items():
        assert any(needle in sample for sample in samples), label
    assert drive_path.search(samples[-1])
