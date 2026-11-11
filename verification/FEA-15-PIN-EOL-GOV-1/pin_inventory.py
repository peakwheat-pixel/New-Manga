#!/usr/bin/env python3
"""Inventory pinned evidence from tracked Task cards and frozen contracts.

The snapshot is intentionally bound to one committed HEAD. It compares each
recorded SHA-256 with both the current working-tree bytes and the referenced
commit blob, and records the current index/worktree EOL and attributes.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from pathlib import PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "verification" / "FEA-15-PIN-EOL-GOV-1" / "pin-inventory.json"
HEX64 = re.compile(r"(?i)\b[0-9a-f]{64}\b")


def git(*args: str, check: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check
    )


def text_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^\[([^]]+)\]\([^)]+\)$", r"\1", value)
    return value.strip(" `\t")


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_table_rows(path: str) -> list[dict[str, str]]:
    content = (ROOT / path).read_text(encoding="utf-8-sig", errors="replace")
    active = False
    headers: list[str] | None = None
    result: list[dict[str, str]] = []
    for line in content.splitlines():
        if re.match(r"^#{2,}\s+.*Canonical Evidence\b", line, re.IGNORECASE):
            active, headers = True, None
            continue
        if active and re.match(r"^#{2,}\s+", line):
            active, headers = False, None
            continue
        if not active or not line.lstrip().startswith("|"):
            continue
        cells = split_row(line)
        lowered = [re.sub(r"[^a-z0-9/_]", "", c.lower()) for c in cells]
        if "evidence_id" in lowered and "path" in lowered and "commit" in lowered and "sha256" in lowered:
            headers = lowered
            continue
        if not headers or len(cells) != len(headers):
            continue
        if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
            continue
        row = {headers[i]: text_cell(cells[i]) for i in range(len(headers))}
        if row.get("evidence_id") and row.get("path"):
            result.append(row)
    return result


def frozen_records(tracked: list[str], expected_map: dict[str, str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    paths = [p for p in tracked if p.startswith("doc/plan/FEA-CONTRACT-FROZEN-") and p.endswith(".md")]
    for record_path in sorted(paths):
        content = (ROOT / record_path).read_text(encoding="utf-8-sig", errors="replace")
        freeze_section = content.split("## 1B.", 1)[0]
        contract_match = re.search(r"(?m)^\|\s*文件\s*\|\s*`([^`]+)`\s*\|", freeze_section)
        if not contract_match:
            contract_match = re.search(r"(?m)^契约：\s*`([^`]+)`", freeze_section)
        pin_match = re.search(r"(?mi)^\|\s*sha256[^|]*\|\s*`([0-9a-f]{64})`", freeze_section)
        record_id = Path(record_path).stem.removeprefix("FEA-CONTRACT-FROZEN-")
        contract_path = contract_match.group(1) if contract_match else ""
        result.append(
            {
                "source_file": record_path,
                "evidence_id": f"FROZEN-{record_id}",
                "ac_gate": "frozen contract bytes",
                "path": contract_path,
                "commit": "",
                "pin_sha256": pin_match.group(1).lower() if pin_match else "",
                "class": "FROZEN_PIN",
                "expected_source_filename": expected_map.get(record_id, ""),
                "commit_field_present": False,
            }
        )
    return result


def verify_pins_map() -> dict[str, str]:
    content = (ROOT / "tools/governance/verify_pins.ps1").read_text(encoding="utf-8-sig")
    return {key: value for key, value in re.findall(r"'([^']+)'\s*=\s*'([^']+)'", content)}


def sha(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def blob_bytes(commit: str, path: str) -> tuple[bytes | None, str | None]:
    if not commit or not path:
        return None, None
    proc = git("cat-file", "blob", f"{commit}:{path}")
    return (proc.stdout, None) if proc.returncode == 0 else (None, proc.stderr.decode("utf-8", "replace").strip())


def indexed_eol_map() -> dict[str, tuple[str, str, str]]:
    result: dict[str, tuple[str, str, str]] = {}
    output = git("ls-files", "--eol").stdout.decode("utf-8", "replace")
    for line in output.splitlines():
        match = re.match(r"i/(\S+)\s+w/(\S+)\s+attr/(.*?)\s{2,}(.*)$", line)
        if match:
            result[match.group(4).replace("\\", "/")] = (match.group(1), match.group(2), match.group(3).strip())
    return result


def attribute_map(paths: list[str]) -> dict[str, list[str]]:
    if not paths:
        return {}
    payload = b"\0".join(p.encode("utf-8", "surrogateescape") for p in paths) + b"\0"
    proc = subprocess.run(
        ["git", "check-attr", "--all", "-z", "--stdin"],
        cwd=ROOT,
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    fields = proc.stdout.split(b"\0")
    result: dict[str, list[str]] = {}
    for i in range(0, len(fields) - 2, 3):
        path = fields[i].decode("utf-8", "surrogateescape").replace("\\", "/")
        key = fields[i + 1].decode("utf-8", "replace")
        value = fields[i + 2].decode("utf-8", "replace")
        if path and key and value:
            result.setdefault(path, []).append(f"{key}={value}")
    return result


def blob_map(specs: list[str]) -> tuple[dict[str, bytes], dict[str, str]]:
    if not specs:
        return {}, {}
    proc = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        input=("\n".join(specs) + "\n").encode("utf-8", "surrogateescape"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    output = proc.stdout
    blobs: dict[str, bytes] = {}
    errors: dict[str, str] = {}
    offset = 0
    for spec in specs:
        end = output.find(b"\n", offset)
        if end < 0:
            errors[spec] = "git cat-file --batch returned a truncated header"
            break
        header = output[offset:end].decode("utf-8", "replace").split()
        offset = end + 1
        if len(header) >= 2 and header[1] == "missing":
            errors[spec] = "commit:path is missing"
            continue
        if len(header) != 3 or header[1] != "blob":
            errors[spec] = "unexpected cat-file header: " + " ".join(header)
            continue
        size = int(header[2])
        data = output[offset : offset + size]
        offset += size
        if len(data) != size:
            errors[spec] = "git cat-file --batch returned a truncated blob"
            break
        blobs[spec] = data
        if output[offset : offset + 1] == b"\n":
            offset += 1
    return blobs, errors


def eol_profile(data: bytes | None) -> str:
    if data is None:
        return "MISSING"
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    if b"\x00" in data:
        return "BINARY"
    kinds = sum(n > 0 for n in (crlf, lf, cr))
    if kinds > 1:
        return "MIXED_EOL"
    if crlf:
        return "CRLF"
    if lf:
        return "LF"
    if cr:
        return "CR"
    return "NO_EOL"


def normalize_pin(value: str) -> str:
    match = HEX64.search(value or "")
    return match.group(0).lower() if match else ""


def normalized_commit(value: str) -> str:
    value = (value or "").strip()
    match = re.search(r"(?i)\b[0-9a-f]{7,40}\b", value)
    return match.group(0) if match else ("HEAD" if value == "HEAD" else "")


def repo_relative(path: str) -> bool:
    path = path.replace("\\", "/").strip()
    if not path or path in {"-", "—", "N/A", "NOT_APPLICABLE"}:
        return False
    if re.search(r"\s\+\s", path):
        return False
    if re.match(r"^[A-Za-z]:/", path) or path.startswith("//") or path.startswith("/"):
        return False
    normalized = (ROOT / Path(*PurePosixPath(path).parts)).resolve()
    try:
        normalized.relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def enrich(
    record: dict[str, str],
    measured_head: str,
    blobs: dict[str, bytes],
    blob_errors: dict[str, str],
    eol_map: dict[str, tuple[str, str, str]],
    attrs: dict[str, list[str]],
) -> dict[str, object]:
    path = record.get("path", "").replace("\\", "/")
    original_commit = record.get("commit", "")
    commit = normalized_commit(original_commit)
    pin = normalize_pin(record.get("pin_sha256", "") or record.get("sha256", ""))
    if record.get("class") == "FROZEN_PIN":
        commit_for_measurement = measured_head
    else:
        commit_for_measurement = commit
    is_composite = bool(re.search(r"\s\+\s", path))
    is_repo = repo_relative(path)
    work_path = ROOT / Path(*PurePosixPath(path).parts) if is_repo else (Path(path) if path and Path(path).is_absolute() else None)
    work_data = work_path.read_bytes() if work_path and work_path.is_file() else None
    spec = f"{commit_for_measurement}:{path}" if is_repo and commit_for_measurement and path else ""
    blob_data = blobs.get(spec)
    blob_error = blob_errors.get(spec)
    wsha, bsha = sha(work_data), sha(blob_data)
    bmatch = bool(pin and bsha and pin == bsha)
    wmatch = bool(pin and wsha and pin == wsha)
    if not pin:
        basis = "UNPINNED"
    elif is_composite:
        basis = "COMPOSITE_PATH"
    elif not path or path in {"-", "—", "N/A", "NOT_APPLICABLE"}:
        basis = "UNRESOLVED_PATH"
    elif not is_repo and work_data is None:
        basis = "EXTERNAL_UNAVAILABLE"
    elif not is_repo and wmatch:
        basis = "WORKTREE"
    elif not is_repo:
        basis = "EXTERNAL_UNVERIFIED"
    elif record.get("class") != "FROZEN_PIN" and not commit:
        basis = "WORKTREE" if wmatch else "UNRESOLVED_COMMIT"
    elif bmatch and wmatch:
        basis = "MIXED"
    elif bmatch:
        basis = "BLOB"
    elif wmatch:
        basis = "WORKTREE"
    elif bsha is None and wsha is None:
        basis = "MISSING"
    else:
        basis = "INCONSISTENT"
    index_eol, worktree_eol, tracked_attributes = eol_map.get(path, ("not-in-index", "not-in-index", ""))
    return {
        **record,
        "path": path,
        "path_scope": "COMPOSITE" if is_composite else ("REPOSITORY" if is_repo else ("EXTERNAL" if work_path else "UNRESOLVED")),
        "pin_sha256": pin,
        "measurement_commit": commit_for_measurement,
        "commit_has_path": blob_data is not None if is_repo else None,
        "commit_field_present": bool(original_commit),
        "worktree_exists": work_data is not None,
        "worktree_sha256": wsha,
        "blob_sha256": bsha,
        "pin_matches_worktree": wmatch,
        "pin_matches_blob": bmatch,
        "basis": basis,
        "worktree_eol_profile": eol_profile(work_data),
        "blob_eol_profile": eol_profile(blob_data),
        "index_eol": index_eol,
        "worktree_eol": worktree_eol,
        "attributes": ";".join(attrs.get(path, [])) or tracked_attributes or ("UNSPECIFIED" if is_repo else ("NOT_APPLICABLE_EXTERNAL" if work_path else "UNKNOWN")),
        "blob_error": blob_error,
    }


def main() -> None:
    head_proc = git("rev-parse", "HEAD", check=True)
    head = head_proc.stdout.decode().strip()
    branch = git("branch", "--show-current", check=True).stdout.decode().strip()
    tracked = git("ls-files", "-z", check=True).stdout.decode("utf-8", "surrogateescape").split("\0")
    tracked = [p for p in tracked if p]
    task_files = [p for p in tracked if p.startswith("doc/tasks/") and p.endswith(".md")]
    expected_map = verify_pins_map()
    records: list[dict[str, str]] = []
    task_counts: dict[str, int] = {}
    for path in task_files:
        rows = parse_table_rows(path)
        task_counts[path] = len(rows)
        for row in rows:
            records.append(
                {
                    "source_file": path,
                    "evidence_id": row.get("evidence_id", ""),
                    "ac_gate": row.get("ac/gate", ""),
                    "path": row.get("path", ""),
                    "commit": row.get("commit", ""),
                    "pin_sha256": row.get("sha256", ""),
                    "class": row.get("class", ""),
                    "expected_source_filename": "",
                    "commit_field_present": bool(row.get("commit", "")),
                }
            )
    records.extend(frozen_records(tracked, expected_map))

    specs = sorted(
        {
            f"{normalized_commit(record.get('commit', '')) or head}:{record.get('path', '').replace('\\', '/')}"
            for record in records
            if record.get("path") and repo_relative(record.get("path", ""))
        }
    )
    blobs, blob_errors = blob_map(specs)
    unique_paths = sorted(
        {
            record.get("path", "").replace("\\", "/")
            for record in records
            if record.get("path") and repo_relative(record.get("path", ""))
        }
    )
    eol_map = indexed_eol_map()
    attrs = attribute_map(unique_paths)
    rows = [enrich(record, head, blobs, blob_errors, eol_map, attrs) for record in records]
    unique_files: dict[str, dict[str, object]] = {}
    for row in rows:
        if row.get("path_scope") != "REPOSITORY":
            continue
        path = str(row["path"])
        if path in unique_files:
            continue
        file_path = ROOT / Path(*PurePosixPath(path).parts)
        exists = file_path.is_file()
        unique_files[path] = {
            "path": path,
            "worktree_eol_profile": row["worktree_eol_profile"],
            "attributes": row["attributes"],
            "worktree_exists": exists,
            "size_bytes": file_path.stat().st_size if exists else 0,
        }
    basis_counts = Counter(str(r["basis"]) for r in rows)
    eol_counts = Counter(str(r["worktree_eol_profile"]) for r in rows)
    class_counts = Counter(str(r.get("class") or "UNSPECIFIED_CLASS") for r in rows)
    unique_eol_counts = Counter(str(r["worktree_eol_profile"]) for r in unique_files.values())
    unique_attribute_counts = Counter(str(r["attributes"]) for r in unique_files.values())
    contract_checks = []
    for record in rows:
        if record.get("class") != "FROZEN_PIN":
            continue
        expected = expected_map.get(str(record["source_file"]).split("FEA-CONTRACT-FROZEN-", 1)[-1].removesuffix(".md"), "")
        contract_checks.append(
            {
                "source_file": record["source_file"],
                "path_matches_verify_pins_map": str(record["path"]).endswith(expected) if expected else False,
                "mapped_contract": expected,
                "basis": record["basis"],
            }
        )
    errors = [
        {"source_file": r["source_file"], "evidence_id": r["evidence_id"], "reason": r["basis"]}
        for r in rows
        if r["basis"] in {"INCONSISTENT", "MISSING", "UNPINNED", "UNRESOLVED_PATH", "COMPOSITE_PATH", "UNRESOLVED_COMMIT", "EXTERNAL_UNAVAILABLE", "EXTERNAL_UNVERIFIED"}
    ]
    autocrlf = git("config", "--show-origin", "--get-all", "core.autocrlf").stdout.decode("utf-8", "replace").splitlines()
    system_autocrlf = git("config", "--system", "--show-origin", "--get", "core.autocrlf").stdout.decode("utf-8", "replace").splitlines()
    tracked_diff = git("diff", "--quiet").returncode == 0 and git("diff", "--cached", "--quiet").returncode == 0
    status_porcelain = git("status", "--porcelain").stdout.decode("utf-8", "replace").splitlines()
    output = {
        "schema_version": 1,
        "generated_at_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "branch": branch,
        "measured_head": head,
        "tracked_task_card_count": len(task_files),
        "task_cards_with_canonical_evidence_rows": sum(n > 0 for n in task_counts.values()),
        "task_card_pin_rows": sum(task_counts.values()),
        "frozen_contract_record_count": sum(r.get("class") == "FROZEN_PIN" for r in rows),
        "verify_pins_map_count": len(expected_map),
        "total_pin_rows": len(rows),
        "measurement_environment": {
            "git_version": git("--version").stdout.decode("utf-8", "replace").strip(),
            "core_autocrlf_effective_with_origin": autocrlf,
            "core_autocrlf_system_with_origin": system_autocrlf,
            "tracked_worktree_and_index_clean": tracked_diff,
            "status_porcelain": status_porcelain,
        },
        "basis_counts": dict(sorted(basis_counts.items())),
        "worktree_eol_profile_counts": dict(sorted(eol_counts.items())),
        "class_counts": dict(sorted(class_counts.items())),
        "unique_repository_path_count": len(unique_files),
        "unique_repository_paths_present": sum(bool(r["worktree_exists"]) for r in unique_files.values()),
        "unique_repository_path_bytes_present": sum(int(r["size_bytes"]) for r in unique_files.values()),
        "unique_repository_paths_by_worktree_eol_profile": dict(sorted(unique_eol_counts.items())),
        "unique_repository_paths_by_attribute_state": dict(sorted(unique_attribute_counts.items())),
        "frozen_contract_map_checks": contract_checks,
        "exceptions": errors,
        "records": rows,
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"HEAD={head}")
    print(f"TASK_CARDS={len(task_files)} TASK_PIN_ROWS={sum(task_counts.values())}")
    print(f"FROZEN_RECORDS={output['frozen_contract_record_count']} VERIFY_PINS_MAP={len(expected_map)}")
    print(f"TOTAL_PIN_ROWS={len(rows)} BASIS_COUNTS={dict(sorted(basis_counts.items()))}")
    print(f"WORKTREE_EOL_PROFILES={dict(sorted(eol_counts.items()))}")
    print(f"UNIQUE_REPOSITORY_PATHS={len(unique_files)} PRESENT={output['unique_repository_paths_present']} BY_EOL={dict(sorted(unique_eol_counts.items()))}")
    print(f"EXCEPTIONS={len(errors)} OUTPUT={OUT.relative_to(ROOT)}")
    if len(expected_map) != 18 or output["frozen_contract_record_count"] != 18:
        raise SystemExit("expected exactly 18 frozen contract records and verify_pins entries")


if __name__ == "__main__":
    main()
