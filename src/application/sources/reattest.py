"""FEA-11-L-S4-B (C-16 v1.5 §2.5): ``ReattestSourceLocation`` condition write.

B1's explicit "re-authorize" click only changes the Host Registry (a new live
entry, the old entry revoked); the Core ``source_locations`` row keeps the OLD
``(registry_id, authorization_generation)`` pair, so the Host's exact-match
enumeration typed-skips the source on every cold start / refresh. This module
implements the ONE additive Core fact-propagation path that lets the user's
EXPLICIT action flow into that row: after the Host mints a live source-read
grant over the live entry's file, the Core proves that the grant is about the
SAME Core source and the SAME physical identity as the recorded current
location, and conditionally rewrites the two auth columns in place.

Frozen semantics (C-16 v1.5 §2.5, do not widen):

* the request is a closed shape ``{source_id, grant_id}`` (exactly two keys);
* the grant must be live / unexpired / unrevoked, its signed
  ``scope.source_id`` must equal the request's ``source_id``, and its four
  physical facts (``sha256``/``volume_serial``/``file_id``/``size``) must equal
  the CURRENT ``source_locations`` row (``content_digest``/``volume_serial``/
  ``file_id``/``size_bytes``); any mismatch is a typed refusal with ZERO writes;
* the only write is the two auth columns, through the single
  :meth:`SqliteLibraryRepository.refresh_source_location_auth` implementation
  (``FEA-11-L-S4-LOCATION-AUTH-REFRESH-1``); ``last_verified_at`` is read from
  the current row by the caller and written back unchanged (no audit refresh,
  no ``now()``);
* folder sources are excluded (L-S4-2); this module never creates/revives a
  grant, never rebuilds an identity, never touches ``page_bindings`` and never
  adds a location row;
* idempotent/monotonic: the shared SQL's ``(registry_id <> ? OR
  authorization_generation <= ?)`` + equality branch means a repeated same-grant
  call reports ``updated: 0`` and writes nothing, a same-registry generation
  regression is a no-op, and a cross-registry re-registration is allowed.

This is NOT an automatic recovery: it only records the fact that the user
already completed an explicit re-authorization. Nothing here re-authorizes a
revoked source, rebuilds an identity, or runs without a live Host-minted grant.
"""

from __future__ import annotations

from typing import Any, Protocol

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import ResolvedSourceRead


class SourceGrantAccess(Protocol):
    """The live source-read grant face this command reads (C-16 §2.5 ③/④).

    ``live_grant_scopes`` enforces the frozen §6 grant priority (unknown/session
    mismatch -> ``SOURCE_ACCESS_DENIED``, expiry -> ``SOURCE_GRANT_EXPIRED``,
    revocation -> ``SOURCE_GRANT_REVOKED``) while returning the signed scope
    snapshot; ``resolve`` returns the grant's Host-collected physical facts.
    Both are read-only and mutate nothing.
    """

    def live_grant_scopes(
        self, grant_ids: list[str]
    ) -> tuple[tuple[str, dict], ...]: ...

    def resolve(self, grant_id: str) -> ResolvedSourceRead: ...


class SourceLocationStore(Protocol):
    """The read-only Core store subset this command needs."""

    def latest_source_version(self, source_id: str) -> dict[str, Any] | None: ...


class SourceLocationAuthWriter(Protocol):
    """The ONE in-place location-auth refresh implementation (L-S4 A)."""

    def commit_source_location_auth_refresh(self, refresh: dict[str, Any]) -> int: ...


#: The closed request shape (C-16 v1.5 §2.5 request, exactly two keys).
_REQUEST_FIELDS = frozenset({"source_id", "grant_id"})
#: The frozen answer shape (C-16 v1.5 §2.5 response, closed).
_RESPONSE_FIELDS = ("source_id", "updated", "version")


def _invalid_request(message: str) -> SourceImportError:
    return SourceImportError("INVALID_REQUEST", message)


def _denied(message: str) -> SourceImportError:
    return SourceImportError("SOURCE_ACCESS_DENIED", message)


