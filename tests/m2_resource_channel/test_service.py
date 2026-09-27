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

from conftest import issue_for, sha256_hex


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
        from application.resource_channel import DEFAULT_TTL_SECONDS
        assert DEFAULT_TTL_SECONDS == 300.0  # T6 default (F-13: asserted, not assumed)


class TestF13CoverageAdds:
    # DSH F-13: coverage adds for the claims the review found unchecked.

    def test_default_ttl_is_300s_and_touch_renews(self, reader, scope):
        from application.resource_channel import DEFAULT_TTL_SECONDS

        clock = {"now": 0.0}
        service = ResourceChannelService(
            clock=lambda: clock["now"], default_ttl_seconds=DEFAULT_TTL_SECONDS
        )
        opaque = issue_for(reader, service, scope)
        # far inside the default window
        clock["now"] = DEFAULT_TTL_SECONDS - 10
        assert service.resolve(opaque) is not None
        # touch re-arms from *now* (sliding, T6)
        service.touch(opaque)
        clock["now"] = DEFAULT_TTL_SECONDS + 5
        assert service.resolve(opaque) is not None

    def test_pin_release_alias_revokes(self, reader, service, scope):
        # deletion/pin-release call sites revoke every reference of the
        # resource (the alias exists to make those call sites explicit)
        a = issue_for(reader, service, scope, resource_id="res-pin", revision="rev-1")
        assert service.revoke_bookkeeping_for("res-pin") == 1
        assert codes(lambda: service.resolve(a)) == "REF_REVOKED"

    def test_inflight_consumption_survives_revoke(self, reader, service, scope):
        # T6 carve-out: revoking a reference does not force-abort a read that
        # already resolved its grant (the handle holder owns the lifecycle)
        opaque = issue_for(reader, service, scope)
        grant = service.resolve(opaque)  # in-flight consumption starts here
        service.revoke(opaque)
        # the granted object still reads through its verified handle
        data = reader.read(grant, opaque)
        assert sha256_hex(data) == scope.small_sha
        # while the *next* resolve is rejected immediately
        assert codes(lambda: service.resolve(opaque)) == "REF_REVOKED"

    def test_t2_concurrent_subscriber_matrix(self, reader, service, scope):
        # F-13: real concurrent acquisition up to the T2 subscriber limit
        import threading

        opaque = issue_for(reader, service, scope)
        accepted, rejected = [], []
        lock = threading.Lock()

        def try_acquire():
            try:
                service.acquire_subscriber(opaque)
                with lock:
                    accepted.append(1)
            except TypedResourceChannelError as error:
                with lock:
                    rejected.append(error.code)

        threads = [threading.Thread(target=try_acquire) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
        assert len(accepted) == MAX_SUBSCRIBERS_PER_RESOURCE
        assert rejected == ["RESOURCE_LIMIT_EXCEEDED"] * (20 - MAX_SUBSCRIBERS_PER_RESOURCE)

    def test_default_active_reference_limit_is_32(self, reader, scope):
        # F-13: the DEFAULT (unconfigured) limit must be the ruled 32
        service = ResourceChannelService()
        ids = [
            issue_for(reader, service, scope, resource_id=f"res-{i}", revision="rev-1")
            for i in range(32)
        ]
        assert len(ids) == 32
        assert codes(
            lambda: issue_for(reader, service, scope, resource_id="res-33", revision="rev-1")
        ) == "RESOURCE_LIMIT_EXCEEDED"

    def test_same_resource_17th_reference_rejected(self, reader, service, scope):
        # F-13: 16 active references of ONE resource are the T2 subscriber
        # ceiling; the 17th is typed-rejected
        ids = [
            issue_for(reader, service, scope, resource_id="res-same", revision=f"rev-{i}")
            for i in range(16)
        ]
        assert len(ids) == 16
        assert codes(
            lambda: issue_for(reader, service, scope, resource_id="res-same", revision="rev-17")
        ) == "RESOURCE_LIMIT_EXCEEDED"

    def test_reader_opens_read_only_generic_access(self, reader, service, scope, monkeypatch):
        # F-13/R-04: capture the REAL CreateFileW arguments by wrapping the
        # module-level kernel32 binding (a spy on _open_read_handle can only
        # echo module constants back, which is tautological). The default
        # narrow-share open must request GENERIC_READ / FILE_SHARE_READ with
        # no write flag; the availability-first variant opts into
        # FILE_SHARE_WRITE explicitly.
        import infrastructure.resource_channel.handle_resolver as resolver_mod

        captured: list[tuple[str, int, int]] = []

        class _K32Spy:
            def __init__(self, real):
                self._real = real

            def CreateFileW(self, name, desired_access, share_mode, *rest):
                captured.append((str(name), desired_access, share_mode))
                return self._real.CreateFileW(name, desired_access, share_mode, *rest)

            def __getattr__(self, item):
                return getattr(self._real, item)

        monkeypatch.setattr(resolver_mod, "_k32", _K32Spy(resolver_mod._k32))

        opaque = issue_for(reader, service, scope)
        grant = service.resolve(opaque)
        reader.read(grant, opaque)
        reader.read(grant, opaque, share_write=True)

        assert captured, "CreateFileW was never invoked through the resolver"
        share_modes = {share for _, _, share in captured}
        for name, access, share in captured:
            assert access == resolver_mod.GENERIC_READ
            assert access & resolver_mod.GENERIC_WRITE == 0
            assert share in (
                resolver_mod.FILE_SHARE_READ,
                resolver_mod.FILE_SHARE_READ | resolver_mod.FILE_SHARE_WRITE,
            ), f"unexpected share mode {share:#x} for {name}"
        assert resolver_mod.FILE_SHARE_READ in share_modes
        assert (resolver_mod.FILE_SHARE_READ | resolver_mod.FILE_SHARE_WRITE) in share_modes

    def test_read_only_channel_has_no_write_surface(self, reader, service, scope):
        # F-13/F-07: the control plane has no write mode; the reader only
        # opens GENERIC_READ. REF_READ_ONLY is a documented non-reachable code
        # for this slice (no write-mode request shape exists)
        opaque = issue_for(reader, service, scope)
        grant = service.resolve(opaque)
        # the grant carries no write capability and the reader takes no mode
        data = reader.read(grant, opaque)
        assert sha256_hex(data) == scope.small_sha
        # writing through the *channel* is not expressible: the service has
        # no write entry point at all
        write_entries = [
            name for name in dir(service)
            if name.startswith("write") and callable(getattr(service, name))
        ]
        assert write_entries == []
