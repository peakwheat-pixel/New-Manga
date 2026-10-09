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


def synthetic_scan(host, guest, readonly, index, mismatch=False):
    baseline = summary["mappings"][index - 1]
    result = {key: baseline[key] for key in (
        "status", "records_count", "files", "directories", "verified_files",
        "not_computed_files", "records_sha256", "hash_mode")}
    result["issues"] = []
    if mismatch and index == 1:
        result["records_sha256"] = "0" * 64
    return result


for mismatch, expected in ((False, 0), (True, 2)):
    scanner.scan_mapping = lambda host, guest, readonly, index, mismatch=mismatch: synthetic_scan(
        host, guest, readonly, index, mismatch)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        actual = tool.recheck(scanner, summary, summary_sha)
    lines = output.getvalue().splitlines()
    result = json.loads(lines[-1])
    assert actual == expected
    assert result["result"] == ("PASS" if expected == 0 else "BLOCKED")
    assert result["mismatch_count"] == (0 if expected == 0 else 1)

tool_sha = hashlib.sha256(open(TOOL_PATH, "rb").read()).hexdigest()
print(f"RECHECK_SELFTEST=PASS matching=PASS mismatch=BLOCKED host_scan=NOT_RUN tool_sha256={tool_sha}")