#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

CLONE = r"G:\CODEX\P02-scratch-build-source"
ROOT = r"G:\CODEX\New Manga"
PINNED_HEAD = "7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a"
CONFIG_SHA256 = "9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d"
REPARSE = 0x400
EXPECTED = [
    (CLONE, r"C:\P02\scratch", False),
    (os.path.join(CLONE, "verification", "P02", "tmp", "smoke-readonly-probe"), r"C:\P02\readonly-canary", True),
    (r"C:\Users\49745\AppData\Local\Programs\Python\Python312", r"C:\Users\49745\AppData\Local\Programs\Python\Python312", True),
    (r"G:\CODEX\New Manga.task-envs\m2ac5-build", r"C:\P02\inputs\python-venv", True),
    (r"G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector", r"C:\P02\inputs\weights\detector", True),
    (r"G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b", r"C:\P02\inputs\weights\sfx", True),
    (r"E:\Program Files\nodejs", r"C:\P02\inputs\nodejs", True),
    (r"C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc", r"C:\P02\inputs\rust-toolchain", True),
    (r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools", r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools", True),
    (r"C:\Program Files (x86)\Microsoft Visual Studio\Installer", r"C:\Program Files (x86)\Microsoft Visual Studio\Installer", True),
    (r"C:\Program Files (x86)\Windows Kits\10", r"C:\Program Files (x86)\Windows Kits\10", True),
]
CANARY = EXPECTED[1][0]
FULL_ROOTS = {
    os.path.normcase(os.path.abspath(CLONE)),
    os.path.normcase(os.path.abspath(CANARY)),
    os.path.normcase(os.path.abspath(EXPECTED[3][0])),
    os.path.normcase(os.path.abspath(EXPECTED[4][0])),
    os.path.normcase(os.path.abspath(EXPECTED[5][0])),
}
SAMPLES = {
    os.path.normcase(os.path.abspath(EXPECTED[2][0])): {"python.exe", "python312.dll"},
    os.path.normcase(os.path.abspath(EXPECTED[6][0])): {"node.exe", "npm.cmd", "npx.cmd"},
    os.path.normcase(os.path.abspath(EXPECTED[7][0])): {"cargo.exe", "rustc.exe"},
    os.path.normcase(os.path.abspath(EXPECTED[8][0])): {"cl.exe", "link.exe", "msbuild.exe"},
    os.path.normcase(os.path.abspath(EXPECTED[9][0])): {"vswhere.exe"},
    os.path.normcase(os.path.abspath(EXPECTED[10][0])): {"rc.exe", "mt.exe", "windows.h"},
}

def norm(path):
    return os.path.normcase(os.path.abspath(path))

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def run_git(path, *args):
    result = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"git {args!r} failed with {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()

def is_reparse(info):
    return bool(getattr(info, "st_file_attributes", 0) & REPARSE)

def file_hash(path, expected):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        before = os.fstat(stream.fileno())
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
        after = os.fstat(stream.fileno())
    signature = lambda x: (x.st_size, x.st_mtime_ns, getattr(x, "st_ino", None))
    if signature(before) != signature(after) or signature(after) != expected:
        raise RuntimeError("file_changed_during_hash")
    return digest.hexdigest()

def record(path, kind, size=None, digest=None, digest_status=None):
    if kind == "directory":
        return {"schema_version": 1, "path": path, "type": kind, "size_bytes": None,
                "sha256": None, "sha256_status": "not_applicable"}
    return {"schema_version": 1, "path": path, "type": kind, "size_bytes": size,
            "sha256": digest, "sha256_status": digest_status}

