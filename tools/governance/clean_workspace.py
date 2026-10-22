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
import copy
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
# Repository that hosts THIS tool (may be a worktree while auditing another
# checkout); the non-declaration exception manifest is read from here.
TOOL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

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


def read_text(path, what="file", legacy_warn=None):
    try:
        with io.open(path, "rb") as handle:
            raw = handle.read()
    except PermissionError as exc:
        fail("PERMISSION_DENIED", "cannot read %s %s: %s" % (what, path, exc))
    except OSError as exc:
        fail("IO_READ_FAILED", "cannot read %s %s: %s" % (what, path, exc))
    # F-05 (review r2): reject binary payloads before any decoding.  A legacy
    # Chinese declaration note has no NUL bytes and almost no ASCII controls.
    if b"\x00" in raw:
        fail("FILE_UNREADABLE",
             "%s %s contains NUL bytes; refusing a binary file as text"
             % (what, path))
    # Review r3 F-05: the control-byte ratio applies to EVERY length.  A short
    # payload (e.g. 24 bytes, 20 control bytes, decodable GB18030 CJK) must be
    # rejected too, not just files >= 64 bytes.
    controls = sum(1 for byte in raw
                   if byte < 0x20 and byte not in (0x09, 0x0A, 0x0D))
    if controls and controls * 100 > len(raw):
        fail("FILE_UNREADABLE",
             "%s %s has %.2f%% control bytes; refusing a binary file as text"
             % (what, path, controls * 100.0 / len(raw)))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        # AC4 (WORKSPACE-DECLARATION-REMEDIATION-1): legacy P02/P04 notes are
        # GB18030.  A strict fallback keeps fail-closed behaviour (no
        # replacement characters can silently corrupt a declaration) while
        # still reading the file; the caller records FILE_ENCODING_LEGACY.
        # Review r2 F-05: the fallback must not accept arbitrary binary.  It is
        # limited to payloads that decode to actual CJK text.
        try:
            text = raw.decode("gb18030")
        except UnicodeDecodeError as exc:
            fail("FILE_UNREADABLE",
                 "%s %s is neither valid UTF-8 nor valid GB18030: %s"
                 % (what, path, exc))
        if not CJK_RE.search(text):
            fail("FILE_UNREADABLE",
                 "%s %s decodes as GB18030 but contains no CJK text; refusing "
                 "it as a legacy declaration note" % (what, path))
        if legacy_warn is not None:
            legacy_warn("FILE_ENCODING_LEGACY",
                        "%s %s is not valid UTF-8; decoded as GB18030 (legacy "
                        "history, bytes preserved)" % (what, path))
    return text.replace("\r\n", "\n")


def load_json(path, what="JSON file"):
    text = read_text(path, what)
    # BOM-prefixed JSON is common in historical evidence; the BOM is an
    # encoding artefact, not declaration content (AC2 remediation).
    try:
        return json.loads(text.lstrip("\ufeff"))
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


# ---------------------------------------------------------------------------
# AC3/AC5 remediation: distinguish a declaration value from narrative text
# ---------------------------------------------------------------------------
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
CJK_PUNCT_RE = re.compile(r"[，。；：、（）【】「」]")
# Values that are explicitly "not a path" rather than an unresolved identity.
NON_PATH_WORDS = frozenset({
    "not_applicable", "not applicable", "n/a", "na", "none", "none yet",
    "no", "无", "不适用", "待定", "待填写", "-", "--", "—", "–", "null",
    "todo", "pending",
})
# Review r4 F-01: only these resolution failures may be treated as prose
# (value is not an identity at all).  Every other GuardError means the value
# resolved to an unsafe/unreadable identity and must stay fatal.
PROSE_SAFE_ERROR_CODES = frozenset({
    "DECL_BARE_NAME", "DECL_RELATIVE_UNRESOLVED", "DECL_RELATIVE_NO_ROOT"})
# Unparsable JSON is fatal unless it is listed in the explicit, SHA-256-bound
# non-declaration exception manifest (review r2 F-02).  File names are mutable
# and must never exempt a file.
DEFAULT_JSON_EXCEPTION_MANIFEST = (
    "tools/governance/non-declaration-json-exceptions.json")


def load_json_exceptions(repo_root, manifest_path=None):
    """Load the explicit ``path + sha256`` non-declaration JSON exceptions.

    Every entry must carry ``path``, ``sha256`` and ``reason``.  An exemption is
    applied only when the file still exists with exactly that SHA-256; a missing
    or changed file simply grants nothing (the file is then handled by the
    normal fatal JSON_PARSE rule).  This keeps a stale list harmless without
    weakening fail-closed behaviour, and lets the same tool run against fixture
    repositories that do not contain the real manifest's paths.
    """
    relative_manifest = manifest_path or DEFAULT_JSON_EXCEPTION_MANIFEST
    if os.path.isabs(relative_manifest):
        path = relative_manifest
    else:
        path = os.path.join(TOOL_ROOT, relative_manifest.replace("/", os.sep))
    if not os.path.isfile(path):
        return {}
    data = load_json(path, "JSON non-declaration exception manifest")
    if not isinstance(data, list):
        fail("JSON_EXCEPTION_SCHEMA",
             "JSON exception manifest %s must be a list" % path)
    exceptions = {}
    for position, item in enumerate(data):
        if not isinstance(item, dict):
            fail("JSON_EXCEPTION_SCHEMA",
                 "JSON exception entry %d is not an object" % position)
        entry_path = item.get("path")
        entry_sha = item.get("sha256")
        reason = item.get("reason")
        if not isinstance(entry_path, str) or not entry_path.strip():
            fail("JSON_EXCEPTION_SCHEMA",
                 "JSON exception entry %d has no path" % position)
        if not isinstance(entry_sha, str) or not re.match(
                r"^[0-9a-fA-F]{64}$", entry_sha.strip()):
            fail("JSON_EXCEPTION_SCHEMA",
                 "JSON exception entry %d has no valid sha256" % position)
        if not isinstance(reason, str) or not reason.strip():
            fail("JSON_EXCEPTION_SCHEMA",
                 "JSON exception entry %d has no reason" % position)
        relative = entry_path.strip().replace("\\", "/")
        if relative.startswith("/") or ".." in relative.split("/"):
            fail("JSON_EXCEPTION_SCHEMA",
                 "JSON exception path %r escapes the repository" % relative)
        absolute = os.path.join(repo_root, relative.replace("/", os.sep))
        if not os.path.isfile(absolute):
            continue  # stale entry: grants nothing, never a fatal for other repos
        actual = hashlib.sha256(io.open(absolute, "rb").read()).hexdigest()
        if actual != entry_sha.strip().lower():
            continue  # changed file: grants nothing
        exceptions[(relative, actual)] = reason.strip()
    return exceptions


