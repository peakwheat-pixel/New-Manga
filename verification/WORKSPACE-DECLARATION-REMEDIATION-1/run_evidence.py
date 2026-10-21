# -*- coding: utf-8 -*-
"""Reproducible evidence for WORKSPACE-DECLARATION-REMEDIATION-1.

Runs (all read-only against the real repository except writing into this Task's
verification directory):

1. new AC2–AC5 fixtures;
2. the previous Task's 80-test regression suite (read-only, bytecode cached
   outside both evidence trees);
3. both incident replays;
4. the real-repository ``--audit-declarations`` after remediation;
5. report generation and the protection-delta check;
6. environment + SHA-256 manifest.

Exit 0 only when every gate is green.
"""
import hashlib
import io
import json
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAIN = r"G:\CODEX\New Manga"
WS = r"G:\CODEX\New Manga.workspace"
PYTHON = sys.executable
TOOLS = os.path.join(ROOT, "tools", "governance")
OLD_TESTS = os.path.join(ROOT, "verification",
                         "WORKSPACE-CLEANUP-TOOL-HARDENING-1", "tests")
LEDGER = os.path.join(ROOT, "verification", "WORKSPACE-CONSOLIDATION-1",
                      "incident-ledger-r208.json")
EVIDENCE = os.path.join(HERE, "evidence")
PYCACHE = os.path.join(WS, "temp", "WORKSPACE-DECL-REMEDIATION", "pycache")
if PYCACHE not in sys.path:
    pass

os.makedirs(EVIDENCE, exist_ok=True)
os.makedirs(PYCACHE, exist_ok=True)


