"""Stdio JSON-lines control bridge between the Tauri host and the Python Core
(M2-RC1; command-surface hardening M2-RC2).

The Tauri/Rust host spawns this module as a sidecar process and speaks
one-JSON-object-per-line over stdin/stdout. This is the **control plane
only**: the host learns the derived-cache relative path + issue-time facts of
a granted resource and then reads the file itself (route-A semantics,
Contract 1.1 §10.1 T5.2). Resource bytes never cross this bridge -- they are
not in JSON, Base64, events, logs or errors.

Wire (v1, RC2 issue shape):
  request  {"id": <int>, "method": "<name>", "params": {...}}
  response {"id": <int>, "result": {...}} | {"id": <int>, "error": {"code": "..."}}
  fatal    {"event": "fatal", "code": "..."}   (then exit non-zero)

Methods: ping, issue, resolve, touch, revoke, revoke_resource, shutdown.

RC2 (F-03) hardening: the catalog (``resource_id -> rel_path``) is Core/SQLite
authority. ``issue`` takes ``resource_id`` + ``revision_fingerprint`` only and
resolves the path from the catalog store; a ``rel_path`` or ``scope_class``
request parameter is refused outright, so no host-side caller can name files
through the bridge. ``ttl_seconds`` may shorten but never extend a grant.

Every failure is a stable typed code; messages on the wire never contain OS
paths, mapping-table contents or digests (the resolve result does carry the
issue-time facts -- relative path, size, digest, identity -- because the host
is the trusted layer per T5.2 and needs them for handle-verified reads).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from application.resource_channel.dto import TypedResourceChannelError
from application.resource_channel.service import ResourceChannelService
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from infrastructure.resource_channel.scope import ScopeRoots

#: RC2 (F-03): parameters that would let the host name paths or scopes are
#: Core-owned; their presence in an issue request is a typed refusal.
_CORE_OWNED_ISSUE_PARAMS = ("rel_path", "scope_class")


class CoreChannelServer:
    """Serves the control bridge against one in-memory service instance."""

    def __init__(
        self,
        service: ResourceChannelService | None = None,
        roots: ScopeRoots | None = None,
        *,
        derived_root: Path | None = None,
        managed_root: Path | None = None,
        catalog: ResourceCatalogStore | None = None,
        stdin=None,
        stdout=None,
    ) -> None:
        self._service = service or ResourceChannelService()
        if roots is None:
            temp = Path(__import__("tempfile").gettempdir())
            roots = ScopeRoots(
                derived_root=derived_root or temp / "m2rc1-lab" / "scope" / "derived",
                managed_root=managed_root or temp / "m2rc1-lab" / "scope" / "managed",
            )
        self._roots = roots
        # fail-closed: no catalog source -> an empty store, so every issue is
        # RESOURCE_NOT_CATALOGED while the bridge itself stays responsive
        self._catalog = catalog or ResourceCatalogStore(":memory:")
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout

    # ------------------------------------------------------------- methods

    def _handle_request(self, request: dict) -> dict:
        method = request.get("method", "")
        params = request.get("params", {}) or {}
        if method == "ping":
            return {"result": {"pong": True, "service": "m2-rc1-resource-channel"}}
        if method == "issue":
            for smuggled in _CORE_OWNED_ISSUE_PARAMS:
                if smuggled in params:
                    raise TypedResourceChannelError(
                        "REF_MALFORMED", f"{smuggled} is Core-owned catalog state"
                    )
            entry = self._catalog.lookup(params["resource_id"])
            if entry is None:
                raise TypedResourceChannelError(
                    "RESOURCE_NOT_CATALOGED", "resource_id has no Core catalog entry"
                )
            reader = self._roots.reader_for(entry.scope_class)
            facts = reader.capture_facts(entry.rel_path)
            opaque_id = self._service.issue(
                scope_class=entry.scope_class,
                resource_id=entry.resource_id,
                revision_fingerprint=params["revision_fingerprint"],
                rel_path=entry.rel_path,
                facts=facts,
                ttl_seconds=params.get("ttl_seconds"),
            )
            return {"result": {"id": opaque_id, "size": facts.size}}
        if method == "resolve":
            grant = self._service.resolve(params["id"])
            return {
                "result": {
                    "scope_class": grant.scope_class,
                    "resource_id": grant.resource_id,
                    "revision_fingerprint": grant.revision_fingerprint,
                    "rel_path": grant.rel_path,
                    "size": grant.facts.size,
                    "sha256": grant.facts.sha256,
                    "volume_serial": grant.facts.volume_serial,
                    "file_index": grant.facts.file_index,
                }
            }
        if method == "touch":
            self._service.touch(params["id"])
            return {"result": {"touched": True}}
        if method == "revoke":
            self._service.revoke(params["id"])
            return {"result": {"revoked": True}}
        if method == "revoke_resource":
            revoked = self._service.revoke_resource(
                params["resource_id"], params.get("revision_fingerprint")
            )
            return {"result": {"revoked_count": revoked}}
        if method == "shutdown":
            return {"result": {"bye": True}}
        return {"error": {"code": "REF_MALFORMED"}}

    def _dispatch(self, request: dict) -> dict:
        request_id = request.get("id")
        try:
            response = self._handle_request(request)
        except TypedResourceChannelError as error:
            response = {"error": {"code": error.code}}
        except (KeyError, TypeError, ValueError):
            response = {"error": {"code": "REF_MALFORMED"}}
        response["id"] = request_id
        return response

    # -------------------------------------------------------------- serving

    def serve_forever(self) -> int:
        for line in self._stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                response = {"id": None, "error": {"code": "REF_MALFORMED"}}
            else:
                response = self._dispatch(request)
                if response.get("result", {}).get("bye"):
                    self._emit(response)
                    return 0
            self._emit(response)
        return 0

    def _emit(self, payload: dict) -> None:
        self._stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self._stdout.flush()


def main() -> int:
    import os

    # RC2 (F-05) isolation evidence: when M2RC2_MODULE_DUMP is set, record the
    # module set this sidecar process actually loaded. The set must not contain
    # unrelated infrastructure adapters (filesystem/sqlite) -- the sidecar
    # entry imports only what the resource channel needs.
    dump_path = os.environ.get("M2RC2_MODULE_DUMP")
    if dump_path:
        import json

        Path(dump_path).write_text(
            json.dumps(
                {
                    "pid": os.getpid(),
                    "argv": sys.argv[1:],
                    "modules": sorted(sys.modules),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    derived = os.environ.get("M2RC1_DERIVED_ROOT")
    managed = os.environ.get("M2RC1_MANAGED_ROOT")
    roots = ScopeRoots(
        derived_root=Path(derived) if derived else None,
        managed_root=Path(managed) if managed else None,
    )
    catalog_db = os.environ.get("M2RC2_CATALOG_DB")
    catalog = (
        ResourceCatalogStore(Path(catalog_db)) if catalog_db else ResourceCatalogStore(":memory:")
    )
    server = CoreChannelServer(roots=roots, catalog=catalog)
    return server.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