def is_descriptive_value(text):
    """AC3: True only for explicit placeholders or pure narrative text.

    Review r2 F-01: a path-like value must NEVER be skipped, whatever spaces or
    CJK characters it contains.  ``is_path_like`` wins; an unresolvable
    path-like value then fails closed in ``_declared_identity``.  Only values
    with no path syntax at all may be skipped as prose.
    """
    stripped = text.strip()
    if stripped.lower() in NON_PATH_WORDS:
        return True
    if is_path_like(stripped):
        return False
    if CJK_RE.search(stripped) or CJK_PUNCT_RE.search(stripped):
        return True
    return len(stripped.split()) >= 2


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

    def _resolve_identity(self, text, source_file, locator, warn_alias=True):
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
        if warn_alias and real != normalized and source_file is not None:
            self.add_warning(
                "DECL_ALIAS_REAL_TARGET",
                "declaration %r is reached through a symlink/junction; the real "
                "target %s is protected as well" % (text, real),
                source_file, locator)
        return normalized, real

    def _declared_identity(self, text, source_file, locator):
        return self._resolve_identity(text, source_file, locator, True)

    def _prose_probe(self, text):
        """Classify a prose-looking value before skipping it (review r4 F-01).

        Returns ``("identity", normalized)`` when the value resolves safely,
        ``("error", GuardError)`` when it resolves but the identity is unsafe /
        unreadable (generalized junction, escape, env, glob, traversal...), and
        ``("prose", GuardError)`` only for the two "not an identity" codes
        (bare name / unresolved relative path).  Review r4: a generalized
        junction must NOT fall through as prose warning -- it stays fatal.
        """
        try:
            normalized, _real = self._resolve_identity(
                text, None, None, warn_alias=False)
        except GuardError as exc:
            if exc.code in PROSE_SAFE_ERROR_CODES:
                return "prose", exc
            return "error", exc
        return "identity", normalized

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
        if is_descriptive_value(text):
            verdict, payload = self._prose_probe(text)
            if verdict == "prose":
                # AC3: explicit placeholder / pure prose that is not an
                # identity.  Skipped with warning; never registers protection.
                self.add_warning("DECL_SOURCE_NOT_A_PATH",
                                 "source %r is descriptive text, not a path; "
                                 "skipped without protection" % text,
                                 source_file, locator)
                return None
            if verdict == "error":
                # Review r4 F-01: value resolved but its identity is unsafe /
                # unreadable (e.g. generalized junction).  Keep fatal with the
                # original code; prose must not swallow it.
                self.add_error(payload.code, payload.message, source_file, locator)
                return None
            # verdict == "identity": fall through and register protection.
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
        if is_descriptive_value(text):
            verdict, payload = self._prose_probe(text)
            if verdict == "prose":
                self.add_warning("DECL_EVIDENCE_NOT_A_PATH",
                                 "evidence path %r is descriptive text, not a "
                                 "path; skipped without protection" % text,
                                 source_file, locator)
                return None
            if verdict == "error":
                self.add_error(payload.code, payload.message, source_file, locator)
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
            # path (F-03).  Do NOT widen this to path-like prose: F-03 keeps a
            # path-like but unresolvable destination an integrity error.
            self.add_warning("DECL_DESTINATION_PROSE",
                             "destination %r is descriptive text, not a path; "
                             "it is not protection" % text,
                             source_file, locator)
            return None
        try:
            normalized, real = self._declared_identity(text, source_file, locator)
        except GuardError as exc:
            if exc.code == "DECL_GENERALIZED":
                # Review r2 F-03: a path-like over-broad destination weakens
                # F-03 exactly like an over-broad source.  Keep it fatal; no
                # root-policy exception is granted by this Task.
                self.add_error("DECL_DESTINATION_GENERALIZED", exc.message,
                               source_file, locator)
                return None
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


def _exact_column(header, *names):
    """Exact names plus the single frozen Canonical Evidence template label."""
    lowered = [cell.strip().lower() for cell in header]
    lowered = ["path" if cell == "path（仓库相对路径或绝对路径）" else cell
               for cell in lowered]
    for name in names:
        if name in lowered:
            return lowered.index(name)
    return None


def _duplicate_identity_columns(header, names):
    """Review r7 F-05: duplicate identity columns must not be silently reduced
    to the first index -- that would hide declarations in later columns."""
    lowered = [cell.strip().lower() for cell in header]
    lowered = ["path" if cell == "path（仓库相对路径或绝对路径）" else cell
               for cell in lowered]
    duplicates = []
    for name in names:
        count = lowered.count(name)
        if count > 1:
            duplicates.append("%s x%d" % (name, count))
    return duplicates


