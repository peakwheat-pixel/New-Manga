"""FEA-09 Core-side source-read grant registry (C-16 §2/§7).

Validates the Host-minted, HMAC-signed ``RegisterSourceReadGrant`` payloads,
keeps them in-process (never persisted), enforces the frozen failure-code
priority and exposes the ``SourceReadAccess`` port consumed by the
referenced-import orchestration: ``resolve`` (strict verify) /
``verify_before_commit`` (strong re-check at each commit unit) /
``revoke_all_for_session`` (EOF/transport failure kills every grant).

Signed-field shape (both sides must byte-match): the payload minus
``signing_key``/``signature``, with the top-level ``expires_at`` rendered as
``"%.6f"``; nested objects (``budget``/``scope``/``secret_ref``) keep their
wire JSON shape. The ``scope.rendition.decoder`` value carries the five-kind
source classification (image|folder|zip|cbz|pdf — the C-16 §2 four-dimension
scope's rendition dimension applied to imports).
"""

from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager, ExitStack
import base64
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import stat
import threading
import time

from application.importing.referenced.access import SourceReadAccess
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import (
    GrantFacts,
    ResolvedSourceRead,
    SourceReadBudget,
    validate_locator,
)
from application.resource_channel.dto import USER_SOURCE_SCOPE

