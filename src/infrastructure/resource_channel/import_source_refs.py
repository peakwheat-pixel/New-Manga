"""Core-only resolver for host-issued, read-only ImportPages source grants."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import threading
import time
from types import SimpleNamespace

from application.importing.images.sorting import IMAGE_EXTENSIONS, natural_sort_key
from application.resource_channel.dto import (
    ResourceFacts,
    TypedResourceChannelError,
    USER_SOURCE_SCOPE,
    E_EXPIRED,
    E_IDENTITY_CHANGED,
    E_NOT_FOUND,
    E_OUT_OF_SCOPE,
    E_REPARSE,
    E_SCOPE_DENIED,
)
from infrastructure.resource_channel.handle_resolver import HandleVerifiedFileReader

_ID = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
_SIGNATURE = re.compile(r"^[A-Za-z0-9_-]{43}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_IMAGE_AND_PDF = IMAGE_EXTENSIONS | {".pdf"}


@dataclass
class _Entry:
    path: Path
    rel_path: str
    filename: str
    facts: ResourceFacts


@dataclass
class _Grant:
    grant_id: str
    session_id: str
    source_path: Path
    source_kind: str
    scope_identity: tuple[int, int] | None
    entries: tuple[_Entry, ...]
    expires_at: float
    signing_key: bytes
    signature: str
    revoked: bool = False
    consumed: bool = False


class ResolvedImportFile:
    def __init__(self, entry: _Entry, handle) -> None:
        self.filename = entry.filename
        self.facts = entry.facts
        self._handle = handle
        self._data: bytes | None = None

    def read(self) -> bytes:
        if self._data is None:
            try:
                self._data = self._handle.read()
            except TypedResourceChannelError as error:
                raise OSError("verified import source read failed") from error
        return self._data

    def verify(self) -> None:
        self._handle.verify()

    @property
    def data(self) -> bytes | None:
        return self._data

    def release_data(self) -> None:
        self._data = None

    def close(self) -> None:
        self._handle.close()


@dataclass
class ResolvedImportSelection:
    source_index: int
    source_name: str
    files: list[ResolvedImportFile]

    def close(self) -> None:
        for file in self.files:
            file.close()


class ImportSourceGrantRegistry:
    """Validates opaque ImportSourceRef values and pins selected sources."""

    def __init__(self, *, clock=time.time) -> None:
        self._clock = clock
        self._lock = threading.RLock()
        self._grants: dict[str, _Grant] = {}
        self._session_id: str | None = None

    def register(
        self,
        *,
        grant_id: str,
        session_id: str,
        scope_class: str,
        operation: str,
        access: str,
        source_path: str,
        source_kind: str,
        scope_identity: list[int] | None,
        entries: list[dict],
        expires_at: float,
        signing_key: bytes,
        signature: str,
    ) -> None:
        if (
            not isinstance(grant_id, str) or not _ID.fullmatch(grant_id)
            or not isinstance(session_id, str) or not session_id
            or not isinstance(source_kind, str) or source_kind not in {"file", "directory"}
            or not isinstance(source_path, str) or not source_path
            or isinstance(expires_at, bool) or not isinstance(expires_at, (int, float))
            or not math.isfinite(expires_at)
            or not isinstance(signing_key, bytes) or len(signing_key) < 32
            or not isinstance(signature, str) or not _SIGNATURE.fullmatch(signature)
            or not isinstance(entries, list)
            or (scope_identity is not None and (
                not isinstance(scope_identity, list) or len(scope_identity) != 2
                or any(isinstance(value, bool) or not isinstance(value, int) or value < 0
                       for value in scope_identity)
            ))
        ):
            raise TypedResourceChannelError("REF_MALFORMED")
        if (
            scope_class != USER_SOURCE_SCOPE
            or operation != "ImportPages"
            or access != "read-only"
        ):
            raise TypedResourceChannelError(E_SCOPE_DENIED)

        path = self._absolute_path(source_path)
        now = self._clock()
        if expires_at <= now or expires_at > now + 300:
            raise TypedResourceChannelError(E_EXPIRED)
        if source_kind == "directory" and scope_identity is None:
            raise TypedResourceChannelError("REF_MALFORMED")

        parsed_entries: list[_Entry] = []
        for item in entries:
            if not isinstance(item, dict) or set(item) != {"path", "facts"}:
                raise TypedResourceChannelError("REF_MALFORMED")
            entry_path = self._absolute_path(item["path"])
            facts = self._facts(item["facts"])
            if source_kind == "file":
                if len(entries) != 1 or self._norm(entry_path) != self._norm(path):
                    raise TypedResourceChannelError(E_SCOPE_DENIED)
                if entry_path.suffix.lower() not in _IMAGE_AND_PDF:
                    raise TypedResourceChannelError(E_SCOPE_DENIED)
            else:
                if self._norm(entry_path.parent) != self._norm(path):
                    raise TypedResourceChannelError("REF_OUT_OF_SCOPE")
                if entry_path.suffix.lower() not in IMAGE_EXTENSIONS:
                    raise TypedResourceChannelError(E_SCOPE_DENIED)
            parsed_entries.append(_Entry(
                entry_path, self._relative_to_volume(entry_path), entry_path.name, facts
            ))
        if source_kind == "file" and len(parsed_entries) != 1:
            raise TypedResourceChannelError("REF_MALFORMED")
        if source_kind == "directory":
            names = [entry.filename for entry in parsed_entries]
            if names != sorted(names, key=natural_sort_key):
                raise TypedResourceChannelError("REF_MALFORMED")

        fields = self._signed_fields(
            grant_id, session_id, path, source_kind, scope_identity, parsed_entries,
            float(expires_at),
        )
        expected = self._sign(signing_key, fields)
        if not hmac.compare_digest(signature, expected):
            raise TypedResourceChannelError("REF_SIGNATURE_INVALID")

        with self._lock:
            if self._session_id is None:
                self._session_id = session_id
            elif self._session_id != session_id:
                raise TypedResourceChannelError(E_SCOPE_DENIED)
            if grant_id in self._grants:
                raise TypedResourceChannelError("REF_UNKNOWN_ID")
            self._grants[grant_id] = _Grant(
                grant_id, session_id, path, source_kind,
                tuple(scope_identity) if scope_identity is not None else None,
                tuple(parsed_entries), float(expires_at), signing_key, signature,
            )

    def revoke(self, grant_id: str) -> None:
        with self._lock:
            grant = self._grants.get(grant_id)
            if grant is None:
                raise TypedResourceChannelError("REF_UNKNOWN_ID")
            grant.revoked = True

    def resolve_many(self, references: object) -> list[ResolvedImportSelection]:
        if not isinstance(references, list) or not references:
            raise TypedResourceChannelError("REF_MALFORMED")
        parsed: list[tuple[str, str]] = []
        for reference in references:
            if (
                not isinstance(reference, dict)
                or set(reference) != {"grant_id", "host_signature"}
                or not isinstance(reference.get("grant_id"), str)
                or not _ID.fullmatch(reference["grant_id"])
                or not isinstance(reference.get("host_signature"), str)
                or not _SIGNATURE.fullmatch(reference["host_signature"])
            ):
                raise TypedResourceChannelError("REF_MALFORMED")
            parsed.append((reference["grant_id"], reference["host_signature"]))

        if len({grant_id for grant_id, _ in parsed}) != len(parsed):
            raise TypedResourceChannelError("REF_ALREADY_CONSUMED")

        opened: list[ResolvedImportSelection] = []
        with self._lock:
            grants: list[_Grant] = []
            for grant_id, signature in parsed:
                grant = self._grants.get(grant_id)
                if grant is None:
                    raise TypedResourceChannelError("REF_UNKNOWN_ID")
                fields = self._signed_fields(
                    grant.grant_id, grant.session_id, grant.source_path,
                    grant.source_kind, list(grant.scope_identity) if grant.scope_identity else None,
                    grant.entries, grant.expires_at,
                )
                if (
                    not hmac.compare_digest(signature, self._sign(grant.signing_key, fields))
                    or not hmac.compare_digest(signature, grant.signature)
                ):
                    raise TypedResourceChannelError("REF_SIGNATURE_INVALID")
                if grant.session_id != self._session_id:
                    raise TypedResourceChannelError(E_SCOPE_DENIED)
                if grant.expires_at <= self._clock():
                    raise TypedResourceChannelError(E_EXPIRED)
                if grant.revoked:
                    raise TypedResourceChannelError("REF_REVOKED")
                if grant.consumed:
                    raise TypedResourceChannelError("REF_ALREADY_CONSUMED")
                grants.append(grant)

            try:
                for grant in grants:
                    self._validate_scope_object(grant)
                for source_index, grant in enumerate(grants):
                    files: list[ResolvedImportFile] = []
                    selection = ResolvedImportSelection(
                        source_index, grant.source_path.name, files
                    )
                    opened.append(selection)
                    for entry in grant.entries:
                        reader = HandleVerifiedFileReader(
                            entry.path.parent, limit=sys.maxsize
                        )
                        handle = reader.open_pinned(
                            SimpleNamespace(rel_path=entry.rel_path, facts=entry.facts)
                        )
                        files.append(ResolvedImportFile(entry, handle))
                for selection in opened:
                    for file in selection.files:
                        file.verify()
                for grant in grants:
                    grant.consumed = True
                return opened
            except TypedResourceChannelError:
                for selection in opened:
                    selection.close()
                raise
            except (OSError, ValueError) as error:
                for selection in opened:
                    selection.close()
                raise TypedResourceChannelError(E_NOT_FOUND) from error

    def _validate_scope_object(self, grant: _Grant) -> None:
        try:
            self._reject_reparse_path(grant.source_path)
            info = grant.source_path.stat()
        except FileNotFoundError as error:
            raise TypedResourceChannelError(E_NOT_FOUND) from error
        except OSError as error:
            raise TypedResourceChannelError(E_SCOPE_DENIED) from error
        if grant.source_kind == "directory":
            if not stat.S_ISDIR(info.st_mode):
                raise TypedResourceChannelError(E_SCOPE_DENIED)
            if (int(info.st_dev), int(info.st_ino)) != grant.scope_identity:
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
        elif not stat.S_ISREG(info.st_mode):
            raise TypedResourceChannelError(E_SCOPE_DENIED)

    @staticmethod
    def _signed_fields(
        grant_id, session_id, source_path, source_kind, scope_identity,
        entries: tuple[_Entry, ...] | list[_Entry], expires_at,
    ) -> dict:
        return {
            "grant_id": grant_id,
            "session_id": session_id,
            "scope_class": USER_SOURCE_SCOPE,
            "operation": "ImportPages",
            "access": "read-only",
            "source_path": str(source_path),
            "source_kind": source_kind,
            "scope_identity": scope_identity,
            "entries": [
                {
                    "path": str(entry.path),
                    "facts": {
                        "volume_serial": entry.facts.volume_serial,
                        "file_index": entry.facts.file_index,
                        "size": entry.facts.size,
                        "sha256": entry.facts.sha256,
                    },
                }
                for entry in entries
            ],
            "expires_at": f"{expires_at:.6f}",
        }

    @staticmethod
    def _sign(key: bytes, fields: dict) -> str:
        import base64

        encoded = json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(
            hmac.new(key, encoded, hashlib.sha256).digest()
        ).decode().rstrip("=")

    @staticmethod
    def _facts(raw: object) -> ResourceFacts:
        if not isinstance(raw, dict) or set(raw) != {
            "volume_serial", "file_index", "size", "sha256"
        }:
            raise TypedResourceChannelError("REF_MALFORMED")
        numbers = (raw["volume_serial"], raw["file_index"], raw["size"])
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in numbers):
            raise TypedResourceChannelError("REF_MALFORMED")
        if not isinstance(raw["sha256"], str) or not _SHA256.fullmatch(raw["sha256"]):
            raise TypedResourceChannelError("REF_MALFORMED")
        return ResourceFacts(*numbers, raw["sha256"])

    @staticmethod
    def _absolute_path(raw: object) -> Path:
        if not isinstance(raw, str) or not raw:
            raise TypedResourceChannelError("REF_MALFORMED")
        if any(part in {".", ".."} for part in re.split(r"[\\/]", raw)):
            raise TypedResourceChannelError(E_OUT_OF_SCOPE)
        path = Path(raw)
        if not path.is_absolute() or not path.name:
            raise TypedResourceChannelError(E_SCOPE_DENIED)
        return path

    @staticmethod
    def _relative_to_volume(path: Path) -> str:
        return path.name

    @staticmethod
    def _norm(path: Path) -> str:
        return os.path.normcase(os.path.normpath(str(path)))

    @staticmethod
    def _reject_reparse_path(path: Path) -> None:
        probe = Path(path.anchor)
        for part in path.parts[1:]:
            probe /= part
            try:
                info = os.lstat(probe)
            except OSError as error:
                raise TypedResourceChannelError(E_NOT_FOUND) from error
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise TypedResourceChannelError(E_REPARSE)