def _table_header(block):
    preview = _split_table_row(block[0]) if block else None
    return preview or []


def parse_markdown_declarations(index, text, source_file):
    manifest = section_text(text, "Resource Manifest")
    if manifest:
        for start, block in iter_table_blocks(manifest):
            header = _table_header(block)
            source_col = _exact_column(header, "source_path")
            disposition_col = _exact_column(header, "disposition")
            resource_type_col = _exact_column(header, "resource_type")
            destination_col = _exact_column(header, "destination_path")
            claims_manifest = (resource_type_col is not None
                               or source_col is not None
                               or disposition_col is not None
                               or destination_col is not None)
            if not claims_manifest:
                # A table with none of the identity columns is narrative; it
                # cannot enumerate protection.
                index.add_warning(
                    "TABLE_NOT_RESOURCE_MANIFEST",
                    "table at line %d does not declare resource/evidence "
                    "identity columns; skipped as narrative" % start,
                    source_file)
                continue
            duplicates = _duplicate_identity_columns(
                header, ("resource_type", "source_path", "disposition",
                         "destination_path"))
            if duplicates:
                index.add_error(
                    "TABLE_DUPLICATE_IDENTITY_COLUMN",
                    "table at line %d repeats identity column(s): %s; refusing "
                    "to silently choose one column"
                    % (start, ", ".join(duplicates)),
                    source_file)
                continue
            if source_col is None or disposition_col is None:
                # Review r2 F-04: a table that claims resource identity but
                # lacks a required column is malformed, not narrative.  Skipping
                # it could hide declarations, so fail closed.
                index.add_error(
                    "TABLE_SCHEMA_INCOMPLETE",
                    "table at line %d declares resource identity columns but "
                    "lacks %s; incomplete resource schemas cannot be trusted "
                    "for protection"
                    % (start, " and ".join(
                        name for name, column in
                        (("source_path", source_col),
                         ("disposition", disposition_col))
                        if column is None)),
                    source_file)
                continue
            try:
                header, rows = parse_table_block(block, start)
            except GuardError as exc:
                index.add_error(exc.code, exc.message, source_file)
                continue
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
            path_col = _exact_column(header, "path")
            evidence_col = _exact_column(header, "evidence_id")
            claims_evidence = path_col is not None or evidence_col is not None
            if not claims_evidence:
                index.add_warning(
                    "TABLE_NOT_CANONICAL_EVIDENCE",
                    "table at line %d does not declare canonical-evidence "
                    "identity columns; skipped as narrative" % start,
                    source_file)
                continue
            duplicates = _duplicate_identity_columns(header,
                                                     ("evidence_id", "path"))
            if duplicates:
                index.add_error(
                    "TABLE_DUPLICATE_IDENTITY_COLUMN",
                    "table at line %d repeats canonical-evidence identity "
                    "column(s): %s; refusing to silently choose one column"
                    % (start, ", ".join(duplicates)),
                    source_file)
                continue
            if path_col is None or evidence_col is None:
                index.add_error(
                    "TABLE_SCHEMA_INCOMPLETE",
                    "table at line %d declares canonical-evidence identity "
                    "columns but lacks %s; incomplete schemas cannot be trusted "
                    "for protection"
                    % (start, " and ".join(
                        name for name, column in
                        (("evidence_id", evidence_col), ("path", path_col))
                        if column is None)),
                    source_file)
                continue
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


BROAD_PRESERVATION_POLICY = "tools/governance/broad-root-preservation.json"
BROAD_PRESERVATION_RULING = (
    "verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/ruling.md")


def _finish_declaration_scan(index, scanned):
    result = dict(scanned)
    result.update(declarations=len(index.declarations),
                  errors=len(index.errors), warnings=len(index.warnings))
    if "protected_roots" in result:
        result["protected_roots"] = len(index.protected)
    return index, result


def _unique_preservation_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("POLICY_INVALID", "duplicate preservation policy key: %s" % key)
        result[key] = value
    return result


