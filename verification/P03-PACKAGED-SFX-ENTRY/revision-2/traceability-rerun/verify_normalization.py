"""
Read-Only Verification Script for P03 Traceability Logs Normalization.

This script strictly performs in-memory verification and assertions:
- Does NOT create directories or write/modify any files on disk (idempotent read-only).
- Asserts that all 6 canonical logs match in-memory formal grammar derivations bit-for-bit.
- Asserts that canonical logs are NUL-free, decodable UTF-8, and free of trailing whitespace.
- Explicitly asserts that U+2420 UTF-8 bytes do NOT occur in original raw body.
- Performs inverse token mapping on canonical logs and asserts 100% bit-for-bit reconstruction of raw files.
- Fully verifies that 07-encoding-normalization.json matches all computed hashes, sizes, NUL counts,
  reconstruction properties, and per-file assertion statuses.
"""

import os
import glob
import hashlib
import json
import sys

def verify_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "canonical-utf8")
    manifest_path = os.path.join(base_dir, "07-encoding-normalization.json")

    # Ensure required paths exist
    assert os.path.isdir(out_dir), f"Directory missing: {out_dir}"
    assert os.path.isfile(manifest_path), f"Manifest missing: {manifest_path}"

    raw_files = sorted(glob.glob(os.path.join(base_dir, "*.log")))
    assert len(raw_files) == 6, f"Expected 6 raw log files, found {len(raw_files)}"

    sep_u8 = b"=====================================\r\n"
    footer_tag = b"=====================================\r\nEndTime:"
    ESCAPE_SPACE = "\u2420"  # U+2420 SYMBOL FOR SPACE (␠)
    ESCAPE_SPACE_UTF8 = ESCAPE_SPACE.encode("utf-8")  # b"\xe2\x90\xa0"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("schema_version") == "2.1", "Expected manifest schema_version 2.1"
    assert manifest.get("files_count") == 6, "Expected manifest files_count == 6"
    assert manifest.get("all_assertions_passed") is True, "Manifest all_assertions_passed must be True"
    assert manifest.get("all_reconstructions_verified") is True, "Manifest all_reconstructions_verified must be True"

    manifest_file_map = {item["filename"]: item for item in manifest["files"]}
    assert len(manifest_file_map) == 6, "Manifest must document all 6 files"

    print("=== P03 Traceability Logs Read-Only Verification ===")

    for raw_path in raw_files:
        fname = os.path.basename(raw_path)
        canon_path = os.path.join(out_dir, fname)
        assert os.path.isfile(canon_path), f"Canonical file missing: {canon_path}"

        # 1. Read raw bytes
        with open(raw_path, "rb") as f:
            raw_bytes = f.read()
        raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        raw_len = len(raw_bytes)
        actual_raw_nul_count = raw_bytes.count(b"\x00")

        # 2. Read canonical bytes from disk
        with open(canon_path, "rb") as f:
            disk_canon_bytes = f.read()
        disk_canon_sha256 = hashlib.sha256(disk_canon_bytes).hexdigest()
        disk_canon_len = len(disk_canon_bytes)
        actual_canon_nul_count = disk_canon_bytes.count(b"\x00")

        # 3. Structural partition of raw file
        hdr_end = raw_bytes.find(sep_u8) + len(sep_u8)
        footer_start = raw_bytes.find(footer_tag)
        assert hdr_end > len(sep_u8), f"{fname}: malformed header partition"
        assert footer_start >= hdr_end, f"{fname}: malformed footer partition"

        raw_hdr = raw_bytes[:hdr_end]
        raw_body = raw_bytes[hdr_end:footer_start]
        raw_footer = raw_bytes[footer_start:]

        # Explicit assertion: U+2420 UTF-8 bytes must not appear anywhere in original raw body
        assert ESCAPE_SPACE_UTF8 not in raw_body, f"{fname}: U+2420 UTF-8 bytes found in original raw body!"

        # 4. In-memory derivation of expected canonical
        if fname == "05-rerun-diff-check.log":
            assert len(raw_body) == 0, f"{fname}: expected empty body"
            expected_canon_bytes = raw_bytes
        else:
            idx = 0
            expected_body_tokens = []
            while idx < len(raw_body):
                if raw_body.startswith(b" \x00\r\n\x00\r\n\x00", idx):
                    expected_body_tokens.append(ESCAPE_SPACE + "\r\n\r\n")
                    idx += 8
                elif raw_body.startswith(b"\r\n\x00\r\n\x00", idx):
                    expected_body_tokens.append("\r\n\r\n")
                    idx += 6
                elif idx + 1 < len(raw_body) and raw_body[idx + 1] == 0:
                    c = chr(raw_body[idx])
                    assert c not in ("\r", "\n"), f"{fname}: unexpected unescaped newline char at {idx}"
                    expected_body_tokens.append(c)
                    idx += 2
                else:
                    raise ValueError(f"{fname}: malformed byte at {idx}")

            expected_body_text = "".join(expected_body_tokens)
            expected_canon_text = raw_hdr.decode("utf-8-sig") + expected_body_text + raw_footer.decode("utf-8")
            expected_canon_bytes = expected_canon_text.encode("utf-8-sig")

        # Assert disk canonical matches memory derivation bit-for-bit
        assert disk_canon_bytes == expected_canon_bytes, f"{fname}: disk canonical diverges from formal grammar!"

        # 5. Quality assertions on canonical file
        assert actual_canon_nul_count == 0, f"{fname}: NUL byte found in canonical output!"
        canon_text = disk_canon_bytes.decode("utf-8-sig")
        assert "=== Traceability Execution Record ===" in canon_text, f"{fname}: header record missing"
        assert "EXIT=0" in canon_text, f"{fname}: EXIT=0 missing"
        assert canon_text.strip().endswith("====================================="), f"{fname}: footer missing"

        # Trailing whitespace check on all canonical lines
        for line_no, line in enumerate(canon_text.splitlines(), start=1):
            assert not line.endswith(" ") and not line.endswith("\t"), (
                f"{fname}:{line_no}: trailing whitespace found in canonical line: {line!r}"
            )

        # 6. Inverse transform: reconstruct raw bytes from canonical
        if fname == "05-rerun-diff-check.log":
            reconstructed_raw = disk_canon_bytes
        else:
            canon_hdr_end = disk_canon_bytes.find(sep_u8) + len(sep_u8)
            canon_footer_start = disk_canon_bytes.find(footer_tag)
            canon_body_text = disk_canon_bytes[canon_hdr_end:canon_footer_start].decode("utf-8")

            recon_idx = 0
            recon_body = bytearray()
            while recon_idx < len(canon_body_text):
                if canon_body_text.startswith(ESCAPE_SPACE + "\r\n\r\n", recon_idx):
                    recon_body.extend(b" \x00\r\n\x00\r\n\x00")
                    recon_idx += len(ESCAPE_SPACE) + 4
                elif canon_body_text.startswith("\r\n\r\n", recon_idx):
                    recon_body.extend(b"\r\n\x00\r\n\x00")
                    recon_idx += 4
                else:
                    c = ord(canon_body_text[recon_idx])
                    recon_body.extend([c, 0])
                    recon_idx += 1

            reconstructed_raw = raw_hdr + bytes(recon_body) + raw_footer

        assert reconstructed_raw == raw_bytes, f"{fname}: inverse reconstruction failed to match original bytes bit-for-bit!"

        # 7. Validate manifest consistency with complete assertions
        meta = manifest_file_map[fname]

        # 7a. Original properties
        assert meta["original"]["size_bytes"] == raw_len, f"{fname}: original size mismatch"
        assert meta["original"]["sha256"] == raw_sha256, f"{fname}: original sha256 mismatch"
        assert meta["original"]["nul_bytes_count"] == actual_raw_nul_count, (
            f"{fname}: manifest original nul_bytes_count ({meta['original']['nul_bytes_count']}) != actual ({actual_raw_nul_count})"
        )

        # 7b. Canonical properties
        assert meta["canonical"]["size_bytes"] == disk_canon_len, f"{fname}: canonical size mismatch"
        assert meta["canonical"]["sha256"] == disk_canon_sha256, f"{fname}: canonical sha256 mismatch"
        assert meta["canonical"]["nul_bytes_count"] == actual_canon_nul_count, (
            f"{fname}: manifest canonical nul_bytes_count ({meta['canonical']['nul_bytes_count']}) != actual ({actual_canon_nul_count})"
        )

        # 7c. Reconstruction verification properties
        recon_computed_sha256 = hashlib.sha256(reconstructed_raw).hexdigest()
        recon_computed_len = len(reconstructed_raw)
        assert meta["reconstruction_verification"]["reconstructed_sha256"] == recon_computed_sha256, (
            f"{fname}: manifest reconstructed_sha256 ({meta['reconstruction_verification']['reconstructed_sha256']}) != computed ({recon_computed_sha256})"
        )
        assert meta["reconstruction_verification"]["reconstructed_size_bytes"] == recon_computed_len, (
            f"{fname}: manifest reconstructed_size_bytes ({meta['reconstruction_verification']['reconstructed_size_bytes']}) != computed ({recon_computed_len})"
        )
        assert meta["reconstruction_verification"]["reconstructed_matches_original_bit_for_bit"] is True, (
            f"{fname}: manifest reconstructed_matches_original_bit_for_bit must be True"
        )

        # 7d. Per-file assertion statuses
        assertions = meta["assertions"]
        assert assertions["nul_free"] is True, f"{fname}: manifest nul_free assertion is not True"
        assert assertions["trailing_whitespace_free"] is True, f"{fname}: manifest trailing_whitespace_free assertion is not True"
        assert assertions["utf8_decodable"] is True, f"{fname}: manifest utf8_decodable assertion is not True"
        assert assertions["header_record_present"] is True, f"{fname}: manifest header_record_present assertion is not True"
        assert assertions["exit_zero_present"] is True, f"{fname}: manifest exit_zero_present assertion is not True"
        assert assertions["footer_delimiter_present"] is True, f"{fname}: manifest footer_delimiter_present assertion is not True"
        assert assertions["reconstruction_verified"] is True, f"{fname}: manifest reconstruction_verified assertion is not True"
        assert assertions["status"] == "PASS", f"{fname}: manifest assertion status is not PASS"

        if fname == "05-rerun-diff-check.log":
            assert assertions["byte_copy_for_05"] is True, f"{fname}: manifest byte_copy_for_05 must be True"
        else:
            assert assertions["byte_copy_for_05"] is None, f"{fname}: manifest byte_copy_for_05 must be None"

        print(f"  [PASS] {fname}:")
        print(f"         raw: {raw_len} B ({raw_sha256[:12]}..., NUL={actual_raw_nul_count}) | canon: {disk_canon_len} B ({disk_canon_sha256[:12]}..., NUL={actual_canon_nul_count})")
        print(f"         U+2420 absent from raw body: TRUE | NUL-free: TRUE | trailing-whitespace-free: TRUE")
        print(f"         bit-for-bit inverse reconstruction: MATCH | manifest consistency: 100% VERIFIED")

    print("\nALL 6 FILES VERIFIED READ-ONLY: Grammar, Hashes, Trailing Whitespace, Bijective Reconstruction & Manifest Consistency 100% PASS.")
    return 0

if __name__ == "__main__":
    sys.exit(verify_all())
