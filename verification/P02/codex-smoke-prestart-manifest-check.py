#!/usr/bin/env python3
"""Validate saved R2 artifacts or compare current mapped trees with that baseline."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCANNER_PATH = os.path.join(HERE, "codex-smoke-prestart-manifest-r2.py")
CONFIG_PATH = os.path.join(HERE, "codex-p02-wsb-smoke-config-r3.xml")
BASELINE_DIR = os.path.join(HERE, "smoke-prestart-manifests-r2")
PINNED_TREE = "ce8056b8ef4d2ebd11bb4754b206adf921a39e41"
EXPECTED_TOTALS = {"records": 204419, "verified_files": 50389, "full_hashed_files": 50356, "sample_files": 33, "not_computed_files": 138947}
RECORD_KEYS = {"schema_version", "path", "type", "size_bytes", "sha256", "sha256_status"}


def load_scanner():
    spec = importlib.util.spec_from_file_location("p02_manifest_r2", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen R2 scanner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path):
    with open(path, "rb") as stream:
        return json.loads(stream.read().decode("utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def validate_artifacts(scanner):
    with open(CONFIG_PATH, "rb") as stream:
        config = stream.read()
    require(len(config) == 2609 and b"\r\n" not in config, "r3 config byte/EOL mismatch")
    require(sha256(config) == scanner.CONFIG_SHA256, "r3 config hash mismatch")
    xml_mappings = []
    root = ET.fromstring(config)
    for node in root.findall("./MappedFolders/MappedFolder"):
        host = node.findtext("HostFolder")
        guest = node.findtext("SandboxFolder")
        readonly = node.findtext("ReadOnly")
        require(host is not None and guest is not None and readonly in ("true", "false"), "invalid r3 mapping")
        xml_mappings.append((scanner.norm(host), guest.casefold(), readonly == "true"))
    expected = [(scanner.norm(host), guest.casefold(), readonly) for host, guest, readonly in scanner.EXPECTED]
    require(xml_mappings == expected and len(xml_mappings) == 11, "r3 XML differs from the fixed Smoke mappings")

    summary_path = os.path.join(BASELINE_DIR, "summary.json")
    with open(summary_path, "rb") as stream:
        summary_bytes = stream.read()
    summary = json.loads(summary_bytes.decode("utf-8"))
    require(summary["overall_status"] == "PASS" and summary["mapping_count"] == 11, "R2 summary is not PASS/11")
    require(summary["scratch_clone_head"] == scanner.PINNED_HEAD and summary["scratch_clone_tree"] == PINNED_TREE, "R2 scratch clone pin mismatch")
    require(summary["config_bytes"] == len(config) and summary["config_sha256"] == sha256(config), "summary config binding mismatch")
    require(not summary["issues"] and summary["writable_mapping_count"] == 1, "R2 summary has issues or wrong writable count")
    require([item["index"] for item in summary["mappings"]] == list(range(1, 12)), "mapping indices are not 1..11")

    totals = {"records": 0, "verified_files": 0, "full_hashed_files": 0, "sample_files": 0, "not_computed_files": 0}
    names = ["scratch", "readonly-canary", "python-base", "python-venv", "detector-weights", "sfx-weights",
             "nodejs", "rust-toolchain", "vs-buildtools", "vs-installer", "windows-kits"]
    for index, (mapping, fixed) in enumerate(zip(summary["mappings"], scanner.EXPECTED), 1):
        host, guest, readonly = fixed
        require(mapping["index"] == index and os.path.normcase(mapping["host_folder"]) == os.path.normcase(host),
                f"mapping {index} host path mismatch")
        require(mapping["sandbox_folder"].casefold() == guest.casefold() and mapping["read_only"] is readonly,
                f"mapping {index} guest/read-only mismatch")
        require(mapping["status"] == "PASS" and not mapping["issues"], f"mapping {index} is not PASS")
        expected_file = names[index - 1] + ".records.json"
        require(mapping["records_file"] == expected_file, f"mapping {index} records filename mismatch")
        path = os.path.join(BASELINE_DIR, expected_file)
        with open(path, "rb") as stream:
            raw = stream.read()
        require(sha256(raw) == mapping["records_sha256"], f"mapping {index} records SHA-256 mismatch")
        records = json.loads(raw.decode("utf-8"))
        require(len(records) == mapping["records_count"], f"mapping {index} record count mismatch")
        require(json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") == raw,
                f"mapping {index} records are not canonical bytes")
        keys = [(item["path"].casefold(), item["path"]) for item in records]
        require(keys == sorted(keys), f"mapping {index} paths are not sorted")
        folded = [item["path"].casefold() for item in records]
        require(len(folded) == len(set(folded)), f"mapping {index} has a case-fold path collision")
        for item in records:
            require(set(item) == RECORD_KEYS and item["schema_version"] == 1, f"mapping {index} record schema mismatch")
            if item["type"] == "directory":
                require(item["size_bytes"] is None and item["sha256"] is None and item["sha256_status"] == "not_applicable",
                        f"mapping {index} directory record mismatch")
            else:
                require(item["type"] == "file" and isinstance(item["size_bytes"], int) and item["size_bytes"] >= 0,
                        f"mapping {index} file record mismatch")
                if item["sha256_status"] == "verified":
                    require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"] or "") is not None,
                            f"mapping {index} verified hash malformed")
                else:
                    require(item["sha256_status"] == "not_computed" and item["sha256"] is None,
                            f"mapping {index} uncomputed hash mismatch")
        files = [item for item in records if item["type"] == "file"]
        directories = len(records) - len(files)
        verified = sum(item["sha256_status"] == "verified" for item in files)
        uncomputed = sum(item["sha256_status"] == "not_computed" for item in files)
        require(len(files) == mapping["files"] and directories == mapping["directories"], f"mapping {index} type counts mismatch")
        require(verified == mapping["verified_files"] and uncomputed == mapping["not_computed_files"],
                f"mapping {index} hash counts mismatch")
        totals["records"] += len(records)
        totals["verified_files"] += verified
        if mapping["hash_mode"] == "full":
            totals["full_hashed_files"] += verified
        else:
            totals["sample_files"] += verified
        totals["not_computed_files"] += uncomputed
    require(totals == EXPECTED_TOTALS, f"aggregate totals mismatch: {totals}")
    # The legacy summary field is not trusted; derive this count from observed issue records.
    reparse_issue_count = sum(issue.get("reason") == "reparse_point_not_followed"
                              for mapping in summary["mappings"] for issue in mapping["issues"])
    return summary, sha256(summary_bytes), totals, reparse_issue_count


def verify_clone(scanner, summary):
    clone = scanner.CLONE
    require(scanner.norm(clone) == scanner.norm(os.path.abspath(clone)), "fixed clone path normalization mismatch")
    require(scanner.run_git(clone, "rev-parse", "HEAD") == summary["scratch_clone_head"], "scratch clone HEAD changed")
    require(scanner.run_git(clone, "rev-parse", "HEAD^{tree}") == summary["scratch_clone_tree"], "scratch clone tree changed")
    require(not scanner.run_git(clone, "status", "--porcelain=v1", "--untracked-files=all"), "scratch clone is dirty")
    common = scanner.run_git(clone, "rev-parse", "--path-format=absolute", "--git-common-dir")
    require(scanner.norm(common) == scanner.norm(os.path.join(clone, ".git")), "scratch clone common Git directory is not private")
    require(not os.path.exists(os.path.join(clone, ".git", "objects", "info", "alternates")), "scratch clone has alternates")
    require(not scanner.run_git(clone, "remote", "-v"), "scratch clone has remotes")
    require(scanner.run_git(clone, "config", "--get", "core.autocrlf").casefold() == "true", "scratch clone core.autocrlf mismatch")


def recheck(scanner, summary, summary_sha):
    verify_clone(scanner, summary)
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    print(f"RECHECK_START at={started} baseline_summary_sha256={summary_sha}", flush=True)
    mismatches = []
    mapping_results = []
    for index, (host, guest, readonly) in enumerate(scanner.EXPECTED, 1):
        print(f"SCAN_START {index}/11 {host}", flush=True)
        current = scanner.scan_mapping(host, guest, readonly, index)
        current.pop("_records", None)
        expected = summary["mappings"][index - 1]
        fields = ("status", "records_count", "files", "directories", "verified_files", "not_computed_files", "records_sha256", "hash_mode")
        mismatch_start = len(mismatches)
        for field in fields:
            if current.get(field) != expected.get(field):
                mismatches.append({"mapping_index": index, "field": field,
                                   "expected": expected.get(field), "actual": current.get(field)})
        if current.get("issues"):
            mismatches.extend({"mapping_index": index, **issue} for issue in current["issues"])
        mapping_results.append({"index": index, "host_folder": host, "status": current["status"],
                                "records_count": current["records_count"],
                                "records_sha256": current["records_sha256"],
                                "baseline_records_sha256": expected["records_sha256"],
                                "issue_count": len(current["issues"]),
                                "matches_baseline": len(mismatches) == mismatch_start})
        print(f"SCAN_DONE {index}/11 status={current['status']} entries={current['records_count']} "
              f"records_sha256={current['records_sha256']} baseline_sha256={expected['records_sha256']} "
              f"verified={current['verified_files']} not_computed={current['not_computed_files']} "
              f"issues={len(current['issues'])}", flush=True)
    completed = datetime.now().astimezone().isoformat(timespec="seconds")
    result = "PASS" if not mismatches else "BLOCKED"
    with open(__file__, "rb") as stream:
        tool_sha = sha256(stream.read())
    print(json.dumps({"result": result, "started_at": started, "completed_at": completed,
                      "tool_sha256": tool_sha,
                      "baseline_summary_sha256": summary_sha, "mapping_count": 11,
                      "mismatch_count": len(mismatches), "mismatches": mismatches,
                      "mappings": mapping_results}, ensure_ascii=False, sort_keys=True), flush=True)
    return 0 if not mismatches else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("validate", "recheck"))
    args = parser.parse_args()
    scanner = load_scanner()
    summary, summary_sha, totals, reparse_issue_count = validate_artifacts(scanner)
    with open(__file__, "rb") as stream:
        tool_sha = sha256(stream.read())
    print(json.dumps({"artifact_validation": "PASS", "validated_at": datetime.now().astimezone().isoformat(timespec="seconds"), "tool_sha256": tool_sha, "summary_sha256": summary_sha, "reparse_point_issue_count": reparse_issue_count, **totals},
                     ensure_ascii=False, sort_keys=True), flush=True)
    if args.operation == "validate":
        return 0
    return recheck(scanner, summary, summary_sha)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"BLOCKED {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        sys.exit(2)
