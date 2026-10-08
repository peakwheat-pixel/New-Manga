import os
import glob
import hashlib
import json
import datetime

base_dir = r"verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun"
out_dir = os.path.join(base_dir, "canonical-utf8")
os.makedirs(out_dir, exist_ok=True)

raw_files = sorted(glob.glob(os.path.join(base_dir, "*.log")))
assert len(raw_files) == 6, f"Expected 6 log files, found {len(raw_files)}"

sep_u8 = b"=====================================\r\n"
footer_tag = b"=====================================\r\nEndTime:"

files_meta = []

for filepath in raw_files:
    fname = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        orig_bytes = f.read()

    orig_sha256 = hashlib.sha256(orig_bytes).hexdigest()
    orig_len = len(orig_bytes)
    orig_nul_count = orig_bytes.count(b"\x00")

    hdr_end = orig_bytes.find(sep_u8) + len(sep_u8)
    footer_start = orig_bytes.find(footer_tag)
    assert hdr_end > len(sep_u8), f"Invalid header in {fname}"
    assert footer_start >= hdr_end, f"Invalid footer in {fname}"

    hdr_bytes = orig_bytes[:hdr_end]
    body_bytes = orig_bytes[hdr_end:footer_start]
    footer_bytes = orig_bytes[footer_start:]

    token_stats = {
        "char_tokens_count": 0,
        "newline_tokens_count": 0,
        "total_tokens": 0,
    }

    if fname == "05-rerun-diff-check.log":
        assert len(body_bytes) == 0, "05 should have empty body"
        assert orig_nul_count == 0, "05 should have 0 NULs"
        canonical_bytes = orig_bytes
        reconstructed_bytes = orig_bytes
    else:
        # Tokenize body according to strict bijective grammar
        idx = 0
        canonical_body = bytearray()
        while idx < len(body_bytes):
            if body_bytes.startswith(b"\r\n\x00\r\n\x00", idx):
                canonical_body.extend(b"\r\n\r\n")
                token_stats["newline_tokens_count"] += 1
                idx += 6
            elif idx + 1 < len(body_bytes) and body_bytes[idx + 1] == 0:
                c = body_bytes[idx]
                assert c not in (ord("\r"), ord("\n")), f"Unexpected raw newline in {fname} at {idx}"
                canonical_body.append(c)
                token_stats["char_tokens_count"] += 1
                idx += 2
            else:
                raise ValueError(f"Malformed byte at {idx} in {fname}: {body_bytes[idx:idx+10]!r}")

        token_stats["total_tokens"] = token_stats["char_tokens_count"] + token_stats["newline_tokens_count"]
        canonical_bytes = hdr_bytes + bytes(canonical_body) + footer_bytes

        # Inverse transform to prove bijectivity and zero information loss
        recon_idx = 0
        reconstructed_body = bytearray()
        while recon_idx < len(canonical_body):
            if canonical_body.startswith(b"\r\n\r\n", recon_idx):
                reconstructed_body.extend(b"\r\n\x00\r\n\x00")
                recon_idx += 4
            else:
                c = canonical_body[recon_idx]
                reconstructed_body.extend([c, 0])
                recon_idx += 1

        reconstructed_bytes = hdr_bytes + bytes(reconstructed_body) + footer_bytes

    # Bit-for-bit assertion
    assert reconstructed_bytes == orig_bytes, f"Reconstruction failed for {fname}"

    # Save canonical
    out_path = os.path.join(out_dir, fname)
    with open(out_path, "wb") as f:
        f.write(canonical_bytes)

    # Assertions on canonical
    assert b"\x00" not in canonical_bytes, f"NUL detected in canonical {fname}"
    canon_text = canonical_bytes.decode("utf-8")
    assert "=== Traceability Execution Record ===" in canon_text, f"Missing header in {fname}"
    assert "EXIT=0" in canon_text, f"Missing EXIT=0 in {fname}"
    assert canon_text.strip().endswith("====================================="), f"Missing footer in {fname}"

    canon_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
    canon_len = len(canonical_bytes)
    canon_nul_count = canonical_bytes.count(b"\x00")

    files_meta.append({
        "filename": fname,
        "original": {
            "relative_path": os.path.relpath(filepath, ".").replace("\\", "/"),
            "size_bytes": orig_len,
            "sha256": orig_sha256,
            "nul_bytes_count": orig_nul_count,
        },
        "canonical": {
            "relative_path": os.path.relpath(out_path, ".").replace("\\", "/"),
            "size_bytes": canon_len,
            "sha256": canon_sha256,
            "nul_bytes_count": canon_nul_count,
        },
        "segments": {
            "header": {
                "start_byte": 0,
                "end_byte": hdr_end,
                "raw_encoding": "utf-8-sig",
                "canonical_encoding": "utf-8-sig",
                "byte_transform": "identity",
            },
            "body": {
                "start_byte": hdr_end,
                "end_byte": footer_start,
                "raw_encoding": "utf-16le-ascii-with-splitline-crlf" if len(body_bytes) > 0 else "empty",
                "canonical_encoding": "utf-8" if len(body_bytes) > 0 else "empty",
                "raw_body_bytes": len(body_bytes),
                "canonical_body_bytes": len(canonical_bytes) - len(hdr_bytes) - len(footer_bytes),
                "token_statistics": token_stats,
                "byte_transform": "bijective_token_mapping" if len(body_bytes) > 0 else "identity",
            },
            "footer": {
                "start_byte": footer_start,
                "end_byte": orig_len,
                "raw_encoding": "utf-8",
                "canonical_encoding": "utf-8",
                "byte_transform": "identity",
            },
        },
        "reconstruction_verification": {
            "reconstructed_matches_original_bit_for_bit": True,
            "reconstructed_sha256": orig_sha256,
            "reconstructed_size_bytes": orig_len,
            "inverse_transform": "inverse_token_mapping" if len(body_bytes) > 0 else "identity",
        },
        "assertions": {
            "nul_free": True,
            "utf8_decodable": True,
            "header_record_present": True,
            "exit_zero_present": True,
            "footer_delimiter_present": True,
            "byte_copy_for_05": (canon_sha256 == orig_sha256) if fname == "05-rerun-diff-check.log" else None,
            "reconstruction_verified": True,
            "status": "PASS",
        },
    })