class SourceLocationReattest:
    """C-16 v1.5 §2.5 ``ReattestSourceLocation`` condition-write service.

    The wire layer owns the host-control envelope checks (host-only session);
    everything this class validates runs after them, in the frozen order:
    shape -> grant liveness/scope -> location identity -> conditional update.
    """

    def __init__(
        self,
        *,
        access: SourceGrantAccess,
        store: SourceLocationStore,
        repository: SourceLocationAuthWriter,
        read_current_location,
    ) -> None:
        self._access = access
        self._store = store
        self._repository = repository
        #: Read-only row projection of the caller (the bootstrap has the one
        #: shared connection). It MUST include the CURRENT row's
        #: ``last_verified_at`` so this command can write the original audit
        #: value back unchanged (C-16 v1.5 §2.5 action clause).
        self._read_current_location = read_current_location

    # ------------------------------------------------------------- public
    def reattest(self, payload: object) -> dict[str, Any]:
        """Validate and conditionally re-attest ONE location; zero write on refusal."""
        source_id, grant_id = self._parse_request(payload)

        # ③ grant live/未过期/未撤销 + session; the frozen §6 priority lives in
        # the registry (``_checked``) and is reused verbatim — no new code.
        scope = self._live_scope(grant_id)

        # ④ the grant must be about the SAME Core source.
        if scope.get("source_id") != source_id:
            raise _denied("granted source does not match the requested source")

        resolved = self._access.resolve(grant_id)
        facts = resolved.container_facts
        if facts is None:
            # folder sources are out of this card's promise (L-S4-2): there is
            # no single physical file identity to compare.
            raise _denied("a folder source has no single physical location identity")

        # ⑤ the grant's four physical facts must equal the CURRENT row. The
        # row is read (not written) before the conditional UPDATE so the audit
        # column can be preserved exactly.
        location = self._read_current_location(source_id)
        if not isinstance(location, dict):
            raise _denied("the source has no current location row")
        self._require_identity(location, facts)

        # ``version`` is a read-only diagnostic in the frozen response; it
        # never participates in authorization and is never stored.
        current_version = self._store.latest_source_version(source_id)
        version_id = (
            current_version.get("version_id")
            if isinstance(current_version, dict)
            else None
        )
        if not isinstance(version_id, str) or not version_id:
            raise _denied("the source has no current version")

        # ⑥ conditional single-row UPDATE through the ONE implementation. The
        # original ``last_verified_at`` is written back unchanged: this command
        # propagates the two auth columns only and does not refresh the audit
        # time (C-16 v1.5 §2.5).
        updated = self._repository.commit_source_location_auth_refresh(
            {
                "source_id": source_id,
                "content_digest": location["content_digest"],
                "volume_serial": int(location["volume_serial"]),
                "file_id": int(location["file_id"]),
                "registry_id": resolved.registry_id,
                "authorization_generation": int(resolved.generation),
                "last_verified_at": location.get("last_verified_at"),
            }
        )
        try:
            updated_count = int(updated or 0)
        except (TypeError, ValueError) as error:
            raise SourceImportError(
                "SOURCE_REGISTRY_UNAVAILABLE", "location refresh result is invalid"
            ) from error
        return {"source_id": source_id, "updated": updated_count, "version": version_id}

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _parse_request(payload: object) -> tuple[str, str]:
        """Closed shape: exactly two non-empty string keys (C-16 v1.5 §2.5 ②)."""
        if not isinstance(payload, dict) or set(payload) != _REQUEST_FIELDS:
            raise _invalid_request("reattest request is invalid")
        source_id = payload["source_id"]
        grant_id = payload["grant_id"]
        if (
            not isinstance(source_id, str)
            or not source_id
            or not isinstance(grant_id, str)
            or not grant_id
        ):
            raise _invalid_request("reattest request is invalid")
        return source_id, grant_id

    def _live_scope(self, grant_id: str) -> dict:
        """Frozen §6 liveness for the ONE grant id, returning its signed scope."""
        grants = self._access.live_grant_scopes([grant_id])
        if len(grants) != 1 or grants[0][0] != grant_id:
            raise _denied("source-read grant is not usable")
        scope = grants[0][1]
        if not isinstance(scope, dict):
            raise _denied("source-read grant scope is not usable")
        return scope

    @staticmethod
    def _require_identity(location: dict, facts) -> None:
        """The four frozen keys must match the current row exactly (no path fallback)."""
        content_digest = location.get("content_digest")
        volume_serial = location.get("volume_serial")
        file_id = location.get("file_id")
        size_bytes = location.get("size_bytes")
        if (
            not isinstance(content_digest, str)
            or isinstance(volume_serial, bool)
            or not isinstance(volume_serial, int)
            or isinstance(file_id, bool)
            or not isinstance(file_id, int)
            or isinstance(size_bytes, bool)
            or not isinstance(size_bytes, int)
        ):
            raise _denied("the current location identity is not usable")
        if (
            content_digest != facts.sha256
            or volume_serial != facts.volume_serial
            or file_id != facts.file_id
            or size_bytes != facts.size
        ):
            raise _denied(
                "the granted physical identity does not match the current location"
            )
