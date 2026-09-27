"""Resource channel application service (M2-RC1).

Contract-Aligned Large-Media Resource Channel Runtime -- Core-side authority
for reference issuance, resolution, sliding-TTL expiry and immediate
revocation on revision switch/delete/pin release (Contract 1.1 §10.1 T6,
blob ``fc35913801297ee1876ea395f9c5041a16226f20``).

Design boundaries:

- The service owns an **in-memory** table. A Core restart therefore starts
  with an empty table: every pre-restart ID resolves to ``REF_UNKNOWN_ID``
  and a fresh random 256-bit ID space guarantees old IDs are never re-bound
  to new resources (RC1-AC3). Persistence/replay across restarts is the
  S1-B5 design space and is out of this slice.
- The caller-visible part of a reference is the opaque ID only. Relative
  paths, issue-time facts and revision fingerprints live in the
  control-plane :class:`ReferenceGrant`, which is handed to the trusted host
  layer (T5.2) and never reaches the WebView.
- Bytes never travel through this service: it is control-only
  (authorise/resolve/revoke). The trusted host reads the file itself
  (M2-S1 route-A semantics) with handle-verified checks (M2-S2 semantics,
  productised in ``infrastructure.resource_channel``).
- ``user-source`` is refused at issue time (T5.3): no grant for it can ever
  exist, so no frontend-visible surface can reach a user source file.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, replace

from application.resource_channel.dto import (
    ALLOWED_SCOPE_CLASSES,
    DEFAULT_TTL_SECONDS,
    MAX_ACTIVE_REFERENCES,
    MAX_RESOURCE_BYTES,
    MAX_SUBSCRIBERS_PER_RESOURCE,
    ReferenceGrant,
    ResourceFacts,
    TypedResourceChannelError,
    E_EXPIRED,
    E_LIMIT_EXCEEDED,
    E_MALFORMED,
    E_REVOKED,
    E_SCOPE_DENIED,
    E_TOO_LARGE,
    E_UNKNOWN_ID,
    validate_rel_path,
)


@dataclass
class _Entry:
    grant: ReferenceGrant
    expires_at: float
    revoked: bool
    subscribers: int


def _utc_now() -> float:
    return time.time()


class ResourceChannelService:
    """Core-side authority for the large-media resource channel."""

    def __init__(self, *, clock=_utc_now, default_ttl_seconds: float = DEFAULT_TTL_SECONDS,
                 max_active_references: int = MAX_ACTIVE_REFERENCES,
                 max_subscribers_per_resource: int = MAX_SUBSCRIBERS_PER_RESOURCE) -> None:
        self._clock = clock
        self._default_ttl = default_ttl_seconds
        self._max_active = max_active_references
        self._max_subscribers = max_subscribers_per_resource
        self._lock = threading.Lock()
        self._table: dict[str, _Entry] = {}

    # ------------------------------------------------------------ issuing

    def issue(
        self,
        *,
        scope_class: str,
        resource_id: str,
        revision_fingerprint: str,
        rel_path: str,
        facts: ResourceFacts,
        ttl_seconds: float | None = None,
    ) -> str:
        """Authorise a resource and return its opaque mapping ID.

        ``rel_path`` must be a derived-cache relative path (plain '/'-separated
        segments). Absolute paths, traversal segments and the ``user-source``
        scope are refused with typed errors before any ID exists. A
        ``ttl_seconds`` override may only *shorten* the reference lifetime:
        zero/negative values and anything above the ruled default are refused,
        so no caller (WebView or host) can extend a grant beyond the Core's
        sliding default (RC2-AC1).
        """

        if scope_class not in ALLOWED_SCOPE_CLASSES:
            raise TypedResourceChannelError(
                E_SCOPE_DENIED, f"scope class not servable: {scope_class}"
            )
        validate_rel_path(rel_path)
        if ttl_seconds is not None and (
            not isinstance(ttl_seconds, (int, float))
            or ttl_seconds <= 0
            or ttl_seconds > self._default_ttl
        ):
            raise TypedResourceChannelError(
                E_MALFORMED,
                "ttl_seconds must be within (0, default TTL]; lifetime cannot be extended",
            )
        if facts.size < 0:
            raise TypedResourceChannelError(E_MALFORMED, "negative size")
        if facts.size > MAX_RESOURCE_BYTES:
            raise TypedResourceChannelError(
                E_TOO_LARGE, f"size {facts.size} exceeds {MAX_RESOURCE_BYTES}"
            )
        if not resource_id or not revision_fingerprint:
            raise TypedResourceChannelError(E_MALFORMED, "resource_id/revision required")

        with self._lock:
            self._enforce_limits(scope_class, resource_id)
            opaque_id = self._fresh_id()
            grant = ReferenceGrant(
                scope_class=scope_class,
                resource_id=resource_id,
                revision_fingerprint=revision_fingerprint,
                rel_path=rel_path,
                facts=facts,
            )
            ttl = self._default_ttl if ttl_seconds is None else ttl_seconds
            self._table[opaque_id] = _Entry(
                grant=grant,
                expires_at=self._clock() + ttl,
                revoked=False,
                subscribers=0,
            )
        return opaque_id

    def _fresh_id(self) -> str:
        import secrets

        while True:
            candidate = "m2id.v1." + secrets.token_urlsafe(32)
            if candidate not in self._table:
                return candidate

    def _enforce_limits(self, scope_class: str, resource_id: str) -> None:
        now = self._clock()
        active = [
            entry
            for entry in self._table.values()
            if not entry.revoked and entry.expires_at > now
        ]
        if len(active) + 1 > self._max_active:
            raise TypedResourceChannelError(
                E_LIMIT_EXCEEDED, f"active reference limit {self._max_active} reached"
            )
        same_resource = sum(
            1
            for entry in active
            if entry.grant.resource_id == resource_id and entry.grant.scope_class == scope_class
        )
        if same_resource + 1 > self._max_subscribers:
            raise TypedResourceChannelError(
                E_LIMIT_EXCEEDED,
                f"subscriber limit {self._max_subscribers} reached for resource",
            )

    # ---------------------------------------------------------- resolving

    def resolve(self, opaque_id: str, *, renew: bool = True) -> ReferenceGrant:
        """Resolve an opaque ID to the control-plane grant (trusted host only).

        Resolution renews the sliding TTL (T6) unless ``renew=False``. Every
        failure mode is a stable typed error; no message carries mapping-table
        contents.
        """

        if not opaque_id:
            raise TypedResourceChannelError(E_MALFORMED, "empty id")
        with self._lock:
            entry = self._table.get(opaque_id)
            if entry is None:
                raise TypedResourceChannelError(E_UNKNOWN_ID)
            if entry.revoked:
                raise TypedResourceChannelError(E_REVOKED)
            now = self._clock()
            if entry.expires_at <= now:
                raise TypedResourceChannelError(E_EXPIRED)
            if renew:
                entry.expires_at = now + self._default_ttl
            return entry.grant

    def acquire_subscriber(self, opaque_id: str) -> None:
        """Register an active consumer (T2 subscriber accounting)."""

        with self._lock:
            entry = self._table.get(opaque_id)
            if entry is None:
                raise TypedResourceChannelError(E_UNKNOWN_ID)
            if entry.revoked:
                raise TypedResourceChannelError(E_REVOKED)
            if entry.expires_at <= self._clock():
                raise TypedResourceChannelError(E_EXPIRED)
            if entry.subscribers + 1 > self._max_subscribers:
                raise TypedResourceChannelError(
                    E_LIMIT_EXCEEDED,
                    f"subscriber limit {self._max_subscribers} reached for resource",
                )
            entry.subscribers += 1

    def release_subscriber(self, opaque_id: str) -> None:
        with self._lock:
            entry = self._table.get(opaque_id)
            if entry is not None and entry.subscribers > 0:
                entry.subscribers -= 1

    # ---------------------------------------------------------- lifecycle

    def touch(self, opaque_id: str) -> None:
        """Explicit sliding renewal (T6)."""

        with self._lock:
            entry = self._table.get(opaque_id)
            if entry is None:
                raise TypedResourceChannelError(E_UNKNOWN_ID)
            if entry.revoked:
                raise TypedResourceChannelError(E_REVOKED)
            if entry.expires_at <= self._clock():
                raise TypedResourceChannelError(E_EXPIRED)
            entry.expires_at = self._clock() + self._default_ttl

    def revoke(self, opaque_id: str) -> None:
        """Revoke one reference; the next resolve returns ``REF_REVOKED``.

        An in-flight read that already holds the opened handle is not forced
        to abort (T6 carve-out); enforcement lives with the handle owner.
        """

        with self._lock:
            entry = self._table.get(opaque_id)
            if entry is None:
                raise TypedResourceChannelError(E_UNKNOWN_ID)
            entry.revoked = True

    def revoke_resource(
        self, resource_id: str, revision_fingerprint: str | None = None
    ) -> int:
        """Revoke every reference of a resource (revision switch, delete, pin
        release, management op). With ``revision_fingerprint`` only references
        bound to that revision are revoked; otherwise all revisions are."""

        revoked = 0
        with self._lock:
            for entry in self._table.values():
                if entry.revoked:
                    continue
                if entry.grant.resource_id != resource_id:
                    continue
                if (
                    revision_fingerprint is not None
                    and entry.grant.revision_fingerprint != revision_fingerprint
                ):
                    continue
                entry.revoked = True
                revoked += 1
        return revoked

    def revoke_bookkeeping_for(self, resource_id: str) -> int:
        """Alias kept explicit for the deletion/pin-release call sites."""

        return self.revoke_resource(resource_id)

    # ----------------------------------------------------------- inspection

    def active_reference_count(self) -> int:
        now = self._clock()
        with self._lock:
            return sum(
                1
                for entry in self._table.values()
                if not entry.revoked and entry.expires_at > now
            )

    def entry_count(self) -> int:
        with self._lock:
            return len(self._table)