def _apply_broad_preservation(index, scanned):
    """Replace only the adjudicated error pairs with whole-root protection.

    The normal scanner still parses every source. No staged collection is
    published until all bindings, warnings, counts and byte snapshots succeed.
    """
    def require(condition, code, message):
        if not condition:
            fail(code, message)

    snapshots = {}

    def read(relative):
        absolute = os.path.join(index.repo_root.replace("/", os.sep),
                                relative.replace("/", os.sep))
        if absolute not in snapshots:
            with io.open(absolute, "rb") as handle:
                snapshots[absolute] = handle.read()
        return snapshots[absolute]

    def digest(raw):
        return hashlib.sha256(raw).hexdigest()

    def matches_hash(value, raw):
        return (isinstance(value, str)
                and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None
                and value.lower() == digest(raw))

    try:
        tracked = git_checked(
            index.repo_root, "ls-files", "-z", "--", BROAD_PRESERVATION_POLICY,
            what="git ls-files broad preservation policy")
        tracked = BROAD_PRESERVATION_POLICY in tracked.split("\x00")
        absolute = os.path.join(index.repo_root.replace("/", os.sep),
                                BROAD_PRESERVATION_POLICY.replace("/", os.sep))
        exists = os.path.lexists(absolute)
        if not tracked and not exists:
            return _finish_declaration_scan(index, scanned)
        require(tracked, "POLICY_UNTRACKED",
                "an untracked policy cannot activate broad preservation")
        require(exists, "BROAD_PRESERVATION_POLICY_MISSING",
                "tracked broad preservation policy is missing")
        policy = json.loads(read(BROAD_PRESERVATION_POLICY).decode("utf-8"),
                            object_pairs_hook=_unique_preservation_object)
        require(isinstance(policy, dict) and set(policy) == {
            "schema_version", "policy_kind", "scope_id", "decision_ref",
            "decision_sha256", "bindings"}, "POLICY_INVALID",
            "unexpected broad preservation policy schema")
        require(type(policy["schema_version"]) is int
                and policy["schema_version"] == 1
                and policy["policy_kind"] == "BROAD_ROOT_PRESERVATION"
                and policy["scope_id"] == "workspace-preserve-20261021-5roots",
                "POLICY_INVALID", "unsupported preservation policy version/scope")
        require(policy["decision_ref"] == BROAD_PRESERVATION_RULING,
                "POLICY_INVALID", "unexpected preservation ruling reference")
        require(matches_hash(policy["decision_sha256"],
                             read(BROAD_PRESERVATION_RULING)),
                "RULING_DRIFT", "preservation ruling bytes do not match")
        bindings = policy["bindings"]
        require(isinstance(bindings, list) and len(bindings) == 6,
                "POLICY_INVALID", "preservation requires exactly six bindings")
        first = "doc/tasks/SEC-FIX-PATH-ECHO-1.md"
        second = "doc/tasks/WORKSPACE-CONSOLIDATION-1.md"
        roots = {index.ws_root}
        roots.update(index.ws_root.rstrip("/") + "/" + name for name in
                     ("task-envs", "worktrees", "review-scratch", "temp"))
        expected = {(first, index.ws_root)}
        expected.update((second, root) for root in roots)
        contexts, identifiers, removed, pending = set(), set(), [], []
        fields = {"id", "origin_file", "origin_raw_sha256", "global_line",
                  "row_raw_sha256", "row_verbatim", "parser_locator",
                  "root_abs", "root_normalized", "root_real_expected",
                  "source_keep", "error_pair"}
        for binding in bindings:
            require(isinstance(binding, dict) and set(binding) == fields,
                    "POLICY_INVALID", "unexpected preservation binding schema")
            require(isinstance(binding["id"], str)
                    and re.fullmatch(r"BPR-0[1-6]", binding["id"]) is not None
                    and binding["id"] not in identifiers,
                    "POLICY_INVALID", "invalid or duplicate preservation id")
            identifiers.add(binding["id"])
            origin = binding["origin_file"]
            require(isinstance(origin, str) and origin in (first, second),
                    "POLICY_INVALID", "unexpected preservation source file")
            raw = read(origin)
            require(matches_hash(binding["origin_raw_sha256"], raw),
                    "SOURCE_DRIFT", "preservation source bytes changed: %s"
                    % origin)
            lines = raw.splitlines(keepends=True)
            line = binding["global_line"]
            require(type(line) is int and 1 <= line <= len(lines),
                    "RECORD_DRIFT", "invalid preservation source line")
            require(isinstance(binding["row_verbatim"], str)
                    and binding["row_verbatim"].encode("utf-8") == lines[line - 1]
                    and matches_hash(binding["row_raw_sha256"], lines[line - 1]),
                    "RECORD_DRIFT", "preservation source row bytes changed")
            text = raw.decode("utf-8")
            manifest = section_text(text, "Resource Manifest")
            require(bool(manifest), "RECORD_DRIFT", "missing Resource Manifest")
            offset = text[:text.index(manifest)].count("\n")
            matches = []
            for start, block in iter_table_blocks(manifest):
                header = _table_header(block)
                columns = [_exact_column(header, name) for name in
                           ("resource_type", "source_path", "disposition",
                            "destination_path")]
                if any(column is None for column in columns):
                    continue
                require(not _duplicate_identity_columns(header, (
                    "resource_type", "source_path", "disposition",
                    "destination_path")), "RECORD_DRIFT",
                    "duplicate preservation identity column")
                _header, rows = parse_table_block(block, start)
                for number, row in rows:
                    if offset + number == line:
                        matches.append((number, row, columns))
            require(len(matches) == 1, "RECORD_DRIFT",
                    "preservation row is not uniquely in its resource table")
            number, row, columns = matches[0]
            require(binding["parser_locator"] == "line %d" % number,
                    "RECORD_DRIFT", "preservation parser locator changed")
            source = clean_cell(row[columns[1]])
            destination = clean_cell(row[columns[3]])
            keep = clean_cell(row[columns[2]])
            require(isinstance(binding["root_abs"], str)
                    and is_abs_path(binding["root_abs"])
                    and not any(part in (".", "..") for part in
                                binding["root_abs"].replace("\\", "/").split("/"))
                    and source == destination == binding["root_abs"],
                    "RECORD_DRIFT", "preservation requires the same absolute root")
            normalized = index.resolve_declared_path(
                source, origin, binding["parser_locator"])
            real = resolve_real_target(normalized, "preservation root")
            require(normalized == binding["root_normalized"]
                    and normalized in roots, "POLICY_INVALID",
                    "preservation root is outside the adjudicated scope")
            require(real == binding["root_real_expected"] == normalized,
                    "REAL_DRIFT", "preservation real target changed")
            context = (origin, normalized)
            require(context in expected and context not in contexts,
                    "POLICY_INVALID", "unexpected or duplicate preservation record")
            contexts.add(context)
            expected_keep = ("PRESERVE_UNKNOWN" if normalized in (
                index.ws_root.rstrip("/") + "/review-scratch",
                index.ws_root.rstrip("/") + "/temp") else "PRESERVE_REFERENCED")
            require(keep == binding["source_keep"] == expected_keep,
                    "RECORD_DRIFT", "preservation disposition changed")
            pair = binding["error_pair"]
            require(isinstance(pair, list) and len(pair) == 2
                    and all(isinstance(error, dict) and set(error) == {
                        "code", "message", "file", "locator"} for error in pair),
                    "POLICY_INVALID", "invalid preservation error pair")
            try:
                index._resolve_identity(source, origin,
                                        binding["parser_locator"], warn_alias=False)
            except GuardError as exc:
                require(exc.code == "DECL_GENERALIZED", "ERROR_MISMATCH",
                        "preservation no longer has a generalized identity")
                message = exc.message
            else:
                fail("ERROR_MISMATCH", "preservation identity no longer rejected")
            for role, code, disposition in (
                    ("source", "DECL_GENERALIZED", keep),
                    ("destination", "DECL_DESTINATION_GENERALIZED",
                     "DESTINATION_PIN")):
                error = {"code": code, "message": message, "file": origin,
                         "locator": binding["parser_locator"]}
                require(pair[0 if role == "source" else 1] == error
                        and index.errors.count(error) == 1
                        and error not in removed, "ERROR_MISMATCH",
                        "preservation error pair is absent, duplicated or changed")
                removed.append(error)
                pending.append((Declaration(source, disposition, origin,
                                            binding["parser_locator"],
                                            normalized, real), role, keep))
        require(contexts == expected, "POLICY_INVALID",
                "preservation bindings do not cover all six adjudicated records")
        # Clone all mutable collections: an interrupted staging step cannot
        # remove an original error or publish half of the root protection.
        staged = copy.copy(index)
        staged.declarations = list(index.declarations)
        staged.protected = {root: list(items)
                            for root, items in index.protected.items()}
        staged.non_protective = list(index.non_protective)
        staged.errors = [error for error in index.errors if error not in removed]
        staged.warnings = list(index.warnings)
        staged._repo_tops = (set(index._repo_tops)
                            if index._repo_tops is not None else None)
        for declaration, role, keep in pending:
            staged._register_protective(declaration)
            staged.add_warning(
                "DECL_BROAD_ROOT_PRESERVED",
                "role=%s policy=%s origin=%s locator=%s root=%s source_keep=%s"
                % (role, BROAD_PRESERVATION_POLICY, declaration.source_file,
                   declaration.locator, declaration.normalized, keep),
                declaration.source_file, declaration.locator)
        result = _finish_declaration_scan(staged, scanned)
        for absolute, raw in snapshots.items():
            with io.open(absolute, "rb") as handle:
                require(handle.read() == raw, "SOURCE_DRIFT",
                        "preservation input changed during scanning: %s" % absolute)
        for root in {declaration.normalized for declaration, _, _ in pending}:
            require(resolve_real_target(root, "preservation final target") == root,
                    "REAL_DRIFT", "preservation real target changed during scanning")
        return result
    except Exception as exc:
        code = exc.code if isinstance(exc, GuardError) else "POLICY_INVALID"
        message = exc.message if isinstance(exc, GuardError) else str(exc)
        index.add_error(code, message, BROAD_PRESERVATION_POLICY)
        return _finish_declaration_scan(index, scanned)