def run(command, cwd, label, log_name):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPYCACHEPREFIX"] = PYCACHE
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env)
    output = (result.stdout or "") + (result.stderr or "")
    with io.open(os.path.join(EVIDENCE, log_name), "w", encoding="utf-8",
                 newline="\n") as handle:
        handle.write("COMMAND: %s\nCWD: %s\nEXIT_CODE: %d\n\n"
                     % (" ".join(command), cwd, result.returncode))
        handle.write(output)
    record = {"label": label, "command": command, "cwd": cwd,
              "exit_code": result.returncode, "log": log_name,
              "stdout_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest()}
    print("[%s] exit=%d (%.2fs)" % (label, result.returncode, 0.0))
    return record, result


def write_text(name, text):
    with io.open(os.path.join(HERE, name), "w", encoding="utf-8",
                 newline="\n") as handle:
        handle.write(text)


def main():
    runs = []
    failures = []
    new_tests = os.path.join(HERE, "tests")
    command = [PYTHON, "-B", "-m", "unittest", "test_declaration_remediation",
               "-v"]
    record, result = run(command, new_tests, "new-declaration-fixtures",
                         "new-tests.log")
    runs.append(record)
    if result.returncode != 0:
        failures.append("new-declaration-fixtures")
    with io.open(os.path.join(EVIDENCE, "new-tests.log"), encoding="utf-8") as handle:
        new_log = handle.read()
    write_text("tests.log", new_log)

    command = [PYTHON, "-B", "run_suite.py"]
    record, result = run(command, OLD_TESTS, "existing-80-tests",
                         "existing-tests.log")
    runs.append(record)
    if result.returncode != 0:
        failures.append("existing-80-tests")

    replay_reports = {}
    for script, report_name in (
            ("clean_workspace.py", "incident-replay-clean-workspace.json"),
            ("remove_worktrees.py", "incident-replay-remove-worktrees.json")):
        command = [PYTHON, "-B", os.path.join(TOOLS, script),
                   "--replay-incident", LEDGER, "--out", HERE]
        record, result = run(command, ROOT, "replay-" + script,
                             "incident-replay-%s.log" % script[:-3])
        runs.append(record)
        report_path = os.path.join(HERE, report_name)
        if result.returncode != 0 or not os.path.isfile(report_path):
            failures.append("replay-" + script)
            continue
        report = json.load(open(report_path, encoding="utf-8"))
        replay_reports[script] = {
            "candidates": report["totals"]["candidates"],
            "rejected": report["totals"]["rejected"],
            "deleted": report["totals"]["deleted"],
            "violations": report["totals"]["violations"],
            "sources_covering_roots": report["coverage"]["sources_covering_roots"],
        }
        if (report["totals"]["candidates"] != report["totals"]["rejected"]
                or report["totals"]["deleted"] != 0
                or report["totals"]["violations"] != 0
                or report["coverage"]["sources_covering_roots"] != 18):
            failures.append("replay-gate-" + script)

    audit_dir = os.path.join(EVIDENCE, "audit-after-run")
    command = [PYTHON, "-B", os.path.join(TOOLS, "clean_workspace.py"),
               "--repo", MAIN, "--workspace-root", WS,
               "--audit-declarations", "--out", audit_dir]
    record, result = run(command, ROOT, "audit-after-real-repo",
                         "audit-after.log")
    runs.append(record)
    audit_path = os.path.join(audit_dir, "declaration-audit.json")
    if result.returncode != 2 or not os.path.isfile(audit_path):
        failures.append("audit-after-real-repo")
    else:
        with open(audit_path, "rb") as source:
            data = source.read()
        with open(os.path.join(HERE, "audit-after.json"), "wb") as target:
            target.write(data)
        write_text("audit-after.exitcode", "%d\n" % result.returncode)
    # Frozen before-audit (generated before the parser changes).
    if not os.path.isfile(os.path.join(HERE, "audit-before.json")):
        failures.append("missing-audit-before")

    record, result = run([PYTHON, "-B", os.path.join(HERE, "build_reports.py")],
                         HERE, "build-reports", "build-reports.log")
    runs.append(record)
    if result.returncode != 0:
        failures.append("build-reports")

    record, result = run([PYTHON, "-B", os.path.join(HERE, "protection_delta.py")],
                         HERE, "protection-delta", "protection-delta.log")
    runs.append(record)
    if result.returncode != 0:
        failures.append("protection-delta")

    after = json.load(open(os.path.join(HERE, "audit-after.json"),
                           encoding="utf-8"))
    before = json.load(open(os.path.join(HERE, "audit-before.json"),
                            encoding="utf-8"))
    triage = json.load(open(os.path.join(EVIDENCE, "triage-summary.json"),
                            encoding="utf-8"))
    delta = json.load(open(os.path.join(EVIDENCE, "protection-delta.json"),
                           encoding="utf-8"))

    environment = {
        "schema_version": 1,
        "task_id": "WORKSPACE-DECLARATION-REMEDIATION-1",
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "host": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "python_executable": PYTHON,
            "git": subprocess.run(["git", "--version"], capture_output=True,
                                  text=True).stdout.strip(),
            "cwd": HERE,
        },
        "commands": runs,
        "audit": {
            "command": "clean_workspace.py --repo %s --workspace-root %s "
                       "--audit-declarations" % (MAIN, WS),
            "before": {"errors": len(before["errors"]),
                       "warnings": len(before.get("warnings", [])),
                       "declarations": before["counts"]["declarations"],
                       "protected_roots": before["counts"]["protected_roots"],
                       "exit_code": 2},
            "after": {"errors": len(after["errors"]),
                      "warnings": len(after.get("warnings", [])),
                      "declarations": after["counts"]["declarations"],
                      "protected_roots": after["counts"]["protected_roots"],
                      "exit_code": 2},
        },
        "triage": triage,
        "protection_delta": {"verdict": delta["verdict"],
                             "dropped": len(delta["dropped_declarations"]),
                             "old_roots": delta["old"]["protected_roots"],
                             "new_roots": delta["new"]["protected_roots"]},
        "replays": replay_reports,
        "failures": failures,
    }
    with io.open(os.path.join(EVIDENCE, "environment.json"), "w",
                 encoding="utf-8", newline="\n") as handle:
        json.dump(environment, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    files = []
    for base, _dirs, names in os.walk(HERE):
        for name in names:
            if name == "manifest.sha256":
                continue
            full = os.path.join(base, name)
            relative = os.path.relpath(full, HERE).replace("\\", "/")
            if relative.startswith("evidence/audit-after-run/"):
                continue
            files.append(relative)
    files.sort()
    lines = []
    for relative in files:
        full = os.path.join(HERE, relative.replace("/", os.sep))
        digest = hashlib.sha256(open(full, "rb").read()).hexdigest()
        lines.append("%s  %s" % (digest, relative))
    with io.open(os.path.join(EVIDENCE, "manifest.sha256"), "w",
                 encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")

    print("new tests: exit %d" % runs[0]["exit_code"])
    print("existing 80 tests: exit %d" % runs[1]["exit_code"])
    print("replays: %s" % json.dumps(replay_reports))
    print("audit after: errors=%d warnings=%d declarations=%d roots=%d"
          % (len(after["errors"]), len(after.get("warnings", [])),
             after["counts"]["declarations"],
             after["counts"]["protected_roots"]))
    print("protection delta:", delta["verdict"])
    print("evidence files:", len(files))
    if failures:
        print("FAILURES:", failures)
        return 1
    print("evidence-ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
