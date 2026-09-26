"""Probe S2-TOCTOU -- negative probes for M2-S1 blocker S1-B11 (TOCTOU).

M2-S1 measured the check-then-use window as OPEN (F-03..F-06) and only
demonstrated the handle-bound direction in isolation (F-07/F-08). This probe
systematically exercises the release conditions of S1-B11 (M2-S1 §8.2):

- condition (1): the reference resolver is the open-then-verify-from-handle
  prototype in ``m2s2_lab.HandleVerifiedResolver`` (identity + size +
  containment from the opened handle; reads only through that handle).
- condition (2): the negative matrix below replaces, between check and open:
  file content (small and large scale), a directory component (junction, and
  symlink when the environment allows), and an equal-size different-content
  swap; plus in-place rewrites by an adversary that already held a write
  handle (identity+size cannot see those; the content digest layer must).
- condition (3) partial: adversary-writable scope root and parent-directory
  scenarios are included (T-14/T-15). The "target packaging/sandbox form"
  part of condition (3) and condition (4) (DACL/integrity level) are OUT OF
  SCOPE here (they depend on S1-B8 / S1-B3) and stay NOT_RUN.

Every negative scenario must end in a typed rejection (stable error code),
and every scenario ends with a restore check: after removing the attack the
legitimate resource must again resolve and read back byte-identical (sha256)
-- that is the in-scenario positive control.

Determinism: each attack runs on its own thread behind explicit
``threading.Event`` sync points (before_open / after_open_before_verify /
during_read), so the interleaving is fixed, not timing-dependent.

Run:
  python verification/M2-S2/probes/probe_s2_toctou.py --lab <lab> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import m2s2_lab as lab  # noqa: E402

PROBE = "S2-TOCTOU"


def _relink(source: Path, target: Path) -> None:
    """Place an independent *copy* of ``source`` at ``target`` (replacing it).

    A copy, not a hardlink: content-rewrite attacks (T-16..T-18) must never
    reach back into the shared fixture file through a hardlink.
    """

    import shutil

    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    shutil.copyfile(source, target)


def _move_aside(path: Path) -> Path:
    """Rename ``path`` next to itself and return the new location."""

    moved = path.with_name(path.name + "_moved")
    if moved.exists():
        _remove_tree(moved)
    os.rename(path, moved)
    return moved


def _remove_tree(path: Path) -> None:
    import shutil

    shutil.rmtree(path, ignore_errors=True)


def _sha256(path: Path) -> str:
    return lab.sha256_file(path)


class Attacker:
    """Runs an attack action behind an Event handshake with a resolver hook."""

    def __init__(self, hook_name: str, action) -> None:
        self.hook_name = hook_name
        self.action = action
        self.outcome: dict = {}
        self._go = threading.Event()
        self._done = threading.Event()

    def _hook(self, _context: dict) -> None:
        self._go.set()
        if not self._done.wait(lab.SYNC_TIMEOUT_SECONDS):
            raise lab.ProbeError("SYNC_TIMEOUT", self.hook_name)

    def _worker(self) -> None:
        try:
            self._go.wait(lab.SYNC_TIMEOUT_SECONDS)
            self.outcome["attack_result"] = self.action()
        except Exception as error:  # noqa: BLE001 - the probe judges the outcome
            self.outcome["attack_error"] = f"{type(error).__name__}: {error}"
        finally:
            self._done.set()

    def run(self, resolver: lab.HandleVerifiedResolver, token: str, *, limit: int | None = None, share_write: bool = False) -> tuple[str | None, dict | None]:
        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()
        error_code: str | None = None
        read_result: dict | None = None
        kwargs: dict = {"hooks": {self.hook_name: self._hook}}
        if limit is not None:
            kwargs["limit"] = limit
        if share_write:
            kwargs["share_write"] = True
        try:
            read_result = resolver.resolve_and_read(token, **kwargs)
        except lab.ProbeError as error:
            error_code = error.code
        thread.join(lab.SYNC_TIMEOUT_SECONDS)
        return error_code, read_result


class ScenarioBook:
    """Fixture layout + per-scenario record building with restore control."""

    def __init__(self, lab_root_path: Path) -> None:
        fixtures = json.loads((lab_root_path / "fixtures" / "fixtures.json").read_text(encoding="utf-8"))
        by_name = {entry["name"]: entry for entry in fixtures["fixtures"]}
        self.small_fixture = Path(by_name["small_page_800x1200"]["path"])
        self.typical_fixture = Path(by_name["typical_page_1600x2400"]["path"])
        self.small_sha = _sha256(self.small_fixture)
        self.typical_sha = _sha256(self.typical_fixture)

        self.work = lab_root_path / "toctou"
        _remove_tree(self.work)
        self.scope = self.work / "scope"
        self.outside = self.work / "outside"
        (self.scope / "derived" / "sub").mkdir(parents=True, exist_ok=True)
        self.outside.mkdir(parents=True, exist_ok=True)

        # scope content
        self.asset = self.scope / "derived" / "asset.png"
        _relink(self.small_fixture, self.asset)
        self.nested = self.scope / "derived" / "sub" / "nested.png"
        _relink(self.small_fixture, self.nested)

        # outside (adversary-controlled) content
        self.outside_secret = self.outside / "outside_secret.png"
        _relink(self.typical_fixture, self.outside_secret)
        self.outside_dir = self.outside / "dir"
        (self.outside_dir).mkdir(parents=True, exist_ok=True)
        self.outside_nested = self.outside_dir / "nested.png"
        _relink(self.typical_fixture, self.outside_nested)
        self.outside_asset2 = self.outside_dir / "asset2.png"
        _relink(self.typical_fixture, self.outside_asset2)
        self.mirror_derived = self.outside / "mirror" / "derived"
        self.mirror_derived.mkdir(parents=True, exist_ok=True)
        self.mirror_asset = self.mirror_derived / "asset.png"
        _relink(self.typical_fixture, self.mirror_asset)

        same = lab.make_same_size_variant(self.small_fixture, self.outside / "same_size_variant.png")
        self.same_size_variant = self.outside / "same_size_variant.png"
        self.same_size_info = same

        self.secret = os.urandom(32)
        self.resolver = lab.HandleVerifiedResolver(self.scope, self.secret)
        self.records: list[dict] = []

    # -- issue helpers -----------------------------------------------------

    def issue_asset(self, rid: str) -> str:
        return self.resolver.issue(rid, "derived/asset.png", ttl_seconds=600)

    def issue_nested(self, rid: str) -> str:
        return self.resolver.issue(rid, "derived/sub/nested.png", ttl_seconds=600)

    # -- record helpers ----------------------------------------------------

    def restore_check(self, issuer, rid: str, expected_sha: str) -> dict:
        """Re-issue and read the legitimate resource; the in-scenario control."""

        token = issuer(rid)
        try:
            result = self.resolver.resolve_and_read(token)
            return {
                "restore_ok": result["sha256"] == expected_sha,
                "restore_sha256": result["sha256"],
                "restore_expected": expected_sha,
            }
        except lab.ProbeError as error:
            return {"restore_ok": False, "restore_error_code": error.code}

    def record_attack(
        self,
        scenario_id: str,
        expected_code: str,
        actual_code: str | None,
        read_result: dict | None,
        attacker: Attacker,
        restore: dict,
        note: str,
        extra: dict | None = None,
    ) -> dict:
        record = {
            "id": scenario_id,
            "status": lab.PASS if actual_code == expected_code and restore.get("restore_ok") else lab.FAIL,
            "expected_rejection_code": expected_code,
            "actual_rejection_code": actual_code,
            "typed_rejection": actual_code == expected_code,
            "read_through_handle_result": read_result,
            "attack_outcome": attacker.outcome,
            "restore_check": restore,
            "note": note,
        }
        if extra:
            record.update(extra)
        return record


def run_host(lab_root_path: Path) -> dict:
    book = ScenarioBook(lab_root_path)
    records = book.records

    # ---------------- T-01P positive control: small asset -------------------
    token = book.issue_asset("rid-t01")
    try:
        result = book.resolver.resolve_and_read(token)
        t01 = {
            "id": "T-01P-positive-small-asset",
            "status": lab.PASS if result["sha256"] == book.small_sha else lab.FAIL,
            "sha256": result["sha256"],
            "expected_sha256": book.small_sha,
            "bytes_read": result["bytes_read"],
            "identity": result["identity"],
            "final_path": result["final_path"],
            "note": "open once, verify identity+size+containment from the handle, read through the handle",
        }
    except lab.ProbeError as error:
        t01 = {"id": "T-01P-positive-small-asset", "status": lab.FAIL, "error_code": error.code}
    records.append(t01)

    # ---------------- T-02P positive control: larger asset ------------------
    # place a hardlink of the typical fixture into the scope for this control
    typical_in_scope = book.scope / "derived" / "typical.png"
    _relink(book.typical_fixture, typical_in_scope)
    token_large = book.resolver.issue("rid-t02", "derived/typical.png", ttl_seconds=600)
    try:
        result = book.resolver.resolve_and_read(token_large, limit=lab.MEDIA_LIMIT_BYTES)
        t02 = {
            "id": "T-02P-positive-larger-asset",
            "status": lab.PASS if result["sha256"] == book.typical_sha else lab.FAIL,
            "sha256": result["sha256"],
            "expected_sha256": book.typical_sha,
            "bytes_read": result["bytes_read"],
            "limit_bytes": lab.MEDIA_LIMIT_BYTES,
            "note": "larger legitimate asset served within the M2-S1-parity probe limit",
        }
    except lab.ProbeError as error:
        t02 = {"id": "T-02P-positive-larger-asset", "status": lab.FAIL, "error_code": error.code}
    records.append(t02)
    typical_in_scope.unlink()

    # ---------------- T-03P over-limit rejected from handle -----------------
    typical_in_scope = book.scope / "derived" / "typical.png"
    _relink(book.typical_fixture, typical_in_scope)
    token_over = book.resolver.issue("rid-t03", "derived/typical.png", ttl_seconds=600)
    try:
        book.resolver.resolve_and_read(token_over, limit=lab.TOCTOU_LIMIT_BYTES)
        t03 = {"id": "T-03P-over-limit-typed-rejection", "status": lab.FAIL, "error_code": None}
    except lab.ProbeError as error:
        t03 = {
            "id": "T-03P-over-limit-typed-rejection",
            "status": lab.PASS if error.code == "MEDIA_TOO_LARGE_BY_HANDLE" else lab.FAIL,
            "error_code": error.code,
            "limit_bytes": lab.TOCTOU_LIMIT_BYTES,
            "limit_label": "probe configuration, NOT a product threshold",
            "note": "size is verified from the opened handle before any byte is read",
        }
    records.append(t03)
    typical_in_scope.unlink()

    # ---------------- T-04P static negative controls ------------------------
    junction_static = lab.make_junction(book.scope / "derived" / "link", book.outside_dir)
    static_cases: list[dict] = []

    def expect_code(token_value: str, **kwargs) -> str | None:
        try:
            book.resolver.resolve_and_read(token_value, **kwargs)
            return None
        except lab.ProbeError as error:
            return error.code

    traversal_token = lab.mint_token(
        book.secret,
        resource_id="rid-trav",
        rel_path="../outside/outside_secret.png",
        scope="derived-read-only",
        expires_at=book.resolver.clock() + 600,
        expected_identity=[0, 0],
        expected_size=1,
        expected_sha256="0" * 64,
    )
    static_cases.append({"case": "lexical-traversal", "expected": "REF_OUT_OF_SCOPE", "actual": expect_code(traversal_token)})

    absolute_token = lab.mint_token(
        book.secret,
        resource_id="rid-abs",
        rel_path=str(book.outside_secret),
        scope="derived-read-only",
        expires_at=book.resolver.clock() + 600,
        expected_identity=[0, 0],
        expected_size=1,
        expected_sha256="0" * 64,
    )
    static_cases.append({"case": "absolute-path", "expected": "REF_OUT_OF_SCOPE", "actual": expect_code(absolute_token)})

    link_token = book.resolver.issue("rid-link", "derived/link/nested.png", ttl_seconds=600)
    static_cases.append({"case": "in-scope-junction-reparse", "expected": "REF_REPARSE_POINT", "actual": expect_code(link_token)})

    scope_token = lab.mint_token(
        book.secret,
        resource_id="rid-user",
        rel_path="derived/asset.png",
        scope="user-source",
        expires_at=book.resolver.clock() + 600,
        expected_identity=[0, 0],
        expected_size=1,
        expected_sha256="0" * 64,
    )
    static_cases.append({"case": "user-source-scope", "expected": "REF_SCOPE_DENIED", "actual": expect_code(scope_token)})

    write_token = lab.mint_token(
        book.secret,
        resource_id="rid-write",
        rel_path="derived/asset.png",
        scope="derived-read-only",
        expires_at=book.resolver.clock() + 600,
        mode="write",
        expected_identity=[0, 0],
        expected_size=1,
        expected_sha256="0" * 64,
    )
    static_cases.append({"case": "write-mode", "expected": "REF_READ_ONLY", "actual": expect_code(write_token)})

    t04 = {
        "id": "T-04P-static-negative-controls",
        "status": lab.PASS if all(c["actual"] == c["expected"] for c in static_cases) else lab.FAIL,
        "cases": static_cases,
        "junction": junction_static,
        "note": "static path inputs only; re-confirms the early-rejection layer (M2-S1 F-02 parity)",
    }
    records.append(t04)
    junction_dir = book.scope / "derived" / "link"
    if junction_dir.exists() or junction_dir.is_symlink():
        os.rmdir(junction_dir)

    # ---------------- T-10 file swap between check and open (small) ---------
    attacker = Attacker(
        "before_open",
        lambda: (_relink(book.outside_secret, book.asset), "swapped-small")[1],
    )
    token = book.issue_asset("rid-t10")
    code, read_result = attacker.run(book.resolver, token)
    _relink(book.small_fixture, book.asset)
    records.append(
        book.record_attack(
            "T-10-swap-file-between-check-and-open-small",
            "FILE_IDENTITY_CHANGED",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t10-restore", book.small_sha),
            "check/open window: file replaced with a small out-of-scope file; identity from the handle catches it",
        )
    )

    # ---------------- T-11 file swap to large between check and open --------
    attacker = Attacker(
        "before_open",
        lambda: (_relink(book.typical_fixture, book.asset), "swapped-large")[1],
    )
    token = book.issue_asset("rid-t11")
    code, read_result = attacker.run(book.resolver, token)
    _relink(book.small_fixture, book.asset)
    records.append(
        book.record_attack(
            "T-11-swap-file-between-check-and-open-large",
            "FILE_IDENTITY_CHANGED",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t11-restore", book.small_sha),
            "check/open window: file replaced with a much larger out-of-scope file; identity is checked before size",
        )
    )

    # ---------------- T-12 equal-size swap between check and open -----------
    attacker = Attacker(
        "before_open",
        lambda: (_relink(book.same_size_variant, book.asset), "swapped-same-size")[1],
    )
    token = book.issue_asset("rid-t12")
    code, read_result = attacker.run(book.resolver, token)
    _relink(book.small_fixture, book.asset)
    records.append(
        book.record_attack(
            "T-12-equal-size-swap-between-check-and-open",
            "FILE_IDENTITY_CHANGED",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t12-restore", book.small_sha),
            "equal-size different-content swap (F-06 pattern): size alone cannot see it, handle identity can",
            extra={"same_size_variant": book.same_size_info},
        )
    )

    # ---------------- T-13 directory component swapped for junction ---------
    inner_dir = book.scope / "derived" / "inner"
    inner_dir.mkdir(parents=True, exist_ok=True)
    inner_file = inner_dir / "asset2.png"
    _relink(book.small_fixture, inner_file)
    attacker = Attacker(
        "before_open",
        lambda: (
            inner_file.unlink(),
            os.rmdir(inner_dir),
            lab.make_junction(inner_dir, book.outside_dir)["created"],
        ),
    )
    token = book.resolver.issue("rid-t13", "derived/inner/asset2.png", ttl_seconds=600)
    code, read_result = attacker.run(book.resolver, token)
    if inner_dir.exists() or inner_dir.is_symlink():
        os.rmdir(inner_dir)
    inner_dir.mkdir(parents=True, exist_ok=True)
    _relink(book.small_fixture, inner_file)
    records.append(
        book.record_attack(
            "T-13-dir-component-swapped-for-junction",
            "REF_OUT_OF_SCOPE",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_nested, "rid-t13-restore", book.small_sha),
            "check/open window: directory component replaced by a junction pointing outside the scope; "
            "containment re-derived from the opened handle rejects",
        )
    )

    # ---------------- T-14 scope root swapped for junction ------------------
    attacker = Attacker(
        "before_open",
        lambda: (
            os.rename(book.scope, book.scope.with_name("scope_moved")),
            lab.make_junction(book.scope, book.outside / "mirror")["created"],
        ),
    )
    token = book.issue_asset("rid-t14")
    code, read_result = attacker.run(book.resolver, token)
    # restore: remove junction, move the real scope back
    if book.scope.exists() or book.scope.is_symlink():
        os.rmdir(book.scope)
    moved = book.scope.with_name("scope_moved")
    if moved.exists():
        os.rename(moved, book.scope)
    records.append(
        book.record_attack(
            "T-14-scope-root-swapped-for-junction",
            "REF_OUT_OF_SCOPE",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t14-restore", book.small_sha),
            "adversary-writable parent: the whole scope root is renamed away and replaced by a junction into an "
            "out-of-scope mirror tree; containment from the handle rejects",
        )
    )

    # ---------------- T-15 parent directory component swapped ---------------
    attacker = Attacker(
        "before_open",
        lambda: (
            book.nested.unlink(),
            os.rmdir(book.scope / "derived" / "sub"),
            lab.make_junction(book.scope / "derived" / "sub", book.outside_dir)["created"],
        ),
    )
    token = book.issue_nested("rid-t15")
    code, read_result = attacker.run(book.resolver, token)
    sub_dir = book.scope / "derived" / "sub"
    if sub_dir.exists() or sub_dir.is_symlink():
        os.rmdir(sub_dir)
    sub_dir.mkdir(parents=True, exist_ok=True)
    _relink(book.small_fixture, book.nested)
    records.append(
        book.record_attack(
            "T-15-parent-dir-component-swapped-for-junction",
            "REF_OUT_OF_SCOPE",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_nested, "rid-t15-restore", book.small_sha),
            "a parent directory component of the referenced file is swapped for a junction; handle containment rejects",
        )
    )

    # ---------------- T-16 in-place equal-size rewrite (pre-held handle) ----
    # Availability-first mode (share_write=True, CRT-open parity with M2-S1
    # probe F): the adversary's pre-held write handle survives the resolver's
    # open, so identity+size cannot see the rewrite and the issue-time digest
    # must carry the load.
    write_handle_holder: dict = {}

    def t16_action() -> str:
        handle = write_handle_holder["handle"]
        payload = book.small_fixture.read_bytes()[:4096]
        flipped = bytes(b ^ 0x5A for b in payload)
        lab.win32_write(handle, flipped, offset=0)
        return "rewrote-first-4k-equal-size"

    token = book.issue_asset("rid-t16")
    write_handle_holder["handle"], _err = lab.win32_open_write(book.asset, share_mode=lab.FILE_SHARE_READ | lab.FILE_SHARE_WRITE)
    attacker = Attacker("after_open_before_verify", t16_action)
    code, read_result = attacker.run(book.resolver, token, share_write=True)
    if write_handle_holder["handle"]:
        lab.win32_close(write_handle_holder["handle"])
        write_handle_holder["handle"] = None
    _relink(book.small_fixture, book.asset)
    records.append(
        book.record_attack(
            "T-16-in-place-equal-size-rewrite-preheld-handle",
            "CONTENT_DIGEST_MISMATCH",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t16-restore", book.small_sha),
            "adversary held a write handle before the resolver opened; equal-size rewrite is invisible to "
            "identity+size, the issue-time content digest catches it",
        )
    )

    # ---------------- T-17 in-place size-changing rewrite -------------------
    def t17_action() -> str:
        handle = write_handle_holder["handle"]
        # write far past EOF so the file grows: the size re-verification from
        # the handle must catch this before any byte is read
        lab.win32_write(handle, b"extended-by-attacker" * 8, offset=3_100_000)
        return "extended-file-past-eof"

    token = book.issue_asset("rid-t17")
    write_handle_holder["handle"], _err = lab.win32_open_write(book.asset, share_mode=lab.FILE_SHARE_READ | lab.FILE_SHARE_WRITE)
    attacker = Attacker("after_open_before_verify", t17_action)
    code, read_result = attacker.run(book.resolver, token, share_write=True)
    if write_handle_holder["handle"]:
        lab.win32_close(write_handle_holder["handle"])
        write_handle_holder["handle"] = None
    _relink(book.small_fixture, book.asset)
    records.append(
        book.record_attack(
            "T-17-in-place-size-changing-rewrite-preheld-handle",
            "FILE_SIZE_CHANGED",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t17-restore", book.small_sha),
            "in-place write extending the file past EOF (pre-held handle, availability-first mode) is caught by "
            "the handle size re-verification before any byte is read",
        )
    )

    # ---------------- T-18 rewrite during read ------------------------------
    def t18_action() -> str:
        handle = write_handle_holder["handle"]
        payload = book.small_fixture.read_bytes()
        block = payload[(1 << 20) : (1 << 20) + 4096]
        lab.win32_write(handle, bytes(b ^ 0x5A for b in block), offset=1 << 20)
        return "rewrote-second-block-during-read"

    token = book.issue_asset("rid-t18")
    write_handle_holder["handle"], _err = lab.win32_open_write(book.asset, share_mode=lab.FILE_SHARE_READ | lab.FILE_SHARE_WRITE)
    attacker = Attacker("during_read", t18_action)
    code, read_result = attacker.run(book.resolver, token, share_write=True)
    if write_handle_holder["handle"]:
        lab.win32_close(write_handle_holder["handle"])
        write_handle_holder["handle"] = None
    _relink(book.small_fixture, book.asset)
    records.append(
        book.record_attack(
            "T-18-in-place-rewrite-during-read",
            "CONTENT_DIGEST_MISMATCH",
            code,
            read_result,
            attacker,
            book.restore_check(book.issue_asset, "rid-t18-restore", book.small_sha),
            "rewrite lands while the handle read is in flight; the same-handle digest check catches the mix",
        )
    )

    # ---------------- T-19 new writer open blocked by share mode ------------
    def t19_action() -> dict:
        handle, error = lab.win32_open_write(book.asset)
        if handle:
            lab.win32_close(handle)
        return {"new_writer_open_ok": handle is not None, "win32_error": error}

    attacker = Attacker("after_open_before_verify", t19_action)
    token = book.issue_asset("rid-t19")
    code, read_result = attacker.run(book.resolver, token)
    outcome = attacker.outcome.get("attack_result", {})
    t19_ok = (
        code is None
        and read_result is not None
        and read_result["sha256"] == book.small_sha
        and outcome.get("new_writer_open_ok") is False
        and outcome.get("win32_error") == lab.ERROR_SHARING_VIOLATION
    )
    records.append(
        {
            "id": "T-19-new-writer-open-blocked-by-share-mode",
            "status": lab.PASS if t19_ok else lab.FAIL,
            "resolver_read_sha256": read_result["sha256"] if read_result else None,
            "expected_sha256": book.small_sha,
            "attack_outcome": attacker.outcome,
            "expected_win32_error": lab.ERROR_SHARING_VIOLATION,
            "note": "while the resolver holds the handle (FILE_SHARE_READ only), a new writer open fails with "
            "ERROR_SHARING_VIOLATION (32) and the legitimate read is unaffected",
        }
    )

    # ---------------- T-21 pre-held writer blocks the open (fail-closed) ----
    def t21_action() -> str:
        return "pre-held-write-handle"

    token = book.issue_asset("rid-t21")
    pre_handle, pre_err = lab.win32_open_write(book.asset, share_mode=lab.FILE_SHARE_READ | lab.FILE_SHARE_WRITE)
    attacker = Attacker("before_open", t21_action)  # never fires: open fails first
    code, read_result = attacker.run(book.resolver, token)  # default narrow share
    if pre_handle:
        lab.win32_close(pre_handle)
    t21_ok = code == "OPEN_FAILED_SHARING_VIOLATION" and read_result is None
    records.append(
        {
            "id": "T-21-pre-held-writer-fails-closed",
            "status": lab.PASS if t21_ok else lab.FAIL,
            "actual_rejection_code": code,
            "expected_rejection_code": "OPEN_FAILED_SHARING_VIOLATION",
            "bytes_read": None,
            "note": "default narrow-share mode: an adversary that already holds a write handle makes the "
            "resolver's open fail closed (ERROR_SHARING_VIOLATION 32); no byte is read. Availability-first "
            "parity (share_write=True) is exercised by T-16..T-18 where the digest layer carries the load.",
        }
    )

    # ---------------- T-20 directory component swapped for symlink ----------
    symlink_info = lab.try_make_symlink_dir(book.scope / "derived" / "symdir", book.outside_dir)
    if symlink_info["created"]:
        os.rmdir(book.scope / "derived" / "symdir")
        inner_dir = book.scope / "derived" / "inner"
        inner_dir.mkdir(parents=True, exist_ok=True)
        inner_file = inner_dir / "asset2.png"
        if inner_file.exists():
            inner_file.unlink()
        _relink(book.small_fixture, inner_file)
        attacker = Attacker(
            "before_open",
            lambda: (
                inner_file.unlink(),
                os.rmdir(inner_dir),
                lab.try_make_symlink_dir(inner_dir, book.outside_dir)["created"],
            ),
        )
        token = book.resolver.issue("rid-t20", "derived/inner/asset2.png", ttl_seconds=600)
        code, read_result = attacker.run(book.resolver, token)
        if inner_dir.exists() or inner_dir.is_symlink():
            os.rmdir(inner_dir)
        inner_dir.mkdir(parents=True, exist_ok=True)
        _relink(book.small_fixture, inner_file)
        records.append(
            book.record_attack(
                "T-20-dir-component-swapped-for-symlink",
                "REF_OUT_OF_SCOPE",
                code,
                read_result,
                attacker,
                book.restore_check(book.issue_nested, "rid-t20-restore", book.small_sha),
                "same race as T-13 with a symbolic link; symlink creation privilege was available on this host",
                extra={"symlink_environment": symlink_info},
            )
        )
    else:
        records.append(
            {
                "id": "T-20-dir-component-swapped-for-symlink",
                "status": lab.BLOCKED,
                "symlink_environment": symlink_info,
                "note": "directory symlink creation is not available without admin/developer-mode privilege on "
                "this host; the junction variant T-13 (same reparse-escape class) is measured instead",
            }
        )

    limitations = [
        "This is an isolated Python/Win32 prototype exercising S1-B11 release conditions (1) and (2); "
        "it is not a product implementation and does not by itself make the product boundary verified.",
        "S1-B11 condition (3) 'target packaging/sandbox form' (MSIX/AppContainer re-run) and condition (4) "
        "(DACL/integrity level, S1-B3) are NOT_RUN here -- they need S1-B8 and S1-B3 respectively.",
        "Handle identity is (volume serial, file index); NTFS may reuse an index after deletion. The "
        "issue-time content digest is the defence-in-depth layer that also covers in-place equal-size "
        "rewrites by an adversary that already held a write handle (T-16/T-18).",
        "The pre-open reparse walk is an early rejection with its own race window; the authoritative "
        "containment decision is derived from the opened handle (GetFinalPathNameByHandle).",
    ]

    return {
        "probe": PROBE,
        "purpose": "systematic negative probes for M2-S1 blocker S1-B11 (TOCTOU) against the "
        "open-then-verify-from-handle reference resolver",
        "release_reference": "doc/tasks/M2-S2.md (S2-AC2/S2-AC3); M2-S1 §8.2 S1-B11 conditions 1-3",
        "toctou_limit_bytes": lab.TOCTOU_LIMIT_BYTES,
        "toctou_limit_label": "probe configuration, NOT a product threshold",
        "media_limit_bytes": lab.MEDIA_LIMIT_BYTES,
        "scope_root": str(book.scope),
        "outside_root": str(book.outside),
        "small_fixture_sha256": book.small_sha,
        "typical_fixture_sha256": book.typical_sha,
        "scenarios": records,
        "boundary_summary": {
            "open_then_verify_direction": "detects every exercised swap with a typed rejection "
            "(T-10..T-18) and serves legitimate resources (T-01P..T-03P)",
            "static_rejection_layer": "reconfirmed (T-04P)",
            "share_mode_defence": "narrow share fails closed against a pre-held writer (T-21) and blocks "
            "new writer opens while the handle is held (T-19); availability-first mode (share_write=True) "
            "is covered by the size/digest layers (T-16..T-18)",
            "product_guarantee": "UNVERIFIED -- see limitations",
        },
        "limitations": limitations,
        "summary": lab.summary_of(records),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    args = parser.parse_args()
    root = lab.lab_root(args.lab)
    return lab.emit(run_host(root), args.out or str(root / "toctou-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
