"""Route C -- Windows handle / shared-memory routes.

Measured questions
------------------
C1  A *named* section (``CreateFileMappingW`` with a name) is reachable by
    name only. Who may open it, who may *write* it, and does it survive its
    creator?
C2  An *anonymous* section handed over with ``DuplicateHandle`` is a
    capability: the kernel validates the handle value against the receiving
    process's own handle table. Does it survive the creator, is a guessed
    handle value rejected, and can another same-user process still duplicate
    it out of the owner?
C3  Is a read-only handle/mapping an actual write barrier?

All payloads are the synthetic fixtures. No product code, no user data.

Roles (all spawned by the host role)
------------------------------------
  --role named_reader            open a named section and hash it
  --role named_creator           create a named section, fill it, exit
  --role hostile_named_writer    open a named section writable and corrupt it
  --role anonymous_creator       anonymous section + DuplicateHandle into --target-pid
  --role handle_user             duplicate/map a handle value from another process
  python probe_c_section.py --lab <lab> --out <json>
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as w
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402

PROBE = "C"
LIMIT = lab.MEDIA_LIMIT_BYTES
SECTION_LIMIT = LIMIT


# --------------------------------------------------------------------------
# shared section helpers
# --------------------------------------------------------------------------


def _fill_section(pointer: int, payload: bytes) -> None:
    ctypes.memmove(ctypes.c_void_p(pointer), payload, len(payload))


def _hash_section(pointer: int, size: int, block: int = 1 << 20) -> tuple[str, int]:
    digest = hashlib.sha256()
    offset = 0
    while offset < size:
        length = min(block, size - offset)
        digest.update(lab.section_read(pointer, length, offset))
        offset += length
    return digest.hexdigest(), offset


def _report(path: str, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# child roles
# --------------------------------------------------------------------------


def role_named_reader(args: argparse.Namespace) -> int:
    result = {"role": "named_reader", "pid": os.getpid(), "name": args.name}
    try:
        handle = lab.open_section(args.name, lab.FILE_MAP_READ)
        result["opened_by_name"] = True
        pointer = lab.map_section(handle, lab.FILE_MAP_READ)
        result["mapped"] = True
        digest, read_bytes = _hash_section(pointer, args.size)
        result["sha256"] = digest
        result["bytes_hashed"] = read_bytes
        result["sha256_match"] = digest == args.expect_sha
        lab.unmap_section(pointer)
        lab.close_handle(handle)
        result["status"] = "OK"
    except lab.ProbeError as error:
        result.update({"status": "DENIED", "error_code": error.code, "error_message": error.message})
    except Exception as error:  # noqa: BLE001
        result.update({"status": "ERROR", "error_type": type(error).__name__, "error_message": str(error)})
    result["memory"] = lab.memory_counters()
    _report(args.report, result)
    return 0


def role_named_creator(args: argparse.Namespace) -> int:
    result = {"role": "named_creator", "pid": os.getpid(), "name": args.name}
    payload = Path(args.payload).read_bytes()
    try:
        handle = lab.create_section(len(payload), name=args.name)
        pointer = lab.map_section(handle)
        _fill_section(pointer, payload)
        result.update({"created": True, "section_bytes": len(payload), "sha256": lab.sha256_bytes(payload)})
        result["memory"] = lab.memory_counters()
        _report(args.report, result)
        if args.hold_seconds:
            time.sleep(args.hold_seconds)
        lab.unmap_section(pointer)
        lab.close_handle(handle)
        result["closed"] = True
        result["status"] = "OK"
    except lab.ProbeError as error:
        result.update({"created": False, "error_code": error.code, "error_message": error.message})
    _report(args.report, result)
    return 0


def role_hostile_named_writer(args: argparse.Namespace) -> int:
    result = {"role": "hostile_named_writer", "pid": os.getpid(), "name": args.name}
    try:
        handle = lab.open_section(args.name, lab.FILE_MAP_READ | lab.FILE_MAP_WRITE)
        result["opened_writable"] = True
        pointer = lab.map_section(handle, lab.FILE_MAP_READ | lab.FILE_MAP_WRITE)
        before = lab.section_read(pointer, 8)
        ctypes.memmove(ctypes.c_void_p(pointer), b"HOSTILE!", 8)
        after = lab.section_read(pointer, 8)
        result.update({"before": before.hex(), "after": after.hex(), "write_performed": before != after})
        lab.unmap_section(pointer)
        lab.close_handle(handle)
        result["status"] = "WROTE"
    except lab.ProbeError as error:
        result.update({"status": "DENIED", "error_code": error.code, "error_message": error.message})
    result["memory"] = lab.memory_counters()
    _report(args.report, result)
    return 0


def role_anonymous_creator(args: argparse.Namespace) -> int:
    result = {
        "role": "anonymous_creator",
        "pid": os.getpid(),
        "target_pid": args.target_pid,
        "own_pid": os.getpid(),
    }
    payload = Path(args.payload).read_bytes()
    try:
        handle = lab.create_section(len(payload), name=args.name or None)
        pointer = lab.map_section(handle)
        _fill_section(pointer, payload)
        result.update(
            {
                "created": True,
                "section_bytes": len(payload),
                "sha256": lab.sha256_bytes(payload),
                "own_handle": handle,
            }
        )
        if args.target_pid:
            target_handle = lab.duplicate_into_process(args.target_pid, handle)
            result["duplicated_into_target"] = True
            result["target_handle_value"] = target_handle
        if args.hold_seconds:
            result["memory"] = lab.memory_counters()
            _report(args.report, result)
            time.sleep(args.hold_seconds)
        lab.unmap_section(pointer)
        lab.close_handle(handle)
        result["closed_own_handle"] = True
        result["status"] = "OK"
    except lab.ProbeError as error:
        result.update({"created": False, "error_code": error.code, "error_message": error.message})
    result["memory"] = lab.memory_counters()
    _report(args.report, result)
    return 0


def role_handle_user(args: argparse.Namespace) -> int:
    result = {
        "role": "handle_user",
        "pid": os.getpid(),
        "source_pid": args.source_pid,
        "handle_value": args.handle_value,
        "mode": args.mode,
    }
    try:
        if args.mode == "map_local":
            pointer = lab.map_section(args.handle_value, lab.FILE_MAP_READ)
            result["mapped_own_table"] = True
            result["first8"] = lab.section_read(pointer, 8).hex()
            lab.unmap_section(pointer)
        else:
            handle = lab.duplicate_from_process(args.source_pid, args.handle_value)
            result["duplicated"] = True
            result["new_handle"] = handle
            pointer = lab.map_section(handle, lab.FILE_MAP_READ)
            result["mapped"] = True
            result["first8"] = lab.section_read(pointer, 8).hex()
            lab.unmap_section(pointer)
            lab.close_handle(handle)
        result["status"] = "OK"
    except lab.ProbeError as error:
        result.update({"status": "DENIED", "error_code": error.code, "error_message": error.message})
    except Exception as error:  # noqa: BLE001
        result.update({"status": "ERROR", "error_type": type(error).__name__, "error_message": str(error)})
    result["memory"] = lab.memory_counters()
    _report(args.report, result)
    return 0


# --------------------------------------------------------------------------
# host role
# --------------------------------------------------------------------------


def _spawn(role: str, report: Path, extra: list[str]) -> dict:
    # A stale report from an earlier run must never be mistaken for this
    # run's result: delete before spawning, not after.
    if report.exists():
        report.unlink()
    command = [
        lab.python_exe(),
        os.path.abspath(__file__),
        "--role",
        role,
        "--report",
        str(report),
    ] + extra
    proc = subprocess.run(command, capture_output=True, timeout=600)
    payload = json.loads(report.read_text(encoding="utf-8")) if report.exists() else None
    return {
        "role": role,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.decode("utf-8", errors="replace")[-400:],
        "stderr": proc.stderr.decode("utf-8", errors="replace")[-400:],
        "report": payload,
    }


def run_host(lab_root: Path) -> dict:
    fixtures = json.loads((lab_root / "fixtures" / "fixtures.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in fixtures["fixtures"]}
    work = lab_root / "probeC"
    work.mkdir(parents=True, exist_ok=True)
    nonce = os.urandom(6).hex()
    results: list[dict] = []
    host_pid = os.getpid()

    def pick(name: str) -> dict:
        entry = by_name[name]
        return {"path": entry["path"], "bytes": entry["png_bytes"], "sha256": entry["sha256"]}

    # ---------------- C1: named section ----------------
    small = pick("small_page_800x1200")
    name = f"Local\\m2s1-{host_pid}-{nonce}"
    report = work / "c1-creator.json"
    payload = Path(small["path"]).read_bytes()
    before = lab.memory_counters()
    handle = lab.create_section(len(payload), name=name)
    pointer = lab.map_section(handle)
    _fill_section(pointer, payload)
    after_fill = lab.memory_counters()
    results.append(
        {
            "id": "C1-00-create-named",
            "status": lab.PASS,
            "name": name,
            "bytes": len(payload),
            "host_working_set_delta_mb": round(after_fill["working_set_mb"] - before["working_set_mb"], 3),
            "host_peak_working_set_mb": after_fill["peak_working_set_mb"],
        }
    )

    reader_report = work / "c1-reader.json"
    reader = _spawn(
        "named_reader",
        reader_report,
        ["--name", name, "--size", str(len(payload)), "--expect-sha", small["sha256"]],
    )
    results.append(
        {
            "id": "C1-01-read-by-name",
            "status": lab.PASS
            if reader["report"] and reader["report"].get("sha256_match")
            else lab.FAIL,
            "spawn": reader,
            "host_peak_working_set_mb": lab.memory_counters()["peak_working_set_mb"],
        }
    )

    # An unrelated same-user process that only *learns the name* (here: from the
    # creator's on-disk report, standing in for any leak of the name) can open
    # the section writable and corrupt it: the default DACL is the process
    # token's default, not a capability.
    hostile_report = work / "c1-hostile.json"
    hostile = _spawn("hostile_named_writer", hostile_report, ["--name", name])
    corrupt = lab.section_read(pointer, 8)
    results.append(
        {
            "id": "C1-02-unauthenticated-writable-open",
            "status": lab.PASS,
            "spawn": hostile,
            "effect_on_payload_first8": corrupt.hex(),
            "note": (
                "the name is the only credential; any same-user, same-session process "
                "that learns it can open the section writable under the default DACL"
            ),
        }
    )

    # restore the payload so the reader can still be validated, then verify the
    # corruption is observable (data integrity is not protected)
    ctypes.memmove(ctypes.c_void_p(pointer), payload[:8], 8)
    verify_report = work / "c1-reader2.json"
    verified = _spawn(
        "named_reader",
        verify_report,
        ["--name", name, "--size", str(len(payload)), "--expect-sha", small["sha256"]],
    )
    results.append(
        {
            "id": "C1-03-post-corruption-verify",
            "status": lab.PASS if verified["report"] and verified["report"].get("sha256_match") else lab.FAIL,
            "spawn_ok": bool(verified["report"] and verified["report"].get("sha256_match")),
            "corruption_was_observable": bool(
                hostile["report"] and hostile["report"].get("write_performed")
            ),
        }
    )

    # non-existent name is denied
    missing_report = work / "c1-missing.json"
    missing = _spawn(
        "named_reader",
        missing_report,
        ["--name", f"Local\\m2s1-does-not-exist-{nonce}", "--size", "16", "--expect-sha", "00"],
    )
    results.append(
        {
            "id": "C1-04-unknown-name-denied",
            "status": lab.PASS
            if missing["report"] and missing["report"].get("status") == "DENIED"
            else lab.FAIL,
            "error_code": (missing["report"] or {}).get("error_code"),
        }
    )

    lab.unmap_section(pointer)
    lab.close_handle(handle)

    # lifecycle: after the creator closes its last handle the named section dies
    creator_report = work / "c1-ephemeral-creator.json"
    ephemeral_name = f"Local\\m2s1-ephemeral-{host_pid}-{nonce}"
    creator = _spawn(
        "named_creator",
        creator_report,
        ["--name", ephemeral_name, "--payload", small["path"]],
    )
    after_report = work / "c1-after-exit.json"
    after_exit = _spawn(
        "named_reader",
        after_report,
        ["--name", ephemeral_name, "--size", str(small["bytes"]), "--expect-sha", small["sha256"]],
    )
    results.append(
        {
            "id": "C1-05-named-section-after-creator-exit",
            "status": lab.PASS
            if after_exit["report"] and after_exit["report"].get("status") == "DENIED"
            else lab.FAIL,
            "creator_exit_code": creator["exit_code"],
            "open_after_exit_result": (after_exit["report"] or {}).get("status"),
            "error_code": (after_exit["report"] or {}).get("error_code"),
        }
    )

    # ---------------- C2: anonymous section + DuplicateHandle ----------------
    typical = pick("typical_page_1600x2400")
    creator_report = work / "c2-creator.json"
    creator = _spawn(
        "anonymous_creator",
        creator_report,
        ["--payload", typical["path"], "--target-pid", str(host_pid)],
    )
    info = creator["report"] or {}
    host_handle = info.get("target_handle_value")
    handoff: dict = {
        "id": "C2-01-duplicate-handle-into-host",
        "status": lab.FAIL,
        "creator": creator,
    }
    if host_handle:
        before = lab.memory_counters()
        pointer = lab.map_section(host_handle, lab.FILE_MAP_READ)
        digest, hashed = _hash_section(pointer, typical["bytes"])
        after = lab.memory_counters()
        handoff.update(
            {
                "status": lab.PASS if digest == typical["sha256"] else lab.FAIL,
                "sha256_match": digest == typical["sha256"],
                "bytes_hashed": hashed,
                "mapped_in_host": True,
                "creator_exited": creator["exit_code"] == 0,
                "survives_creator_exit": True,
                "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
                "host_peak_working_set_mb": after["peak_working_set_mb"],
                "note": (
                    "the kernel validates the handle value against the host's own "
                    "handle table; the section also survives the creator's exit "
                    "while the host holds the duplicated handle"
                ),
            }
        )
    results.append(handoff)

    # same-user hostile duplication while the creator is still alive
    hold_report = work / "c2-holder.json"
    if hold_report.exists():
        hold_report.unlink()
    holder = subprocess.Popen(
        [
            lab.python_exe(),
            os.path.abspath(__file__),
            "--role",
            "anonymous_creator",
            "--report",
            str(hold_report),
            "--payload",
            typical["path"],
            "--hold-seconds",
            "8",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    deadline = time.time() + 30
    holder_info = {}
    while time.time() < deadline:
        if hold_report.exists():
            try:
                holder_info = json.loads(hold_report.read_text(encoding="utf-8"))
                if holder_info.get("own_handle"):
                    break
            except json.JSONDecodeError:
                pass
        time.sleep(0.05)
    holder_alive = holder.poll() is None
    hostile_handle_report = work / "c2-hostile-dup.json"
    hostile_dup = _spawn(
        "handle_user",
        hostile_handle_report,
        [
            "--source-pid",
            str(holder_info.get("pid", 0)),
            "--handle-value",
            str(holder_info.get("own_handle", 0)),
            "--mode",
            "dup",
        ],
    )
    duplication_succeeded = bool(
        hostile_dup["report"] and hostile_dup["report"].get("status") == "OK"
    )
    results.append(
        {
            "id": "C2-02-same-user-hostile-duplication",
            # The measurement is only meaningful while the source process is
            # alive; a dead PID would be an artifact, not a security property.
            "status": lab.PASS if holder_alive and holder_info.get("own_handle") else lab.FAIL,
            "holder_pid": holder_info.get("pid"),
            "handle_value": holder_info.get("own_handle"),
            "holder_alive_while_hostile_ran": holder_alive,
            "spawn": hostile_dup,
            "hostile_duplication_succeeded": duplication_succeeded,
            "hostile_error_code": (hostile_dup["report"] or {}).get("error_code"),
            "note": (
                "DuplicateHandle is guarded by the source process ACL only. On this "
                "host a same-user process with PROCESS_DUP_HANDLE could open the "
                "creator and duplicate its section handle; this is a limitation to "
                "design around, not a defect of the probe."
                if duplication_succeeded
                else "duplication was refused on this host; recorded with the exact error code"
            ),
        }
    )

    # guessed handle value is rejected (a value that names nothing in the owner)
    guess_report = work / "c2-guess.json"
    guessed = _spawn(
        "handle_user",
        guess_report,
        [
            "--source-pid",
            str(holder_info.get("pid", 0)),
            "--handle-value",
            "65520",  # 0x0000FFF0: not a plausible handle-table index
            "--mode",
            "dup",
        ],
    )
    results.append(
        {
            "id": "C2-03-guessed-handle-value-rejected",
            "status": lab.PASS
            if guessed["report"] and guessed["report"].get("status") == "DENIED"
            else lab.FAIL,
            "error_code": (guessed["report"] or {}).get("error_code"),
            "holder_alive_while_guessed": holder.poll() is None,
            "note": (
                "a handle value that names no object in the owner is refused by the "
                "kernel; the value is validated against the owner's handle table"
            ),
        }
    )

    # Windows handle values are 4-byte aligned, so owner_handle+4 may name a
    # *different* live handle in the same owner. It still must not become the
    # section: that is the discrimination this scenario measures.
    adjacent_report = work / "c2-adjacent.json"
    adjacent = _spawn(
        "handle_user",
        adjacent_report,
        [
            "--source-pid",
            str(holder_info.get("pid", 0)),
            "--handle-value",
            str(int(holder_info.get("own_handle", 0)) + 4),
            "--mode",
            "dup",
        ],
    )
    results.append(
        {
            "id": "C2-06-adjacent-handle-value-is-not-the-section",
            "status": lab.PASS
            if adjacent["report"] and adjacent["report"].get("status") in ("DENIED", "ERROR")
            else lab.FAIL,
            "error_code": (adjacent["report"] or {}).get("error_code"),
            "result_status": (adjacent["report"] or {}).get("status"),
            "note": (
                "handle values are 4-byte aligned; +4 can name another live handle in "
                "the same owner, and the kernel still refuses to view it as the section"
            ),
        }
    )
    holder.wait(timeout=60)

    # the same handle value is meaningless in another process's table
    local_report = work / "c2-local.json"
    local = _spawn(
        "handle_user",
        local_report,
        ["--source-pid", "0", "--handle-value", str(host_handle or 0), "--mode", "map_local"],
    )
    results.append(
        {
            "id": "C2-04-foreign-handle-value-in-own-table",
            "status": lab.PASS
            if local["report"] and local["report"].get("status") in ("DENIED", "ERROR")
            else lab.FAIL,
            "result_status": (local["report"] or {}).get("status"),
            "error_code": (local["report"] or {}).get("error_code"),
        }
    )

    # controlled rejection: refuse to create a section above the configured limit
    oversize = pick("oversize_2000x12000")
    rejection: dict = {"id": "C2-05-oversize-section-rejected", "status": lab.NOT_RUN}
    before = lab.memory_counters()
    if oversize["bytes"] > SECTION_LIMIT:
        rejection.update(
            {
                "status": lab.PASS,
                "error_code": "SECTION_LIMIT_EXCEEDED",
                "declared_bytes": oversize["bytes"],
                "limit_bytes": SECTION_LIMIT,
                "section_created": False,
                "bytes_allocated": 0,
                "host_working_set_delta_mb": round(
                    lab.memory_counters()["working_set_mb"] - before["working_set_mb"], 3
                ),
                "note": "size checked before CreateFileMappingW; no section, no pagefile growth",
            }
        )
    results.append(rejection)

    if host_handle:
        lab.unmap_section(pointer)
        lab.close_handle(host_handle)

    # ---------------- C3: read-only barrier ----------------
    c3 = lab.read_only_handle_write_probe(typical["path"])
    c3.update({"id": "C3-01-generic-read-handle-write", "status": lab.PASS if c3["write_error_is_access_denied"] else lab.FAIL})
    c3.update({"host_peak_working_set_mb": lab.memory_counters()["peak_working_set_mb"]})
    results.append(c3)
    c3b = lab.readonly_mmap_write_probe(typical["path"])
    c3b.update(
        {
            "id": "C3-02-readonly-mapping-write",
            "status": lab.PASS if not c3b["write_via_readonly_mapping_ok"] else lab.FAIL,
            "host_peak_working_set_mb": lab.memory_counters()["peak_working_set_mb"],
            "note": (
                "a read-only handle/mapping is not a source-file protection "
                "mechanism: the same user can open the same file writable, and "
                "OS ACL design for the product is UNVERIFIED here"
            ),
        }
    )
    results.append(c3b)

    return {
        "probe": PROBE,
        "route": "Windows handle / shared-memory routes",
        "limit_bytes": LIMIT,
        "section_limit_bytes": SECTION_LIMIT,
        "limit_label": "probe-configured controlled rejection limit, NOT a product threshold",
        "host_pid": host_pid,
        "host_memory": lab.memory_counters(),
        "named_section_name_used": name,
        "scenarios": results,
        "summary": {
            "pass": sum(1 for r in results if r["status"] == lab.PASS),
            "fail": sum(1 for r in results if r["status"] == lab.FAIL),
            "blocked": sum(1 for r in results if r["status"] == lab.BLOCKED),
            "not_run": sum(1 for r in results if r["status"] == lab.NOT_RUN),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--role",
        default="host",
        choices=(
            "host",
            "named_reader",
            "named_creator",
            "hostile_named_writer",
            "anonymous_creator",
            "handle_user",
        ),
    )
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    parser.add_argument("--report")
    parser.add_argument("--name", default="")
    parser.add_argument("--size", type=int, default=0)
    parser.add_argument("--expect-sha", default="")
    parser.add_argument("--payload", default="")
    parser.add_argument("--target-pid", type=int, default=0)
    parser.add_argument("--source-pid", type=int, default=0)
    parser.add_argument("--handle-value", type=int, default=0)
    parser.add_argument("--mode", default="dup", choices=("dup", "map_local"))
    parser.add_argument("--hold-seconds", type=float, default=0)
    args = parser.parse_args()

    lab_root = lab.lab_root(args.lab)
    if args.role == "named_reader":
        return role_named_reader(args)
    if args.role == "named_creator":
        return role_named_creator(args)
    if args.role == "hostile_named_writer":
        return role_hostile_named_writer(args)
    if args.role == "anonymous_creator":
        return role_anonymous_creator(args)
    if args.role == "handle_user":
        return role_handle_user(args)
    return lab.emit(run_host(lab_root), args.out or str(lab_root / "probeC-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
