"""Offline pre-push triage. Reports locations and hashes, never matched secrets."""
import collections
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[3]
RULES = {
    "private_key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----",
    "github_token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{70,255})\b",
    "openai_token": rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,255}\b",
    "aws_access_key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "google_api_key": rb"\bAIza[A-Za-z0-9_-]{35}\b",
    "slack_token": rb"\bxox[baprs]-[A-Za-z0-9-]{20,255}\b",
    "credential_assignment": rb"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd)[\"']?\s*[:=]\s*[\"']([^\r\n\"']{12,200})[\"']",
}
PATTERNS = {name: re.compile(pattern) for name, pattern in RULES.items()}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def inspect(data, oid, path, findings):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        data = data.decode("utf-16", errors="replace").encode()
    for rule, pattern in PATTERNS.items():
        for match in pattern.finditer(data):
            value = match.group(1) if rule == "credential_assignment" else match.group()
            findings.append({"rule": rule, "object": oid, "path": path,
                             "line": data.count(b"\n", 0, match.start()) + 1,
                             "value_sha256": hashlib.sha256(value).hexdigest()})


def kind(data):
    if len(data) >= 2 and data[0] == 0x78 and (data[0] * 256 + data[1]) % 31 == 0:
        return "zlib"
    for prefix, label in [(b"PK\x03\x04", "zip"), (b"\x89PNG", "png"),
                          (b"\xff\xd8\xff", "jpeg"), (b"%PDF", "pdf"),
                          (b"SQLite format 3", "sqlite"), (b"MZ", "pe"),
                          (b"\x1f\x8b", "gzip"), (b"7z\xbc\xaf\x27\x1c", "7z")]:
        if data.startswith(prefix):
            return label
    return "binary" if b"\0" in data[:8192] else "text"


def selfcheck():
    found = []
    inspect(b"hello\napi_key='" + b"a" * 20 + b"'\n", "test", "fixture", found)
    assert len(found) == 1 and found[0]["line"] == 2
    assert "a" * 20 not in json.dumps(found)
    assert kind(b"PK\x03\x04test") == "zip"
    assert kind(zlib.compress(b"test")) == "zlib"
    found = []
    inspect(("api_key='" + "a" * 20 + "'").encode("utf-16"), "test", "fixture", found)
    assert len(found) == 1
    for name, value in [("github_token", b"ghp_" + b"a" * 36),
                        ("openai_token", b"sk-proj-" + b"b" * 40),
                        ("private_key", b"-----BEGIN PRIVATE KEY-----")]:
        assert PATTERNS[name].search(value)


def main():
    selfcheck()
    base = git("rev-parse", "origin/main").decode().strip()
    head = git("rev-parse", "main").decode().strip()
    lines = git("rev-list", "--objects", f"{base}..{head}").decode().splitlines()
    objects = dict(line.split(" ", 1) if " " in line else (line, "") for line in lines)
    source_paths = dict(line.split(" ", 1) for line in
                        git("rev-list", "--objects", head).decode().splitlines() if " " in line)
    source_paths.update(objects)
    metadata = subprocess.run(["git", "-C", str(ROOT), "cat-file",
                               "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
                              input=("\n".join(objects) + "\n").encode(),
                              capture_output=True, check=True).stdout.decode().splitlines()
    blobs = [(parts[0], int(parts[2])) for row in metadata
             if (parts := row.split())[1] == "blob"]
    findings, archives, material, compressed = [], [], [], []
    counts = collections.Counter()
    # One persistent process avoids thousands of subprocesses; each response has exact size.
    process = subprocess.Popen(["git", "-C", str(ROOT), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for oid, size in blobs:
            process.stdin.write((oid + "\n").encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            assert header == [oid.encode(), b"blob", str(size).encode()]
            data = process.stdout.read(size)
            assert len(data) == size and process.stdout.read(1) == b"\n"
            path = objects[oid]
            label = kind(data)
            counts[label] += 1
            inspect(data, oid, path, findings)
            if label != "text" or path.startswith(".tmp.driveupload/"):
                material.append({"object": oid, "path": path, "kind": label, "bytes": size,
                                 "sha256": hashlib.sha256(data).hexdigest()})
            if label == "zlib":
                entry = {"object": oid, "path": path}
                try:
                    decoder = zlib.decompressobj()
                    payload = decoder.decompress(data, 64 * 1024**2 + 1)
                    if len(payload) > 64 * 1024**2 or not decoder.eof or decoder.unused_data:
                        entry["blocked"] = "size_limit_or_incomplete_or_trailing_data"
                    else:
                        entry["decoded_bytes"] = len(payload)
                        git_header = re.match(rb"(blob|tree|commit|tag) ([0-9]+)\x00", payload)
                        inner_path = path + "!zlib"
                        if git_header:
                            entry["git_type"] = git_header.group(1).decode()
                            entry["git_object"] = hashlib.sha1(payload).hexdigest()
                            entry["git_size_valid"] = int(git_header.group(2)) == len(payload) - git_header.end()
                            entry["representative_source_path"] = source_paths.get(entry["git_object"])
                            payload = payload[git_header.end():]
                        entry["payload_kind"] = kind(payload)
                        entry["payload_sha256"] = hashlib.sha256(payload).hexdigest()
                        inspect(payload, oid, inner_path, findings)
                        # Reuse the archive pass if a compressed Git blob contains a ZIP.
                        if entry["payload_kind"] == "zip":
                            data, path, label = payload, inner_path, "zip"
                except zlib.error:
                    entry["blocked"] = "invalid_zlib"
                compressed.append(entry)
            if label == "zip":
                entry = {"object": oid, "path": path, "scanned": 0, "blocked": []}
                try:
                    with zipfile.ZipFile(io.BytesIO(data)) as archive:
                        total = 0
                        for member in archive.infolist():
                            if member.is_dir():
                                continue
                            if member.flag_bits & 1 or member.file_size > 64 * 1024**2 or total + member.file_size > 256 * 1024**2:
                                entry["blocked"].append(member.filename)
                                continue
                            payload = archive.read(member)
                            total += len(payload)
                            inspect(payload, oid, path + "!" + member.filename, findings)
                            entry["scanned"] += 1
                except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError) as exc:
                    entry["error"] = type(exc).__name__
                archives.append(entry)
    finally:
        process.stdin.close()
        process.stdout.close()
        assert process.wait() == 0
    report = {"base": base, "head": head, "commit_count": int(git("rev-list", "--count", f"{base}..{head}")),
              "blob_count": len(blobs), "blob_bytes": sum(s for _, s in blobs),
              "kinds": dict(counts), "rules": list(RULES), "findings": findings,
              "archives": archives, "compressed": compressed, "material": material,
              "limitations": ["Heuristic triage, not proof that secrets are absent.",
                              "Object path is one representative path, not all historical aliases.",
                              "Zlib and ZIP decoded one layer each; deeper nesting, other compression, encoded secrets and image text not decoded.",
                              "No credentials are tested online; material redistribution rights require separate evidence."]}
    output = ROOT / "audit/V1-FULL-AUDIT/evidence/push-history-scan.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"base": base, "head": head, "blobs": len(blobs), "kinds": dict(counts),
                      "findings_by_rule": dict(collections.Counter(f["rule"] for f in findings)),
                      "archives": len(archives), "report": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