_ID = re.compile(r"^[A-Za-z0-9_.:-]{8,128}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
#: Rendition decoder values the import face accepts (five source kinds).
_KINDS = frozenset({"image", "folder", "zip", "cbz", "pdf"})
_ENVELOPE_FIELDS = {
    "grant_id", "session_id", "operation", "scope_class", "registry_id",
    "generation", "expires_at", "budget", "scope", "signing_key", "signature",
}
_OPTIONAL_FIELDS = {"secret_ref"}


@dataclass
class _SourceReadGrant:
    grant_id: str
    session_id: str
    registry_id: str
    generation: int
    expires_at: float
    budget: SourceReadBudget
    source_kind: str
    container_path: str | None
    container_facts: GrantFacts | None
    folder_root: str | None
    folder_entries: tuple[tuple[str, GrantFacts], ...]
    scope: dict
    secret_ref: dict | None
    revoked: bool = False


def _signed_fields(payload: dict, *, expires_at: float) -> dict:
    """Canonical signed-field dict (compact sorted-key JSON input)."""
    fields = {
        key: value for key, value in payload.items()
        if key not in {"signing_key", "signature"}
    }
    fields["expires_at"] = f"{expires_at:.6f}"
    return fields


def _sign(key: bytes, fields: dict) -> str:
    encoded = json.dumps(
        fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return base64.urlsafe_b64encode(
        hmac.new(key, encoded, hashlib.sha256).digest()
    ).decode().rstrip("=")


class SourceReadGrantRegistry(SourceReadAccess):
    """In-process registry of Host-minted source-read grants."""

    def __init__(self, *, clock=time.time) -> None:
        self._clock = clock
        self._lock = threading.RLock()
        self._grants: dict[str, _SourceReadGrant] = {}
        self._session_id: str | None = None
        self._disconnected = False
        self._min_generation: dict[str, int] = {}  # registry_id -> floor

    # ------------------------------------------------------------- register
    def register(self, payload: dict) -> None:
        if not isinstance(payload, dict) or not (
            _ENVELOPE_FIELDS <= set(payload)
            and set(payload) <= _ENVELOPE_FIELDS | _OPTIONAL_FIELDS
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant payload is malformed"
            )
        grant_id = payload["grant_id"]
        expires_at = payload["expires_at"]
        if (
            not isinstance(grant_id, str) or not _ID.fullmatch(grant_id)
            or not isinstance(payload["session_id"], str) or not payload["session_id"]
            or payload["operation"] != "source-read"
            or payload["scope_class"] != USER_SOURCE_SCOPE
            or not isinstance(payload["registry_id"], str) or not payload["registry_id"]
            or isinstance(payload["generation"], bool)
            or not isinstance(payload["generation"], int)
            or payload["generation"] < 1
            or isinstance(expires_at, bool)
            or not isinstance(expires_at, (int, float))
            or not math.isfinite(float(expires_at))
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant payload is malformed"
            )
        signature = payload["signature"]
        key_text = payload["signing_key"]
        if (
            not isinstance(signature, str) or not signature
            or not isinstance(key_text, str) or not key_text
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant payload is malformed"
            )
        try:
            signing_key = base64.urlsafe_b64decode(
                key_text + "=" * (-len(key_text) % 4)
            )
        except Exception as error:  # noqa: BLE001 - malformed key material
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant key is malformed"
            ) from error
        if len(signing_key) < 32:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant key is malformed"
            )
        expected = _sign(
            signing_key, _signed_fields(payload, expires_at=float(expires_at))
        )
        if not hmac.compare_digest(signature, expected):
            raise SourceImportError(
                "REF_SIGNATURE_INVALID", "source-read grant signature is invalid"
            )
        now = self._clock()
        if float(expires_at) <= now or float(expires_at) > now + 300:
            raise SourceImportError("SOURCE_GRANT_EXPIRED", "source-read grant window is invalid")
        budget = self._parse_budget(payload["budget"])
        raw_scope = payload["scope"]
        if not isinstance(raw_scope, dict) or not isinstance(raw_scope.get("entries"), list):
            raise SourceImportError("SOURCE_ACCESS_DENIED", "source-read scope is malformed")
        if len(raw_scope["entries"]) > budget.max_entries:
            raise SourceImportError("SOURCE_BUDGET_EXCEEDED", "source-read entry budget exceeded")
        scope = self._parse_scope(raw_scope)
        secret_ref = payload.get("secret_ref")
        if secret_ref is not None and (
            not isinstance(secret_ref, dict)
            or not {"token", "path", "expires_at"} <= set(secret_ref)
            or not isinstance(secret_ref.get("path"), str)
            or not secret_ref["path"]
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant secret ref is malformed"
            )

        grant = _SourceReadGrant(
            grant_id=grant_id,
            session_id=payload["session_id"],
            registry_id=payload["registry_id"],
            generation=int(payload["generation"]),
            expires_at=float(expires_at),
            budget=budget,
            source_kind=scope[0],
            container_path=scope[1],
            container_facts=scope[2],
            folder_root=scope[3],
            folder_entries=scope[4],
            scope=json.loads(json.dumps(payload["scope"])),
            secret_ref=json.loads(json.dumps(secret_ref)),
        )
        with self._lock:
            if self._disconnected:
                raise SourceImportError("SOURCE_GRANT_REVOKED", "source session is closed")
            if self._session_id is None:
                self._session_id = grant.session_id
            elif self._session_id != grant.session_id:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "grant session does not match"
                )
            if grant_id in self._grants:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "grant id is already registered"
                )
            self._grants[grant_id] = grant

    # --------------------------------------------------------------- revoke
    def revoke_grants(self, registry_id: str, generation: int, grant_ids: list) -> int:
        """Host push ``RevokeSourceReadGrant``: kill grants, raise floor."""
        if (
            not isinstance(registry_id, str) or not registry_id
            or isinstance(generation, bool) or not isinstance(generation, int)
            or not isinstance(grant_ids, list)
            or any(not isinstance(item, str) or not item for item in grant_ids)
            or generation < 1
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "revocation payload is malformed"
            )
        revoked = 0
        with self._lock:
            floor = self._min_generation.get(registry_id, 0)
            self._min_generation[registry_id] = max(floor, generation)
            for grant_id in grant_ids:
                grant = self._grants.get(grant_id)
                if grant is not None and grant.registry_id == registry_id:
                    grant.revoked = True
                    revoked += 1
        return revoked

    def revoke_all_for_session(self) -> int:
        """EOF/transport failure: every grant dies immediately (C-15 §6.6)."""
        self._disconnected = True
        with self._lock:
            count = len(self._grants)
            for grant in self._grants.values():
                grant.revoked = True
            return count

    def revoke_grant_ids(self, grant_ids: list) -> int:
        """Session teardown: kill specific grants by id (no generation bump)."""
        with self._lock:
            revoked = 0
            for grant_id in grant_ids:
                grant = self._grants.get(grant_id)
                if grant is not None:
                    grant.revoked = True
                    revoked += 1
            return revoked

    # --------------------------------------------------------------- access
    def resolve(self, grant_id: str) -> ResolvedSourceRead:
        grant = self._checked(grant_id)
        return ResolvedSourceRead(
            grant_id=grant.grant_id,
            registry_id=grant.registry_id,
            generation=grant.generation,
            source_kind=grant.source_kind,
            budget=grant.budget,
            expires_at=grant.expires_at,
            container_path=grant.container_path,
            container_facts=grant.container_facts,
            folder_root=grant.folder_root,
            folder_entries=grant.folder_entries,
        )

    def verify_before_commit(self, grant_id: str) -> None:
        with self.commit_guard(grant_id):
            pass

    @contextmanager
    def commit_guard(self, grant_id: str):
        from infrastructure.resource_channel.source_strict_read import source_lease
        with self._lock, ExitStack() as stack:
            grant = self._checked(grant_id)
            files = grant.folder_entries if grant.source_kind == "folder" else (
                (grant.container_path, grant.container_facts),)
            for path, facts in files:
                stack.enter_context(source_lease(path, facts, grant.budget.max_bytes))
            self._checked(grant_id)
            yield

    def verify_secret_ref(self, grant_ids, secret_ref):
        if secret_ref is None:
            return
        if not isinstance(grant_ids, list) or not isinstance(secret_ref, dict):
            raise SourceImportError("SOURCE_PASSWORD_REQUIRED", "password reference is invalid")
        with self._lock:
            grants = [self._checked(g) for g in grant_ids]
            matching = [g for g in grants if g.secret_ref == secret_ref]
            if not matching:
                raise SourceImportError("SOURCE_PASSWORD_REQUIRED", "password reference is not grant-bound")
            expiry = secret_ref.get("expires_at")
            if (isinstance(expiry, bool) or not isinstance(expiry, (int, float))
                or not math.isfinite(expiry) or expiry <= self._clock()
                or any(expiry > g.expires_at for g in matching)):
                raise SourceImportError("SOURCE_PASSWORD_REQUIRED", "password reference is unavailable")

    def find_for_source(self, source_id: str) -> tuple[str, ResolvedSourceRead]:
        """Return the live grant bound to ``source_id`` (highest generation).

        ``resolve_page_resource`` has no grant parameter on the frozen wire, so
        the Core derives the grant from the page binding's source. Missing,
        expired or revoked grants stay typed refusals.
        """
        if not isinstance(source_id, str) or not source_id:
            raise SourceImportError("SOURCE_ACCESS_DENIED", "source id is invalid")
        with self._lock:
            candidates = [
                grant for grant in self._grants.values()
                if grant.scope.get("source_id") == source_id
            ]
            live: list[_SourceReadGrant] = []
            for grant in candidates:
                try:
                    self._checked(grant.grant_id)
                except SourceImportError:
                    continue
                live.append(grant)
            if not live:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED",
                    "no active source-read grant covers this source",
                )
            chosen = max(live, key=lambda grant: (grant.generation, grant.grant_id))
        return chosen.grant_id, self.resolve(chosen.grant_id)

    def verify_scope(self, grant_id, *, source_id, version, rendition, entries):
        with self._lock:
            grant = self._checked(grant_id)
            expected = {"source_id": source_id, "version": version,
                        "rendition": rendition, "entries": entries}
            if grant.scope != expected:
                raise SourceImportError("SOURCE_ACCESS_DENIED", "source scope does not match")

    # ------------------------------------------------------------- internals
    def _checked(self, grant_id: str) -> _SourceReadGrant:
        with self._lock:
            grant = self._grants.get(grant_id) if isinstance(grant_id, str) else None
            if grant is None:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "source-read grant is not registered"
                )
            if self._disconnected:
                raise SourceImportError("SOURCE_GRANT_REVOKED", "source session is closed")
            if grant.expires_at <= self._clock():
                raise SourceImportError("SOURCE_GRANT_EXPIRED", "source-read grant expired")
            if grant.revoked:
                raise SourceImportError(
                    "SOURCE_GRANT_REVOKED", "source-read grant was revoked"
                )
            if grant.session_id != self._session_id:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "grant session does not match"
                )
            floor = self._min_generation.get(grant.registry_id, 0)
            if grant.generation < floor:
                # Revocation bumped the registry generation past this grant.
                raise SourceImportError(
                    "SOURCE_GRANT_REVOKED", "source-read grant was revoked"
                )
            return grant

    def _parse_budget(self, raw) -> SourceReadBudget:
        if not isinstance(raw, dict) or set(raw) != {
            "max_bytes", "max_decode_bytes", "max_entries"
        }:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant budget is malformed"
            )
        values = []
        for key in ("max_bytes", "max_decode_bytes", "max_entries"):
            value = raw[key]
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "source-read grant budget is malformed"
                )
            values.append(value)
        return SourceReadBudget(*values)

    def _parse_scope(self, raw):
        if not isinstance(raw, dict) or set(raw) != {
            "source_id", "version", "rendition", "entries"
        }:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant scope is malformed"
            )
        if any(not isinstance(raw[k], str) or not raw[k] for k in ("source_id", "version")):
            raise SourceImportError("SOURCE_ACCESS_DENIED", "source scope is malformed")
        rendition = raw["rendition"]
        if (not isinstance(rendition, dict) or set(rendition) != {"decoder", "scale", "params_digest"}
            or isinstance(rendition.get("scale"), bool)
            or not isinstance(rendition.get("scale"), (int, float))
            or not math.isfinite(rendition["scale"]) or rendition["scale"] <= 0
            or not isinstance(rendition.get("params_digest"), str)
            or not _SHA256.fullmatch(rendition["params_digest"])):
            raise SourceImportError("SOURCE_ACCESS_DENIED", "source rendition is malformed")
        if not isinstance(rendition, dict) or not isinstance(
            rendition.get("decoder"), str
        ) or rendition["decoder"] not in _KINDS:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant rendition is malformed"
            )
        kind = rendition["decoder"]
        entries = raw["entries"]
        if not isinstance(entries, list) or not entries:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant entries are malformed"
            )
        if len(entries) > 10000:
            raise SourceImportError(
                "SOURCE_BUDGET_EXCEEDED", "source-read grant entry budget exceeded"
            )
        parsed: list[tuple[str, GrantFacts]] = []
        for item in entries:
            if not isinstance(item, dict) or not {
                "entry_key", "locator", "ordinal", "path", "facts"
            } <= set(item):
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "source-read grant entry is malformed"
                )
            path = item["path"]
            locator = item["locator"]
            ordinal = item["ordinal"]
            if not isinstance(path, str) or not path:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "source-read grant entry is malformed"
                )
            if not isinstance(locator, str) or not locator:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "source-read grant entry is malformed"
                )
            if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "source-read grant entry is malformed"
                )
            if any(
                part in {".", ".."} for part in re.split(r"[\\/]", path)
            ) or not Path(path).is_absolute():
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "granted path escapes its root"
                )
            self._reject_reparse(Path(path))
            try:
                info = os.stat(path)
            except OSError as error:
                raise SourceImportError(
                    "SOURCE_ENTRY_MISSING", "granted source file is missing"
                ) from error
            if not stat.S_ISREG(info.st_mode):
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "granted path is not a file"
                )
            facts = self._facts(item["facts"])
            parsed.append((path, facts))
        if kind == "folder":
            # The folder root is the common parent of the granted members
            # (the Host enumerates an authorized root's direct files; the
            # envelope carries member paths, not the root itself).
            try:
                candidates = []
                for item in entries:
                    validate_locator(item["locator"])
                    candidate = Path(item["path"])
                    for _ in item["locator"].split("/"):
                        candidate = candidate.parent
                    if os.path.normcase(str(candidate.joinpath(*item["locator"].split("/")))) != os.path.normcase(item["path"]):
                        raise ValueError("folder locator mismatch")
                    candidates.append(str(candidate))
                if len(set(os.path.normcase(p) for p in candidates)) != 1:
                    raise ValueError("folder roots differ")
                root = candidates[0]
            except ValueError as error:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "granted folder members span roots"
                ) from error
            root_norm = os.path.normcase(os.path.normpath(root))
            members: list[tuple[str, GrantFacts]] = []
            for path, facts in parsed:
                target_norm = os.path.normcase(os.path.normpath(path))
                if not target_norm.startswith(root_norm.rstrip("\\/") + os.sep):
                    raise SourceImportError(
                        "SOURCE_ACCESS_DENIED", "granted folder member escapes its root"
                    )
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                try:
                    validate_locator(rel)
                except ValueError as error:
                    raise SourceImportError(
                        "SOURCE_ACCESS_DENIED", "folder member name is unsafe"
                    ) from error
                members.append((path, facts))
            return kind, None, None, root, tuple(members)
        if len(parsed) != 1:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "container grant must carry one entry"
            )
        return kind, parsed[0][0], parsed[0][1], None, ()

    @staticmethod
    def _facts(raw) -> GrantFacts:
        if not isinstance(raw, dict) or set(raw) != {
            "volume_serial", "file_id", "size", "sha256"
        }:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant facts are malformed"
            )
        numbers = (raw["volume_serial"], raw["file_id"], raw["size"])
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in numbers
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant facts are malformed"
            )
        if not isinstance(raw["sha256"], str) or not _SHA256.fullmatch(raw["sha256"]):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "source-read grant facts are malformed"
            )
        return GrantFacts(*numbers, raw["sha256"])

    @staticmethod
    def _reject_reparse(path: Path) -> None:
        probe = Path(path.anchor)
        for part in path.parts[1:]:
            probe /= part
            try:
                info = os.lstat(probe)
            except OSError as error:
                raise SourceImportError(
                    "SOURCE_ENTRY_MISSING", "granted path cannot be inspected"
                ) from error
            if stat.S_ISLNK(info.st_mode) or (
                getattr(info, "st_file_attributes", 0) & 0x400
            ):
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED", "granted path crosses a reparse point"
                )
