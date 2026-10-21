# -*- coding: utf-8 -*-
"""Phase C (hardened): release disk held by derived workspace areas.

HARDENING TASK: WORKSPACE-CLEANUP-TOOL-HARDENING-1.  The r208 incident destroyed
18 protected sources (15 deleted roots), including a preserved-root descendant
(``P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree``).  This rewrite repairs
the root causes and is fail-closed by construction.  It performs **no** deletion
unless ``--apply`` *and* a matching release-window record are supplied.

This module also hosts the shared fail-closed guard core used by the other four
consolidation tools (``remove_worktrees.py``, ``archive_branches.py``,
``delete_branches.py``, ``consolidate.py``).  A dedicated ``safety.py`` module
would be cleaner, but the frozen ``allowed_paths`` for this Task list exactly
these five files, so the core lives in the first tool that needed it.  The core
is import-safe: importing this module has no side effects and parses no argv.

PROTECTION RULES (AC1, frozen; mirrored by tests)
=================================================
1. Identity is a normalised absolute path: ``os.path.normpath`` + ``normcase``
   (case-insensitive on Windows) with forward slashes.  Relative paths are
   *never* resolved against the current directory: a bare or relative path for a
   declaration or a deletion candidate is a hard error.
2. A ``PRESERVE_*`` declaration is a protected ROOT.  A candidate is protected if
   it is the same path, a DESCENDANT of that root (any depth), or an ANCESTOR of
   it.  Ancestor protection exists because deleting a parent destroys a
   protected descendant just as surely as deleting the descendant itself.
   Comparison is by path component boundary: ``temp/P02-NEW-TIME-X`` does not
   protect ``temp/P02-NEW-TIME-X6``.
3. Shared/generalised declarations:
   - the SAME path declared by several Task files/JSON records is merged: the
     union of the declarations is used and protection is never weakened by
     de-duplication;
   - a declaration that is the workspace root, any managed area root below it,
     or an ancestor of the workspace root is a GENERALISED declaration.  It is
     rejected as an integrity error (fail closed) instead of silently blocking
     every cleanup forever or being ignored: an over-broad declaration needs an
     explicit ruling, and a typo must not be mistaken for one.
4. Any declaration that cannot be resolved to a normalised absolute path
   (wildcard, environment variable, ``..`` traversal, ambiguous relative path,
   empty/unparsable cell) is an integrity error.  When the declaration index has
   any integrity error the tools refuse to delete anything and report why -- they
   never silently count zero.
5. Unknown dispositions are integrity errors (fail closed).  ``MIGRATE`` and
   ``ARCHIVE`` are treated as protective while a destination cannot be proven,
   and every resolvable ``destination_path`` is protective as well.

AC3: a per-file ignored/untracked/unknown-origin inventory (relative path, size,
SHA-256, link target) is produced BEFORE any deletion.  No inventory => no apply.
Ignored content is NEVER assumed to be cache: a ``purpose_hint`` is informational
only and every non-empty inventory requires an explicit, hash-bound acceptance in
the release-window record.

AC5: default mode is dry-run.  Apply requires ``--apply`` plus a release-window
record whose ``candidates_sha256`` equals the freshly recomputed candidate set
(so apply cannot drift from the reviewed dry-run) and whose window contains
"now".

USAGE
=====
    python clean_workspace.py                       # dry run, report to stdout
    python clean_workspace.py --out <dir>           # write report + inventories
    python clean_workspace.py --apply --release-window <record.json> --out <dir>
    python clean_workspace.py --replay-incident <incident-ledger-r208.json> [--out <dir>]
    python clean_workspace.py --audit-declarations [--incident-ledger <json>] [--out <dir>]

There is no ``--force`` and no way to skip a protection check.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys

TOOL_ID = "clean_workspace.py"
SCHEMA_VERSION = 1

REPO_DEFAULT = r"G:\CODEX\New Manga"
WS_DEFAULT = r"G:\CODEX\New Manga.workspace"

# The four derived areas this tool owns.  ``worktrees`` and ``task-envs`` remain
# deliberately excluded (recovery points / detection venv).
ROOTS = (
    ("review-scratch", "review-scratch"),
    ("builds", "builds"),
    ("temp", "temp"),
    ("tmp", "tmp"),
)

# Frozen disposition vocabulary (same set check.ps1 accepts, minus the
# checker-only ALREADY_ABSENT which is also accepted as a non-protective state).
DISPOSITIONS = frozenset({
    "DELETE_SAFE", "MIGRATE", "ARCHIVE", "ALREADY_ABSENT", "NOT_APPLICABLE",
    "PRESERVE_REFERENCED", "PRESERVE_USER_DATA", "PRESERVE_UNKNOWN",
})
NON_PROTECTIVE = frozenset({"DELETE_SAFE", "NOT_APPLICABLE", "ALREADY_ABSENT"})
DISPOSITION_RE = re.compile(
    r"^(DELETE_SAFE|MIGRATE|ARCHIVE|ALREADY_ABSENT|NOT_APPLICABLE|PRESERVE_[A-Z0-9_]+)$")

# Managed area names below the workspace root.  A declaration that resolves to
# one of these roots (or above) is a generalised declaration (rule 3).
WORKSPACE_SUBDIRS = frozenset({
    "worktrees", "builds", "artifacts", "temp", "tmp", "review-scratch",
    "agent-output", "task-envs", "exchange", "archive", "datasets", "models",
    "test-materials", "data-registry",
})

GLOB_RE = re.compile(r"[*?\[\]]")
ENV_RE = re.compile(r"%[A-Za-z_][A-Za-z0-9_]*%|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?")
PLACEHOLDERS = frozenset({
    "", "-", "--", "—", "–", "n/a", "na", "none", "null", "todo", "pending",
    "待填写", "待定", "无",
})
# Informational only.  Being listed here NEVER authorises deletion (AC3).
PURPOSE_DIR_NAMES = frozenset({
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".venv", "venv", "dist", "build", "target", ".cache", ".next", ".turbo",
})

INVENTORY_MAX_FILES = 200000
INVENTORY_MAX_BYTES = 4 * 1024 * 1024 * 1024


# ---------------------------------------------------------------------------
# errors
# ---------------------------------------------------------------------------
class GuardError(Exception):
    """A fail-closed refusal.  ``code`` is machine readable, message is human."""

    def __init__(self, code, message):
        super().__init__("%s: %s" % (code, message))
        self.code = code
        self.message = message


def fail(code, message):
    raise GuardError(code, message)


# ---------------------------------------------------------------------------
# path identity (AC1)
# ---------------------------------------------------------------------------
def is_abs_path(raw):
    if not isinstance(raw, str):
        return False
    return bool(re.match(r"^(?:[A-Za-z]:[\\/]|\\\\|//)", raw.strip()))


def norm_abs(raw, what="path"):
    """Return the canonical identity of an absolute path.

    Never guesses: relative/bare paths, NUL bytes, drive-relative rooted paths
    and empty strings all raise ``GuardError``.
    """
    if not isinstance(raw, str) or not raw.strip():
        fail("PATH_EMPTY", "%s is empty; refusing to guess its identity" % what)
    text = raw.strip().strip('"').strip("'").strip()
    if not text:
        fail("PATH_EMPTY", "%s is empty after stripping quotes" % what)
    if "\x00" in text:
        fail("PATH_NUL", "%s contains a NUL byte" % what)
    if text.startswith(("/", "\\")) and not text.startswith(("//", "\\\\")):
        fail("PATH_AMBIGUOUS_DRIVE",
             "%s is drive-relative (%r); use a drive-letter or UNC path"
             % (what, text))
    if not is_abs_path(text):
        fail("PATH_NOT_ABSOLUTE",
             "%s is not an absolute path (%r); a bare/relative path has no "
             "provable identity and is refused" % (what, text))
    normalised = os.path.normcase(os.path.normpath(text)).replace("\\", "/")
    return normalised


class Identity(object):
    __slots__ = ("raw", "normalised", "real", "is_alias", "exists", "is_dir",
                 "is_link")

    def __init__(self, raw, normalised, real, is_alias, exists, is_dir, is_link):
        self.raw = raw
        self.normalised = normalised
        self.real = real
        self.is_alias = is_alias
        self.exists = exists
        self.is_dir = is_dir
        self.is_link = is_link


def resolve_identity(raw, what="path"):
    """Resolve a path and flag symlink/junction aliases (AC2)."""
    normalised = norm_abs(raw, what)
    text = raw.strip().strip('"').strip("'")
    lexists = os.path.lexists(text)
    is_link = False
    if lexists:
        try:
            is_link = os.path.islink(text)
            if hasattr(os.path, "isjunction"):
                is_link = is_link or os.path.isjunction(text)
        except OSError:
            is_link = True
    try:
        real = os.path.normcase(os.path.realpath(text)).replace("\\", "/")
    except OSError:
        real = normalised
    is_alias = real != normalised
    return Identity(
        raw=text,
        normalised=normalised,
        real=real,
        is_alias=is_alias,
        exists=os.path.exists(text),
        is_dir=os.path.isdir(text) if lexists else False,
        is_link=is_link,
    )


def path_relation(a, b):
    """Component-boundary relation between two normalised paths.

    Returns one of ``same``, ``descendant`` (a inside b), ``ancestor`` (b inside
    a), ``disjoint``.  String prefixes that are not directory boundaries are
    deliberately NOT related.
    """
    if a == b:
        return "same"
    a_prefix = a if a.endswith("/") else a + "/"
    b_prefix = b if b.endswith("/") else b + "/"
    if a.startswith(b_prefix):
        return "descendant"
    if b.startswith(a_prefix):
        return "ancestor"
    return "disjoint"


def ensure_within(child, root, what="candidate"):
    """Fail closed unless ``child`` equals or is inside ``root`` (AC2 escape)."""
    rel = path_relation(child, root)
    if rel == "disjoint":
        fail("PATH_ESCAPE",
             "%s %s is outside the managed root %s" % (what, child, root))
    return rel


def require_plain_identity(raw, what, must_exist=False, allow_file=False):
    """Identity that must not be a symlink/junction alias (AC2)."""
    ident = resolve_identity(raw, what)
    if ident.is_alias:
        fail("PATH_ALIAS",
             "%s %r resolves through a symlink/junction to %s; alias paths are "
             "refused because what would be deleted cannot be proven"
             % (what, ident.raw, ident.real))
    if must_exist and not ident.exists:
        fail("PATH_MISSING", "%s %r does not exist" % (what, ident.raw))
    if ident.exists and not ident.is_dir and not allow_file:
        fail("PATH_NOT_DIRECTORY", "%s %r is not a directory" % (what, ident.raw))
    return ident


# ---------------------------------------------------------------------------
# files, JSON, digests
# ---------------------------------------------------------------------------
def sha256_file(path):
    digest = hashlib.sha256()
    try:
        with io.open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except PermissionError as exc:
        fail("PERMISSION_DENIED", "cannot read %s: %s" % (path, exc))
    except OSError as exc:
        fail("IO_READ_FAILED", "cannot read %s: %s" % (path, exc))
    return digest.hexdigest()


def file_size(path):
    try:
        return os.path.getsize(path)
    except PermissionError as exc:
        fail("PERMISSION_DENIED", "cannot stat %s: %s" % (path, exc))
    except OSError as exc:
        fail("IO_STAT_FAILED", "cannot stat %s: %s" % (path, exc))


def read_text(path, what="file"):
    try:
        with io.open(path, "r", encoding="utf-8", errors="strict") as handle:
            return handle.read().replace("\r\n", "\n")
    except PermissionError as exc:
        fail("PERMISSION_DENIED", "cannot read %s %s: %s" % (what, path, exc))
    except OSError as exc:
        fail("IO_READ_FAILED", "cannot read %s %s: %s" % (what, path, exc))
    except UnicodeDecodeError as exc:
        fail("IO_DECODE_FAILED", "%s %s is not valid UTF-8: %s" % (what, path, exc))


def load_json(path, what="JSON file"):
    text = read_text(path, what)
    try:
        return json.loads(text)
    except ValueError as exc:
        fail("JSON_PARSE", "%s %s is not valid JSON: %s" % (what, path, exc))


def canonical_bytes(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def canonical_sha256(obj):
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def write_json_atomic(path, obj):
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        try:
            os.makedirs(parent, exist_ok=True)
        except OSError as exc:
            fail("OUT_CREATE_FAILED", "cannot create output directory %s: %s"
                 % (parent, exc))
    tmp = path + ".tmp-%d" % os.getpid()
    try:
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(obj, ensure_ascii=False, indent=2))
            handle.write("\n")
        os.replace(tmp, path)
    except OSError as exc:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        fail("OUT_WRITE_FAILED", "cannot write %s: %s" % (path, exc))


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(
        timespec="seconds")


def parse_iso8601(text, what):
    if not isinstance(text, str) or not text.strip():
        fail("WINDOW_INVALID", "%s is missing/empty" % what)
    try:
        value = datetime.datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        fail("WINDOW_INVALID", "%s is not ISO-8601: %r (%s)" % (what, text, exc))
    if value.tzinfo is None:
        fail("WINDOW_INVALID", "%s has no timezone offset; local naive times are "
             "ambiguous" % what)
    return value


def candidates_digest(paths):
    """Deterministic digest of a candidate SET (paths only, AC5)."""
    return canonical_sha256(sorted(set(paths)))


# ---------------------------------------------------------------------------
# git helpers: every relevant call checks the exit code (AC2 -- the old
# ``git() -> ""`` silently treated failure as "empty result")
# ---------------------------------------------------------------------------
def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def git_checked(repo, *args, **kwargs):
    what = kwargs.pop("what", "git command")
    assert not kwargs, kwargs
    result = git(repo, *args)
    if result.returncode != 0:
        fail("GIT_CMD_FAILED", "%s failed (exit %d) in %s: %s"
             % (what, result.returncode, repo,
                (result.stderr or result.stdout or "").strip()[:240]))
    return result.stdout or ""


def parse_worktree_list(text):
    """Strict parse of ``git worktree list --porcelain`` (AC2)."""
    entries = []
    current = None
    for raw_line in text.split("\n"):
        line = raw_line.rstrip("\r")
        if not line.strip():
            continue
        if line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": line[len("worktree "):],
                       "head": None, "branch": None, "locked": False,
                       "bare": False, "detached": False}
            continue
        if current is None:
            fail("GIT_PARSE", "worktree list begins with %r" % line)
        if line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):].strip()
        elif line.startswith("branch "):
            ref = line[len("branch "):].strip()
            current["branch"] = (ref[len("refs/heads/"):]
                                 if ref.startswith("refs/heads/") else ref)
        elif line == "detached":
            current["detached"] = True
        elif line == "bare":
            current["bare"] = True
        elif line == "locked":
            current["locked"] = True
        elif line.startswith("locked "):
            current["locked"] = True
        elif line.startswith("prunable"):
            current["prunable"] = True
        else:
            fail("GIT_PARSE", "unexpected worktree list line: %r" % line)
    if current:
        entries.append(current)
    for entry in entries:
        if not is_abs_path(entry["path"]):
            fail("GIT_PARSE", "worktree path is not absolute: %r" % entry["path"])
        entry["normalized"] = norm_abs(entry["path"], "worktree path")
        if entry["head"] is not None and not re.fullmatch(
                r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", entry["head"]):
            fail("GIT_PARSE", "worktree HEAD is not a full object id: %r"
                 % entry["head"])
    return entries


def list_worktrees(repo):
    return parse_worktree_list(
        git_checked(repo, "worktree", "list", "--porcelain",
                    what="git worktree list"))


def git_status_entries(path):
    out = git_checked(path, "status", "--porcelain",
                      what="git status --porcelain")
    return [line for line in out.split("\n") if line.strip()]


def git_stash_entries(path):
    out = git_checked(path, "stash", "list", what="git stash list")
    return [line for line in out.split("\n") if line.strip()]


def git_branch_tips(repo):
    out = git_checked(repo, "for-each-ref", "--format=%(refname:short) %(objectname)",
                      "refs/heads", what="git for-each-ref refs/heads")
    tips = {}
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.rsplit(" ", 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-fA-F]{40,64}", parts[1]):
            fail("GIT_PARSE", "unexpected for-each-ref line: %r" % line)
        tips[parts[0]] = parts[1]
    return tips


def git_is_ancestor(repo, ancestor, descendant):
    result = git(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    fail("GIT_CMD_FAILED", "git merge-base --is-ancestor exited %d: %s"
         % (result.returncode, (result.stderr or "").strip()[:200]))


# ---------------------------------------------------------------------------
# pre-delete inventory (AC3)
# ---------------------------------------------------------------------------
def _is_link(path):
    try:
        if os.path.islink(path):
            return True
        if hasattr(os.path, "isjunction") and os.path.isjunction(path):
            return True
    except OSError:
        return True
    return False


def _walk_files(root, relative=""):
    """Yield (relative_posix, absolute, kind) without following links."""
    entries = []
    try:
        with os.scandir(root) as iterator:
            for entry in iterator:
                entries.append(entry)
    except PermissionError as exc:
        fail("PERMISSION_DENIED", "cannot list %s: %s" % (root, exc))
    except OSError as exc:
        fail("IO_READ_FAILED", "cannot list %s: %s" % (root, exc))
    entries.sort(key=lambda item: os.path.normcase(item.name))
    for entry in entries:
        rel = relative + entry.name if not relative else relative + "/" + entry.name
        try:
            if _is_link(entry.path):
                yield rel, entry.path, "link"
            elif entry.is_dir(follow_symlinks=False):
                for item in _walk_files(entry.path, rel):
                    yield item
            elif entry.is_file(follow_symlinks=False):
                yield rel, entry.path, "file"
            else:
                fail("INVENTORY_UNEXPECTED_ENTRY",
                     "%s is neither a regular file, directory nor link"
                     % entry.path)
        except PermissionError as exc:
            fail("PERMISSION_DENIED", "cannot inspect %s: %s" % (entry.path, exc))


def _inventory_entry(rel, absolute, origin, kind):
    entry = {"path": rel, "origin": origin, "type": kind,
             "size": 0, "sha256": None, "link_target": None}
    if kind == "link":
        try:
            entry["link_target"] = os.readlink(absolute)
        except OSError:
            entry["link_target"] = "(unreadable)"
    else:
        entry["size"] = file_size(absolute)
        entry["sha256"] = sha256_file(absolute)
        head = rel.split("/")[0].lower()
        if head in PURPOSE_DIR_NAMES:
            # Informational hint only; never authorises deletion (AC3).
            entry["purpose_hint"] = head
    return entry


def _git_inventory(candidate, limits):
    """Ignored + untracked per-file inventory for a git worktree/directory."""
    top = git_checked(candidate, "rev-parse", "--show-toplevel",
                      what="git rev-parse --show-toplevel").strip()
    if not top:
        fail("GIT_CMD_FAILED", "git rev-parse --show-toplevel returned no path")
    if norm_abs(top, "worktree toplevel") != candidate:
        fail("IDENTITY_MISMATCH",
             "git toplevel %s does not equal the candidate %s" % (top, candidate))
    entries = []
    seen = set()

    def collect(args, origin):
        out = git_checked(candidate, "ls-files", "-z", *args,
                          what="git ls-files %s" % " ".join(args))
        for rel in out.split("\x00"):
            if not rel:
                continue
            rel = rel.replace("\\", "/")
            if rel.startswith("../") or rel == ".." or "/../" in rel:
                fail("INVENTORY_ESCAPE", "git listed a path outside the "
                     "candidate: %r" % rel)
            absolute = os.path.join(candidate.replace("/", os.sep),
                                    rel.replace("/", os.sep))
            normalised = norm_abs(absolute, "inventory file")
            if path_relation(normalised, candidate) == "disjoint":
                fail("INVENTORY_ESCAPE", "inventory path escapes candidate: %r"
                     % rel)
            if rel in seen:
                continue
            seen.add(rel)
            entries.append(_inventory_entry(rel, absolute, origin, "file"))

    collect(["--others", "--exclude-standard"], "git_untracked")
    collect(["--others", "--ignored", "--exclude-standard"], "git_ignored")
    entries.sort(key=lambda item: item["path"])
    return entries


def _plain_inventory(candidate):
    entries = []
    for rel, absolute, kind in _walk_files(candidate.replace("/", os.sep)):
        entries.append(_inventory_entry(rel, absolute, "non_git", kind))
    entries.sort(key=lambda item: item["path"])
    return entries


def build_inventory(candidate, git_worktree=False,
                    max_files=INVENTORY_MAX_FILES,
                    max_bytes=INVENTORY_MAX_BYTES):
    """Per-file ignored/untracked/unknown-origin inventory (AC3).

    Raises ``GuardError`` instead of silently skipping unreadable files: an
    incomplete inventory is never a licence to delete.
    """
    candidate_norm = norm_abs(candidate, "inventory candidate")
    if git_worktree:
        entries = _git_inventory(candidate_norm, {"files": max_files,
                                                  "bytes": max_bytes})
    else:
        if not os.path.isdir(candidate_norm.replace("/", os.sep)):
            fail("INVENTORY_NOT_DIRECTORY",
                 "candidate %r is not a directory" % candidate)
        entries = _plain_inventory(candidate_norm)
    total_bytes = sum(item["size"] for item in entries)
    if len(entries) > max_files:
        fail("INVENTORY_LIMIT", "candidate %s has %d files (limit %d); a complete "
             "inventory is required before any deletion"
             % (candidate, len(entries), max_files))
    if total_bytes > max_bytes:
        fail("INVENTORY_LIMIT", "candidate %s has %d bytes (limit %d); a complete "
             "inventory is required before any deletion"
             % (candidate, total_bytes, max_bytes))
    counts = {
        "files": sum(1 for item in entries if item["type"] == "file"),
        "links": sum(1 for item in entries if item["type"] == "link"),
        "bytes": total_bytes,
        "git_ignored": sum(1 for item in entries if item["origin"] == "git_ignored"),
        "git_untracked": sum(1 for item in entries
                             if item["origin"] == "git_untracked"),
        "non_git": sum(1 for item in entries if item["origin"] == "non_git"),
    }
    body = {
        "candidate": candidate_norm,
        "entries": entries,
        "counts": counts,
        "limits": {"max_files": max_files, "max_bytes": max_bytes},
    }
    body["digest"] = canonical_sha256(body)
    return body


def inventory_requires_acceptance(inventory):
    """True when there is any content whose purpose is not proven by git."""
    counts = inventory["counts"]
    return bool(counts["git_ignored"] or counts["git_untracked"]
                or counts["non_git"] or counts["links"])


# ---------------------------------------------------------------------------
# declarations and protection index (AC1, AC2)
# ---------------------------------------------------------------------------
def clean_cell(cell):
    if not isinstance(cell, str):
        return ""
    text = cell.strip()
    text = text.replace("`", "").replace("**", "")
    return text.strip()


def _is_placeholder(text):
    return text.strip().lower() in PLACEHOLDERS


def is_path_like(text):
    """True when a cell/prose value uses path syntax (F-03 rule).

    Only path-like values must resolve; descriptive text without path syntax is
    allowed as a destination annotation (recorded as a warning, never as
    protection).  This keeps "destination = sentence" legal while refusing
    "destination = path-like but unresolvable".
    """
    if not isinstance(text, str):
        return False
    if re.search(r"[\\/]", text):
        return True
    if re.match(r"^[A-Za-z]:", text):
        return True
    if text.startswith((".", "~")):
        return True
    if ENV_RE.search(text):
        return True
    return False


class Declaration(object):
    __slots__ = ("raw", "disposition", "source_file", "locator", "normalized",
                 "real_normalized")

    def __init__(self, raw, disposition, source_file, locator, normalized,
                 real_normalized=None):
        self.raw = raw
        self.disposition = disposition
        self.source_file = source_file
        self.locator = locator
        self.normalized = normalized
        # Real target after resolving symlinks/junctions (F-01).  When it
        # differs, BOTH identities are registered as protection: a junction
        # declaration must protect what the junction actually points at.
        self.real_normalized = real_normalized or normalized


def resolve_real_target(normalized, what):
    """Resolve a normalised path to its real target (junction/symlink aware)."""
    try:
        real = os.path.normcase(
            os.path.realpath(normalized.replace("/", os.sep))).replace("\\", "/")
    except OSError as exc:
        fail("REALPATH_FAILED", "cannot resolve the real target of %s %s: %s"
             % (what, normalized, exc))
    return real


def is_protective(disposition):
    return disposition not in NON_PROTECTIVE


class ProtectionIndex(object):
    """Union of protective declarations, keyed by normalised absolute path."""

    def __init__(self, repo_root=None, ws_root=None):
        self.repo_root = norm_abs(repo_root, "repo root") if repo_root else None
        self.ws_root = norm_abs(ws_root, "workspace root") if ws_root else None
        self.declarations = []
        self.protected = {}          # normalized -> [Declaration]
        self.non_protective = []
        self.errors = []             # [{"code", "message", "file", "locator"}]
        self.warnings = []
        self._repo_tops = None

    # -- bookkeeping --------------------------------------------------------
    def add_error(self, code, message, source_file=None, locator=None):
        self.errors.append({"code": code, "message": message,
                            "file": source_file, "locator": locator})

    def add_warning(self, code, message, source_file=None, locator=None):
        self.warnings.append({"code": code, "message": message,
                              "file": source_file, "locator": locator})

    def error_summary(self, limit=12):
        lines = []
        for item in self.errors[:limit]:
            location = item.get("file") or ""
            locator = item.get("locator") or ""
            if locator:
                location = "%s %s" % (location, locator)
            if location:
                location = " [%s]" % location.strip()
            lines.append("%s: %s%s" % (item["code"], item["message"], location))
        if len(self.errors) > limit:
            lines.append("... and %d more declaration errors"
                         % (len(self.errors) - limit))
        return lines

    def counts(self):
        by_disposition = {}
        for declaration in self.declarations:
            by_disposition[declaration.disposition] = \
                by_disposition.get(declaration.disposition, 0) + 1
        return {
            "declarations": len(self.declarations),
            "protected_roots": len(self.protected),
            "by_disposition": dict(sorted(by_disposition.items())),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
        }

    # -- resolution ---------------------------------------------------------
    def _repo_top_level(self):
        if self._repo_tops is None:
            if not self.repo_root:
                self._repo_tops = set()
            else:
                try:
                    self._repo_tops = {name.lower() for name in
                                       os.listdir(self.repo_root.replace("/", os.sep))}
                except OSError as exc:
                    fail("REPO_ROOT_UNREADABLE",
                         "cannot list repo root %s: %s" % (self.repo_root, exc))
        return self._repo_tops

    def resolve_declared_path(self, raw, source_file, locator):
        text = clean_cell(raw)
        if GLOB_RE.search(text):
            fail("DECL_GLOB", "declared path %r contains a glob wildcard" % text)
        if ENV_RE.search(text) or text.startswith("~"):
            fail("DECL_ENV", "declared path %r contains an environment variable "
                 "or shell home token" % text)
        if is_abs_path(text):
            return norm_abs(text, "declared path")
        relative = text.replace("\\", "/")
        if relative.startswith("../") or relative == ".." or "/../" in relative:
            fail("DECL_TRAVERSAL", "declared path %r traverses with '..'" % text)
        first = relative.split("/")[0].lower()
        if first in WORKSPACE_SUBDIRS:
            fail("DECL_RELATIVE_AMBIGUOUS",
                 "declared path %r looks workspace-relative; it may mean the "
                 "workspace root or the repository root and is refused" % text)
        if self.repo_root and first in self._repo_top_level():
            return norm_abs(os.path.join(self.repo_root.replace("/", os.sep),
                                         relative.replace("/", os.sep)),
                            "declared path")
        if "/" not in text and "\\" not in text and ":" not in text:
            # A bare name such as a worktree name is not an identity.
            fail("DECL_BARE_NAME",
                 "declared path %r is a bare name, not an absolute or resolvable "
                 "repo-relative path" % text)
        if not self.repo_root:
            fail("DECL_RELATIVE_NO_ROOT",
                 "declared path %r is relative but no repo root is configured"
                 % text)
        fail("DECL_RELATIVE_UNRESOLVED",
             "declared relative path %r is not an existing repo top-level "
             "entry; identity is ambiguous" % text)

    def _generalized(self, normalized):
        bases = []
        if self.ws_root:
            bases.append(self.ws_root)
            for name in sorted(WORKSPACE_SUBDIRS):
                bases.append(self.ws_root.rstrip("/") + "/" + name)
        for base in bases:
            if path_relation(normalized, base) in ("same", "ancestor"):
                return base
        return None

    def _register_protective(self, declaration):
        """Register a protective declaration under lexical and real identity."""
        self.declarations.append(declaration)
        keys = [declaration.normalized]
        if declaration.real_normalized != declaration.normalized:
            keys.append(declaration.real_normalized)
        for key in keys:
            self.protected.setdefault(key, []).append(declaration)

    def _declared_identity(self, text, source_file, locator):
        """Resolve a declaration to (lexical, real) normalised identities."""
        normalized = self.resolve_declared_path(text, source_file, locator)
        real = resolve_real_target(normalized, "declaration")
        for value in (normalized, real):
            generalized = self._generalized(value)
            if generalized:
                fail("DECL_GENERALIZED",
                     "declaration %r resolves to %s, which is the workspace root "
                     "or a managed area root (%s) or above; over-broad "
                     "declarations need an explicit ruling"
                     % (text, value, generalized))
        if real != normalized:
            self.add_warning(
                "DECL_ALIAS_REAL_TARGET",
                "declaration %r is reached through a symlink/junction; the real "
                "target %s is protected as well" % (text, real),
                source_file, locator)
        return normalized, real

    def add_declaration(self, raw, disposition, source_file, locator):
        text = clean_cell(raw)
        disp = clean_cell(disposition).upper()
        if _is_placeholder(text):
            if disp == "NOT_APPLICABLE":
                return None
            self.add_error("DECL_MISSING_SOURCE",
                           "resource row has placeholder source %r with "
                           "disposition %r" % (raw, disposition),
                           source_file, locator)
            return None
        if not disp:
            self.add_error("DECL_EMPTY_DISPOSITION",
                           "resource row for %r has no disposition; safety "
                           "cannot be determined" % text, source_file, locator)
            return None
        if not DISPOSITION_RE.match(disp):
            self.add_error("DECL_UNKNOWN_DISPOSITION",
                           "resource %r has unknown disposition %r"
                           % (text, disposition), source_file, locator)
            return None
        try:
            normalized, real = self._declared_identity(text, source_file, locator)
        except GuardError as exc:
            self.add_error(exc.code, exc.message, source_file, locator)
            return None
        declaration = Declaration(text, disp, source_file, locator, normalized,
                                  real)
        if is_protective(disp):
            self._register_protective(declaration)
        else:
            self.declarations.append(declaration)
            self.non_protective.append(declaration)
        return declaration

    def add_evidence_pin(self, raw, source_file, locator):
        text = clean_cell(raw)
        if _is_placeholder(text):
            return None
        try:
            normalized, real = self._declared_identity(text, source_file, locator)
        except GuardError as exc:
            self.add_error(exc.code, exc.message, source_file, locator)
            return None
        declaration = Declaration(text, "EVIDENCE_PIN", source_file, locator,
                                  normalized, real)
        self._register_protective(declaration)
        return declaration

    def add_destination(self, raw, source_file, locator):
        text = clean_cell(raw)
        if _is_placeholder(text):
            return None
        if not is_path_like(text):
            # Descriptive destination (e.g. "由管理员裁定").  Explicitly allowed
            # and recorded; it cannot declare protection because it is not a
            # path (F-03).
            self.add_warning("DECL_DESTINATION_PROSE",
                             "destination %r is descriptive text, not a path; "
                             "it is not protection" % text,
                             source_file, locator)
            return None
        try:
            normalized, real = self._declared_identity(text, source_file, locator)
        except GuardError as exc:
            # Path-like destination that cannot be resolved is an integrity
            # error, not a warning: its protection cannot be enumerated (F-03).
            self.add_error("DECL_DESTINATION_UNRESOLVED", exc.message,
                           source_file, locator)
            return None
        declaration = Declaration(text, "DESTINATION_PIN", source_file, locator,
                                  normalized, real)
        self._register_protective(declaration)
        return declaration

    # -- evaluation ---------------------------------------------------------
    def evaluate(self, candidate):
        """Return protection reasons for a normalised candidate path."""
        hits = []
        for root in sorted(self.protected):
            relation = path_relation(candidate, root)
            if relation == "disjoint":
                continue
            declarations = self.protected[root]
            sources = sorted({"%s%s" % (decl.source_file,
                                        " " + decl.locator if decl.locator else "")
                              for decl in declarations})
            dispositions = sorted({decl.disposition for decl in declarations})
            kind = {"same": "exact_source_path",
                    "descendant": "descendant_of_preserved_root",
                    "ancestor": "ancestor_of_preserved_source"}[relation]
            hits.append({
                "kind": kind,
                "root": root,
                "dispositions": dispositions,
                "sources": sources,
            })
        return hits

    def reasons(self, candidate):
        return [describe_hit(hit) for hit in self.evaluate(candidate)]

    def protected_worktree_names(self, worktrees_root):
        """Map worktree directory name -> declaration sources.

        Names keep the casing written by the declaration (the normalised key is
        lower-cased), so the inventory stays readable.  Only direct children of
        ``worktrees_root`` are mapped; a deeper path cannot be addressed as a
        worktree name and is protected by path only.
        """
        worktrees_root = norm_abs(worktrees_root, "worktrees root")
        names = {}
        for root in self.protected:
            if path_relation(root, worktrees_root) != "descendant":
                continue
            remainder = root[len(worktrees_root) + 1:]
            if not remainder or "/" in remainder:
                continue
            display = None
            for declaration in self.protected[root]:
                candidate = declaration.raw.replace("\\", "/").rstrip("/")
                base = candidate.rsplit("/", 1)[-1]
                if base and base.lower() == remainder:
                    display = base
                    break
            display = display or remainder
            names.setdefault(display, []).extend(
                "%s%s" % (declaration.source_file,
                          " " + declaration.locator if declaration.locator else "")
                for declaration in self.protected[root])
        return {name: sorted(set(sources))
                for name, sources in sorted(names.items())}

    def finalize(self):
        if self.errors:
            fail("DECLARATION_INTEGRITY",
                 "%d declaration integrity error(s); refusing to delete anything "
                 "until protection declarations can be trusted: %s"
                 % (len(self.errors), "; ".join(self.error_summary(6))))


def describe_hit(hit):
    dispositions = "/".join(hit["dispositions"])
    sources = ", ".join(hit["sources"][:2])
    if len(hit["sources"]) > 2:
        sources += ", +%d" % (len(hit["sources"]) - 2)
    return "%s:%s [%s] {%s}" % (hit["kind"], hit["root"], dispositions, sources)


# ---------------------------------------------------------------------------
# markdown / JSON declaration scanners
# ---------------------------------------------------------------------------
TABLE_DELIMITER_RE = re.compile(r"^:?-{3,}:?$")


def section_text(text, name):
    match = re.search(r"(?m)^##\s+" + re.escape(name) + r"\s*$", text)
    if not match:
        return ""
    rest = text[match.end():]
    following = re.search(r"(?m)^##\s", rest)
    return rest[:following.start()] if following else rest


def _split_table_row(line):
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def iter_table_blocks(text):
    """Yield ``(first_line_number, block_lines)`` for every pipe table."""
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        if not lines[index].strip().startswith("|"):
            index += 1
            continue
        start = index + 1
        block = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            block.append(lines[index])
            index += 1
        yield start, block


def parse_table_block(block, start):
    """Strictly parse one table block into ``(header, [(line, cells)])``.

    Called only for blocks whose header declares a protection-relevant schema
    (resource or evidence table).  Unrelated prose tables in the same section are
    not policed -- they cannot declare protection -- but a table that DOES claim
    the schema must be well-formed (AC2).
    """
    cells = [_split_table_row(line) for line in block]
    if len(cells) < 2 or cells[0] is None or cells[1] is None:
        fail("TABLE_INCOMPLETE", "table at line %d has no delimiter row" % start)
    header = cells[0]
    delimiter = cells[1]
    if len(header) != len(delimiter):
        fail("TABLE_HEADER_ARITY",
             "table at line %d header has %d columns but delimiter has %d"
             % (start, len(header), len(delimiter)))
    if not all(TABLE_DELIMITER_RE.match(cell) for cell in delimiter if cell):
        fail("TABLE_DELIMITER", "table at line %d has an invalid delimiter row"
             % start)
    rows = []
    for offset, row in enumerate(cells[2:]):
        if row is None:
            continue
        if len(row) != len(header):
            fail("TABLE_ROW_ARITY",
                 "table row at line %d has %d columns, header has %d; "
                 "non-standard tables cannot be trusted for protection"
                 % (start + 2 + offset, len(row), len(header)))
        rows.append((start + 2 + offset, row))
    return header, rows


def _find_column(header, *names):
    lowered = [cell.strip().lower() for cell in header]
    for name in names:
        if name in lowered:
            return lowered.index(name)
    return None


def _table_header(block):
    preview = _split_table_row(block[0]) if block else None
    return preview or []


def parse_markdown_declarations(index, text, source_file):
    manifest = section_text(text, "Resource Manifest")
    if manifest:
        for start, block in iter_table_blocks(manifest):
            header = _table_header(block)
            source_col = _find_column(header, "source_path", "源", "source")
            disposition_col = _find_column(header, "disposition", "处置")
            if source_col is None or disposition_col is None:
                continue  # not a resource table: no declaration semantics
            try:
                header, rows = parse_table_block(block, start)
            except GuardError as exc:
                index.add_error(exc.code, exc.message, source_file)
                continue
            destination_col = _find_column(header, "destination_path", "目标")
            for line_number, row in rows:
                locator = "line %d" % line_number
                index.add_declaration(row[source_col], row[disposition_col],
                                      source_file, locator)
                if destination_col is not None:
                    index.add_destination(row[destination_col], source_file,
                                          locator)

    evidence = section_text(text, "Canonical Evidence")
    if evidence:
        for start, block in iter_table_blocks(evidence):
            header = _table_header(block)
            path_col = _find_column(header, "path", "路径")
            if path_col is None or _find_column(header, "evidence_id") is None:
                continue  # not a canonical-evidence table
            try:
                header, rows = parse_table_block(block, start)
            except GuardError as exc:
                index.add_error(exc.code, exc.message, source_file)
                continue
            for line_number, row in rows:
                index.add_evidence_pin(row[path_col], source_file,
                                       "line %d" % line_number)


def _walk_json(node, callback, locator="$"):
    if isinstance(node, dict):
        callback(node, locator)
        for key in node:
            _walk_json(node[key], callback, "%s.%s" % (locator, key))
    elif isinstance(node, list):
        for position, item in enumerate(node):
            _walk_json(item, callback, "%s[%d]" % (locator, position))


def parse_json_declarations(index, data, source_file):
    def callback(node, locator):
        has_source = "source_path" in node
        disposition_key = None
        for candidate in ("disposition", "disposition_original"):
            if candidate in node:
                disposition_key = candidate
                break
        if has_source and disposition_key is not None:
            index.add_declaration(node["source_path"], node[disposition_key],
                                  source_file, locator + "." + disposition_key)
            if "destination_path" in node:
                index.add_destination(node["destination_path"], source_file,
                                      locator + ".destination_path")
        elif ("resource_type" in node and "path" in node
              and "disposition" in node):
            index.add_declaration(node["path"], node["disposition"], source_file,
                                  locator + ".path")
            if "destination_path" in node:
                index.add_destination(node["destination_path"], source_file,
                                      locator + ".destination_path")

    _walk_json(data, callback)


def scan_repo_declarations(repo_root, ws_root):
    """Build the protection index from ``doc/tasks/**`` and ``verification/**``.

    Read-only.  Both TRACKED files and non-ignored UNTRACKED ``.md``/``.json``
    files are scanned (F-02): a declaration that only exists as an untracked
    draft still names a protected resource, and silently ignoring it is exactly
    the r208 failure mode.  Untracked declarations that cannot be parsed are
    integrity errors, so apply is refused rather than run with incomplete
    protection.

    ``git ls-files`` failure is fatal (AC2).  ANY ``.json`` declaration file
    that cannot be parsed is an integrity error (``JSON_PARSE``) and refuses the
    whole run: protection cannot be enumerated from a file whose declarations
    may include protective MIGRATE/ARCHIVE rows.  Do NOT reintroduce a
    "PRESERVE marker present?" heuristic or a warning-and-continue path for
    unparsable JSON (see Review r2 F-02); there is no marker-based exemption.
    """
    index = ProtectionIndex(repo_root=repo_root, ws_root=ws_root)
    repo = index.repo_root
    tracked = git_checked(repo, "ls-files", "-z", "--", "doc/tasks",
                          "verification", what="git ls-files")
    untracked = git_checked(repo, "ls-files", "-z", "--others",
                            "--exclude-standard", "--", "doc/tasks",
                            "verification",
                            what="git ls-files --others --exclude-standard")
    tracked_files = {item for item in tracked.split("\x00") if item}
    untracked_files = {item for item in untracked.split("\x00") if item}
    files = sorted(tracked_files | untracked_files)
    scanned = {"markdown": 0, "json": 0, "unparsable_json": 0,
               "tracked_declaration_files": len(tracked_files),
               "untracked_declaration_files": len(untracked_files)}
    for relative in files:
        absolute = os.path.join(repo.replace("/", os.sep),
                                relative.replace("/", os.sep))
        source_kind = "tracked" if relative in tracked_files else "untracked"
        if relative.endswith(".md"):
            scanned["markdown"] += 1
            try:
                text = read_text(absolute, "%s markdown" % source_kind)
            except GuardError as exc:
                index.add_error("FILE_UNREADABLE", exc.message, relative)
                continue
            parse_markdown_declarations(index, text, relative)
        elif relative.endswith(".json"):
            scanned["json"] += 1
            try:
                data = load_json(absolute, "%s JSON" % source_kind)
            except GuardError as exc:
                scanned["unparsable_json"] += 1
                # F-02 (R2 Review): an unparsable JSON declaration file is ALWAYS
                # an integrity error.  Looking for the literal "PRESERVE" marker
                # missed MIGRATE/ARCHIVE declarations (also protective) and let
                # apply continue with incomplete protection.
                index.add_error(
                    "JSON_PARSE",
                    "unparsable %s JSON declaration file; protection cannot be "
                    "enumerated, so cleaning is refused: %s"
                    % (source_kind, exc.message), relative)
                continue
            parse_json_declarations(index, data, relative)
    scanned["declarations"] = len(index.declarations)
    scanned["errors"] = len(index.errors)
    scanned["warnings"] = len(index.warnings)
    return index, scanned


# ---------------------------------------------------------------------------
# incident replay (AC6)
# ---------------------------------------------------------------------------
LEDGER_TOOL_FIELDS = ("protected_sources", "removed_roots")


def load_incident_ledger(path):
    data = load_json(path, "incident ledger")
    if not isinstance(data, dict):
        fail("LEDGER_SCHEMA", "incident ledger root is not an object")
    for field in LEDGER_TOOL_FIELDS:
        if field not in data or not isinstance(data[field], list) or not data[field]:
            fail("LEDGER_SCHEMA", "incident ledger has no non-empty %r list" % field)
    sources = data["protected_sources"]
    for position, item in enumerate(sources):
        if not isinstance(item, dict):
            fail("LEDGER_SCHEMA", "protected_sources[%d] is not an object" % position)
        if not isinstance(item.get("id"), str) or not item["id"].strip():
            fail("LEDGER_SCHEMA", "protected_sources[%d] has no id" % position)
        if not isinstance(item.get("source_path"), str) or not item["source_path"].strip():
            fail("LEDGER_SCHEMA", "protected_sources[%d] has no source_path" % position)
        if not isinstance(item.get("disposition_original"), str):
            fail("LEDGER_SCHEMA",
                 "protected_sources[%d] has no disposition_original" % position)
    roots = data["removed_roots"]
    for position, item in enumerate(roots):
        if not isinstance(item, dict):
            fail("LEDGER_SCHEMA", "removed_roots[%d] is not an object" % position)
        if not isinstance(item.get("id"), str) or not item["id"].strip():
            fail("LEDGER_SCHEMA", "removed_roots[%d] has no id" % position)
        if not isinstance(item.get("path"), str) or not item["path"].strip():
            fail("LEDGER_SCHEMA", "removed_roots[%d] has no path" % position)
    return data


def build_incident_replay(ledger_path, ws_root=None, repo_root=None):
    """Replay the r208 ledger: every deleted root must be rejected (AC6).

    Protection comes from the ledger's own 18 ``protected_sources`` records; the
    15 ``removed_roots`` are the deletion candidates.  All decisions must be
    REJECT and the source->root coverage must be complete, otherwise the report
    records a violation and the caller exits non-zero.  No deletion code path is
    reachable from this mode.
    """
    ledger = load_incident_ledger(ledger_path)
    ledger_sha = sha256_file(ledger_path)
    index = ProtectionIndex(repo_root=repo_root, ws_root=ws_root)
    for position, source in enumerate(ledger["protected_sources"]):
        index.add_declaration(source["source_path"],
                              source["disposition_original"],
                              ledger_path.replace("\\", "/"),
                              "protected_sources[%d] (%s)"
                              % (position, source["id"]))
    index.finalize()

    decisions = []
    violations = []
    covered_sources = set()
    for position, root in enumerate(ledger["removed_roots"]):
        try:
            ident = resolve_identity(root["path"], "removed root")
        except GuardError as exc:
            violations.append({"id": root["id"], "path": root["path"],
                               "violation": exc.message})
            decisions.append({"id": root["id"], "path": root["path"],
                              "normalized": None, "decision": "VIOLATION",
                              "reasons": [exc.message]})
            continue
        hits = index.evaluate(ident.normalised)
        for hit in hits:
            for declaration in index.protected.get(hit["root"], []):
                if declaration.source_file == ledger_path.replace("\\", "/"):
                    for source in ledger["protected_sources"]:
                        if source["source_path"].strip() == declaration.raw.strip():
                            covered_sources.add(source["id"])
        reasons = [describe_hit(hit) for hit in hits]
        if not hits:
            violations.append({"id": root["id"], "path": root["path"],
                               "violation": "no protected source covers this "
                               "incident deleted root"})
            decision = "VIOLATION"
        else:
            decision = "REJECT"
        decisions.append({
            "id": root["id"],
            "path": root["path"],
            "normalized": ident.normalised,
            "decision": decision,
            "reasons": reasons,
        })
    for source in ledger["protected_sources"]:
        if source["id"] not in covered_sources:
            violations.append({"id": source["id"], "path": source["source_path"],
                               "violation": "protected source does not cover any "
                               "incident deleted root"})
    rejected = sum(1 for item in decisions if item["decision"] == "REJECT")
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": "incident_replay",
        "generated_at": now_iso(),
        "ledger": {
            "path": ledger_path.replace("\\", "/"),
            "sha256": ledger_sha,
            "ledger_id": ledger.get("ledger_id"),
            "ledger_sha256": ledger_sha,
        },
        "input_counts": {
            "protected_sources": len(ledger["protected_sources"]),
            "removed_roots": len(ledger["removed_roots"]),
        },
        "decisions": decisions,
        "coverage": {
            "sources_covering_roots": len(covered_sources),
            "sources_without_root": [source["id"] for source
                                     in ledger["protected_sources"]
                                     if source["id"] not in covered_sources],
        },
        "violations": violations,
        "totals": {
            "candidates": len(decisions),
            "rejected": rejected,
            "deleted": 0,
            "violations": len(violations),
        },
    }
    report["ok"] = (report["totals"]["violations"] == 0
                    and rejected == len(decisions)
                    and report["totals"]["deleted"] == 0)
    report["report_sha256"] = canonical_sha256(
        {key: value for key, value in report.items()
         if key not in ("generated_at", "report_sha256")})
    return report


# ---------------------------------------------------------------------------
# release-window record (AC5)
# ---------------------------------------------------------------------------
WINDOW_MAX_HOURS = 48


def verify_release_window(record_path, expected):
    """Validate an explicit release-window record before any mutation.

    ``expected`` carries ``tool``, ``repo``, ``workspace_root``, ``roots``,
    ``candidates_sha256`` and ``candidate_count``.  Any mismatch is fatal.
    """
    record = load_json(record_path, "release-window record")
    if not isinstance(record, dict):
        fail("WINDOW_INVALID", "release-window record is not an object")
    for key in ("schema_version", "task_id", "authorized_by", "authorization_ref",
                "created_at", "release_window", "tool", "candidates_sha256",
                "candidate_count", "roots"):
        if key not in record:
            fail("WINDOW_INVALID", "release-window record is missing %r" % key)
    if record["schema_version"] != 1:
        fail("WINDOW_INVALID", "release-window schema_version must be 1")
    for key in ("task_id", "authorized_by", "authorization_ref"):
        if not isinstance(record[key], str) or not record[key].strip():
            fail("WINDOW_INVALID", "release-window %r must be a non-empty string"
                 % key)
    parse_iso8601(record["created_at"], "created_at")
    window = record["release_window"]
    if not isinstance(window, dict) or "start" not in window or "end" not in window:
        fail("WINDOW_INVALID", "release_window must have start/end")
    start = parse_iso8601(window["start"], "release_window.start")
    end = parse_iso8601(window["end"], "release_window.end")
    if end < start:
        fail("WINDOW_INVALID", "release_window.end is before start")
    if (end - start) > datetime.timedelta(hours=WINDOW_MAX_HOURS):
        fail("WINDOW_INVALID", "release window is wider than %d hours"
             % WINDOW_MAX_HOURS)
    now = datetime.datetime.now(datetime.timezone.utc)
    if not (start <= now <= end):
        fail("WINDOW_CLOSED", "release window %s..%s does not contain now %s"
             % (start.isoformat(), end.isoformat(), now.isoformat()))
    if record["tool"] != expected["tool"]:
        fail("WINDOW_TOOL_MISMATCH", "record is for tool %r, not %r"
             % (record["tool"], expected["tool"]))
    if expected.get("repo") is not None:
        if norm_abs(record.get("repo") or "", "record repo") != expected["repo"]:
            fail("WINDOW_REPO_MISMATCH", "record repo does not match this run")
    if expected.get("workspace_root") is not None:
        if norm_abs(record.get("workspace_root") or "",
                    "record workspace_root") != expected["workspace_root"]:
            fail("WINDOW_WS_MISMATCH",
                 "record workspace_root does not match this run")
    record_roots = record["roots"]
    if not isinstance(record_roots, list) or not record_roots:
        fail("WINDOW_INVALID", "record roots must be a non-empty list")
    normalised_roots = sorted({norm_abs(item, "record root")
                               for item in record_roots})
    if normalised_roots != sorted(expected["roots"]):
        fail("WINDOW_ROOTS_MISMATCH",
             "record roots do not match the configured roots")
    digest = record["candidates_sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        fail("WINDOW_INVALID", "candidates_sha256 is not a SHA-256 hex digest")
    if digest != expected["candidates_sha256"]:
        fail("WINDOW_CANDIDATE_DRIFT",
             "the candidate set changed after the reviewed dry-run: record %s != "
             "current %s; rerun the dry-run and obtain a new release window"
             % (digest, expected["candidates_sha256"]))
    if record["candidate_count"] != expected["candidate_count"]:
        fail("WINDOW_CANDIDATE_DRIFT",
             "record candidate_count %r != current %r"
             % (record["candidate_count"], expected["candidate_count"]))
    dry_run = record.get("dry_run_report")
    if dry_run is not None:
        if not isinstance(dry_run, dict) or "path" not in dry_run:
            fail("WINDOW_INVALID", "dry_run_report must carry a path")
        parsed = load_json(dry_run["path"], "dry-run report referenced by record")
        if not isinstance(parsed, dict):
            fail("WINDOW_INVALID", "referenced dry-run report is not an object")
        if parsed.get("candidates_sha256") != expected["candidates_sha256"]:
            fail("WINDOW_CANDIDATE_DRIFT",
                 "referenced dry-run report has a different candidate digest")
        if "sha256" in dry_run:
            if sha256_file(dry_run["path"]) != dry_run["sha256"]:
                fail("WINDOW_DRYRUN_HASH",
                     "referenced dry-run report bytes do not match the pinned "
                     "sha256")
    return record


def verify_inventory_acceptance(record, inventories):
    """AC3: non-empty inventories need an explicit hash-bound acceptance."""
    requiring = [item for item in inventories
                 if inventory_requires_acceptance(item["inventory"])]
    if not requiring:
        return
    acceptance = record.get("inventory_acceptance")
    if not isinstance(acceptance, dict):
        fail("INVENTORY_ACCEPTANCE_MISSING",
             "%d candidate(s) carry ignored/untracked/unknown content; apply "
             "requires an explicit inventory_acceptance block"
             % len(requiring))
    if acceptance.get("reviewed") is not True:
        fail("INVENTORY_ACCEPTANCE_MISSING",
             "inventory_acceptance.reviewed must be true")
    for key in ("reviewer", "reference", "inventory_sha256"):
        if not isinstance(acceptance.get(key), str) or not acceptance[key].strip():
            fail("INVENTORY_ACCEPTANCE_MISSING",
                 "inventory_acceptance.%s must be a non-empty string" % key)
    digest = inventory_acceptance_digest(inventories)
    if acceptance["inventory_sha256"] != digest:
        fail("INVENTORY_ACCEPTANCE_MISMATCH",
             "inventory acceptance hash does not match the inventory that would "
             "be deleted; a stale review cannot authorise deletion")


def inventory_acceptance_digest(inventories):
    return canonical_sha256([
        {"candidate": item["inventory"]["candidate"],
         "digest": item["inventory"]["digest"],
         "counts": item["inventory"]["counts"]}
        for item in sorted(inventories, key=lambda value: value["inventory"]["candidate"])
    ])


# ---------------------------------------------------------------------------
# deletion (the only place that mutates the filesystem)
# ---------------------------------------------------------------------------
def delete_path(path):
    """Remove a file or directory tree.  Only reachable from apply mode."""
    import shutil
    normalised = norm_abs(path, "delete target")
    ident = resolve_identity(path, "delete target")
    if ident.is_alias:
        fail("PATH_ALIAS", "refusing to delete through an alias: %s" % path)
    try:
        if os.path.isdir(path) and not _is_link(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except PermissionError as exc:
        fail("PERMISSION_DENIED", "cannot delete %s: %s" % (path, exc))
    except OSError as exc:
        fail("DELETE_FAILED", "cannot delete %s: %s" % (path, exc))
    if os.path.lexists(path):
        fail("DELETE_FAILED", "%s still exists after deletion" % normalised)


def remove_worktree(repo, path):
    """``git worktree remove`` WITHOUT ``--force``; rc is returned to the caller."""
    result = git(repo, "worktree", "remove", path)
    return (result.returncode, result.stdout or "", result.stderr or "")


def ensure_out_outside_candidates(out_dir, candidates, what="--out"):
    """F-04: refuse an output directory that lives inside a deletion candidate.

    The pre-delete inventory/report is written before deletion, so an ``--out``
    inside (or aliasing into) a candidate would be deleted along with it and the
    inventory would disappear.  Compared lexically AND by real target so a
    junction cannot smuggle the output into a candidate.
    """
    if not out_dir:
        return
    out_ident = resolve_identity(out_dir, what)
    out_values = {out_ident.normalised, out_ident.real}
    for candidate in candidates:
        candidate_norm = norm_abs(candidate, "deletion candidate")
        candidate_real = resolve_real_target(candidate_norm, "deletion candidate")
        for out_value in out_values:
            for candidate_value in {candidate_norm, candidate_real}:
                relation = path_relation(out_value, candidate_value)
                if relation in ("same", "descendant"):
                    fail("OUT_INSIDE_CANDIDATE",
                         "%s %r is %s deletion candidate %s; the pre-delete "
                         "inventory/report would be deleted with the candidate"
                         % (what, out_dir,
                            "equal to" if relation == "same" else "inside",
                            candidate_value))


# ---------------------------------------------------------------------------
# reports / output
# ---------------------------------------------------------------------------
def _write_report(out_dir, filename, report):
    if not out_dir:
        return None
    target = os.path.join(out_dir, filename)
    write_json_atomic(target, report)
    return target.replace("\\", "/")


def _write_inventory(out_dir, candidate_norm, inventory):
    if not out_dir:
        return None
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", candidate_norm)
    safe = safe[-120:]
    target = os.path.join(out_dir, "inventory", safe + ".json")
    write_json_atomic(target, inventory)
    return target.replace("\\", "/")


def _emit(report, out_dir, filename, summary_lines):
    path = _write_report(out_dir, filename, report)
    for line in summary_lines:
        print(line)
    if path:
        print("  report: %s" % path)
    return path


def _print_reasons(prefix, reasons, limit=2):
    for reason in reasons[:limit]:
        print("    %s %s" % (prefix, reason))


# ---------------------------------------------------------------------------
# clean_workspace evaluation
# ---------------------------------------------------------------------------
def _declaration_audit_payload(index, scanned, ledger=None):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": "declaration_audit",
        "generated_at": now_iso(),
        "scan": scanned,
        "counts": index.counts(),
        "errors": index.errors,
        "warnings": index.warnings,
    }
    if ledger is not None:
        coverage = []
        for source in ledger["protected_sources"]:
            hits = index.evaluate(norm_abs(source["source_path"],
                                           "ledger source path"))
            coverage.append({
                "id": source["id"],
                "source_path": source["source_path"],
                "protected_by_repo_declarations": bool(hits),
                "hits": [describe_hit(hit) for hit in hits[:3]],
            })
        payload["incident_source_coverage"] = coverage
        payload["incident_sources_covered"] = sum(
            1 for item in coverage if item["protected_by_repo_declarations"])
        payload["incident_sources_total"] = len(coverage)
    payload["report_sha256"] = canonical_sha256(
        {key: value for key, value in payload.items()
         if key not in ("generated_at", "report_sha256")})
    return payload


def run_audit_declarations(config):
    repo = config["repo"]
    ws = config["ws"]
    index, scanned = scan_repo_declarations(repo, ws)
    ledger = None
    if config.get("incident_ledger"):
        ledger = load_incident_ledger(config["incident_ledger"])
    payload = _declaration_audit_payload(index, scanned, ledger)
    lines = [
        "declaration audit: %d declaration(s), %d protected root(s), %d error(s), "
        "%d warning(s)" % (payload["counts"]["declarations"],
                           payload["counts"]["protected_roots"],
                           payload["counts"]["errors"],
                           payload["counts"]["warnings"]),
    ]
    if ledger is not None:
        lines.append("  incident ledger sources protected by repo declarations: "
                     "%d/%d" % (payload["incident_sources_covered"],
                                payload["incident_sources_total"]))
    for error in payload["errors"][:10]:
        lines.append("  ERROR %s: %s [%s]" % (error["code"], error["message"],
                                              error.get("file") or ""))
    _emit(payload, config.get("out"), "declaration-audit.json", lines)
    return 0 if not index.errors else 2


def _build_candidates(config, index):
    """Return candidate records for the four managed roots, fail-closed."""
    ws = config["ws"]
    candidates = []
    skipped = []
    for label, relative in config["roots"]:
        root_norm = config["root_norm"][label]
        if not os.path.isdir(root_norm.replace("/", os.sep)):
            skipped.append({"area": label, "root": root_norm,
                            "why": "root absent"})
            continue
        try:
            names = sorted(os.listdir(root_norm.replace("/", os.sep)),
                           key=lambda value: os.path.normcase(value))
        except PermissionError as exc:
            fail("PERMISSION_DENIED", "cannot list root %s: %s" % (root_norm, exc))
        except OSError as exc:
            fail("IO_READ_FAILED", "cannot list root %s: %s" % (root_norm, exc))
        for name in names:
            raw = os.path.join(root_norm.replace("/", os.sep), name)
            try:
                ident = resolve_identity(raw, "candidate")
            except GuardError as exc:
                candidates.append({"area": label, "path": raw,
                                   "normalized": None, "decision": "REJECT",
                                   "reasons": [exc.message]})
                continue
            record = {
                "area": label,
                "path": ident.raw.replace("\\", "/"),
                "normalized": ident.normalised,
                "decision": "CANDIDATE",
                "reasons": [],
            }
            if ident.is_alias:
                record["decision"] = "REJECT"
                record["reasons"] = [
                    "PATH_ALIAS: %r resolves to %s; alias paths are refused"
                    % (ident.raw, ident.real)]
            elif not ident.exists:
                record["decision"] = "SKIP"
                record["reasons"] = ["candidate no longer exists"]
            else:
                hits = index.evaluate(ident.normalised)
                if hits:
                    record["decision"] = "REJECT"
                    record["reasons"] = [describe_hit(hit) for hit in hits]
            candidates.append(record)
    return candidates, skipped


def build_clean_report(config, index, scanned):
    candidates, skipped = _build_candidates(config, index)
    inventories = []
    for record in candidates:
        if record["decision"] != "CANDIDATE":
            continue
        try:
            inventory = build_inventory(record["normalized"],
                                        git_worktree=False)
        except GuardError as exc:
            record["decision"] = "REJECT"
            record["reasons"] = ["%s: %s" % (exc.code, exc.message)]
            continue
        inventories.append({"candidate": record["normalized"],
                            "inventory": inventory})
        record["bytes"] = inventory["counts"]["bytes"]
        record["inventory"] = {
            "digest": inventory["digest"],
            "counts": inventory["counts"],
            "requires_acceptance": inventory_requires_acceptance(inventory),
        }
    deletable = [record["normalized"] for record in candidates
                 if record["decision"] == "CANDIDATE"]
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": "dry_run",
        "generated_at": now_iso(),
        "repo_root": config["repo"],
        "workspace_root": config["ws"],
        "roots": [{"area": label, "normalized": config["root_norm"][label]}
                  for label, _ in config["roots"]],
        "declarations": index.counts(),
        "declaration_scan": scanned,
        "declaration_warnings": index.warnings,
        "candidates": candidates,
        "skipped_roots": skipped,
        "totals": {
            "candidates": len(candidates),
            "would_delete": len(deletable),
            "rejected": sum(1 for record in candidates
                            if record["decision"] == "REJECT"),
            "skipped": sum(1 for record in candidates
                           if record["decision"] == "SKIP"),
            "bytes": sum(record.get("bytes", 0) for record in candidates
                         if record["decision"] == "CANDIDATE"),
        },
        "candidates_sha256": candidates_digest(deletable),
        "candidate_count": len(deletable),
    }
    report["report_sha256"] = canonical_sha256(
        {key: value for key, value in report.items()
         if key not in ("generated_at", "report_sha256")})
    return report, inventories


def _write_inventories(config, inventories):
    written = []
    for item in inventories:
        target = _write_inventory(config.get("out"),
                                  item["candidate"], item["inventory"])
        if target:
            item["inventory_path"] = target
            written.append(target)
    return written


def run_clean_workspace(config):
    index, scanned = scan_repo_declarations(config["repo"], config["ws"])
    if index.errors:
        report = {
            "schema_version": SCHEMA_VERSION,
            "tool": TOOL_ID,
            "mode": "dry_run",
            "generated_at": now_iso(),
            "repo_root": config["repo"],
            "workspace_root": config["ws"],
            "declaration_integrity": "FAILED",
            "declaration_errors": index.errors[:50],
            "declaration_error_count": len(index.errors),
            "candidates": [],
            "totals": {"candidates": 0, "would_delete": 0, "rejected": 0,
                       "skipped": 0, "bytes": 0},
            "candidates_sha256": candidates_digest([]),
            "refused": "DECLARATION_INTEGRITY",
        }
        lines = ["REFUSE: %d declaration integrity error(s); no deletion is "
                 "possible until protection declarations can be trusted"
                 % len(index.errors)]
        for error in index.errors[:8]:
            lines.append("  ERROR %s: %s [%s]" % (error["code"], error["message"],
                                                  error.get("file") or ""))
        _emit(report, config.get("out"), "clean-workspace-refused.json", lines)
        return 2

    report, inventories = build_clean_report(config, index, scanned)
    report["mode"] = "apply" if config["apply"] else "dry_run"
    lines = ["%s: %d candidate(s), would delete %d, rejected %d, skipped %d, %.2f MB"
             % (report["mode"], report["totals"]["candidates"],
                report["totals"]["would_delete"], report["totals"]["rejected"],
                report["totals"]["skipped"],
                report["totals"]["bytes"] / 1048576.0)]
    for record in report["candidates"][:20]:
        label = os.path.basename(record["path"].rstrip("/\\"))
        print("    %-8s %-40s %s" % (record["decision"], label,
                                     record["reasons"][0] if record["reasons"] else ""))
    if not config["apply"]:
        _write_inventories(config, inventories)
        _emit(report, config.get("out"), "clean-workspace-dryrun.json", lines)
        return 0

    # ----- apply: explicit record + hash-bound inventory acceptance ---------
    expected = {
        "tool": TOOL_ID,
        "repo": config["repo"],
        "workspace_root": config["ws"],
        "roots": [config["root_norm"][label] for label, _ in config["roots"]],
        "candidates_sha256": report["candidates_sha256"],
        "candidate_count": report["candidate_count"],
    }
    record = verify_release_window(config["release_window"], expected)
    ensure_out_outside_candidates(
        config.get("out"),
        [item["normalized"] for item in report["candidates"]
         if item["decision"] == "CANDIDATE"],
        what="--out")
    _write_inventories(config, inventories)
    verify_inventory_acceptance(record, inventories)

    deleted = []
    refused = []
    for record_candidate in report["candidates"]:
        if record_candidate["decision"] != "CANDIDATE":
            continue
        try:
            delete_path(record_candidate["normalized"])
        except GuardError as exc:
            refused.append({"path": record_candidate["path"],
                            "code": exc.code, "why": exc.message})
            continue
        deleted.append({"path": record_candidate["path"],
                        "normalized": record_candidate["normalized"],
                        "bytes": record_candidate.get("bytes", 0)})
    report["mode"] = "apply"
    report["apply"] = {
        "release_window": {
            "task_id": record["task_id"],
            "authorized_by": record["authorized_by"],
            "authorization_ref": record["authorization_ref"],
            "release_window": record["release_window"],
        },
        "deleted": deleted,
        "refused": refused,
    }
    report["totals"]["deleted"] = len(deleted)
    report = {key: value for key, value in report.items()
              if key != "report_sha256"}
    report["report_sha256"] = canonical_sha256(
        {key: value for key, value in report.items() if key != "report_sha256"})
    lines.append("  deleted %d, refused %d" % (len(deleted), len(refused)))
    for item in refused[:8]:
        lines.append("    REFUSED %s %s" % (item["path"], item["why"]))
    _emit(report, config.get("out"), "clean-workspace-apply.json", lines)
    return 0 if not refused else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_config(args):
    repo = norm_abs(args.repo or REPO_DEFAULT, "repo")
    ws = norm_abs(args.workspace_root or WS_DEFAULT, "workspace root")
    root_norm = {}
    roots = []
    for label, relative in ROOTS:
        root_norm[label] = norm_abs(os.path.join(ws.replace("/", os.sep),
                                                 relative.replace("/", os.sep)),
                                    "root %s" % label)
        roots.append((label, relative))
    out = os.path.abspath(args.out) if args.out else None
    if out:
        out = os.path.normpath(out)
    return {
        "repo": repo,
        "ws": ws,
        "roots": tuple(roots),
        "root_norm": root_norm,
        "out": out,
        "apply": bool(args.apply),
        "release_window": args.release_window,
        "replay": args.replay_incident,
        "audit": bool(args.audit_declarations),
        "incident_ledger": args.incident_ledger,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Hardened Phase C: dry-run by default, explicit release "
                    "window required for apply.")
    parser.add_argument("--repo", help="repository root (default %s)" % REPO_DEFAULT)
    parser.add_argument("--workspace-root",
                        help="workspace root (default %s)" % WS_DEFAULT)
    parser.add_argument("--out", help="directory for JSON report/inventory output")
    parser.add_argument("--apply", action="store_true",
                        help="delete candidates; requires --release-window")
    parser.add_argument("--release-window",
                        help="release-window record JSON (required with --apply)")
    parser.add_argument("--replay-incident",
                        help="replay an incident ledger instead of scanning roots")
    parser.add_argument("--audit-declarations", action="store_true",
                        help="read-only declaration audit; never deletes")
    parser.add_argument("--incident-ledger",
                        help="incident ledger for --audit-declarations coverage")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = build_config(args)
    try:
        if config["replay"]:
            if config["apply"]:
                fail("REPLAY_APPLY_REFUSED",
                     "--replay-incident is a read-only proof; --apply is refused")
            report = build_incident_replay(config["replay"], ws_root=config["ws"],
                                           repo_root=None)
            lines = ["incident replay: %d root(s), rejected %d, deleted %d, "
                     "violations %d" % (report["totals"]["candidates"],
                                        report["totals"]["rejected"],
                                        report["totals"]["deleted"],
                                        report["totals"]["violations"])]
            for item in report["decisions"]:
                print("    %-9s %-6s %-70s %s"
                      % (item["decision"], item["id"],
                         item["path"][-70:],
                         item["reasons"][0] if item["reasons"] else ""))
            _emit(report, config["out"], "incident-replay-clean-workspace.json",
                  lines)
            return 0 if report["ok"] else 2
        if config["audit"]:
            return run_audit_declarations(config)
        if config["apply"] and not config["release_window"]:
            fail("APPLY_NEEDS_RELEASE_WINDOW",
                 "--apply requires an explicit --release-window record")
        if config["apply"] and not config["out"]:
            fail("APPLY_NEEDS_OUT",
                 "--apply requires --out so the pre-delete inventory is preserved")
        return run_clean_workspace(config)
    except GuardError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
