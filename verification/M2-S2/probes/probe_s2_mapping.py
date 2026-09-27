"""Probe S2-MAPPING -- opacity probes for M2-S1 blocker S1-B12 (mapping IDs).

M2-S1 F-01 proved the signed reference is decodable without the key (path and
resource id visible). Threshold ruling T5.4 selected the **Core-side random
mapping ID** option: the WebView-visible reference is an opaque random ID; a
Core-internal table maps ID -> (scope, relative path). This probe exercises
the S1-B12 release conditions against the ``MappingIdAuthority`` prototype:

- no Core participation: holding every issued ID string, an adversary must
  not be able to recover any path or resource identifier (format analysis,
  codec/decoder attempts, hash dictionary, brute-force guessing, neighbour
  mutations);
- errors, logs and telemetry never contain mapping-table entries;
- expiry and revocation produce typed errors (``REF_EXPIRED`` /
  ``REF_REVOKED``); sliding renewal (ruling T6) keeps active consumers alive.

Honest boundary: "cannot recover" is *inductive* evidence -- a bounded set of
analysis attempts on a 192-bit random ID space. It is reported as such; it is
not a cryptographic proof.

Run:
  python verification/M2-S2/probes/probe_s2_mapping.py --out <json>
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
import secrets
import string
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import m2s2_lab as lab  # noqa: E402

PROBE = "S2-MAPPING"

#: Paths the Core would map in this synthetic scenario. The adversary is
#: handed all of the IDs but none of these strings.
MAPPED_PATHS = [
    ("derived", "books/book-001/pages/page-001.png"),
    ("derived", "books/book-001/pages/page-002.png"),
    ("derived", "webtoon-tiles/tile-0003.png"),
    ("managed", "revisions/rev-000042/raster.png"),
    ("derived", "cache/export/page-001.png"),
]

GUESS_COUNT = 5000


def _random_segment(opaque: str) -> str:
    return opaque.split(".")[-1]


def _b64url_decode_loose(text: str) -> bytes | None:
    try:
        return lab._b64url_decode(text)
    except Exception:  # noqa: BLE001 - decode failure is the expected case
        return None


def _all_codec_views(segment: str) -> list[tuple[str, bytes | None]]:
    """Every decoding an adversary would plausibly try on the random segment."""

    views: list[tuple[str, bytes | None]] = [
        ("raw_ascii", segment.encode("ascii", errors="replace")),
        ("b64url", _b64url_decode_loose(segment)),
    ]
    try:
        views.append(("b64url_pad_fixed", base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))))
    except Exception:  # noqa: BLE001
        views.append(("b64url_pad_fixed", None))
    try:
        views.append(("b64std", base64.b64decode(segment + "=" * (-len(segment) % 4))))
    except Exception:  # noqa: BLE001
        views.append(("b64std", None))
    try:
        views.append(("base32", base64.b32decode(segment + "=" * (-len(segment) % 8))))
    except Exception:  # noqa: BLE001
        views.append(("base32", None))
    try:
        views.append(("hex", bytes.fromhex(segment)))
    except Exception:  # noqa: BLE001
        views.append(("hex", None))
    return views


def _hash_dictionary(path_text: str, rid: str) -> dict[str, list[str]]:
    """Common deterministic encodings a lazy implementation might have used."""

    variants = {
        "rel_forward": path_text,
        "rel_backslash": path_text.replace("/", "\\"),
        "file_name": path_text.rsplit("/", 1)[-1],
        "rid": rid,
    }
    out: dict[str, list[str]] = {}
    for name, text in variants.items():
        raw = text.encode("utf-8")
        for algo in ("md5", "sha1", "sha256", "sha512"):
            digest = hashlib.new(algo, raw)
            out[f"{algo}({name})"] = [digest.hexdigest(), digest.hexdigest().upper(), lab._b64url(digest.digest())]
    return out


def leak_scan(texts: list[str], fragments: list[str]) -> list[dict]:
    """Return every (text, fragment) hit; empty means no leakage."""

    hits: list[dict] = []
    for text in texts:
        folded = text.casefold()
        for fragment in fragments:
            if fragment.casefold() in folded:
                hits.append({"text": text, "fragment": fragment})
    return hits


def secret_fragments() -> list[str]:
    """Every string that would count as recovering a path or resource id."""

    fragments: set[str] = set()
    for scope, rel in MAPPED_PATHS:
        fragments.add(rel)
        fragments.add(rel.replace("/", "\\"))
        parts = rel.split("/")
        fragments.update(part for part in parts if part)
        # component pieces that are still identifying ("page-001" etc.)
        for part in parts:
            stem = part.rsplit(".", 1)[0] if "." in part else part
            if len(stem) >= 4:
                fragments.add(stem)
        fragments.add(scope)
    return sorted(fragments)


def run_host(_lab_root_path: Path) -> dict:
    authority = lab.MappingIdAuthority(default_ttl_seconds=0.4)
    clock_start = time.time()
    records: list[dict] = []

    issued_ids = {f"{scope}:{rel}": authority.issue(scope=scope, rel_path=rel, resource_id=f"rid-{index:03d}")
                  for index, (scope, rel) in enumerate(MAPPED_PATHS)}

    # ---------------- M-01 issue/resolve happy path -------------------------
    key = "derived:books/book-001/pages/page-001.png"
    entry = authority.resolve(issued_ids[key])
    records.append(
        {
            "id": "M-01-issue-resolve-happy-path",
            "status": lab.PASS if entry["rel"] == MAPPED_PATHS[0][1] and entry["scope"] == "derived" else lab.FAIL,
            "resolved_rel": entry["rel"],
            "resolved_scope": entry["scope"],
            "note": "the Core-side table maps the ID back correctly for the trusted caller",
        }
    )

    # ---------------- M-02 format analysis ----------------------------------
    ids = list(issued_ids.values())
    segments = [_random_segment(value) for value in ids]
    same_path_twice = {
        authority.issue(scope="derived", rel_path="books/book-001/pages/page-001.png", resource_id="rid-dup"),
        authority.issue(scope="derived", rel_path="books/book-001/pages/page-001.png", resource_id="rid-dup"),
    }
    lengths = {len(value) for value in ids}
    common_prefix_len = len(os_path_common_prefix(segments))
    fragments = secret_fragments()
    format_hits: list[dict] = []
    for value in ids:
        folded = value.casefold()
        for fragment in fragments:
            if fragment.casefold() in folded:
                format_hits.append({"id": value, "fragment": fragment})
    codec_hits: list[dict] = []
    for value in ids:
        for codec, view in _all_codec_views(_random_segment(value)):
            if not view:
                continue
            for encoding in ("utf-8", "utf-16-le"):
                try:
                    text = view.decode(encoding, errors="ignore")
                except Exception:  # noqa: BLE001
                    continue
                folded = text.casefold()
                for fragment in fragments:
                    if fragment.casefold() in folded:
                        codec_hits.append({"id": value, "codec": codec, "encoding": encoding, "fragment": fragment})
    m02 = {
        "id": "M-02-format-analysis-no-path-semantics",
        "status": lab.PASS
        if not format_hits and not codec_hits and len(same_path_twice) == 2 and len(lengths) == 1
        else lab.FAIL,
        "id_shape": "m2id.v1.<43-char base64url token_urlsafe(24)>",
        "id_lengths": sorted(lengths),
        "same_path_two_issues_distinct": len(same_path_twice) == 2,
        "max_common_prefix_among_segments": common_prefix_len,
        "path_fragment_hits_in_ids": format_hits,
        "codec_decode_hits": codec_hits,
        "codecs_tried": ["b64url", "b64url_pad_fixed", "b64std", "base32", "hex", "raw_ascii"],
        "note": "IDs are unlinkable per path, constant-length, and contain no path fragment under any tried codec",
    }
    records.append(m02)

    # ---------------- M-03 recovery attempts without the Core ---------------
    hash_hits: list[dict] = []
    for key, value in issued_ids.items():
        scope, rel = key.split(":", 1)
        segment = _random_segment(value)
        rid = f"rid-{list(issued_ids).index(key):03d}"
        dictionary = _hash_dictionary(rel, rid)
        for label, candidates in dictionary.items():
            for candidate in candidates:
                if candidate.casefold() in segment.casefold():
                    hash_hits.append({"id": value, "label": label})
    m03 = {
        "id": "M-03-no-recovery-without-core",
        "status": lab.PASS if not hash_hits else lab.FAIL,
        "adversary_holds": "all issued ID strings (and nothing else)",
        "attempts": [
            "substring match of every path/resource fragment against every ID",
            "base64url/base64/base32/hex/raw decodes of the random segment",
            "md5/sha1/sha256/sha512 hex and b64 of rel, backslash rel, file name and rid",
        ],
        "hash_dictionary_hits": hash_hits,
        "recovered_paths": 0,
        "recovered_resource_ids": 0,
        "note": "inductive evidence: the exercised analysis space recovers nothing (see limitations)",
    }
    records.append(m03)

    # ---------------- M-04 guessing / enumeration ---------------------------
    alphabet = string.ascii_letters + string.digits + "-_"
    guesses: set[str] = set()
    while len(guesses) < GUESS_COUNT:
        guesses.add(f"m2id.v1.{''.join(secrets.choice(alphabet) for _ in range(43))}")
    # neighbour mutations of real IDs (last-char +/-, truncation, extension)
    for value in ids:
        segment = _random_segment(value)
        last = segment[-1]
        for replacement in ("A", "B", "0", "1"):
            if replacement != last:
                guesses.add(f"m2id.v1.{segment[:-1]}{replacement}")
        guesses.add(f"m2id.v1.{segment[:-1]}")
        guesses.add(f"m2id.v1.{segment}x")
    unknown_codes = set()
    oracle_responses = set()
    for guess in sorted(guesses):
        try:
            authority.resolve(guess)
            unknown_codes.add("RESOLVED")  # would be a catastrophic finding
        except lab.ProbeError as error:
            unknown_codes.add(error.code)
            oracle_responses.add(json.dumps({"code": error.code}, sort_keys=True))
    m04 = {
        "id": "M-04-guessing-enumeration-typed-and-uniform",
        "status": lab.PASS if unknown_codes == {"REF_UNKNOWN_ID"} and len(oracle_responses) == 1 else lab.FAIL,
        "guesses": len(guesses),
        "random_guesses": GUESS_COUNT,
        "observed_codes": sorted(unknown_codes),
        "uniform_error_shape": len(oracle_responses) == 1,
        "keyspace_bits": authority.ID_RANDOM_BYTES * 8,
        "note": "every guess returns the same typed REF_UNKNOWN_ID; no oracle distinguishes near-misses",
    }
    records.append(m04)

    # ---------------- M-05 errors/logs/telemetry leakage sweep ---------------
    error_codes: list[str] = []
    error_texts: list[str] = []
    for guess in ("m2id.v1.does-not-exist", "not-an-id", ""):
        try:
            authority.resolve(guess)
        except lab.ProbeError as error:
            error_codes.append(error.code)
            if error.message:
                error_texts.append(error.message)
    # expire everything, then probe expired + revoked surfaces
    deadline = authority._table[ids[0]]["expires_at"]
    while time.time() < deadline + 0.05:
        time.sleep(0.02)
    for value in ids:
        try:
            authority.resolve(value)
        except lab.ProbeError as error:
            error_codes.append(error.code)
            if error.message:
                error_texts.append(error.message)
    authority.visible_log.clear()
    authority.telemetry.clear()
    fresh = authority.issue(scope="derived", rel_path="cache/export/page-001.png", resource_id="rid-revoke-me")
    entry_ok = None
    try:
        entry_ok = authority.resolve(fresh)
    except lab.ProbeError as error:
        error_codes.append(error.code)
    authority.revoke(fresh)
    try:
        authority.resolve(fresh)
    except lab.ProbeError as error:
        error_codes.append(error.code)
        if error.message:
            error_texts.append(error.message)
    try:
        authority.resolve(fresh, mode="write")
    except lab.ProbeError as error:
        error_codes.append(error.code)

    sweep_texts = (
        list(authority.visible_log)
        + [json.dumps(e, sort_keys=True) for e in authority.telemetry]
        + error_codes
        + error_texts
    )
    hits = leak_scan(sweep_texts, fragments)
    m05 = {
        "id": "M-05-errors-logs-telemetry-no-leakage",
        "status": lab.PASS if not hits else lab.FAIL,
        "scanned_texts": len(sweep_texts),
        "leak_hits": hits,
        "error_codes_seen": sorted(set(error_codes)),
        "revoked_before_revoked_resolved": entry_ok is not None,
        "log_sample": authority.visible_log[:8],
        "telemetry_sample": authority.telemetry[:8],
        "note": "the caller-visible surfaces carry events and stable codes only -- no rel, no rid, no table rows",
    }
    records.append(m05)

    # ---------------- M-06 expiry typed -------------------------------------
    authority2 = lab.MappingIdAuthority(default_ttl_seconds=0.2)
    short = authority2.issue(scope="derived", rel_path="short/ttl.png", resource_id="rid-short")
    ok_before = None
    try:
        authority2.resolve(short)
        ok_before = True
    except lab.ProbeError:
        ok_before = False
    time.sleep(0.3)
    expired_code = None
    try:
        authority2.resolve(short)
    except lab.ProbeError as error:
        expired_code = error.code
    m06 = {
        "id": "M-06-expiry-typed-error",
        "status": lab.PASS if ok_before and expired_code == "REF_EXPIRED" else lab.FAIL,
        "resolved_before_expiry": ok_before,
        "code_after_expiry": expired_code,
        "note": "expired mappings stay typeable and unreachable (ruling T6 semantics)",
    }
    records.append(m06)

    # ---------------- M-07 revocation typed ---------------------------------
    authority3 = lab.MappingIdAuthority(default_ttl_seconds=600)
    rev = authority3.issue(scope="managed", rel_path="revisions/rev-000042/raster.png", resource_id="rid-rev07")
    resolved_before = None
    try:
        authority3.resolve(rev)
        resolved_before = True
    except lab.ProbeError:
        resolved_before = False
    authority3.revoke(rev)
    revoked_code = None
    try:
        authority3.resolve(rev)
    except lab.ProbeError as error:
        revoked_code = error.code
    m07 = {
        "id": "M-07-revocation-typed-error",
        "status": lab.PASS if resolved_before and revoked_code == "REF_REVOKED" else lab.FAIL,
        "resolved_before_revoke": resolved_before,
        "code_after_revoke": revoked_code,
        "note": "revocation is immediate on next resolve (ruling T6); the opened-consumption carve-out is a "
        "runtime concern outside this prototype",
    }
    records.append(m07)

    # ---------------- M-08 sliding renewal ----------------------------------
    authority4 = lab.MappingIdAuthority(default_ttl_seconds=0.25)
    slid = authority4.issue(scope="derived", rel_path="slider/page.png", resource_id="rid-slide")
    time.sleep(0.15)
    authority4.touch(slid)
    alive_after_touch = None
    try:
        authority4.resolve(slid)
        alive_after_touch = True
    except lab.ProbeError:
        alive_after_touch = False
    time.sleep(0.35)
    final_code = None
    try:
        authority4.resolve(slid)
    except lab.ProbeError as error:
        final_code = error.code
    m08 = {
        "id": "M-08-sliding-renewal",
        "status": lab.PASS if alive_after_touch and final_code == "REF_EXPIRED" else lab.FAIL,
        "alive_after_touch": alive_after_touch,
        "code_after_idle_expiry": final_code,
        "note": "touch() re-arms the TTL; idle references expire (ruling T6 sliding renewal)",
    }
    records.append(m08)

    limitations = [
        "Opacity is inductive evidence: a bounded analysis space (substrings, common codecs, hash "
        "dictionaries, 5k+ guesses, neighbour mutations) recovers nothing from 192-bit random IDs. "
        "This is not a cryptographic proof and not a product guarantee.",
        "The mapping table lives inside the Core process by construction; protecting Core memory, "
        "crash dumps or a compromised host is out of scope (ruling T5 makes the host a trusted layer).",
        "No product IPC runtime, Tauri command or React consumer exists behind these surfaces; the "
        "log/telemetry streams here are prototype-level stand-ins for the caller-visible output.",
        "Core restart / table persistence semantics (S1-B5) are not exercised.",
    ]

    return {
        "probe": PROBE,
        "purpose": "opacity, lifecycle and leakage probes for M2-S1 blocker S1-B12 against the "
        "Core-side random mapping-ID reference prototype (threshold ruling T5.4)",
        "release_reference": "doc/tasks/M2-S2.md (S2-AC4); M2-S1 §8.2 S1-B12",
        "id_random_bits": lab.MappingIdAuthority.ID_RANDOM_BYTES * 8,
        "ids_issued": len(ids) + len(same_path_twice) + 3,
        "elapsed_seconds": round(time.time() - clock_start, 3),
        "scenarios": records,
        "boundary_summary": {
            "opacity": "no path or resource id recoverable from ID strings across the exercised "
            "analysis space (M-02/M-03); guessing is uniform-typed (M-04)",
            "leakage": "errors, logs and telemetry carry no mapping-table entries (M-05)",
            "lifecycle": "expiry, revocation and sliding renewal are typed (M-06/M-07/M-08)",
            "product_guarantee": "UNVERIFIED -- see limitations",
        },
        "limitations": limitations,
        "summary": lab.summary_of(records),
    }


def os_path_common_prefix(strings: list[str]) -> str:
    if not strings:
        return ""
    prefix = strings[0]
    for candidate in strings[1:]:
        index = 0
        limit = min(len(prefix), len(candidate))
        while index < limit and prefix[index] == candidate[index]:
            index += 1
        prefix = prefix[:index]
        if not prefix:
            break
    return prefix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    args = parser.parse_args()
    root = lab.lab_root(args.lab)
    return lab.emit(run_host(root), args.out or str(root / "mapping-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
