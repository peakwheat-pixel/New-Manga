"""RC2-AC1: Core/SQLite catalog authority and bridge denial matrix (F-03).

The WebView/host control surface must not be able to name OS paths, extend
reference lifetimes, or fabricate catalog state. These tests pin the denial
side of the allow/deny matrix at the Python Core boundary:

- catalog writes are validated (servable scope class, rel-path gate);
- bridge ``issue`` resolves paths only from the catalog store -- a
  ``rel_path``/``scope_class`` request parameter is a typed refusal;
- an uncataloged resource id is ``RESOURCE_NOT_CATALOGED`` (fail-closed);
- a ``ttl_seconds`` override can only shorten a grant (0/negative and
  above-default values are refused), so no caller can extend a lifetime.
"""

from __future__ import annotations

import io

import pytest

from application.resource_channel import TypedResourceChannelError
from application.resource_channel.dto import DEFAULT_TTL_SECONDS
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from infrastructure.resource_channel.host_bridge import CoreChannelServer
from infrastructure.resource_channel.scope import ScopeRoots

from conftest import issue_for


@pytest.fixture()
def catalog() -> ResourceCatalogStore:
    return ResourceCatalogStore(":memory:")


@pytest.fixture()
def seeded_server(scope, service, catalog):
    catalog.upsert("res-001", "derived-read-only", "asset.png")

    def _server() -> CoreChannelServer:
        roots = ScopeRoots(derived_root=scope.derived, managed_root=scope.managed)
        return CoreChannelServer(
            service=service, roots=roots, catalog=catalog, stdin=io.StringIO(), stdout=io.StringIO()
        )

    return _server


class TestCatalogStoreValidation:
    def test_upsert_lookup_remove_roundtrip(self, catalog, tmp_path):
        assert catalog.count() == 0
        catalog.upsert("res-x", "derived-read-only", "pages/page-002.png")
        entry = catalog.lookup("res-x")
        assert entry == ("res-x", "derived-read-only", "pages/page-002.png")
        assert catalog.count() == 1
        # upsert replaces the mapping: the catalog row is authoritative state
        catalog.upsert("res-x", "managed-read-only", "asset.png")
        assert catalog.lookup("res-x") == ("res-x", "managed-read-only", "asset.png")
        assert catalog.count() == 1
        assert catalog.remove("res-x") is True
        assert catalog.lookup("res-x") is None
        assert catalog.remove("res-x") is False

    def test_persists_across_connections(self, tmp_path):
        db = tmp_path / "catalog.sqlite"
        first = ResourceCatalogStore(db)
        first.upsert("res-disk", "derived-read-only", "asset.png")
        first.close()
        second = ResourceCatalogStore(db)
        try:
            assert second.lookup("res-disk") == ("res-disk", "derived-read-only", "asset.png")
        finally:
            second.close()

    def test_user_source_scope_refused_at_write(self, catalog):
        with pytest.raises(TypedResourceChannelError) as excinfo:
            catalog.upsert("res-user", "user-source", "whatever.png")
        assert excinfo.value.code == "REF_SCOPE_DENIED"
        assert catalog.lookup("res-user") is None

    def test_traversal_rel_path_refused_at_write(self, catalog):
        for bad in ("../outside_secret.png", "a/../../b.png", "C:/win/secret.png", "\\\\srv\\share", ""):
            with pytest.raises(TypedResourceChannelError) as excinfo:
                catalog.upsert("res-bad", "derived-read-only", bad)
            assert excinfo.value.code == "REF_MALFORMED", bad
        assert catalog.count() == 0

    def test_empty_resource_id_refused_at_write(self, catalog):
        with pytest.raises(TypedResourceChannelError) as excinfo:
            catalog.upsert("", "derived-read-only", "asset.png")
        assert excinfo.value.code == "REF_MALFORMED"


class TestBridgeIssueDenialMatrix:
    def test_issue_resolves_path_from_catalog(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
        }})
        assert "error" not in response
        opaque = response["result"]["id"]
        resolved = server._dispatch({"id": 2, "method": "resolve", "params": {"id": opaque}})
        assert resolved["result"]["rel_path"] == "asset.png"
        assert resolved["result"]["scope_class"] == "derived-read-only"

    def test_issue_unknown_resource_fail_closed(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-never-cataloged", "revision_fingerprint": "rev-1",
        }})
        assert response["error"]["code"] == "RESOURCE_NOT_CATALOGED"

    def test_issue_with_rel_path_param_refused(self, scope, service, seeded_server):
        """The host may not name paths: a smuggled rel_path is a typed refusal
        even when the value matches a legitimate catalog row."""

        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "rel_path": "asset.png",
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_issue_with_traversal_rel_path_param_refused(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "rel_path": "../../outside/outside_secret.png",
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_issue_with_scope_class_param_refused(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "scope_class": "user-source",
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_fail_closed_without_catalog_source(self, scope, service):
        roots = ScopeRoots(derived_root=scope.derived, managed_root=scope.managed)
        server = CoreChannelServer(
            service=service, roots=roots, stdin=io.StringIO(), stdout=io.StringIO()
        )
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
        }})
        assert response["error"]["code"] == "RESOURCE_NOT_CATALOGED"
        # the bridge itself stays responsive for control operations
        assert server._dispatch({"id": 2, "method": "ping"})["result"]["pong"] is True


class TestTtlCannotBeExtended:
    def test_issue_with_default_ttl_passes(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "ttl_seconds": DEFAULT_TTL_SECONDS,
        }})
        assert "error" not in response

    def test_issue_with_probe_short_ttl_passes(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "ttl_seconds": 0.3,
        }})
        assert "error" not in response

    def test_issue_with_ttl_above_default_refused(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "ttl_seconds": DEFAULT_TTL_SECONDS + 1,
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_issue_with_non_positive_ttl_refused(self, scope, service, seeded_server):
        server = seeded_server()
        for bad in (0, -1, 0.0, -0.5):
            response = server._dispatch({"id": 1, "method": "issue", "params": {
                "resource_id": "res-001", "revision_fingerprint": "rev-1",
                "ttl_seconds": bad,
            }})
            assert response["error"]["code"] == "REF_MALFORMED", bad

    def test_service_level_ttl_extension_refused(self, reader, service, scope):
        facts = reader.capture_facts("asset.png")
        with pytest.raises(TypedResourceChannelError) as excinfo:
            service.issue(
                scope_class="derived-read-only", resource_id="res-ttl",
                revision_fingerprint="rev-1", rel_path="asset.png", facts=facts,
                ttl_seconds=DEFAULT_TTL_SECONDS * 2,
            )
        assert excinfo.value.code == "REF_MALFORMED"

    def test_sliding_renewal_rearms_to_ruled_default(self, reader, scope):
        """Sliding renewal (T6, unchanged from RC1) always re-arms the ruled
        default TTL -- never a caller-chosen value and never an accumulation
        of shortened issue overrides."""

        from application.resource_channel import ResourceChannelService

        clock = {"now": 1000.0}
        service = ResourceChannelService(clock=lambda: clock["now"])
        facts = reader.capture_facts("asset.png")
        opaque = service.issue(
            scope_class="derived-read-only", resource_id="res-ttl2",
            revision_fingerprint="rev-1", rel_path="asset.png", facts=facts,
            ttl_seconds=10.0,
        )
        clock["now"] += 5.0
        service.resolve(opaque)
        # the renewal armed the DEFAULT ttl, not the shortened issue ttl:
        # the grant now survives until now + 300
        clock["now"] += 200.0
        assert service.resolve(opaque, renew=False) is not None
