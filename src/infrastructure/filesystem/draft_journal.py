"""Atomic, app-owned draft journal and commit receipts (C-13 R-JOURNAL/R-RECEIPT)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import errno
import json
import os
from pathlib import Path
import re
import shutil
import uuid
from typing import Any, Mapping

from domain.drafts.entities import Draft, DraftStatus


_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_RECEIPT_NAME = re.compile(r"^(?P<draft>[A-Za-z0-9_-]{1,128})\.(?P<seq>\d+)\.json$")


def _read_lock_owner(lock_path: Path) -> int | None:
    try:
        return int((lock_path / "pid").read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        return None


def _process_is_alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        still_active = 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            # Unknown owner (permissions): be conservative and treat it as alive.
            return True
        exit_code = ctypes.c_ulong(0)
        try:
            ok = kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        finally:
            kernel32.CloseHandle(handle)
        return bool(ok) and exit_code.value == still_active
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True

_SHARED_LOCKS: dict[str, list] = {}


class DraftJournalError(OSError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class DraftJournal:
    """Own only files below the dedicated drafts directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.receipts_root = self.root / "receipts"
        self.recovery_notices: list[str] = []
        self.durability_limitations: list[str] = []
        if os.name == "nt":
            self.durability_limitations.append(
                "windows-directory-fsync-unavailable; os.replace durability retained"
            )
        self._lock_file = None
        self._lock_key = None
        self.available = True
        self.startup_error: DraftJournalError | None = None
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            if self.root.is_symlink() or not self.root.is_dir():
                raise DraftJournalError("DRAFT_JOURNAL_UNWRITABLE", "draft journal root is unsafe")
            self.receipts_root.mkdir(parents=True, exist_ok=True)
            if self.receipts_root.is_symlink() or not self.receipts_root.is_dir():
                raise DraftJournalError("DRAFT_JOURNAL_UNWRITABLE", "draft receipt root is unsafe")
            self._acquire_writer_lock()
            self._probe_writable()
            self.cleanup_temporary_files()
        except DraftJournalError as error:
            # FEA-03: a second Core (another process) must still START and
            # serve read-only work; only journal WRITES fail closed, so the
            # lock conflict is recorded instead of raised (AC17 write-level).
            self.available = False
            self.startup_error = error
            self.available = False
            self.startup_error = error
        except OSError as error:
            self.available = False
            self.startup_error = DraftJournalError(
                "DRAFT_JOURNAL_UNWRITABLE", "draft journal directory is unavailable"
            )

    def _acquire_writer_lock(self) -> None:
        lock_path = self.root / ".lock"
        key = str(lock_path.resolve()).lower()
        shared = _SHARED_LOCKS.get(key)
        if shared is not None:
            shared[1] += 1
            self._lock_file = shared[0]
            self._lock_key = key
            return
        try:
            lock_path.mkdir()
        except FileExistsError as error:
            owner = _read_lock_owner(lock_path)
            if owner is not None and not _process_is_alive(owner):
                # Crashed writer left the lock behind: reclaim it (the old
                # process is gone, so nobody holds the journal).
                shutil.rmtree(lock_path, ignore_errors=True)
                try:
                    lock_path.mkdir()
                except OSError as retry_error:
                    raise DraftJournalError(
                        "DRAFT_JOURNAL_LOCKED", "another Core instance owns the draft journal"
                    ) from retry_error
            else:
                raise DraftJournalError(
                    "DRAFT_JOURNAL_LOCKED", "another Core instance owns the draft journal"
                ) from error
        except OSError as error:
            raise DraftJournalError(
                "DRAFT_JOURNAL_UNWRITABLE", "draft journal lock is unavailable"
            ) from error
        try:
            (lock_path / "pid").write_text(str(os.getpid()), encoding="ascii")
        except OSError:
            pass
        _SHARED_LOCKS[key] = [lock_path, 1]
        self._lock_file = lock_path
        self._lock_key = key

    def _probe_writable(self) -> None:
        probe = self.root / (".probe-" + uuid.uuid4().hex + ".tmp")
        try:
            with probe.open("xb") as stream:
                stream.write(b"")
                stream.flush()
                os.fsync(stream.fileno())
        finally:
            try:
                probe.unlink()
            except FileNotFoundError:
                pass

    def close(self) -> None:
        handle = self._lock_file
        key = self._lock_key
        self._lock_file = None
        self._lock_key = None
        if handle is None:
            return
        if key is not None:
            shared = _SHARED_LOCKS.get(key)
            if shared is not None and shared[0] == handle:
                shared[1] -= 1
                if shared[1] > 0:
                    return
                _SHARED_LOCKS.pop(key, None)
        try:
            (handle / "pid").unlink()
        except OSError:
            pass
        try:
            handle.rmdir()
        except OSError:
            pass

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:  # noqa: BLE001 - interpreter shutdown may close handles first
            pass

    def cleanup_temporary_files(self) -> list[str]:
        removed: list[str] = []
        for folder in (self.root, self.receipts_root):
            try:
                candidates = list(folder.glob("*.tmp"))
            except OSError:
                continue
            for path in candidates:
                try:
                    if path.is_file() and not path.is_symlink():
                        path.unlink()
                        removed.append(path.name)
                except OSError:
                    self.recovery_notices.append(f"temporary-file-cleanup-failed:{path.name}")
        return removed

    def write_draft(
        self, draft: Draft, *, commit_intent: Mapping[str, Any] | None = None
    ) -> None:
        self._ensure_available()
        target = self._draft_path(draft.draft_id)
        payload = draft.to_json()
        if commit_intent is not None:
            payload["commitIntent"] = dict(commit_intent)
        self._atomic_json_write(target, payload)

    def read_draft_record(self, draft_id: str) -> dict[str, Any] | None:
        path = self._draft_path(draft_id)
        if path.is_symlink():
            self.recovery_notices.append(f"symlink-journal-skipped:{path.name}")
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except FileNotFoundError:
            return None
        except (OSError, UnicodeError, json.JSONDecodeError):
            self._discard_corrupt(path)
            return None

    def load_drafts(
        self, *, active_session_ids: set[str] | None = None
    ) -> list[tuple[Draft, dict[str, Any] | None]]:
        if not self.available:
            return []
        recovered: list[tuple[Draft, dict[str, Any] | None]] = []
        for path in self.root.glob("*.json"):
            if path.parent != self.root or not _SAFE_ID.fullmatch(path.stem):
                continue
            if path.is_symlink():
                self.recovery_notices.append(f"symlink-journal-skipped:{path.name}")
                continue
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(raw, dict):
                    raise ValueError("journal record must be an object")
                draft = Draft.from_json(raw)
                if active_session_ids is not None and draft.session_id not in active_session_ids:
                    draft.status = DraftStatus.DISCARDED
                    draft.saved_at = _utc_now()
                    self.write_draft(draft)
                    self.delete_receipts(draft.draft_id)
                    self.recovery_notices.append(f"orphan-discarded:{draft.draft_id}")
                    continue
                if draft.status not in (DraftStatus.DISCARDED, DraftStatus.CONFLICTED):
                    draft.status = DraftStatus.ACTIVE
                recovered.append((draft, raw.get("commitIntent")))
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                self._discard_corrupt(path)
        return recovered

    def clear_commit_intent(self, draft: Draft) -> None:
        self.write_draft(draft)

    def read_receipt(self, draft_id: str, sequence: int) -> dict[str, Any] | None:
        path = self._receipt_path(draft_id, sequence)
        if path.is_symlink():
            self.recovery_notices.append(f"symlink-receipt-treated-as-missing:{path.name}")
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except FileNotFoundError:
            return None
        except (OSError, UnicodeError, json.JSONDecodeError):
            self.recovery_notices.append(f"corrupt-receipt-treated-as-missing:{path.name}")
            return None

    def write_receipt(self, receipt: Mapping[str, Any]) -> None:
        draft_id = str(receipt["DraftId"])
        sequence = receipt["DraftSequence"]
        self._atomic_json_write(self._receipt_path(draft_id, sequence), dict(receipt))

    def delete_draft(self, draft_id: str) -> None:
        path = self._draft_path(draft_id)
        if path.is_symlink():
            self.recovery_notices.append(f"symlink-journal-delete-skipped:{path.name}")
            return
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def delete_receipts(self, draft_id: str) -> None:
        self._validate_id(draft_id)
        for path in self.receipts_root.glob(f"{draft_id}.*.json"):
            if path.is_file() and not path.is_symlink():
                try:
                    path.unlink()
                except OSError:
                    self.recovery_notices.append(f"receipt-cleanup-failed:{path.name}")

    def cleanup_receipts(self, *, now: datetime | None = None) -> list[str]:
        if not self.available:
            return []
        current = now or datetime.now(timezone.utc)
        cutoff = current - timedelta(days=7)
        removed: list[str] = []
        activity: dict[str, tuple[datetime, str]] = {}
        for path in self.root.glob("*.json"):
            if not _SAFE_ID.fullmatch(path.stem):
                continue
            if path.is_symlink():
                continue
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                saved = _parse_time(record.get("savedAt"))
                if saved is not None:
                    activity[path.stem] = (saved, str(record.get("status", "active")))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
        for path in self.receipts_root.glob("*.json"):
            if not _RECEIPT_NAME.fullmatch(path.name):
                continue
            match = _RECEIPT_NAME.fullmatch(path.name)
            assert match is not None
            draft_id = match.group("draft")
            last_activity, status = activity.get(draft_id, (None, ""))
            if path.is_symlink():
                continue
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                committed = _parse_time(record.get("committedAt"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                committed = None
            expired = (last_activity is not None and last_activity < cutoff) or (
                last_activity is None and committed is not None and committed < cutoff
            )
            if status == DraftStatus.DISCARDED.value or expired:
                try:
                    path.unlink()
                    removed.append(path.name)
                except OSError:
                    self.recovery_notices.append(f"receipt-cleanup-failed:{path.name}")
        return removed

    def _draft_path(self, draft_id: str) -> Path:
        self._validate_id(draft_id)
        return self.root / f"{draft_id}.json"

    def _receipt_path(self, draft_id: str, sequence: int) -> Path:
        self._validate_id(draft_id)
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise ValueError("DraftSequence must be non-negative")
        return self.receipts_root / f"{draft_id}.{sequence}.json"

    @staticmethod
    def _validate_id(draft_id: str) -> None:
        if not _SAFE_ID.fullmatch(draft_id):
            raise ValueError("DraftId is not a safe file name")

    def _ensure_available(self) -> None:
        if not self.available:
            raise DraftJournalError(
                "DRAFT_JOURNAL_UNWRITABLE", "draft journal is not writable"
            ) from self.startup_error

    def _atomic_json_write(self, target: Path, payload: Mapping[str, Any]) -> None:
        self._ensure_available()
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.parent.is_symlink() or not target.parent.is_dir():
                raise OSError("draft journal parent is unsafe")
            temp = target.parent / (target.name + "." + uuid.uuid4().hex + ".tmp")
            data = json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            with temp.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, target)
            self._fsync_directory(target.parent)
        except OSError as error:
            raise DraftJournalError(
                "DRAFT_JOURNAL_UNWRITABLE", "draft journal write failed"
            ) from error

    def _fsync_directory(self, directory: Path) -> None:
        if os.name == "nt":
            marker = "windows-directory-fsync-unavailable; os.replace durability retained"
            if marker not in self.durability_limitations:
                self.durability_limitations.append(marker)
            return
        try:
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        except OSError as error:
            self.durability_limitations.append(
                f"directory-fsync-unavailable:{error.__class__.__name__}"
            )

    def _discard_corrupt(self, path: Path) -> None:
        self.recovery_notices.append(f"corrupt-journal-discarded:{path.name}")
        try:
            if path.is_file() and not path.is_symlink():
                path.unlink()
        except OSError:
            pass


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")

