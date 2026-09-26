"""ResourceChannelService semantics (RC1-AC3/AC4/AC5 control plane)."""

from __future__ import annotations

import pytest

from application.resource_channel import (
    MAX_ACTIVE_REFERENCES,
    MAX_SUBSCRIBERS_PER_RESOURCE,
    ResourceChannelService,
    ResourceFacts,
    TypedResourceChannelError,
)

from conftest import issue_for


def codes(callable_):
    try:
        callable_()
    except TypedResourceChannelError as error:
        return error.code
    return None


FACTS = ResourceFacts(volume_serial=1, file_index=2, size=10, sha256="a" * 64)


class TestIssueAndResolve:
    def test_issue_returns_opaque_id_and_resolve_returns_grant(self, reader, service, scope):
        opaque = issue_for(reader, service, scope)
        assert opaque.startswith("m2id.v1.")
        grant = service.resolve(opaque)
        assert grant.rel_path == "asset.png"
        assert grant.scope_class == "derived-read-only"
        assert grant.resource_id == "res-001"
        assert grant.revision_fingerprint == "rev-1"

    def test_user_source_scope_refused_at_issue(self, service):
        code = codes(lambda: service.issue(
            scope_class="user-source", resource_id="r", revision_fingerprint="v",
            rel_path="whatever.png",
            facts=ResourceFacts(volume_serial=1, file_index=1, size=1, sha256="b" * 64),
        ))
        assert code == "REF_SCOPE_DENIED"

    def test_absolute_and_traversal_rel_paths_refused(self, service):
        facts = ResourceFacts(volume_serial=1, file_index=1, size=1, sha256="c" * 64)
        assert codes(lambda: service.issue(
            scope_class="derived-read-only", resource_id="r", revision_fingerprint="v",
            rel_path="C:/Windows/system32/config", facts=facts,
        )) == "REF_MALFORMED"
        assert codes(lambda: service.issue(
            scope_class="derived-read-only", resource_id="r", revision_fingerprint="v",
            rel_path="../outside/outside_secret.png", facts=facts,
        )) == "REF_MALFORMED"
        assert codes(lambda: service.issue(
            scope_class="derived-read-only", resource_id="r", revision_fingerprint="v",
            rel_path="a/../../b.png", facts=facts,
        )) == "REF_MALFORMED"

    def test_over_limit_resource_refused_at_issue(self, service):
        facts = ResourceFacts(
            volume_serial=1, file_index=1, size=256 * 1024 * 1024 + 1, sha256="d" * 64
        )
        assert codes(lambda: service.issue(
            scope_class="derived-read-only", resource_id="r", revision_fingerprint="v",
            rel_path="big.png", facts=facts,
        )) == "RESOURCE_TOO_LARGE"

    def test_same_path_issued_twice_yields_distinct_unlinkable_ids(self, reader, service, scope):
        first = issue_for(reader, service, scope, resource_id="res-dup", revision="rev-x")
        second = issue_for(reader, service, scope, resource_id="res-dup", revision="rev-x")
        assert first != second
        grant_a = service.resolve(first)
        grant_b = service.resolve(second)
        assert grant_a.rel_path == grant_b.rel_path


class TestLifecycle:
    def test_unknown_id_typed(self, service):
        assert codes(lambda: service.resolve("m2id.v1.NOSUCH")) == "REF_UNKNOWN_ID"

    def test_revoke_then_resolve_typed(self, reader, service, scope):
        opaque = issue_for(reader, service, scope)
        service.revoke(opaque)
        assert codes(lambda: service.resolve(opaque)) == "REF_REVOKED"

    def test_expiry_typed(self, reader, scope):
        clock = {"now": 1000.0}
        service = ResourceChannelService(clock=lambda: clock["now"], default_ttl_seconds=50.0)
        opaque = issue_for(reader, service, scope)
        clock["now"] = 1051.0  # past issued expiry (1000+50)
        assert codes(lambda: service.resolve(opaque)) == "REF_EXPIRED"

    def test_sliding_renewal_extends_window(self, reader, scope):
        clock = {"now": 1000.0}
        service = ResourceChannelService(
            clock=lambda: clock["now"], default_ttl_seconds=100.0
        )
        opaque = issue_for(reader, service, scope)
        clock["now"] = 90.0  # near expiry
        grant = service.resolve(opaque)  # renews to now+100
        assert grant is not None
        clock["now"] = 150.0  # inside the renewed window, would be expired otherwise
        assert service.resolve(opaque) is not None
        clock["now"] = 260.0
        assert codes(lambda: service.resolve(opaque)) == "REF_EXPIRED"

    def test_revision_switch_revokes_immediately(self, reader, service, scope):
        first = issue_for(reader, service, scope, resource_id="res-rev", revision="rev-1")
        issue_for(reader, service, scope, resource_id="res-rev", revision="rev-2")
        revoked_count = service.revoke_resource("res-rev", "rev-1")
        assert revoked_count == 1
        assert codes(lambda: service.resolve(first)) == "REF_REVOKED"
        # the new revision's reference is untouched
        assert service.resolve(
            [k for k, v in service._table.items() if not v.revoked][0]
        ) is not None

    def test_delete_revokes_all_revisions(self, reader, service, scope):
        a = issue_for(reader, service, scope, resource_id="res-del", revision="rev-1")
        b = issue_for(reader, service, scope, resource_id="res-del", revision="rev-2")
        assert service.revoke_resource("res-del") == 2
        assert codes(lambda: service.resolve(a)) == "REF_REVOKED"
        assert codes(lambda: service.resolve(b)) == "REF_REVOKED"

    def test_core_restart_never_rebinds_old_ids(self, reader, scope):
        first = ResourceChannelService()
        opaque = issue_for(reader, first, scope, resource_id="res-old", revision="rev-1")
        restarted = ResourceChannelService()  # fresh process == fresh table
        assert codes(lambda: restarted.resolve(opaque)) == "REF_UNKNOWN_ID"
        # and a same-name resource issued after restart gets a different ID
        fresh = issue_for(reader, restarted, scope, resource_id="res-old", revision="rev-1")
        assert fresh != opaque


class TestLimits:
    def test_active_reference_limit(self, reader, scope):
        service = ResourceChannelService(max_active_references=4)
        ids = [issue_for(reader, service, scope, resource_id=f"res-{i}", revision="rev-1")
               for i in range(4)]
        assert len(ids) == 4
        assert codes(lambda: issue_for(reader, service, scope, resource_id="res-next", revision="rev-1")) \
            == "RESOURCE_LIMIT_EXCEEDED"

    def test_subscriber_limit_per_resource(self, reader, service, scope):
        opaque = issue_for(reader, service, scope)
        for _ in range(MAX_SUBSCRIBERS_PER_RESOURCE):
            service.acquire_subscriber(opaque)
        assert codes(lambda: service.acquire_subscriber(opaque)) == "RESOURCE_LIMIT_EXCEEDED"
        service.release_subscriber(opaque)
        service.acquire_subscriber(opaque)  # released slot is reusable

    def test_max_constants_match_ruling(self):
        assert MAX_ACTIVE_REFERENCES == 32
        assert MAX_SUBSCRIBERS_PER_RESOURCE == 16