def scan_mapping(host, guest, readonly, index):
    started = datetime.now().astimezone().isoformat(timespec="milliseconds")
    root = os.path.abspath(host)
    full = norm(root) in FULL_ROOTS
    required_samples = SAMPLES.get(norm(root), set())
    if not full and not required_samples:
        return {"index": index, "host_folder": host, "sandbox_folder": guest,
                "read_only": readonly, "status": "BLOCKED", "issues": ["hash_policy_missing"],
                "records_count": 0, "files": 0, "directories": 0}
    records = []
    files = []
    directories = []
    issues = []
    seen = {}
    root_info = None
    try:
        root_info = os.lstat(root)
        if is_reparse(root_info):
            issues.append({"path": ".", "reason": "host_root_is_reparse_point",
                           "attributes": root_info.st_file_attributes})
        elif not stat.S_ISDIR(root_info.st_mode):
            issues.append({"path": ".", "reason": "host_root_not_directory"})
        else:
            records.append(record(".", "directory"))
            directories.append((root, root_info))
    except OSError as exc:
        issues.append({"path": ".", "reason": "host_root_stat_error",
                       "error_type": type(exc).__name__, "message": str(exc)})
    stack = [root] if root_info and stat.S_ISDIR(root_info.st_mode) and not is_reparse(root_info) else []
    while stack:
        directory = stack.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = list(iterator)
        except OSError as exc:
            rel_dir = os.path.relpath(directory, root).replace(os.sep, "/")
            issues.append({"path": rel_dir, "reason": "directory_enumeration_error",
                           "error_type": type(exc).__name__, "message": str(exc)})
            continue
        for entry in entries:
            try:
                full_path = os.path.abspath(entry.path)
                if os.path.commonpath([root, full_path]).casefold() != root.casefold():
                    issues.append({"path": entry.name, "reason": "out_of_root_path"})
                    continue
                info = os.lstat(full_path)
                rel = os.path.relpath(full_path, root).replace(os.sep, "/")
                folded = rel.casefold()
                prior = seen.get(folded)
                if prior is not None and prior != rel:
                    issues.append({"path": rel, "reason": "windows_case_collision", "other_path": prior})
                else:
                    seen[folded] = rel
                if is_reparse(info):
                    issues.append({"path": rel, "reason": "reparse_point_not_followed",
                                   "attributes": info.st_file_attributes})
                elif stat.S_ISDIR(info.st_mode):
                    records.append(record(rel, "directory"))
                    directories.append((full_path, info))
                    stack.append(full_path)
                elif stat.S_ISREG(info.st_mode):
                    rec = record(rel, "file", size=info.st_size, digest=None, digest_status="not_computed")
                    records.append(rec)
                    files.append((rel, full_path, rec, info))
                else:
                    issues.append({"path": rel, "reason": "unsupported_filesystem_object",
                                   "mode": info.st_mode})
            except OSError as exc:
                issues.append({"path": entry.name, "reason": "entry_stat_error",
                               "error_type": type(exc).__name__, "message": str(exc)})
    selected_names = set()
    hashed_bytes = 0
    for rel, full_path, rec, info in files:
        basename = os.path.basename(rel).casefold()
        should_hash = full or basename in required_samples
        if not should_hash:
            continue
        try:
            rec["sha256"] = file_hash(full_path, (info.st_size, info.st_mtime_ns, getattr(info, "st_ino", None)))
            rec["sha256_status"] = "verified"
            hashed_bytes += info.st_size
            selected_names.add(basename)
        except (OSError, RuntimeError) as exc:
            issues.append({"path": rel, "reason": "file_hash_error",
                           "error_type": type(exc).__name__, "message": str(exc)})
    missing_samples = sorted(required_samples - selected_names)
    if missing_samples:
        issues.append({"path": ".", "reason": "required_sample_missing", "names": missing_samples})
    for directory, before in directories:
        try:
            after = os.stat(directory, follow_symlinks=False)
            if (before.st_mtime_ns, getattr(before, "st_ino", None)) != (
                    after.st_mtime_ns, getattr(after, "st_ino", None)):
                rel = os.path.relpath(directory, root).replace(os.sep, "/")
                issues.append({"path": rel, "reason": "directory_changed_during_scan"})
        except OSError as exc:
            rel = os.path.relpath(directory, root).replace(os.sep, "/")
            issues.append({"path": rel, "reason": "directory_recheck_error",
                           "error_type": type(exc).__name__, "message": str(exc)})
    records.sort(key=lambda item: (item["path"].casefold(), item["path"]))
    canonical = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if json.loads(canonical.decode("utf-8")) != records:
        issues.append({"path": ".", "reason": "canonical_json_roundtrip_failed"})
    records_hash = sha256_bytes(canonical)
    return {
        "index": index,
        "host_folder": host,
        "sandbox_folder": guest,
        "read_only": readonly,
        "hash_mode": "full" if full else "metadata_only_with_selected_samples",
        "started_at": started,
        "completed_at": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "status": "PASS" if not issues else "BLOCKED",
        "records_count": len(records),
        "files": sum(1 for item in records if item["type"] == "file"),
        "directories": sum(1 for item in records if item["type"] == "directory"),
        "verified_files": sum(1 for item in records if item["sha256_status"] == "verified"),
        "not_computed_files": sum(1 for item in records if item["sha256_status"] == "not_computed"),
        "verified_bytes": hashed_bytes,
        "records_sha256": records_hash,
        "issues": issues,
        "_records": records,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--clone", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = os.path.abspath(args.output_dir)
    expected_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smoke-prestart-manifests-r2")
    if norm(output_dir) != norm(expected_output):
        raise RuntimeError("output directory is outside the fixed verification/P02 evidence path")
    config_bytes = open(args.config, "rb").read()
    actual_config_hash = sha256_bytes(config_bytes)
    if actual_config_hash != CONFIG_SHA256 or len(config_bytes) != 2609 or b"\r\n" in config_bytes:
        raise RuntimeError(f"r3 config bytes/hash mismatch: bytes={len(config_bytes)} sha256={actual_config_hash}")
    config = ET.fromstring(config_bytes)
    mappings = []
    for node in config.findall("./MappedFolders/MappedFolder"):
        host = node.findtext("HostFolder")
        guest = node.findtext("SandboxFolder")
        readonly = node.findtext("ReadOnly")
        if host is None or guest is None or readonly not in ("true", "false"):
            raise RuntimeError("invalid mapping entry in r3 XML")
        mappings.append((os.path.normpath(host), guest, readonly == "true"))
    expected_norm = [(os.path.normpath(h), g, ro) for h, g, ro in EXPECTED]
    if len(mappings) != 11 or [(norm(h), g.casefold(), ro) for h, g, ro in mappings] != [
            (norm(h), g.casefold(), ro) for h, g, ro in expected_norm]:
        raise RuntimeError("r3 XML HostFolder/SandboxFolder/ReadOnly set differs from the frozen 11 mappings")
    if config.findtext("ProtectedClient") != "Enable" or config.findtext("Networking") != "Disabled" or config.findtext("MemoryInMB") != "2048":
        raise RuntimeError("r3 XML protected-client/network/memory settings differ from the frozen config")
    if norm(args.clone) != norm(CLONE) or run_git(args.clone, "rev-parse", "HEAD") != PINNED_HEAD:
        raise RuntimeError("scratch clone does not match the fixed path/source HEAD")
    if run_git(args.clone, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("scratch clone porcelain is not empty before manifest capture")
    common = run_git(args.clone, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if norm(common) != norm(os.path.join(CLONE, ".git")):
        raise RuntimeError("scratch clone common Git directory is not private")
    alternates = os.path.join(CLONE, ".git", "objects", "info", "alternates")
    if os.path.exists(alternates) or run_git(args.clone, "remote", "-v"):
        raise RuntimeError("scratch clone has alternates or remotes")
    if run_git(args.clone, "config", "--get", "core.autocrlf").casefold() != "true":
        raise RuntimeError("scratch clone core.autocrlf is not true")
    if os.path.normcase(os.path.abspath(CLONE)) != norm(args.clone):
        raise RuntimeError("clone path mismatch")
    os.makedirs(output_dir, exist_ok=False)
    overall_started = datetime.now().astimezone().isoformat(timespec="milliseconds")
    results = []
    global_issues = []
    for index, (host, guest, readonly) in enumerate(mappings, 1):
        print(f"SCAN_START {index}/11 {host}", flush=True)
        result = scan_mapping(host, guest, readonly, index)
        records = result.pop("_records", [])
        name = ["scratch", "readonly-canary", "python-base", "python-venv", "detector-weights",
                "sfx-weights", "nodejs", "rust-toolchain", "vs-buildtools", "vs-installer", "windows-kits"][index - 1]
        records_path = os.path.join(output_dir, name + ".records.json")
        with open(records_path, "xb") as stream:
            stream.write(json.dumps(records, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8"))
        result["records_file"] = os.path.basename(records_path)
        global_issues.extend({"mapping_index": index, **issue} for issue in result["issues"])
        results.append(result)
        print(f"SCAN_DONE {index}/11 status={result['status']} entries={result['records_count']} "
              f"files={result['files']} dirs={result['directories']} "
              f"verified={result['verified_files']} issues={len(result['issues'])}", flush=True)
    summary = {
        "schema_version": 1,
        "started_at": overall_started,
        "completed_at": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "config_sha256": actual_config_hash,
        "config_bytes": len(config_bytes),
        "scratch_clone_head": run_git(args.clone, "rev-parse", "HEAD"),
        "scratch_clone_tree": run_git(args.clone, "rev-parse", "HEAD^{tree}"),
        "mapping_count": len(results),
        "writable_mapping_count": sum(1 for item in results if not item["read_only"]),
        "reparse_point_issue_count": sum(1 for issue in global_issues if issue.get("reason") == "reparse_point_not_followed"),
        "overall_status": "PASS" if not global_issues else "BLOCKED",
        "hashing_limit": "metadata-only roots bind path/type/size and only selected executable/sample content; unselected file bytes are not verified",
        "mappings": results,
        "issues": global_issues,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "xb") as stream:
        stream.write(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8"))
    print(json.dumps({"overall_status": summary["overall_status"], "mapping_count": len(results),
                      "issue_count": len(global_issues), "summary_path": summary_path}, ensure_ascii=False))
    return 0 if not global_issues else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"BLOCKED {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