full_manifest = {
    "schema_version": "2.0",
    "title": "Traceability Logs Canonical UTF-8 Normalization and Formal Bijective Verification",
    "timestamp_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "files_count": len(files_meta),
    "all_assertions_passed": True,
    "all_reconstructions_verified": True,
    "grammar_specification": {
        "description": "Formal grammar defining the mixed-encoding body byte stream and its bijective mapping to canonical UTF-8",
        "segments": {
            "header": "UTF-8-SIG bytes from start to separator =====================================\\r\\n",
            "body": "Token stream between header separator and footer separator =====================================\\r\\nEndTime:",
            "footer": "UTF-8 bytes from footer separator to file EOF",
        },
        "tokens": {
            "CHAR_TOKEN": {
                "raw_byte_pattern": "[0x00-0x7F, 0x00] excluding CR/LF in byte 0",
                "raw_byte_length": 2,
                "interpretation": "Standard UTF-16LE encoding of single-byte ASCII characters",
                "forward_canonical_mapping": "Single byte c (UTF-8 ASCII)",
                "inverse_mapping": "bytes([c, 0])",
            },
            "NEWLINE_TOKEN": {
                "raw_byte_pattern": "0x0D 0x0A 0x00 0x0D 0x0A 0x00 (hex: 0d 0a 00 0d 0a 00)",
                "raw_byte_length": 6,
                "interpretation": "Splitline-crlf expansion: UTF-16LE CR (0x0D 0x00) and LF (0x0A 0x00) separated by UTF-8 splitlines re-encoding into \\r\\n\\x00\\r\\n\\x00. Under raw UTF-16LE decoding, this sequence corresponds to U+0A0D U+0D00 U+000A",
                "forward_canonical_mapping": "\\r\\n\\r\\n (hex: 0d 0a 0d 0a, CRLF CRLF, 4 bytes)",
                "inverse_mapping": "b'\\r\\n\\x00\\r\\n\\x00' (6 bytes)",
            },
        },
        "transform_properties": {
            "deterministic": True,
            "bijective": True,
            "information_loss": False,
            "lossless_reconstruction_verified": True,
        },
    },
    "files": files_meta,
}

meta_path = os.path.join(base_dir, "07-encoding-normalization.json")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(full_manifest, f, indent=2, ensure_ascii=False)

print("SUCCESS: 07-encoding-normalization.json generated and verified!")
