#!/usr/bin/env python3
"""Assert that the recheck gate accepts an identical synthetic scan and blocks a mismatch."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os

TOOL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "codex-smoke-prestart-manifest-check.py")
spec = importlib.util.spec_from_file_location("p02_manifest_check", TOOL_PATH)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
scanner = tool.load_scanner()
summary, summary_sha, _, _ = tool.validate_artifacts(scanner)
tool.verify_clone = lambda *_: None


def synthetic_scan(host, guest, readonly, index, mutation=None):
    baseline = summary["mappings"][index - 1]
    result = {key: baseline[key] for key in (
        "status", "records_count", "files", "directories", "verified_files",
        "not_computed_files", "records_sha256", "hash_mode")}
    result["issues"] = []
    if mutation and index == 1:
        if mutation == "records_sha256":
            result["records_sha256"] = "0" * 64
        elif mutation == "records_count":
            result["records_count"] += 1
        elif mutation == "status":
            result["status"] = "BLOCKED"
        elif mutation == "issues":
            result["issues"] = [{"reason": "synthetic_issue"}]
    return result


for mutation, expected in ((None, 0), ("records_sha256", 2), ("records_count", 2), ("status", 2), ("issues", 2)):
    scanner.scan_mapping = lambda host, guest, readonly, index, mutation=mutation: synthetic_scan(
        host, guest, readonly, index, mutation)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        actual = tool.recheck(scanner, summary, summary_sha)
    lines = output.getvalue().splitlines()
    result = json.loads(lines[-1])
    assert actual == expected
    assert result["result"] == ("PASS" if expected == 0 else "BLOCKED")
    assert result["mismatch_count"] == (0 if expected == 0 else 1)

with open(TOOL_PATH, "rb") as stream:
    tool_sha = hashlib.sha256(stream.read()).hexdigest()
print(f"RECHECK_SELFTEST=PASS matching=PASS hash_mismatch=BLOCKED count_mismatch=BLOCKED status_mismatch=BLOCKED issue_mismatch=BLOCKED host_scan=NOT_RUN tool_sha256={tool_sha}")
