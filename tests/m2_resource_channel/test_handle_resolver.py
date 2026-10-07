"""Handle-verified reading semantics (RC1-AC4; M2-S2 productised)."""

from __future__ import annotations

import os
import subprocess
import threading

import pytest

from application.resource_channel import TypedResourceChannelError

from conftest import issue_for, write_noise_png, sha256_hex

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Win32 handle semantics")


def codes(callable_):
    try:
        callable_()
    except TypedResourceChannelError as error:
        return error.code
    return None


def grant_for(reader, service, scope, rel="asset.png"):
    opaque = issue_for(reader, service, scope, rel_path=rel)
    return opaque, service.resolve(opaque)


class TestPositive:
    def test_read_returns_issue_time_bytes(self, reader, service, scope):
        opaque, grant = grant_for(reader, service, scope)
        data = reader.read(grant, opaque)
        assert sha256_hex(data) == scope.small_sha

    def test_read_chunks_streams_same_bytes(self, reader, service, scope):
        opaque, grant = grant_for(reader, service, scope)
        blob = b"".join(reader.read_chunks(grant, chunk_size=4096))
        assert sha256_hex(blob) == scope.small_sha

    def test_nested_rel_path(self, reader, service, scope):
        opaque, grant = grant_for(reader, service, scope, rel="pages/page-002.png")
        assert reader.read(grant, opaque)[:8] == b"\x89PNG\r\n\x1a\n"

    def test_capture_facts_matches_file(self, reader, scope):
        facts = reader.capture_facts("asset.png")
        assert facts.sha256 == scope.small_sha
        assert facts.size > 0
        assert facts.volume_serial > 0
        assert facts.file_index > 0


class TestNegative:
    def test_identity_change_after_issue(self, reader, service, scope):
        opaque, grant = grant_for(reader, service, scope)
        # replace the file with a *new* file (fresh MFT record -> new index),
        # the M2-S2 relink method: an in-place overwrite keeps the same index
        target = scope.derived / "asset.png"
        target.unlink()
        payload = write_noise_png(target, 64, 64, seed=9999)
        assert sha256_hex(payload) != scope.small_sha
        assert codes(lambda: reader.read(grant, opaque)) == "FILE_IDENTITY_CHANGED"

    def test_equal_size_rewrite_digest_mismatch(self, reader, service, scope):
        opaque, grant = grant_for(reader, service, scope)
        target = scope.derived / "asset.png"
        original = target.read_bytes()
        flipped = bytes(b ^ 0xA5 for b in original[:64]) + original[64:]
        target.write_bytes(flipped)  # same size, different content, same path
        assert codes(lambda: reader.read(grant, opaque)) == "CONTENT_DIGEST_MISMATCH"

    def test_size_change_detected_before_read(self, reader, service, scope):
        opaque, grant = grant_for(reader, service, scope)
        target = scope.derived / "asset.png"
        target.write_bytes(original := target.read_bytes() + b"tail")
        assert codes(lambda: reader.read(grant, opaque)) == "FILE_SIZE_CHANGED"
        del original

    def test_junction_escape_at_read(self, reader, service, scope, tmp_path):
        # issue against a REAL directory first (capture must succeed), then
        # swap the directory component for a junction into the adversary tree
        target_dir = scope.derived / "linkj"
        outside_dir = scope.outside / "dir"
        outside_dir.mkdir(parents=True, exist_ok=True)
        write_noise_png(outside_dir / "nested.png", 64, 64, seed=4505)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "nested.png").write_bytes((outside_dir / "nested.png").read_bytes())
        opaque = issue_for(reader, service, scope, rel_path="linkj/nested.png")
        grant = service.resolve(opaque)
        # now swap the component for a junction (adversary, same user)
        (target_dir / "nested.png").unlink()
        target_dir.rmdir()
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target_dir), str(outside_dir)],
            capture_output=True,
        )
        assert created.returncode == 0
        # layered defence: pre-open walk refuses the reparse component, and a
        # race past it still dies on handle-derived containment
        assert codes(lambda: reader.read(grant, opaque)) in (
            "REF_REPARSE_POINT", "REF_OUT_OF_SCOPE",
        )

    def test_reparse_point_refused_on_capture(self, reader, scope):
        target_dir = scope.derived / "link2"
        if target_dir.exists():
            os.rmdir(target_dir)
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target_dir), str(scope.outside)],
            capture_output=True,
        )
        if created.returncode != 0:
            pytest.skip("junction creation unavailable")
        assert codes(lambda: reader.capture_facts("link2")) == "REF_REPARSE_POINT"
        os.rmdir(target_dir)

    def test_shared_violation_fails_closed(self, reader, service, scope):
        import ctypes
        import ctypes.wintypes

        from infrastructure.resource_channel.handle_resolver import (
            GENERIC_WRITE,
            FILE_SHARE_READ,
            FILE_SHARE_WRITE,
        )

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        opaque, grant = grant_for(reader, service, scope)
        # attacker pre-holds a write handle that still allows the reader's
        # read share; the reader's own share mode then cannot also allow the
        # pre-existing write access -> its open must fail closed
        handle = kernel32.CreateFileW(
            str(scope.derived / "asset.png"), GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE, None, 3, 0, None,
        )
        assert handle and handle != -1, "attacker pre-open must succeed"
        try:
            assert codes(lambda: reader.read(grant, opaque)) == "OPEN_FAILED_SHARING_VIOLATION"
        finally:
            kernel32.CloseHandle(ctypes.wintypes.HANDLE(handle))

    def test_missing_file_typed(self, reader, service, scope):
        opaque = issue_for(reader, service, scope, rel_path="pages/page-002.png")
        grant = service.resolve(opaque)
        (scope.derived / "pages" / "page-002.png").unlink()
        # re-issue facts no longer verifiable: open fails -> typed
        assert codes(lambda: reader.capture_facts("pages/page-002.png")) == "REF_NOT_FOUND"
        # a grant for a since-deleted file: read open fails -> OPEN_FAILED family
        code = codes(lambda: reader.read(grant, opaque))
        assert code in ("OPEN_FAILED", "REF_NOT_FOUND")


