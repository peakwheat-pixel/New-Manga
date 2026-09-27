"""Resource channel typed errors and wire DTOs (M2-RC1).

Stable error codes follow Contract 1.1 §10.2's minimum set (blob
``fc35913801297ee1876ea395f9c5041a16226f20``): the runtime may add codes but
must preserve these semantics. Error messages must never carry OS paths,
mapping-table entries, revision fingerprints or digests.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------- thresholds
# Contract 1.1 §10.1 (ruled T1/T2). Probe values from M2-S1 are NOT used here.

#: T1: a single resource must be servable up to this size; larger is a typed
#: rejection with no partial delivery.
MAX_RESOURCE_BYTES = 256 * 1024 * 1024

#: T2: at least this many active references must be supported (typed throttle
#: above it).
MAX_ACTIVE_REFERENCES = 32

#: T2: at least this many concurrent subscribers per resource must be
#: supported (typed throttle above it).
MAX_SUBSCRIBERS_PER_RESOURCE = 16

#: T6: default sliding TTL in seconds (product-configurable).
DEFAULT_TTL_SECONDS = 300.0


class TypedResourceChannelError(Exception):
    """Typed failure; ``code`` is the stable selector, never free text."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ResourceFacts:
    """Issue-time file facts captured by the Core (M2-S2 §7: the content at
    issue time is trusted by construction of the issuing flow; the digest
    pins ``resolved == issued``, not ``issued == legitimate``)."""

    volume_serial: int
    file_index: int
    size: int
    sha256: str


@dataclass(frozen=True)
class ReferenceGrant:
    """Control-plane grant handed to the trusted host layer (T5.2). Carries a
    derived-cache relative path + issue-time facts; never an absolute path,
    never user-source. The WebView never sees any of it."""

    scope_class: str
    resource_id: str
    revision_fingerprint: str
    rel_path: str
    facts: ResourceFacts


#: Scope classes the channel serves. ``user-source`` is deliberately absent
#: (T5.3: no frontend-visible implementation, and the control plane refuses
#: to issue it).
ALLOWED_SCOPE_CLASSES = ("derived-read-only", "managed-read-only")

#: Stable typed error codes (Contract 1.1 §10.2 minimum set + throttle).
E_MALFORMED = "REF_MALFORMED"
E_UNKNOWN_ID = "REF_UNKNOWN_ID"
E_REVOKED = "REF_REVOKED"
E_EXPIRED = "REF_EXPIRED"
E_SCOPE_DENIED = "REF_SCOPE_DENIED"
E_OUT_OF_SCOPE = "REF_OUT_OF_SCOPE"
E_NOT_FOUND = "REF_NOT_FOUND"
E_REPARSE = "REF_REPARSE_POINT"
E_TOO_LARGE = "RESOURCE_TOO_LARGE"
E_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
E_IDENTITY_CHANGED = "FILE_IDENTITY_CHANGED"
E_SIZE_CHANGED = "FILE_SIZE_CHANGED"
E_DIGEST_MISMATCH = "CONTENT_DIGEST_MISMATCH"
E_SHARING_VIOLATION = "OPEN_FAILED_SHARING_VIOLATION"
E_OPEN_FAILED = "OPEN_FAILED"
