"""Stdio control-bridge protocol (RC1-AC2 control plane) and 256 MiB threshold
(RC1-AC5, T1). RC2: issue requests name catalog entries only -- paths are
Core/SQLite authority (``test_catalog_authority.py`` covers the denial side)."""

from __future__ import annotations

import io
import json
import os

import pytest

from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from infrastructure.resource_channel.host_bridge import CoreChannelServer

from conftest import issue_for


def make_server(scope, reader, service, catalog=None):
    from infrastructure.resource_channel.scope import ScopeRoots

    roots = ScopeRoots(derived_root=scope.derived, managed_root=scope.managed)
    return CoreChannelServer(
        service=service,
        roots=roots,
        catalog=catalog or ResourceCatalogStore(":memory:"),
        stdin=io.StringIO(),
        stdout=io.StringIO(),
    )


def seed(catalog: ResourceCatalogStore, resource_id: str, rel_path: str) -> None:
    catalog.upsert(resource_id, "derived-read-only", rel_path)


class TestBridge:
    def test_issue_and_resolve_roundtrip(self, scope, reader, service):
        catalog = ResourceCatalogStore(":memory:")
        seed(catalog, "res-001", "asset.png")
        server = make_server(scope, reader, service, catalog)
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
        }})
        assert "error" not in response
        opaque = response["result"]["id"]
        assert opaque.startswith("m2id.v1.")

        resolved = server._dispatch({"id": 2, "method": "resolve", "params": {"id": opaque}})
        assert resolved["result"]["rel_path"] == "asset.png"
        assert resolved["result"]["sha256"] == scope.small_sha
        assert resolved["result"]["size"] > 0

    def test_typed_error_serialisation_has_no_path_or_digest(self, scope, reader, service):
        server = make_server(scope, reader, service)
        response = server._dispatch({"id": 1, "method": "resolve", "params": {"id": "m2id.v1.NOSUCH"}})
        assert response["error"]["code"] == "REF_UNKNOWN_ID"
        text = json.dumps(response)
        assert "asset.png" not in text
        assert "sha256" not in text

    def test_revoke_via_bridge(self, scope, reader, service):
        server = make_server(scope, reader, service)
        opaque = issue_for(reader, service, scope)
        server._dispatch({"id": 1, "method": "revoke", "params": {"id": opaque}})
        response = server._dispatch({"id": 2, "method": "resolve", "params": {"id": opaque}})
        assert response["error"]["code"] == "REF_REVOKED"

    def test_malformed_method_typed(self, scope, reader, service):
        server = make_server(scope, reader, service)
        response = server._dispatch({"id": 1, "method": "no-such-method", "params": {}})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_wire_loop_end_to_end(self, scope, reader, service):
        """stdin JSON-lines -> stdout JSON-lines, bytes never on the wire."""

        catalog = ResourceCatalogStore(":memory:")
        seed(catalog, "res-001", "asset.png")
        server = make_server(scope, reader, service, catalog)
        issue_request = json.dumps({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
        }})
        server._stdin = io.StringIO(issue_request + "\n" + json.dumps({"id": 2, "method": "shutdown"}) + "\n")
        buffer = io.StringIO()
        server._stdout = buffer
        exit_code = server.serve_forever()
        assert exit_code == 0
        lines = [json.loads(line) for line in buffer.getvalue().splitlines()]
        assert lines[0]["id"] == 1 and "result" in lines[0]
        assert lines[1]["result"]["bye"] is True
        # control plane only: no fixture bytes on the wire
        assert "PNG" not in buffer.getvalue()

    def test_resolve_result_is_control_plane_only(self, scope, reader, service):
        """The host (trusted layer, T5.2) gets issue-time facts; the WebView
        gets none of this. Assert the grant carries no absolute path."""

        server = make_server(scope, reader, service)
        opaque = issue_for(reader, service, scope)
        resolved = server._dispatch({"id": 1, "method": "resolve", "params": {"id": opaque}})
        result_text = json.dumps(resolved["result"])
        assert str(scope.derived) not in result_text
        assert "C:" not in result_text


class TestThreshold256MiB:
    @pytest.mark.slow
    def test_boundary_resource_served(self, reader, service, scope, tmp_path):
        """A 256 MiB resource is servable in bounded chunks; one byte more is
        a typed rejection at issue. Sparse files keep the test cheap; the
        reader still streams every byte through the handle."""

        boundary = 256 * 1024 * 1024
        sparse = scope.derived / "boundary.bin"
        with open(sparse, "wb") as handle:
            handle.truncate(boundary)
        # sparse zeros hash to a known digest; capture_facts streams them
        facts = reader.capture_facts("boundary.bin")
        assert facts.size == boundary
        opaque = service.issue(
            scope_class="derived-read-only", resource_id="res-boundary",
            revision_fingerprint="rev-1", rel_path="boundary.bin", facts=facts,
        )
        grant = service.resolve(opaque)
        served = 0
        for chunk in reader.read_chunks(grant, chunk_size=16 * 1024 * 1024):
            assert len(chunk) <= 16 * 1024 * 1024
            served += len(chunk)
        assert served == boundary

        over = scope.derived / "over.bin"
        with open(over, "wb") as handle:
            handle.truncate(boundary + 1)
        assert _issue_code(reader, service, "over.bin") == "RESOURCE_TOO_LARGE"

        sparse.unlink()
        over.unlink()

    def test_chunked_stream_matches_digest(self, reader, service, scope):
        boundary = 32 * 1024 * 1024
        sparse = scope.derived / "mid.bin"
        with open(sparse, "wb") as handle:
            handle.truncate(boundary)
        facts = reader.capture_facts("mid.bin")
        opaque = service.issue(
            scope_class="derived-read-only", resource_id="res-mid",
            revision_fingerprint="rev-1", rel_path="mid.bin", facts=facts,
        )
        grant = service.resolve(opaque)
        digest_stream = pytest.importorskip("hashlib").sha256()
        served = 0
        for chunk in reader.read_chunks(grant, chunk_size=4 * 1024 * 1024):
            digest_stream.update(chunk)
            served += len(chunk)
        assert served == boundary
        assert digest_stream.hexdigest() == facts.sha256
        sparse.unlink()


def _issue_code(reader, service, rel_path):
    from application.resource_channel import TypedResourceChannelError

    try:
        facts = reader.capture_facts(rel_path)
    except TypedResourceChannelError as error:
        return error.code
    try:
        service.issue(
            scope_class="derived-read-only", resource_id="res-over",
            revision_fingerprint="rev-1", rel_path=rel_path, facts=facts,
        )
    except TypedResourceChannelError as error:
        return error.code
    return None