class TestConcurrency:
    def test_in_place_rewrite_during_read_is_caught(self, reader, service, scope):
        import ctypes
        import ctypes.wintypes

        from infrastructure.resource_channel.handle_resolver import (
            GENERIC_WRITE,
            FILE_SHARE_READ,
            FILE_SHARE_WRITE,
        )

        opaque, grant = grant_for(reader, service, scope)
        target = scope.derived / "asset.png"
        original = target.read_bytes()
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # pre-held write handle (availability-first mode): identity+size cannot
        # see an equal-size in-place rewrite, the issue-time digest must
        write_handle = kernel32.CreateFileW(
            str(target), GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE, None, 3, 0, None,
        )
        assert write_handle and write_handle != -1
        go = threading.Event()
        done = threading.Event()
        outcome: dict = {}

        def attacker():
            try:
                go.wait(10)
                # rewrite the NOT-yet-read second block (M2-S2 T-18 method):
                # flipping already-read bytes cannot change the stream digest
                block = original[64:96]
                flipped_block = bytes(b ^ 0x5A for b in block)
                kernel32.SetFilePointer(ctypes.wintypes.HANDLE(write_handle), 64, None, 0)
                written = ctypes.wintypes.DWORD(0)
                ok = kernel32.WriteFile(
                    ctypes.wintypes.HANDLE(write_handle), flipped_block, len(flipped_block),
                    ctypes.byref(written), None,
                )
                outcome["write_ok"] = bool(ok) and written.value == len(flipped_block)
            except Exception as error:  # noqa: BLE001 - surfaced via the assert
                outcome["attacker_error"] = f"{type(error).__name__}: {error}"
            finally:
                done.set()

        thread = threading.Thread(target=attacker, daemon=True)
        thread.start()

        # reader streams in small chunks; the attacker rewrites after the first
        observed: list = []
        try:
            for index, chunk in enumerate(reader.read_chunks(grant, chunk_size=64, share_write=True)):
                observed.append(chunk)
                if index == 0:
                    go.set()
                    done.wait(10)
            outcome["read_code"] = None
        except TypedResourceChannelError as error:
            outcome["read_code"] = error.code
        thread.join(10)
        if write_handle:
            kernel32.CloseHandle(ctypes.wintypes.HANDLE(write_handle))
        assert outcome.get("write_ok") and outcome.get("read_code") in (
            "CONTENT_DIGEST_MISMATCH", "FILE_SIZE_CHANGED",
        ), outcome

