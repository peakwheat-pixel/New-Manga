"""
Read-Only Verification Script for P03 Traceability Logs Normalization.

This script strictly performs in-memory verification and assertions:
- Does NOT create directories or write/modify any files on disk.
- Asserts that all 6 canonical logs match in-memory formal grammar derivations bit-for-bit.
- Asserts that canonical logs are NUL-free, decodable UTF-8, and free of trailing whitespace.
- Performs inverse token mapping on canonical logs and asserts 100% bit-for-bit reconstruction of raw files.
- Verifies that 07-encoding-normalization.json matches all computed hashes, sizes, and assertions.
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

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("schema_version") == "2.1", "Expected manifest schema_version 2.1"
    assert manifest.get("all_assertions_passed") is True
    assert manifest.get("all_reconstructions_verified") is True

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

        # 2. Read canonical bytes from disk
        with open(canon_path, "rb") as f:
            disk_canon_bytes = f.read()
        disk_canon_sha256 = hashlib.sha256(disk_canon_bytes).hexdigest()
        disk_canon_len = len(disk_canon_bytes)

        # 3. Structural partition of raw file
        hdr_end = raw_bytes.find(sep_u8) + len(sep_u8)
        footer_start = raw_bytes.find(footer_tag)
        assert hdr_end > len(sep_u8), f"{fname}: malformed header partition"
        assert footer_start >= hdr_end, f"{fname}: malformed footer partition"

        raw_hdr = raw_bytes[:hdr_end]
        raw_body = raw_bytes[hdr_end:footer_start]
        raw_footer = raw_bytes[footer_start:]

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
        assert b"\x00" not in disk_canon_bytes, f"{fname}: NUL byte found in canonical output!"
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

        # 7. Validate manifest consistency
        meta = manifest_file_map[fname]
        assert meta["original"]["size_bytes"] == raw_len
        assert meta["original"]["sha256"] == raw_sha256
        assert meta["canonical"]["size_bytes"] == disk_canon_len
        assert meta["canonical"]["sha256"] == disk_canon_sha256
        assert meta["reconstruction_verification"]["reconstructed_matches_original_bit_for_bit"] is True

        print(f"  [PASS] {fname}:")
        print(f"         raw: {raw_len} B ({raw_sha256[:12]}...) | canon: {disk_canon_len} B ({disk_canon_sha256[:12]}...)")
        print(f"         NUL-free: TRUE | trailing-whitespace-free: TRUE | bit-for-bit inverse reconstruction: MATCH")

    print("\nALL 6 FILES VERIFIED READ-ONLY: Grammar, Hashes, Trailing Whitespace & Bijective Reconstruction 100% PASS.")
    return 0

if __name__ == "__main__":
    sys.exit(verify_all())