HISTORICAL_EVIDENCE_POLICY = "tools/governance/historical-evidence-interpretation.json"
HISTORICAL_EVIDENCE_DIGEST = (
    "3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d")


def _apply_historical_evidence_interpretation(index, scanned):
    """Preserve four exact raw sources before interpreting their five errors."""
    if any(e["file"] == BROAD_PRESERVATION_POLICY for e in index.errors):
        return index, scanned

    def require(condition, code, message):
        if not condition:
            fail(code, message)

    def exact(value, keys):
        require(type(value) is dict and set(value) == set(keys.split()),
                "POLICY_INVALID", "unexpected historical policy fields")

    def sha(raw):
        return hashlib.sha256(raw).hexdigest()

    def absolute(relative):
        require(isinstance(relative, str) and not is_abs_path(relative)
                and "\\" not in relative and not GLOB_RE.search(relative)
                and not ENV_RE.search(relative)
                and all(p not in ("", ".", "..") for p in relative.split("/")),
                "POLICY_INVALID", "invalid historical relative path")
        return os.path.join(index.repo_root.replace("/", os.sep),
                            relative.replace("/", os.sep))

    def tracked(relative):
        output = git_checked(index.repo_root, "ls-files", "-z", "--", relative,
                             what="git ls-files historical input")
        return relative in output.split("\x00")

    snapshots = {}
    tracking = {}
    targets = {}

    def read(relative, expected_tracking="tracked"):
        path = absolute(relative)
        require(os.path.isfile(path) and not _is_link(path), "SOURCE_DRIFT",
                "historical input is not a regular file: %s" % relative)
        normalized = norm_abs(path)
        require(resolve_real_target(normalized, "historical input") == normalized,
                "REAL_DRIFT", "historical input has a different real target")
        require(tracked(relative) == (expected_tracking == "tracked"),
                "SOURCE_DRIFT", "historical input tracking changed: %s" % relative)
        with io.open(path, "rb") as handle:
            raw = handle.read()
        if relative in snapshots:
            require(snapshots[relative] == raw, "SOURCE_DRIFT",
                    "historical input changed during scan: %s" % relative)
        snapshots[relative], tracking[relative] = raw, expected_tracking
        targets[normalized] = normalized
        return raw

    def declaration_dict(d):
        return {key: getattr(d, key) for key in Declaration.__slots__}

    def snapshot(i):
        return dict(declarations=[declaration_dict(d) for d in i.declarations],
                    errors=i.errors, warnings=i.warnings)

    def contains(i, frozen):
        return (any(declaration_dict(d) == frozen for d in i.declarations)
                and all(any(declaration_dict(d) == frozen
                            for d in i.protected.get(root, [])) for root in
                        (frozen["normalized"], frozen["real_normalized"])))

    def guard_identity(guard, relative, keep, directory=False):
        exact(guard, "abs normalized real keep")
        require(guard["keep"] == keep and is_abs_path(guard["abs"])
                and not any(p in (".", "..") for p in
                            guard["abs"].replace("\\", "/").split("/")),
                "POLICY_INVALID", "invalid historical preservation guard")
        expected = norm_abs(absolute(relative))
        require(norm_abs(guard["abs"]) == guard["normalized"] == expected,
                "REAL_DRIFT", "historical guard lexical identity changed")
        lexical, real = index._resolve_identity(guard["abs"], None, None,
                                               warn_alias=False)
        require(lexical == real == guard["real"] == expected, "REAL_DRIFT",
                "historical guard real identity changed")
        require(os.path.isdir(absolute(relative)) if directory else
                os.path.isfile(absolute(relative)), "SOURCE_DRIFT",
                "historical guard target missing or wrong type")
        targets[lexical] = real
        return guard

    try:
        present = os.path.lexists(absolute(HISTORICAL_EVIDENCE_POLICY))
        enabled = tracked(HISTORICAL_EVIDENCE_POLICY)
        if not present and not enabled:
            return index, scanned
        require(enabled, "POLICY_UNTRACKED", "historical policy must be tracked")
        require(present, "POLICY_MISSING", "tracked historical policy is missing")
        policy = json.loads(read(HISTORICAL_EVIDENCE_POLICY).decode("utf-8"),
                            object_pairs_hook=_unique_preservation_object)
        exact(policy, "schema_version purpose approved_design template_bindings "
              "raw_non_declaration_bindings reference_guards")
        require(type(policy["schema_version"]) is int
                and policy["schema_version"] == 1
                and policy["purpose"] == "PRESERVE_EXACT_HISTORICAL_EVIDENCE",
                "POLICY_INVALID", "unsupported historical policy version/purpose")
        canonical = json.dumps(policy, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")
        # The approved digest binds every nested key, type, ID and source set.
        require(sha(canonical) == HISTORICAL_EVIDENCE_DIGEST,
                "POLICY_DIGEST_MISMATCH", "historical policy is not approved")

        require(os.path.isfile(absolute(BROAD_PRESERVATION_POLICY))
                and tracked(BROAD_PRESERVATION_POLICY), "DEPENDENCY_INACTIVE",
                "broad preservation policy is not active")
        broad = json.loads(read(BROAD_PRESERVATION_POLICY).decode("utf-8"),
                           object_pairs_hook=_unique_preservation_object)
        expected_warnings = []
        for b in broad["bindings"]:
            require(b["root_normalized"] in index.protected,
                    "DEPENDENCY_INACTIVE", "broad root is not protected")
            for role, keep in (("source", b["source_keep"]),
                               ("destination", "DESTINATION_PIN")):
                frozen = dict(raw=b["root_abs"], disposition=keep,
                              source_file=b["origin_file"],
                              locator=b["parser_locator"],
                              normalized=b["root_normalized"],
                              real_normalized=b["root_real_expected"])
                warning = dict(code="DECL_BROAD_ROOT_PRESERVED",
                    message="role=%s policy=%s origin=%s locator=%s root=%s source_keep=%s"
                    % (role, BROAD_PRESERVATION_POLICY, b["origin_file"],
                       b["parser_locator"], b["root_normalized"], b["source_keep"]),
                    file=b["origin_file"], locator=b["parser_locator"])
                require(sum(declaration_dict(d) == frozen for d in
                            index.declarations) == 1 and contains(index, frozen)
                        and index.warnings.count(warning) == 1,
                        "DEPENDENCY_INACTIVE", "broad role proof is not unique")
                expected_warnings.append(warning)
        markers = [w for w in index.warnings
                   if w["code"] == "DECL_BROAD_ROOT_PRESERVED"]
        require(len(expected_warnings) == len(markers) == 12
                and all(w in expected_warnings for w in markers)
                and len({b["root_normalized"] for b in broad["bindings"]}) == 5,
                "DEPENDENCY_INACTIVE", "incomplete broad preservation proof")

        approved = policy["approved_design"]
        exact(approved, "task_id design_file design_raw_sha256 source_facts_file "
              "source_facts_commit source_facts_raw_sha256")
        for prefix in ("design", "source_facts"):
            require(sha(read(approved[prefix + "_file"])) ==
                    approved[prefix + "_raw_sha256"], "SOURCE_DRIFT",
                    "approved historical provenance changed")
        blob = subprocess.check_output(
            ["git", "show", approved["source_facts_commit"] + ":" +
             approved["source_facts_file"]], cwd=index.repo_root,
            stderr=subprocess.PIPE)
        require(sha(blob) == approved["source_facts_raw_sha256"], "SOURCE_DRIFT",
                "approved historical facts blob changed")
        require(len(policy["template_bindings"]) == 1
                and len(policy["raw_non_declaration_bindings"]) == 3
                and len(policy["reference_guards"]) == 2, "POLICY_INVALID",
                "historical binding set changed")
        bindings = policy["template_bindings"] + policy["raw_non_declaration_bindings"]
        require([b["id"] for b in bindings] ==
                ["HIE-T01", "HIE-O01", "HIE-O02", "HIE-O03"],
                "POLICY_INVALID", "historical binding IDs changed")
        removed, pending, warnings, existing = [], [], [], []
        for number, b in enumerate(bindings):
            exact(b, "id origin_file expected_tracking raw_sha256 byte_length "
                  "strict_utf8 utf8_bom c0_bytes source_guard parser_snapshot errors "
                  + ("fence rows" if number == 0 else "nul_offsets"))
            origin = b["origin_file"]
            require(b["expected_tracking"] ==
                    ("untracked" if number == 3 else "tracked"), "POLICY_INVALID",
                    "historical source tracking policy changed")
            raw = read(origin, b["expected_tracking"])
            require(sha(raw) == b["raw_sha256"]
                    and type(b["byte_length"]) is int and len(raw) == b["byte_length"]
                    and b["strict_utf8"] is True and type(b["utf8_bom"]) is bool
                    and b["utf8_bom"] == raw.startswith(b"\xef\xbb\xbf"),
                    "SOURCE_DRIFT", "historical raw identity changed: %s" % origin)
            controls = [{"offset": n, "byte": c} for n, c in enumerate(raw)
                        if c < 32 and c not in (9, 10, 13)]
            require(json.dumps(b["c0_bytes"], sort_keys=True) ==
                    json.dumps(controls, sort_keys=True), "SOURCE_DRIFT",
                    "historical control-byte identity changed")
            text = raw.decode("utf-8", errors="strict")
            isolated = ProtectionIndex(index.repo_root, index.ws_root)
            parse_markdown_declarations(isolated, text, origin)
            require(snapshot(isolated) == b["parser_snapshot"], "RECORD_DRIFT",
                    "historical isolated parse changed: %s" % origin)
            keep = "PRESERVE_UNKNOWN" if number == 3 else "PRESERVE_REFERENCED"
            guard = guard_identity(b["source_guard"], origin, keep)
            locator = b["id"] + "/raw-file"
            pending.append(Declaration(guard["abs"], keep, origin, locator,
                                       guard["normalized"], guard["real"]))
            if number == 0:
                require(len(isolated.declarations) == 1
                        and len(isolated.errors) == len(isolated.warnings) == 2
                        and len(b["errors"]) == 2, "RECORD_DRIFT",
                        "historical template parse shape changed")
                lines = raw.splitlines(keepends=True)
                f = b["fence"]
                exact(f, "open_global_line close_global_line open_verbatim "
                      "close_verbatim open_raw_sha256 close_raw_sha256 "
                      "draft_notice_global_line draft_notice_verbatim draft_notice_raw_sha256")
                for prefix in ("open", "close", "draft_notice"):
                    n = f[prefix + "_global_line"]
                    require(type(n) is int and 1 <= n <= len(lines)
                            and lines[n - 1].decode("utf-8") == f[prefix + "_verbatim"]
                            and sha(lines[n - 1]) == f[prefix + "_raw_sha256"],
                            "RECORD_DRIFT", "historical template boundary changed")
                require(len(b["rows"]) == 2, "RECORD_DRIFT", "template rows changed")
                for row in b["rows"]:
                    exact(row, "id global_line parser_locator verbatim raw_line_sha256")
                    n = row["global_line"]
                    require(type(n) is int and 1 <= n <= len(lines)
                            and lines[n - 1].decode("utf-8") == row["verbatim"]
                            and sha(lines[n - 1]) == row["raw_line_sha256"],
                            "RECORD_DRIFT", "historical template row changed")
                existing = [declaration_dict(d) for d in isolated.declarations]
                require(all(contains(index, d) for d in existing), "RECORD_DRIFT",
                        "historical template original protection missing")
                for d in existing:
                    targets[d["normalized"]] = d["real_normalized"]
            else:
                require(snapshot(isolated) == dict(declarations=[], errors=[], warnings=[])
                        and b["nul_offsets"] == [c["offset"] for c in controls
                                                 if c["byte"] == 0]
                        and len(b["errors"]) == 1
                        and b["errors"][0]["code"] == "FILE_UNREADABLE"
                        and b["errors"][0]["locator"] is None,
                        "RECORD_DRIFT", "historical raw source is not declaration-free")
            for error in b["errors"]:
                exact(error, "code message file locator")
                require(error["file"] == origin and index.errors.count(error) == 1
                        and error not in removed, "ERROR_MISMATCH",
                        "historical error identity is missing, duplicated or changed")
                removed.append(error)
            warning_locator = ("global 228,229/line 7,8/" + b["id"] if number == 0
                               else b["id"] + "/bytes " +
                               ",".join(str(n) for n in b["nul_offsets"]))
            warnings.append((origin, warning_locator, b, keep))
        for n, ref in enumerate(policy["reference_guards"], 1):
            exact(ref, "id origin_file origin_global_line origin_parser_locator "
                  "path_rel abs normalized real keep")
            require(ref["id"] == "HIE-REF%02d" % n
                    and ref["origin_file"] == bindings[0]["origin_file"],
                    "POLICY_INVALID", "historical reference context changed")
            guard = guard_identity({k: ref[k] for k in ("abs", "normalized", "real", "keep")},
                                   ref["path_rel"], "PRESERVE_REFERENCED", directory=True)
            locator = "global %s/%s/%s" % (ref["origin_global_line"],
                                          ref["origin_parser_locator"], ref["id"])
            pending.append(Declaration(guard["abs"], guard["keep"], ref["origin_file"],
                                       locator, guard["normalized"], guard["real"]))
        require(len(removed) == 5 and len(pending) == 6, "POLICY_INVALID",
                "incomplete historical preservation batch")
        staged = copy.copy(index)
        staged.declarations = list(index.declarations)
        staged.protected = {root: list(items) for root, items in index.protected.items()}
        staged.non_protective = list(index.non_protective)
        staged.errors = [e for e in index.errors if e not in removed]
        staged.warnings = list(index.warnings)
        staged._repo_tops = set(index._repo_tops) if index._repo_tops is not None else None
        for d in pending:
            staged._register_protective(d)
        for origin, locator, b, keep in warnings:
            roots = [d.normalized for d in pending if d.source_file == origin]
            staged.add_warning("DECL_HISTORICAL_EVIDENCE_PRESERVED",
                "mode=%s policy=%s origin=%s locator=%s raw_sha256=%s keep=%s original_codes=%s guard_roots=%s"
                % ("template" if b is bindings[0] else "raw-nondeclaration",
                   HISTORICAL_EVIDENCE_POLICY, origin, locator, b["raw_sha256"], keep,
                   ",".join(e["code"] for e in b["errors"]), json.dumps(roots)),
                origin, locator)
        result = _finish_declaration_scan(staged, scanned)
        for relative in list(snapshots):
            read(relative, tracking[relative])
        for root, real in targets.items():
            require(resolve_real_target(root, "historical final target") == real,
                    "REAL_DRIFT", "historical real target changed during scan")
        require(all(contains(staged, d) for d in existing), "RECORD_DRIFT",
                "historical original protection changed during staging")
        return result
    except Exception as exc:
        code = exc.code if isinstance(exc, GuardError) else "POLICY_INVALID"
        # Avoid emitting raw historical text/control bytes on unexpected failure.
        message = exc.message if isinstance(exc, GuardError) else "historical policy validation failed"
        index.add_error(code, message, HISTORICAL_EVIDENCE_POLICY)
        return _finish_declaration_scan(index, scanned)


def scan_repo_declarations(repo_root, ws_root, json_exceptions=None):
    """Build the protection index from ``doc/tasks/**`` and ``verification/**``.

    Read-only.  Both TRACKED files and non-ignored UNTRACKED ``.md``/``.json``
    files are scanned (F-02): a declaration that only exists as an untracked
    draft still names a protected resource, and silently ignoring it is exactly
    the r208 failure mode.

    JSON classification (AC2 remediation, hardened by review r2 F-02): an
    unparsable JSON file is fatal (``JSON_PARSE``) unless its exact path AND
    SHA-256 appear in the explicit non-declaration exception manifest
    (``non-declaration-json-exceptions.json``; path overridable with
    ``--json-exceptions``).  File names are mutable and never exempt anything.
    The manifest schema is validated and an entry is applied only when the file
    still matches its recorded SHA-256; renames/edits therefore lose the
    exemption and become fatal.  MIGRATE/ARCHIVE declarations cannot hide behind
    a renamed ``*.stdout.json`` because the exemption is byte-bound.

    ``git ls-files`` failure is fatal (AC2).  Legacy non-UTF-8 markdown is read
    as strict GB18030 with ``FILE_ENCODING_LEGACY`` warning (AC4), but binary
    payloads (NUL/control-heavy/no-CJK) remain ``FILE_UNREADABLE`` (F-05).
    """
    index = ProtectionIndex(repo_root=repo_root, ws_root=ws_root)
    repo = index.repo_root
    exceptions = load_json_exceptions(repo, json_exceptions)
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
               "json_non_declaration": 0, "json_parse_fatal": 0,
               "tracked_declaration_files": len(tracked_files),
               "untracked_declaration_files": len(untracked_files)}
    for relative in files:
        absolute = os.path.join(repo.replace("/", os.sep),
                                relative.replace("/", os.sep))
        source_kind = "tracked" if relative in tracked_files else "untracked"
        if relative.endswith(".md"):
            scanned["markdown"] += 1
            try:
                text = read_text(absolute, "%s markdown" % source_kind,
                                 legacy_warn=index.add_warning)
            except GuardError as exc:
                index.add_error("FILE_UNREADABLE", exc.message, relative)
                continue
            parse_markdown_declarations(index, text, relative)
        elif relative.endswith(".json"):
            scanned["json"] += 1
            digest = None
            if exceptions:
                try:
                    digest = hashlib.sha256(
                        io.open(absolute, "rb").read()).hexdigest()
                except OSError as exc:
                    index.add_error(
                        "IO_READ_FAILED",
                        "cannot read %s JSON %s: %s"
                        % (source_kind, absolute, exc), relative)
                    continue
                reason = exceptions.get((relative.replace("\\", "/"), digest))
                if reason is not None:
                    scanned["json_non_declaration"] += 1
                    index.add_warning(
                        "JSON_NON_DECLARATION",
                        "unparsable %s JSON explicitly exempted by path+sha256 "
                        "in the non-declaration manifest (%s)" % (source_kind,
                                                                 reason),
                        relative)
                    continue
            try:
                data = load_json(absolute, "%s JSON" % source_kind)
            except GuardError as exc:
                scanned["unparsable_json"] += 1
                scanned["json_parse_fatal"] += 1
                index.add_error(
                    "JSON_PARSE",
                    "unparsable %s JSON declaration file; protection cannot be "
                    "enumerated and it is not in the explicit path+sha256 "
                    "non-declaration exception manifest: %s"
                    % (source_kind, exc.message), relative)
                continue
            parse_json_declarations(index, data, relative)
    index, scanned = _apply_broad_preservation(index, scanned)
    return _apply_historical_evidence_interpretation(index, scanned)


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
    index, scanned = scan_repo_declarations(repo, ws,
                                            config.get("json_exceptions"))
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
    index, scanned = scan_repo_declarations(config["repo"], config["ws"],
                                            config.get("json_exceptions"))
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
        "json_exceptions": args.json_exceptions,
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
    parser.add_argument("--json-exceptions",
                        help="explicit path+sha256 non-declaration JSON "
                             "exception manifest (default: this tool's "
                             "verification/WORKSPACE-DECLARATION-REMEDIATION-1/"
                             "non-declaration-json-exceptions.json)")
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