class TestPreviewNamespaceLease:
    """M2-DERIVED-GC-2 (design §2.3, G3): the namespace lease is a real
    Windows kernel lock on ``<derived>/.preview-lifecycle.lock``. Shared
    leases coexist across REAL OS processes; an exclusive lease excludes
    every other holder; process death releases it by the OS. No mock lock
    can substitute for these cases."""

    @staticmethod
    def _binding(tmp_path):
        from infrastructure.resource_channel.catalog_store import initialize_namespace

        derived = tmp_path / "derived"
        derived.mkdir(parents=True, exist_ok=True)
        catalog = tmp_path / "catalog.sqlite"
        binding = initialize_namespace(catalog, derived)
        return derived, catalog, binding

    @staticmethod
    def _child_script() -> str:
        import sys as _sys
        from pathlib import Path as _P

        src = _P(__file__).resolve().parents[2] / "src"
        return (
            "import sys; sys.path.insert(0, r'%s'); "
            "from pathlib import Path; "
            "from infrastructure.resource_channel.handle_resolver import acquire_shared_lease; "
            "lease = acquire_shared_lease(Path(sys.argv[1])); "
            "print('HELD', flush=True); "
            "import time; time.sleep(30)"
        ) % str(src)

    def test_shared_lease_in_child_blocks_exclusive_and_death_releases(self, tmp_path):
        import subprocess
        import sys
        import time

        from infrastructure.resource_channel.handle_resolver import (
            try_acquire_exclusive_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        child = subprocess.Popen(
            [sys.executable, "-c", self._child_script(), str(derived)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            assert child.stdout is not None
            line = child.stdout.readline()
            assert line.strip() == "HELD", f"child failed to hold the lease: {child.stderr.read() if child.stderr else ''}"

            # another REAL process holds the shared lease -> the exclusive
            # GC window is refused, non-blocking
            started = time.monotonic()
            assert try_acquire_exclusive_lease(derived) is None
            assert time.monotonic() - started < 2.0, "the exclusive attempt must not block"

            child.kill()
            child.wait(timeout=10)
            # process death releases the kernel lease -> the window opens
            deadline = time.monotonic() + 10
            lease = None
            while time.monotonic() < deadline:
                lease = try_acquire_exclusive_lease(derived)
                if lease is not None:
                    break
                time.sleep(0.1)
            assert lease is not None and lease.exclusive
            lease.release()
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=10)

    def test_two_independent_processes_share_concurrently_then_exclusive(self, tmp_path):
        import subprocess
        import sys
        import time

        from infrastructure.resource_channel.handle_resolver import (
            try_acquire_exclusive_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        children = []
        try:
            for _ in range(2):
                child = subprocess.Popen(
                    [sys.executable, "-c", self._child_script(), str(derived)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                children.append(child)
                assert child.stdout is not None
                assert child.stdout.readline().strip() == "HELD", (
                    f"child {len(children)} failed to hold the shared lease"
                )
            # two REAL processes hold shared leases at the same time
            assert try_acquire_exclusive_lease(derived) is None
            for child in children:
                child.kill()
            for child in children:
                child.wait(timeout=10)
            deadline = time.monotonic() + 10
            lease = None
            while time.monotonic() < deadline:
                lease = try_acquire_exclusive_lease(derived)
                if lease is not None:
                    break
                time.sleep(0.1)
            assert lease is not None and lease.exclusive
            lease.release()
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=10)

    def test_exclusive_lease_blocks_new_shared_holders(self, tmp_path):
        from infrastructure.resource_channel.handle_resolver import (
            acquire_shared_lease,
            namespace_unavailable,
            try_acquire_exclusive_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        lease = try_acquire_exclusive_lease(derived)
        assert lease is not None and lease.exclusive
        try:
            with pytest.raises(TypedResourceChannelError) as excinfo:
                acquire_shared_lease(derived)
            assert excinfo.value.code == "REF_SCOPE_DENIED"
        finally:
            lease.release()
        # after release a shared holder can come back
        shared = acquire_shared_lease(derived)
        shared.release()

    def test_binding_mismatch_and_alias_are_refused(self, tmp_path):
        from infrastructure.resource_channel.handle_resolver import (
            acquire_shared_lease,
            namespace_unavailable,
        )

        derived, catalog, binding = self._binding(tmp_path)
        shared = acquire_shared_lease(derived)
        shared.release()

        # a catalog identity the lock was never bound to -> refusal
        with pytest.raises(TypedResourceChannelError) as excinfo:
            acquire_shared_lease(
                derived, expected_catalog_identity=(binding.catalog_identity[0], 999999)
            )
        assert excinfo.value.code == "REF_SCOPE_DENIED"

        # a junction ALIAS of the same derived root cannot be distinguished
        # as a different root by path alone, but its canonical+identity must
        # resolve identically; a REPLACED root (different identity) must be
        # refused. Use a sibling directory with a copied lock file.
        import shutil

        other = tmp_path / "other-derived"
        shutil.copytree(derived, other)
        with pytest.raises(TypedResourceChannelError) as excinfo2:
            acquire_shared_lease(other)
        assert excinfo2.value.code == "REF_SCOPE_DENIED"

    def test_lock_path_junction_replacement_is_refused(self, tmp_path):
        # Codex r1 F-02: the lstat walk cannot cover a replacement between
        # the walk and CreateFileW, so the OPENED HANDLE is verified (reparse
        # attribute + final path). Here the lock FILE is deleted and the path
        # replaced by a junction BEFORE the lease attempt: CreateFileW would
        # follow it onto a directory, and the post-open checks must refuse
        # the lease instead of locking a foreign object.
        import _winapi
        import os

        from infrastructure.resource_channel.handle_resolver import (
            PREVIEW_NAMESPACE_LOCK_NAME,
            acquire_shared_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        lock = derived / PREVIEW_NAMESPACE_LOCK_NAME
        lock.unlink()
        outside = tmp_path / "outside"
        outside.mkdir()
        _winapi.CreateJunction(str(outside), str(lock))
        try:
            with pytest.raises(TypedResourceChannelError):
                acquire_shared_lease(derived)
            # the junction target is untouched: nothing got locked there
            canary = outside / "canary.txt"
            canary.write_bytes(b"free")
            assert canary.read_bytes() == b"free"
        finally:
            os.rmdir(str(lock))

    def test_race_equivalent_slipped_walk_still_refused(self, tmp_path, monkeypatch):
        # Codex r2 F-02: a real check-then-open race cannot be timed from a
        # test, so test the EQUIVALENT end state: the pre-open lstat walk has
        # already passed (neutralised here) while the path now IS a junction
        # -- exactly what the walk would have seen had it run after the
        # replacement. The lease must still be refused WITHOUT the walk, and
        # the refusal must NOT come from the walk's message family.
        import _winapi
        import os

        from infrastructure.resource_channel import handle_resolver as _hr
        from infrastructure.resource_channel.handle_resolver import (
            PREVIEW_NAMESPACE_LOCK_NAME,
            acquire_shared_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        lock = derived / PREVIEW_NAMESPACE_LOCK_NAME
        lock.unlink()
        outside = tmp_path / "outside"
        outside.mkdir()
        _winapi.CreateJunction(str(outside), str(lock))
        try:
            monkeypatch.setattr(_hr, "_lstat_reparse_walk", lambda path: None)
            with pytest.raises(TypedResourceChannelError) as excinfo:
                acquire_shared_lease(derived)
            # the (neutralised) walk's own message family must be absent:
            # the refusal came from the post-open verification path, which
            # is precisely the line of defence a slipped-past replacement
            # relies on
            assert "reparse component in namespace path" not in str(excinfo.value.message)
        finally:
            os.rmdir(str(lock))

    def test_reparse_derived_root_is_refused(self, tmp_path):
        import _winapi

        from infrastructure.resource_channel.handle_resolver import (
            acquire_shared_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        outside = tmp_path / "outside"
        outside.mkdir()
        junction = tmp_path / "alias-derived"
        _winapi.CreateJunction(str(derived), str(junction))
        try:
            with pytest.raises(TypedResourceChannelError):
                acquire_shared_lease(junction)
        finally:
            import os

            os.rmdir(str(junction))
        del outside

    def test_handle_verified_delete_refuses_reparse_candidate(self, tmp_path):
        import _winapi

        from infrastructure.resource_channel.handle_resolver import (
            handle_verified_delete,
        )

        derived, catalog, binding = self._binding(tmp_path)
        previews = derived / "previews"
        previews.mkdir(exist_ok=True)
        outside_file = tmp_path / "outside.png"
        outside_file.write_bytes(b"precious")
        link = previews / "preview-link.png"
        _winapi.CreateJunction(str(outside_file), str(link))
        try:
            # the pre-open reparse walk refuses the candidate BEFORE any
            # handle exists -- a typed refusal, never a pathname unlink
            with pytest.raises(TypedResourceChannelError):
                handle_verified_delete(
                    derived, "previews/preview-link.png",
                    expected_sha256="0" * 64, expected_size=8,
                )
            assert outside_file.is_file(), "a reparse candidate must never be deleted"
        finally:
            import os

            os.rmdir(str(link))


    def test_race_equivalent_slipped_walk_still_refused(self, tmp_path, monkeypatch):
        # Codex r2/r3 F-02: a real check-then-open race cannot be timed from
        # a test, so test the EQUIVALENT end state: the pre-open lstat walk
        # has already passed (neutralised here) while the path now IS a
        # junction -- exactly what the walk would have seen had it run after
        # the replacement. The lease must still be refused WITHOUT the walk,
        # and the refusal must NOT come from the walk's message family.
        import _winapi
        import os

        from infrastructure.resource_channel import handle_resolver as _hr
        from infrastructure.resource_channel.handle_resolver import (
            PREVIEW_NAMESPACE_LOCK_NAME,
            acquire_shared_lease,
        )

        derived, catalog, binding = self._binding(tmp_path)
        lock = derived / PREVIEW_NAMESPACE_LOCK_NAME
        lock.unlink()
        outside = tmp_path / "outside"
        outside.mkdir()
        _winapi.CreateJunction(str(outside), str(lock))
        try:
            monkeypatch.setattr(_hr, "_lstat_reparse_walk", lambda path: None)
            with pytest.raises(TypedResourceChannelError) as excinfo:
                acquire_shared_lease(derived)
            # the (neutralised) walk's own message family must be absent:
            # the refusal came from the post-open verification path, which
            # is precisely the line of defence a slipped-past replacement
            # relies on
            assert "reparse component in namespace path" not in str(excinfo.value.message)
        finally:
            os.rmdir(str(lock))

    def test_postopen_verification_fires_refuses_and_closes(self, tmp_path, monkeypatch):
        # Codex r3 F-02: unit-level discrimination of the SECOND line of
        # defence. With the pre-open walk neutralised (the state after a
        # replacement slipped past it) and the opened handle REPORTING a
        # reparse attribute, `_open_lock_handle` must (a) run the post-open
        # verification, (b) refuse with its own message, and (c) CLOSE the
        # opened handle -- a lease is never returned for a foreign object.
        from infrastructure.resource_channel import handle_resolver as _hr
        from infrastructure.resource_channel.handle_resolver import (
            FILE_ATTRIBUTE_REPARSE_POINT,
        )

        derived, catalog, binding = self._binding(tmp_path)

        real_attributes = _hr._attributes_of
        real_close = _hr._k32.CloseHandle
        calls = {"attributes": 0, "close": 0}

        def reporting_attributes(handle):
            calls["attributes"] += 1
            return FILE_ATTRIBUTE_REPARSE_POINT  # the opened object claims reparse

        def counting_close(handle):
            calls["close"] += 1
            return real_close(handle)

        monkeypatch.setattr(_hr, "_lstat_reparse_walk", lambda path: None)
        monkeypatch.setattr(_hr, "_attributes_of", reporting_attributes)
        monkeypatch.setattr(_hr._k32, "CloseHandle", counting_close)
        try:
            with pytest.raises(TypedResourceChannelError, match="reparse point"):
                _hr._open_lock_handle(str(derived), exclusive=False)
        finally:
            monkeypatch.setattr(_hr._k32, "CloseHandle", real_close)
        assert calls["attributes"] >= 1, "the post-open verification must have run"
        assert calls["close"] >= 1, "a refused lease must close its opened handle"
