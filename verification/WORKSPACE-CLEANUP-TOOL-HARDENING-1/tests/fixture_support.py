# -*- coding: utf-8 -*-
"""Shared fixtures for WORKSPACE-CLEANUP-TOOL-HARDENING-1 tests.

Every fixture lives under the system temporary directory.  The real workspace
(``G:/CODEX/New Manga`` / ``G:/CODEX/New Manga.workspace``) is never written by
these tests; the only real paths read are the tracked incident ledger used for
AC6 replay and the five tool scripts under test.

The fixture repository is a real ``git init`` repository because the hardened
tools refuse to trust anything but real Git results; ``git worktree add`` is used
to create worktrees, never ``--force``.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
TOOLS = os.path.join(ROOT, "tools", "governance")
LEDGER = os.path.join(ROOT, "verification", "WORKSPACE-CONSOLIDATION-1",
                      "incident-ledger-r208.json")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import clean_workspace as guard  # noqa: E402

SCRIPTS = ("clean_workspace.py", "remove_worktrees.py", "archive_branches.py",
           "delete_branches.py", "consolidate.py")

MANIFEST_HEADER = ("| resource_type | source_path | disposition | "
                   "destination_path | sha256/manifest | "
                   "reference/process check and result |")
MANIFEST_DELIMITER = "|---|---|---|---|---|---|"


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(moment):
    return moment.isoformat(timespec="seconds")


def run_tool(script, *args, cwd=None):
    """Run one hardened tool as a subprocess; returns CompletedProcess."""
    assert script in SCRIPTS, script
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, "-B", os.path.join(TOOLS, script)] + list(args)
    return subprocess.run(command, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          cwd=cwd or ROOT, env=env)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data):
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


class RepoFixture(object):
    """Isolated repository + workspace + output directory under %TEMP%."""

    def __init__(self, prefix="wc-hardening-"):
        self.tmp = tempfile.mkdtemp(prefix=prefix)
        self.repo = os.path.join(self.tmp, "repo")
        self.ws = os.path.join(self.tmp, "New Manga.workspace")
        self.out = os.path.join(self.tmp, "out")
        os.makedirs(self.repo)
        os.makedirs(self.ws)
        os.makedirs(self.out)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "fixture")
        self.write(".gitignore", "node_modules/\nignored.bin\n.cache/\n")
        self.write("README.md", "# fixture\n")
        self.commit("fixture base")

    # -- git ---------------------------------------------------------------
    def git(self, *args, **kwargs):
        check = kwargs.pop("check", True)
        cwd = kwargs.pop("cwd", self.repo)
        assert not kwargs, kwargs
        result = subprocess.run(["git", "-C", cwd] + list(args),
                                capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if check and result.returncode != 0:
            raise AssertionError("fixture git %r failed: %s"
                                 % (args, (result.stderr or result.stdout)))
        return result

    def commit(self, message="fixture commit"):
        self.git("add", "-A")
        result = self.git("commit", "-q", "-m", message, check=False)
        if result.returncode not in (0,):
            raise AssertionError("fixture commit failed: %s" % result.stderr)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.strip()

    # -- files -------------------------------------------------------------
    def write(self, relative, text):
        path = os.path.join(self.repo, *relative.split("/"))
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return path

    def write_abs(self, path, text):
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return path

    def declare(self, rows, relative="doc/tasks/FIXTURE-RESOURCES.md",
                commit=True):
        """Write a standard Resource Manifest table and track it.

        ``rows`` is a list of ``(source_path, disposition[, destination])``.
        """
        lines = ["# Fixture resource declarations", "",
                 "## Resource Manifest", "", MANIFEST_HEADER, MANIFEST_DELIMITER]
        for row in rows:
            source, disposition = row[0], row[1]
            destination = row[2] if len(row) > 2 else "-"
            lines.append("| fixture | %s | %s | %s | - | fixture |"
                         % (source, disposition, destination))
        lines += ["", "## Canonical Evidence", "",
                  "| evidence_id | AC/Gate | path | commit | sha256 | class |",
                  "|---|---|---|---|---|---|",
                  "| F1 | AC1 | `README.md` | `%s` | `%s` | `CANONICAL` |"
                  % (self.head()[:9], guard.sha256_file(
                      os.path.join(self.repo, "README.md"))),
                  ""]
        path = self.write(relative, "\n".join(lines))
        if commit:
            self.commit("fixture declarations")
        return path

    def declare_raw(self, text, relative="doc/tasks/FIXTURE-RESOURCES.md",
                    commit=True):
        path = self.write(relative, text)
        if commit:
            self.commit("fixture raw declarations")
        return path

    # -- workspace ---------------------------------------------------------
    def candidate(self, area, name, files=None):
        path = os.path.join(self.ws, area, name)
        os.makedirs(path, exist_ok=True)
        for relative, content in (files or {}).items():
            full = os.path.join(path, *relative.split("/"))
            parent = os.path.dirname(full)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
        return path

    def make_worktree(self, name, branch, location="worktrees"):
        parent = os.path.join(self.ws, *location.split("/"))
        os.makedirs(parent, exist_ok=True)
        path = os.path.join(parent, name)
        self.git("worktree", "add", "-q", path, "-b", branch)
        return path

    def write_inventory(self, worktrees, protected_names=None,
                        filename="inventory.json"):
        """Write an inventory JSON compatible with the hardened consumer."""
        entries = []
        for item in worktrees:
            entries.append({
                "path": item["path"],
                "branch": item.get("branch", ""),
                "head": item.get("head", ""),
                "exists": os.path.isdir(item["path"]),
                "dirty_entries": item.get("dirty_entries", 0),
                "stashes": item.get("stashes", 0),
                "protected": item.get("protected", []),
            })
        data = {
            "generated_at": "fixture",
            "mainline": "main",
            "counts": {"branches": 0, "merged": 0, "unmerged": 0,
                       "worktrees": len(entries), "protected_worktree_names":
                       len(protected_names or {})},
            "branches": [],
            "worktrees": entries,
            "protected_worktree_names": protected_names or {},
        }
        path = os.path.join(self.tmp, filename)
        write_json(path, data)
        return path

    def write_branches_inventory(self, branches, filename="branches-inventory.json"):
        data = {
            "generated_at": "fixture",
            "mainline": "main",
            "counts": {"branches": len(branches)},
            "branches": branches,
            "worktrees": [],
            "protected_worktree_names": {},
        }
        path = os.path.join(self.tmp, filename)
        write_json(path, data)
        return path

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def make_release_window(path, tool, repo, ws, roots, candidates_sha256,
                        candidate_count, *, dry_run_report=None,
                        inventory_acceptance=None, start_delta_minutes=-5,
                        end_delta_minutes=60, created_at=None):
    """Build a valid release-window record for fixture apply tests."""
    now = created_at or utc_now()
    record = {
        "schema_version": 1,
        "task_id": "FIXTURE-HARDENING-CLI",
        "authorized_by": "unit-test",
        "authorization_ref": "verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests",
        "created_at": iso(now),
        "release_window": {
            "start": iso(now + datetime.timedelta(minutes=start_delta_minutes)),
            "end": iso(now + datetime.timedelta(minutes=end_delta_minutes)),
        },
        "tool": tool,
        "repo": repo,
        "workspace_root": ws,
        "roots": roots,
        "candidates_sha256": candidates_sha256,
        "candidate_count": candidate_count,
    }
    if dry_run_report is not None:
        record["dry_run_report"] = {"path": dry_run_report}
    if inventory_acceptance is not None:
        record["inventory_acceptance"] = inventory_acceptance
    write_json(path, record)
    return path


def acceptance_digest_from_report(report):
    """Reconstruct the AC3 acceptance digest from a dry-run report."""
    items = []
    for candidate in report["candidates"]:
        if candidate["decision"] != "CANDIDATE":
            continue
        inventory = candidate.get("inventory") or {}
        items.append({"candidate": candidate["normalized"],
                      "digest": inventory.get("digest"),
                      "counts": inventory.get("counts")})
    return guard.canonical_sha256(sorted(items, key=lambda item: item["candidate"]))


def acceptance_digest_from_worktree_report(report):
    items = []
    for candidate in report["worktrees"]:
        if candidate["decision"] != "CANDIDATE":
            continue
        inventory = candidate.get("inventory") or {}
        items.append({"candidate": candidate["normalized"],
                      "digest": inventory.get("digest"),
                      "counts": inventory.get("counts")})
    return guard.canonical_sha256(sorted(items, key=lambda item: item["candidate"]))


def snapshot_paths(paths):
    return {path: (os.path.lexists(path),
                   os.path.isdir(path) if os.path.lexists(path) else None)
            for path in paths}
