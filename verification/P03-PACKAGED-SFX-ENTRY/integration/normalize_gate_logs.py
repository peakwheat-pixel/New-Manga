from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

RUN = Path(__file__).parent / "run-2de124f3-py314"
ARCHIVE = RUN / "raw-auxiliary-logs.zip"
MANIFEST = RUN / "raw-log-normalization.json"
FILES = (
    "cleanstart-ac1-catalog-initialize.log",
    "cleanstart-ac1-run1-stdout.log",
    "cleanstart-ac1-run2-stdout.log",
    "cleanstart-probe-stdout.log",
    "cleanstart-production-stdout.log",
    "r1-library-probe.log",
)
SPACE = "\u2420"
TAB = "\u21e5"
CARRIAGE_RETURN = "\u240d"
BLANK_LINE = "\u23ce"
MARKERS = (SPACE, TAB, CARRIAGE_RETURN, BLANK_LINE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonicalize(raw: bytes) -> tuple[bytes, dict[str, int]]:
    text = raw.decode("utf-8")
    if any(marker in text for marker in MARKERS):
        raise ValueError("raw log contains a reserved normalization marker")
    parts = re.split(r"(\r\n|\n)", text)
    counts = {"trailing_spaces": 0, "trailing_tabs": 0, "bare_carriage_returns": 0, "final_blank_lines": 0}
    output: list[str] = []
    for index in range(0, len(parts) - 1, 2):
        body, newline = parts[index], parts[index + 1]
        at_eof = "".join(parts[index + 2 :]) == ""
        if body == "" and newline and at_eof:
            body = BLANK_LINE
            counts["final_blank_lines"] += 1
        else:
            match = re.search(r"[ \t]+$", body)
            if match:
                suffix = match.group()
                counts["trailing_spaces"] += suffix.count(" ")
                counts["trailing_tabs"] += suffix.count("\t")
                body = body[: match.start()] + "".join(SPACE if char == " " else TAB for char in suffix)
        counts["bare_carriage_returns"] += body.count("\r")
        body = body.replace("\r", CARRIAGE_RETURN)
        output.extend((body, newline))
    if len(parts) % 2:
        output.append(parts[-1])
    return "".join(output).encode("utf-8"), counts


def reconstruct(canonical: bytes) -> bytes:
    text = canonical.decode("utf-8")
    parts = re.split(r"(\r\n|\n)", text)
    output: list[str] = []
    for index in range(0, len(parts) - 1, 2):
        body, newline = parts[index], parts[index + 1]
        at_eof = "".join(parts[index + 2 :]) == ""
        if body == BLANK_LINE and newline and at_eof:
            body = ""
        else:
            suffix = ""
            while body and body[-1] in (SPACE, TAB):
                suffix = (" " if body[-1] == SPACE else "\t") + suffix
                body = body[:-1]
            body += suffix
            body = body.replace(CARRIAGE_RETURN, "\r")
        output.extend((body, newline))
    if len(parts) % 2:
        output.append(parts[-1])
    return "".join(output).encode("utf-8")


def normalize() -> int:
    if ARCHIVE.exists():
        with zipfile.ZipFile(ARCHIVE, "r") as archive:
            if sorted(archive.namelist()) != sorted(FILES):
                raise ValueError("existing raw archive does not contain the exact expected log set")
            raw_files = {name: archive.read(name) for name in FILES}
    else:
        if MANIFEST.exists():
            raise FileExistsError("manifest exists without the raw archive; refusing to recreate evidence")
        raw_files = {name: (RUN / name).read_bytes() for name in FILES}
        with zipfile.ZipFile(ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, raw in raw_files.items():
                archive.writestr(name, raw)
    archive_sha = sha256(ARCHIVE.read_bytes())
    rows = []
    for name, raw in raw_files.items():
        canonical, counts = canonicalize(raw)
        (RUN / name).write_bytes(canonical)
        with zipfile.ZipFile(ARCHIVE, "r") as archive:
            archived_raw = archive.read(name)
        on_disk = (RUN / name).read_bytes()
        assert archived_raw == raw, f"{name}: archive did not preserve raw bytes"
        assert on_disk == canonical, f"{name}: canonical output changed on write"
        assert reconstruct(on_disk) == archived_raw, f"{name}: inverse reconstruction was not bit-for-bit"
        assert not any(line.endswith((" ", "\t")) for line in on_disk.decode("utf-8").splitlines())
        rows.append({
            "filename": name,
            "raw_archive_entry": name,
            "raw_size_bytes": len(raw),
            "raw_sha256": sha256(raw),
            "canonical_size_bytes": len(canonical),
            "canonical_sha256": sha256(canonical),
            "tokens": counts,
            "inverse_reconstruction_bit_for_bit": True,
        })
    manifest = {
        "schema_version": "1.0",
        "raw_archive": ARCHIVE.name,
        "raw_archive_size_bytes": ARCHIVE.stat().st_size,
        "raw_archive_sha256": archive_sha,
        "reserved_markers": {"trailing_space": SPACE, "trailing_tab": TAB, "bare_carriage_return": CARRIAGE_RETURN, "final_blank_line": BLANK_LINE},
        "files_count": len(rows),
        "all_assertions_passed": True,
        "files": rows,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"raw archive SHA256={archive_sha}")
    for row in rows:
        print(f"PASS {row['filename']}: raw={row['raw_sha256']} canonical={row['canonical_sha256']} tokens={row['tokens']} inverse=bit-for-bit")
    print("ALL AUXILIARY LOGS: raw archive, hashes, canonical form, and inverse reconstruction PASS")
    return 0


def verify() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1.0"
    assert manifest["all_assertions_passed"] is True
    assert manifest["files_count"] == len(FILES)
    archive_bytes = ARCHIVE.read_bytes()
    assert len(archive_bytes) == manifest["raw_archive_size_bytes"]
    assert sha256(archive_bytes) == manifest["raw_archive_sha256"]
    with zipfile.ZipFile(ARCHIVE, "r") as archive:
        assert sorted(archive.namelist()) == sorted(FILES)
        rows = {row["filename"]: row for row in manifest["files"]}
        assert set(rows) == set(FILES)
        for name in FILES:
            raw = archive.read(name)
            canonical = (RUN / name).read_bytes()
            row = rows[name]
            expected, counts = canonicalize(raw)
            assert canonical == expected, f"{name}: canonical bytes differ from raw-derived form"
            assert reconstruct(canonical) == raw, f"{name}: inverse reconstruction mismatch"
            assert row["raw_size_bytes"] == len(raw) and row["raw_sha256"] == sha256(raw)
            assert row["canonical_size_bytes"] == len(canonical) and row["canonical_sha256"] == sha256(canonical)
            assert row["tokens"] == counts and row["inverse_reconstruction_bit_for_bit"] is True
            assert not any(line.endswith((" ", "\t")) for line in canonical.decode("utf-8").splitlines())
            print(f"PASS {name}: archived raw + canonical hash + inverse reconstruction")
    print("READ-ONLY NORMALIZATION VERIFICATION: ALL SIX LOGS PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    return verify() if args.verify_only else normalize()


if __name__ == "__main__":
    raise SystemExit(main())