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
