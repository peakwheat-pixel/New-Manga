#!/usr/bin/env python3
"""Read-only sweep of Canonical Evidence pins (Codex ruling 2026-11-16 Q3).

Mechanical checks for every canonical row of every task card's
``## Canonical Evidence`` table:

* the sha256 cell must contain at least one 64-hex digest (cells that list both
  the blob and the worktree digest are accepted and reported as MULTI);
* the recorded digest must match one exact byte representation: the commit blob,
  the current worktree bytes, or the pure line-ending counterpart of the current
  bytes (LF/CRLF) -- nothing is normalised beyond line endings;
* a commit cell that is ``-``/empty/not commit-shaped (e.g. ``pending``) is
  treated as "no commit": the row is then judged on the worktree basis;
* a commit that exists but does not contain the path is a WARN when the current
  bytes still match (the file was added after that commit).

Exit codes: 0 = no findings, 1 = findings, 2 = usage error.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HEX64 = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
CANONICAL_CLASSES = ("CANONICAL", "SOURCE_PIN")


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def clean(cell):
    return cell.strip().strip("`").strip()


def is_delimiter(cells):
    return bool(cells) and all(re.match(r"^:?-{3,}:?$", c) for c in cells)


def evidence_tables(text):
    lines = text.split("\n")
    inside = False
    table, header = [], None
    for idx, line in enumerate(lines, 1):
        if re.match(r"^##\s+Canonical\s+Evidence\b", line):
            inside = True
            table, header = [], None
            continue
        if inside and re.match(r"^##\s", line):
            if table:
                yield header, table
            inside = False
            table, header = [], None
            continue
        if not inside or not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if header is None:
            header = [clean(c) for c in cells]
            continue
        if is_delimiter(cells):
            continue
        table.append((idx, cells))
    if inside and table:
        yield header, table


def column_indices(header, width):
    cols = {name: i for i, name in enumerate(header)}

    def pick(*names):
        for name in names:
            if name in cols:
                return cols[name]
        return None

    path_i = pick("path", "path（仓库相对路径或绝对路径）")
    commit_i = pick("commit")
    sha_i = pick("sha256")
    class_i = pick("class", "class (`CANONICAL` / `SOURCE_PIN`)")
    if path_i is None or sha_i is None:
        return None
    if max(path_i, sha_i, commit_i or 0, class_i or 0) >= width:
        return None
    return path_i, commit_i, sha_i, class_i


def collect(cards):
    rows = []
    for card in cards:
        rel_card = "doc/tasks/" + card.name
        try:
            text = card.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            rows.append({"card": rel_card, "verdict": "FAIL", "code": "UNREADABLE",
                         "detail": str(exc), "path": "", "commit": "", "recorded": ""})
            continue
        for header, table in evidence_tables(text):
            for line_no, cells in table:
                idx = column_indices(header, len(cells))
                if not idx:
                    continue
                path_i, commit_i, sha_i, class_i = idx
                klass = clean(cells[class_i]) if class_i is not None else ""
                if klass not in CANONICAL_CLASSES:
                    continue
                rel = clean(cells[path_i]).replace("\\", "/")
                commit = clean(cells[commit_i]) if commit_i is not None else "-"
                recorded_cell = clean(cells[sha_i]).lower()
                digests = HEX64.findall(recorded_cell)
                rows.append({"card": rel_card, "line": line_no, "path": rel,
                             "id": clean(cells[0]) if cells else "",
                             "commit": commit, "recorded_cell": recorded_cell,
                             "digests": digests})
    return rows


def batch_blobs(queries):
    """Resolve many ``<commit>:<path>`` blobs in one git process."""
    out = {}
    if not queries:
        return out
    proc = subprocess.Popen(["git", "-C", str(REPO), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    payload = "".join(q + "\n" for q in queries).encode()
    stdout, _ = proc.communicate(payload)
    pos, data = 0, stdout
    for q in queries:
        nl = data.find(b"\n", pos)
        if nl < 0:
            break
        header = data[pos:nl].decode("utf-8", "replace")
        pos = nl + 1
        parts = header.split()
        if len(parts) == 3 and parts[1] == "blob":
            size = int(parts[2])
            out[q] = data[pos:pos + size]
            pos += size + 1
        else:
            out[q] = None
    proc.wait()
    return out


def representations(path):
    """Exact byte representations of the current worktree file."""
    p = REPO / path
    if not p.exists() or p.is_dir():
        return {}
    raw = p.read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    reps = {"WORKTREE": hashlib.sha256(raw).hexdigest(),
            "LF": hashlib.sha256(lf).hexdigest(),
            "CRLF": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}
    return reps


def judge(row, blob, reps, commit_shaped):
    """Decide one row. Pure function: no I/O, so it is unit-testable."""
    digests = row["digests"]
    if not digests:
        return "FAIL", "SHA_NOT_64_HEX", "no 64-hex digest in the sha256 cell", None
    recorded = set(digests)
    if blob is not None and hashlib.sha256(blob).hexdigest() in recorded:
        return "PASS", "BLOB_MATCH", "", "BLOB"
    for basis in ("WORKTREE", "LF", "CRLF"):
        if reps.get(basis) in recorded:
            if blob is not None:
                # a commit exists but its blob does not match: legacy worktree-basis pin
                return ("WARN", "BLOB_MISMATCH_WORKTREE",
                        "recorded digest matches %s bytes, not the commit blob" % basis, basis)
            # no commit recorded: the worktree basis is the documented legacy form
            return "PASS", "WORKTREE_MATCH", "recorded digest matches %s bytes" % basis, basis
    if not reps:
        return "FAIL", "PATH_MISSING", "path does not exist in the worktree", None
    if commit_shaped and blob is None:
        return "FAIL", "COMMIT_PATH_MISSING", "path is absent at the recorded commit", None
    if not commit_shaped and row["commit"] not in ("", "-"):
        return "FAIL", "COMMIT_NOT_FOUND", "commit cell is not a commit in this repository", None
    return "FAIL", "SHA_MISMATCH", "recorded digest matches none of blob/worktree/LF/CRLF", None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", help="write the full result set as JSON")
    ap.add_argument("--cards", nargs="*", help="restrict to these card paths")
    args = ap.parse_args(argv)

    cards = sorted((REPO / "doc" / "tasks").glob("*.md"))
    if args.cards:
        wanted = {Path(c).name for c in args.cards}
        cards = [c for c in cards if c.name in wanted]

    rows = collect(cards)
    queries = sorted({"%s:%s" % (r["commit"], r["path"]) for r in rows
                      if r.get("commit") and COMMIT.match(r["commit"])})
    blobs = batch_blobs(queries)
    commits_exist = {}
    results = []
    for r in rows:
        if "digests" not in r:
            results.append(r)
            continue
        commit, path = r["commit"], r["path"]
        base = {"card": r["card"], "line": r["line"], "path": path, "commit": commit,
                "id": r.get("id", ""),
                "recorded": ",".join(d[:16] for d in r["digests"])}
        commit_shaped = bool(COMMIT.match(commit))
        blob = None
        if commit_shaped:
            key = "%s:%s" % (commit, path)
            blob = blobs.get(key)
            if key not in commits_exist:
                rc = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--verify",
                                     commit + "^{commit}"], capture_output=True)
                commits_exist[key] = rc.returncode == 0
            if not commits_exist[key]:
                commit_shaped = False
        verdict, code, detail, basis = judge(r, blob, representations(path), commit_shaped)
        results.append(dict(base, verdict=verdict, code=code, detail=detail, basis=basis))

    # Append-only supersession (ruling Q1=D): a FAIL row whose path also carries a
    # PASS row whose id ends with "-supersede" is documented, not silently dropped.
    replacements = {}
    for r in results:
        if r.get("verdict") == "PASS" and r.get("id", "").lower().endswith("-supersede"):
            replacements.setdefault(r["path"], r["id"])
    superseded = []
    for r in results:
        if r.get("verdict") == "FAIL" and r["path"] in replacements:
            r["detail"] = "%s; superseded by %s" % (r["detail"], replacements[r["path"]])
            r["code"] = "SUPERSEDED_BY_" + replacements[r["path"]].upper()
            r["verdict"] = "SUPERSEDED"
            superseded.append(r)

    fails = [r for r in results if r.get("verdict") == "FAIL"]
    superseded = [r for r in results if r.get("verdict") == "SUPERSEDED"]
    warns = [r for r in results if r.get("verdict") == "WARN"]
    print("evidence pin sweep: %d canonical row(s) in %d card(s)"
          % (len(results), len(cards)))
    print("  FAIL: %d   SUPERSEDED: %d   WARN: %d"
          % (len(fails), len(superseded), len(warns)))
    for r in fails:
        print("  FAIL %-38s %-22s %s:%s  %s"
              % (r["card"].split("/")[-1], r["code"], (r["path"] or "")[:42],
                 r.get("line", "?"), r["detail"]))
    for r in superseded:
        print("  SUPERSEDED %-30s %-22s %s:%s  %s"
              % (r["card"].split("/")[-1], r["code"], (r["path"] or "")[:42],
                 r.get("line", "?"), r["detail"]))
    if args.json:
        Path(args.json).write_text(
            json.dumps({"rows": results, "fail": len(fails),
                        "superseded": len(superseded), "warn": len(warns)},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("  json:", args.json)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
