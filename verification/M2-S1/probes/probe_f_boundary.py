"""Probe F -- Review-driven boundary measurement (R-001 TOCTOU, R-002 opacity).

This probe exists because Codex Review `doc/reviews/M2-S1-4eaad68.md` found that
the research report claimed more than the original probes proved:

* **R-001 (P1)** -- `ScopedResourceResolver.resolve()` and
  `read_file_bounded()` are *check-then-use*: they validate a path / a size and
  the caller opens the file afterwards. The static negative scenarios show
  behaviour for a *static* path input only; a concurrent replacement in the
  check-to-open window was never measured.
* **R-002 (P2)** -- the reference was described as opaque. It is not: the
  payload is Base64URL JSON and is readable without the key.

`probe_f_boundary.py` measures the boundary instead of asserting it:

  F-01  token payload is readable without the signing key          (R-002)
  F-02  static negative controls re-confirmed in-process           (limits R-001)
  F-03  file replaced between check and open -> outside bytes read  (R-001)
  F-04  directory component swapped for a junction between the two  (R-001)
  F-05  size validated, then replaced -> more bytes than validated  (R-001)
  F-06  same-size/different-content swap -> size alone cannot catch  (R-001)
  F-07  handle-bound identity+size check detects the swap (isolated mitigation)
  F-08  handle-bound baseline positive control

F-07/F-08 are an **isolated demonstration of a required property**, not a
product guarantee. The product boundary stays `UNVERIFIED` for an adversary with
write access to the scope root; see the `limitations` block in the JSON result
and the research report section 12.

Run:
  python verification/M2-S1/probes/probe_f_boundary.py --lab <lab> --out <json>
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402

PROBE = "F"
LIMIT = lab.MEDIA_LIMIT_BYTES
DEMO_READ_SLACK = 1 << 20  # never load the whole over-limit file in F-05


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _identity(stat_result: os.stat_result) -> dict:
    """Prefer (device, file index); record the fallback so it is auditable."""

    inode = getattr(stat_result, "st_ino", 0)
    if inode:
        return {
            "key": "dev+inode",
            "value": [int(stat_result.st_dev), int(inode)],
            "size": int(stat_result.st_size),
        }
    return {
        "key": "fallback(dev+size+mtime)",
        "value": [
            int(stat_result.st_dev),
            int(stat_result.st_size),
            int(getattr(stat_result, "st_mtime_ns", 0)),
        ],
        "size": int(stat_result.st_size),
    }


def _sha256_path(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _hash_and_count(path: str | Path, cap: int) -> tuple[str, int]:
    """Hash at most ``cap`` bytes, streaming, to keep the demo memory-bounded."""

    digest = hashlib.sha256()
    total = 0
    with open(path, "rb") as handle:
        while total < cap:
            block = handle.read(min(1 << 20, cap - total))
            if not block:
                break
            digest.update(block)
            total += len(block)
    return digest.hexdigest(), total


def _make_junction(link: Path, target: Path) -> dict:
    if link.exists():
        os.rmdir(link)
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        timeout=30,
    )
    return {
        "link": str(link),
        "target": str(target),
        "created": created.returncode == 0 and link.exists(),
        "output": (created.stdout + created.stderr).decode("utf-8", errors="replace")[:200],
    }


def _relink(source: Path, target: Path) -> None:
    if target.exists():
        target.unlink()
    os.link(source, target)


def _make_same_size_variant(source: Path, target: Path) -> dict:
    """Copy ``source`` and flip content bytes, keeping the byte size identical."""

    shutil.copyfile(source, target)
    with open(target, "r+b") as handle:
        head = bytearray(handle.read(256))
        for index in range(0, len(head), 4):
            head[index] ^= 0xA5
        handle.seek(0)
        handle.write(bytes(head))
    source_size = source.stat().st_size
    target_size = target.stat().st_size
    return {
        "source_bytes": source_size,
        "variant_bytes": target_size,
        "same_size": source_size == target_size,
        "variant_sha256": _sha256_path(target),
        "source_sha256": _sha256_path(source),
    }


# --------------------------------------------------------------------------
# scenarios
# --------------------------------------------------------------------------


def run_host(lab_root: Path) -> dict:
    fixtures = json.loads((lab_root / "fixtures" / "fixtures.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in fixtures["fixtures"]}
    work = lab_root / "probeF"
    scope = work / "scope"
    outside = work / "outside"
    for sub in ("derived", "managed"):
        (scope / sub).mkdir(parents=True, exist_ok=True)
    outside.mkdir(parents=True, exist_ok=True)

    asset_fixture = Path(by_name["small_page_800x1200"]["path"])
    other_fixture = Path(by_name["typical_page_1600x2400"]["path"])
    oversize_fixture = Path(by_name["oversize_2000x12000"]["path"])

    asset = scope / "derived" / "asset.png"
    _relink(asset_fixture, asset)
    managed = scope / "managed" / "managed.png"
    _relink(other_fixture, managed)
    outside_secret = outside / "outside_secret.png"
    _relink(other_fixture, outside_secret)

    secret = os.urandom(32)
    resolver = lab.ScopedResourceResolver(scope, secret)
    token = resolver.issue("rid-asset", "derived/asset.png", ttl_seconds=600)
    results: list[dict] = []

    # ---------------- F-01 (R-002): payload readable without the key --------
    unrelated_key = b"x" * 32
    body = token.split(".")[1]
    decoded = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)).decode("utf-8")
    payload = json.loads(decoded)
    signature_rejected = False
    try:
        lab.read_token(unrelated_key, token)
    except lab.ProbeError as error:
        signature_rejected = error.code == "REF_SIGNATURE_INVALID"
    results.append(
        {
            "id": "F-01-token-payload-readable-without-key",
            "finding": "R-002",
            "status": lab.PASS
            if payload.get("rel") == "derived/asset.png" and signature_rejected
            else lab.FAIL,
            "decoded_payload": payload,
            "decoded_codepath_present": "rel" in payload and "rid" in payload,
            "readable_without_key": True,
            "signature_check_without_key_rejects": signature_rejected,
            "confidentiality": "NONE (payload is Base64URL JSON)",
            "integrity": "HMAC-SHA256 over the payload segment",
            "token_chars": len(token),
            "note": (
                "a signed reference proves who minted it; it does not hide the "
                "relative path, resource id, scope, expiry or mode from the holder"
            ),
        }
    )

    # ---------------- F-02: static negative controls re-confirmed -----------
    junction = _make_junction(scope / "derived" / "link_to_managed", scope / "managed")
    static_cases = [
        ("traversal", "rid-t", "../outside/outside_secret.png", "derived-read-only", "read", "REF_OUT_OF_SCOPE"),
        ("absolute", "rid-a", str(outside_secret.resolve()), "derived-read-only", "read", "REF_OUT_OF_SCOPE"),
        (
            "internal-junction",
            "rid-j",
            "derived/link_to_managed/managed.png",
            "derived-read-only",
            "read",
            "REF_REPARSE_POINT",
        ),
        ("scope-denied", "rid-s", "derived/asset.png", "user-source", "read", "REF_SCOPE_DENIED"),
    ]
    static_records = []
    for name, rid, rel, scope_class, mode, expected in static_cases:
        minted = lab.mint_token(
            secret,
            resource_id=rid,
            rel_path=rel,
            scope=scope_class,
            expires_at=resolver.clock() + 600,
            mode=mode,
        )
        try:
            resolver.resolve(minted, mode=mode)
            code = None
        except lab.ProbeError as error:
            code = error.code
        static_records.append({"case": name, "expected": expected, "actual": code, "ok": code == expected})
    # write mode
    write_token = lab.mint_token(
        secret,
        resource_id="rid-w",
        rel_path="derived/asset.png",
        scope="derived-read-only",
        expires_at=resolver.clock() + 600,
        mode="read",
    )
    try:
        resolver.resolve(write_token, mode="write")
        write_code = None
    except lab.ProbeError as error:
        write_code = error.code
    static_records.append(
        {"case": "write-mode", "expected": "REF_READ_ONLY", "actual": write_code, "ok": write_code == "REF_READ_ONLY"}
    )
    results.append(
        {
            "id": "F-02-static-negative-controls-reconfirmed",
            "finding": "R-001 (limits the claim)",
            "status": lab.PASS if all(record["ok"] for record in static_records) else lab.FAIL,
            "cases": static_records,
            "junction": junction,
            "note": (
                "these PASSes apply to a static path input only; they are a "
                "reconfirmation of the original A-09/A-10/A-11/A-12/A-15 results, "
                "not evidence about a concurrent adversary"
            ),
        }
    )

    # ---------------- F-03 (R-001): file swap between check and open --------
    resolved = resolver.resolve(token)
    validated = _identity(os.stat(resolved))
    validated_sha = _sha256_path(resolved)
    _relink(outside_secret, asset)  # happens strictly after validation
    opened_sha = _sha256_path(resolved)
    results.append(
        {
            "id": "F-03-file-replaced-between-check-and-open",
            "finding": "R-001",
            "status": lab.PASS if opened_sha != validated_sha and opened_sha == _sha256_path(outside_secret) else lab.FAIL,
            "resolved_path": str(resolved),
            "validated_identity": validated,
            "validated_sha256": validated_sha,
            "opened_sha256": opened_sha,
            "outside_sha256": _sha256_path(outside_secret),
            "opened_bytes_are_out_of_scope_file": opened_sha == _sha256_path(outside_secret),
            "toctou_window_confirmed": opened_sha != validated_sha,
            "note": (
                "the resolver's checks and the caller's open are two separate "
                "filesystem operations; a replacement in between is not detected "
                "by any static check"
            ),
        }
    )
    _relink(asset_fixture, asset)  # restore

    # ---------------- F-04 (R-001): directory component swapped -------------
    inner_scope = scope / "derived" / "dir"
    inner_scope.mkdir(parents=True, exist_ok=True)
    inner_file = inner_scope / "asset2.png"
    _relink(asset_fixture, inner_file)
    outside_dir = outside / "dir"
    outside_dir.mkdir(parents=True, exist_ok=True)
    _relink(outside_secret, outside_dir / "asset2.png")

    dir_token = resolver.issue("rid-asset2", "derived/dir/asset2.png", ttl_seconds=600)
    resolved_dir = resolver.resolve(dir_token)
    dir_validated_sha = _sha256_path(resolved_dir)
    inner_file.unlink()
    os.rmdir(inner_scope)
    dir_junction = _make_junction(inner_scope, outside_dir)
    dir_opened_sha = _sha256_path(resolved_dir)
    results.append(
        {
            "id": "F-04-directory-component-swapped-for-junction",
            "finding": "R-001",
            "status": lab.PASS
            if dir_junction["created"] and dir_opened_sha != dir_validated_sha
            else (lab.NOT_RUN if not dir_junction["created"] else lab.FAIL),
            "junction": dir_junction,
            "validated_sha256": dir_validated_sha,
            "opened_sha256": dir_opened_sha,
            "reads_out_of_scope_tree": dir_opened_sha == _sha256_path(outside_dir / "asset2.png"),
            "note": (
                "the reparse walk passed while the directory was real; replacing "
                "it with a junction after validation redirects the later open"
            ),
        }
    )
    if dir_junction["created"]:
        os.rmdir(inner_scope)
    inner_scope.mkdir(parents=True, exist_ok=True)
    _relink(asset_fixture, inner_file)

    # ---------------- F-05 (R-001): size validated, then replaced -----------
    size_token = resolver.issue("rid-size", "derived/asset.png", ttl_seconds=600)
    size_path = resolver.resolve(size_token)
    validated_size = os.path.getsize(size_path)
    size_within_limit = validated_size <= LIMIT
    _relink(oversize_fixture, asset)  # strictly after the size check
    actual_size = os.path.getsize(size_path)
    _, bytes_read = _hash_and_count(size_path, LIMIT + DEMO_READ_SLACK)
    results.append(
        {
            "id": "F-05-size-check-then-open-race",
            "finding": "R-001",
            "status": lab.PASS if size_within_limit and bytes_read > LIMIT else lab.FAIL,
            "limit_bytes": LIMIT,
            "validated_size": validated_size,
            "validated_size_within_limit": size_within_limit,
            "actual_size_after_swap": actual_size,
            "bytes_read": bytes_read,
            "bytes_read_exceeds_validated_limit": bytes_read > LIMIT,
            "demo_read_cap_bytes": LIMIT + DEMO_READ_SLACK,
            "note": (
                "the naive read follows getsize() with a separate open; the demo "
                "streams at most limit+1 MiB so the probe itself stays bounded"
            ),
        }
    )
    _relink(asset_fixture, asset)  # restore

    # ---------------- F-06 (R-001): same size, different content ------------
    same_size = outside / "same_size_secret.png"
    same_size_info = _make_same_size_variant(asset, same_size)
    same_token = resolver.issue("rid-same", "derived/asset.png", ttl_seconds=600)
    same_path = resolver.resolve(same_token)
    same_validated = _identity(os.stat(same_path))
    _relink(same_size, asset)  # same byte size, different content
    same_after = _identity(os.stat(same_path))
    size_only_would_pass = same_after["size"] == same_validated["size"]
    identity_caught = same_after["value"] != same_validated["value"]
    results.append(
        {
            "id": "F-06-same-size-different-content-swap",
            "finding": "R-001",
            "status": lab.PASS if size_only_would_pass and identity_caught else lab.FAIL,
            "same_size_variant": same_size_info,
            "identity_key": same_validated["key"],
            "validated_identity": same_validated,
            "identity_after_swap": same_after,
            "size_only_check_would_pass": size_only_would_pass,
            "identity_check_detects_swap": identity_caught,
            "note": (
                "a size re-check alone cannot detect this swap; only a file "
                "identity/version check on the opened handle can"
            ),
        }
    )
    _relink(asset_fixture, asset)  # restore

    # ---------------- F-07/F-08: handle-bound identity+size check -----------
    def bound_read(path: Path, expected_identity: dict, limit: int) -> dict:
        """Open once, verify identity and size from the handle, then read it."""

        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
        try:
            handle_stat = os.fstat(descriptor)
            observed = _identity(handle_stat)
            if observed["value"] != expected_identity["value"]:
                raise lab.ProbeError("FILE_IDENTITY_CHANGED", f"{expected_identity} != {observed}")
            if handle_stat.st_size > limit:
                raise lab.ProbeError("MEDIA_TOO_LARGE_BY_HANDLE", f"size={handle_stat.st_size} limit={limit}")
            digest = hashlib.sha256()
            total = 0
            while True:
                block = os.read(descriptor, 1 << 20)
                if not block:
                    break
                digest.update(block)
                total += len(block)
            return {"sha256": digest.hexdigest(), "bytes": total, "identity": observed}
        finally:
            os.close(descriptor)

    bound_token = resolver.issue("rid-bound", "derived/asset.png", ttl_seconds=600)
    bound_path = resolver.resolve(bound_token)
    expected = _identity(os.stat(bound_path))
    _relink(outside_secret, asset)  # swap after validation
    detected = None
    try:
        bound_read(bound_path, expected, LIMIT)
    except lab.ProbeError as error:
        detected = error.code
    results.append(
        {
            "id": "F-07-handle-bound-identity-check-detects-swap",
            "finding": "R-001 (release-condition direction, isolated)",
            "status": lab.PASS if detected == "FILE_IDENTITY_CHANGED" else lab.FAIL,
            "expected_identity": expected,
            "detected_error": detected,
            "note": (
                "opening once and comparing the identity from the handle defeats "
                "this specific swap on this host; it is a demonstration of the "
                "required property, not a product guarantee"
            ),
        }
    )
    _relink(asset_fixture, asset)  # restore

    bound_ok_sha = None
    bound_error = None
    try:
        bound_ok_sha = bound_read(bound_path, expected, LIMIT)["sha256"]
    except lab.ProbeError as error:
        bound_error = error.code
    results.append(
        {
            "id": "F-08-handle-bound-baseline-positive-control",
            "finding": "R-001 (control)",
            "status": lab.PASS
            if bound_ok_sha == _sha256_path(asset_fixture) and bound_error is None
            else lab.FAIL,
            "sha256": bound_ok_sha,
            "expected_sha256": _sha256_path(asset_fixture),
            "note": "the bound path must still serve the legitimate resource unchanged",
        }
    )

    limitations = [
        "F-07/F-08 show that an open-then-verify implementation detects the two "
        "specific swaps exercised here; they do not make the product boundary verified.",
        "An adversary with write access to the scope root, to its parent directories, "
        "or to the volume can still race the validation, replace a reparse point at "
        "open time, or replace the validated file with a same-identity handle obtained "
        "another way; none of that is measured.",
        "The product design must decide: open with FILE_FLAG_OPEN_REPARSE_POINT / "
        "FILE_FLAG_BACKUP_SEMANTICS as appropriate, re-derive containment from the "
        "opened handle, verify identity+size from that handle, and keep DACL/integrity "
        "level checks (S1-B3) outside this proposal.",
        "No Tauri/WebView asset protocol, no product Core process model and no OS-level "
        "ACL/integrity level were exercised; those remain NOT_RUN/UNVERIFIED.",
    ]

    return {
        "probe": PROBE,
        "purpose": "Review-driven boundary measurement for M2-S1 findings R-001 and R-002",
        "review_reference": "doc/reviews/M2-S1-4eaad68.md (decision=changes_requested)",
        "limit_bytes": LIMIT,
        "limit_label": "probe-configured controlled rejection limit, NOT a product threshold",
        "scope_root": str(scope),
        "outside_root": str(outside),
        "host_pid": os.getpid(),
        "host_memory": lab.memory_counters(),
        "scenarios": results,
        "boundary_summary": {
            "static_path_input": "negative controls PASS (F-02)",
            "check_then_use_window": "CONFIRMED OPEN (F-03, F-04, F-05, F-06)",
            "handle_bound_mitigation_direction": "detects the exercised swaps (F-07), serves the legitimate resource (F-08)",
            "product_guarantee": "UNVERIFIED -- see limitations",
        },
        "limitations": limitations,
        "summary": {
            "pass": sum(1 for r in results if r["status"] == lab.PASS),
            "fail": sum(1 for r in results if r["status"] == lab.FAIL),
            "blocked": sum(1 for r in results if r["status"] == lab.BLOCKED),
            "not_run": sum(1 for r in results if r["status"] == lab.NOT_RUN),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    args = parser.parse_args()
    lab_root = lab.lab_root(args.lab)
    return lab.emit(run_host(lab_root), args.out or str(lab_root / "probeF-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
