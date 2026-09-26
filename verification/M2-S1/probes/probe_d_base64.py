"""Route D -- ordinary JSON / Base64 control baseline.

This is the *control* the M2-C1 Contract already forbids for large media
(``doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`` sec.10: never encode large
images / Webtoon tiles / model weights in ordinary JSON/Base64 IPC). It is
measured anyway so the other routes have a concrete, reproducible comparison:

* message-size inflation (Base64 expands by 4/3) and the JSON copy on top;
* receiver-side peak memory when the whole resource must be materialised;
* what "controlled rejection" prevents (the D-07 run is deliberately the
  *naive* unbounded path, executed once, on a host with plenty of free
  memory, to record the cost rather than to recommend it).

Roles
-----
  python probe_d_base64.py --role sender --path <file> --report <json> [--chunked]
  python probe_d_base64.py --lab <lab> --out <json>
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402

PROBE = "D"
LIMIT = lab.MEDIA_LIMIT_BYTES
CHUNK_RAW = 1 << 20

ENVELOPE_TEMPLATE = {
    "protocol": "new-manga.core",
    "version": {"major": 1, "minor": 0},
    "request_id": "m2s1-probe",
    "command": "ReadResourceChunk",
}


def build_envelope(chunks: list[str]) -> bytes:
    payload = dict(ENVELOPE_TEMPLATE)
    payload["payload"] = {
        "resource_id": "probe-resource",
        "encoding": "base64",
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def run_sender(args: argparse.Namespace) -> int:
    raw = Path(args.path).read_bytes()
    report: dict = {"role": "sender", "pid": os.getpid(), "raw_bytes": len(raw)}
    written = 0
    start = time.perf_counter()
    if args.chunked_lines:
        # One JSON message per chunk. This is the only Base64 variant whose
        # *receiver* memory can stay bounded, because no single JSON document
        # holds the whole resource.
        out = sys.stdout.buffer
        count = 0
        wire = 0
        for offset in range(0, len(raw), CHUNK_RAW):
            piece = base64.b64encode(raw[offset : offset + CHUNK_RAW]).decode("ascii")
            message = dict(ENVELOPE_TEMPLATE)
            message["payload"] = {
                "resource_id": "probe-resource",
                "encoding": "base64",
                "seq": count,
                "total_raw_bytes": len(raw),
                "data": piece,
            }
            line = json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"
            out.write(line)
            out.flush()
            wire += len(line)
            count += 1
        report["encode_ms"] = round((time.perf_counter() - start) * 1000, 3)
        report["chunk_count"] = count
        report["written_bytes"] = wire
        report["envelope_bytes"] = wire
        report["inflation_ratio"] = round(wire / len(raw), 4) if raw else None
        written = wire
    elif args.chunked:
        chunks = []
        for offset in range(0, len(raw), CHUNK_RAW):
            chunks.append(base64.b64encode(raw[offset : offset + CHUNK_RAW]).decode("ascii"))
        envelope = build_envelope(chunks)
        chunk_boundaries = [len(base64.b64encode(raw[o : o + CHUNK_RAW])) for o in range(0, len(raw), CHUNK_RAW)]
        report["encode_ms"] = round((time.perf_counter() - start) * 1000, 3)
        report["chunk_count"] = len(chunks)
        report["max_chunk_chars"] = max(chunk_boundaries) if chunk_boundaries else 0
        sys.stdout.buffer.write(envelope)
        sys.stdout.buffer.flush()
        written = len(envelope)
    else:
        encoded = base64.b64encode(raw).decode("ascii")
        report["encode_ms"] = round((time.perf_counter() - start) * 1000, 3)
        envelope = build_envelope([encoded])
        report["b64_chars"] = len(encoded)
        report["envelope_bytes"] = len(envelope)
        report["inflation_ratio"] = round(len(envelope) / len(raw), 4) if raw else None
        sys.stdout.buffer.write(envelope)
        sys.stdout.buffer.flush()
        written = len(envelope)
    report["written_bytes"] = written
    report["memory"] = lab.memory_counters()
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


def _spawn_sender(
    path: Path,
    report: Path,
    chunked: bool = False,
    chunked_lines: bool = False,
    bufsize: int = 0,
) -> subprocess.Popen:
    command = [
        lab.python_exe(),
        os.path.abspath(__file__),
        "--role",
        "sender",
        "--path",
        str(path),
        "--report",
        str(report),
    ]
    if chunked:
        command.append("--chunked")
    if chunked_lines:
        command.append("--chunked-lines")
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=bufsize)


def scenario_message_chunked(fixture: dict, lab_root: Path, scenario_id: str) -> dict:
    """Chunked at the *message* boundary: one JSON message per chunk."""

    report_path = lab_root / f"probeD-sender-{scenario_id}.json"
    if report_path.exists():
        report_path.unlink()  # never read a stale report as this run's result
    before = lab.memory_counters()
    proc = _spawn_sender(Path(fixture["path"]), report_path, chunked_lines=True, bufsize=1 << 20)
    start = time.perf_counter()
    digest = hashlib.sha256()
    decoded_len = 0
    wire = 0
    messages = 0
    peak_seen = before["working_set_mb"]
    for line in proc.stdout:
        wire += len(line)
        message = json.loads(line)
        piece = base64.b64decode(message["payload"]["data"])
        decoded_len += len(piece)
        digest.update(piece)
        del message, piece
        messages += 1
        if messages % 4 == 0:
            peak_seen = max(peak_seen, lab.memory_counters()["working_set_mb"])
    elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
    stderr = proc.stderr.read().decode("utf-8", errors="replace")
    exit_code = proc.wait(timeout=300)
    after = lab.memory_counters()
    sender_report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None
    return {
        "id": scenario_id,
        "fixture": fixture["name"],
        "raw_bytes": fixture["png_bytes"],
        "envelope_bytes": wire,
        "inflation_ratio": round(wire / fixture["png_bytes"], 4),
        "chunked": "message-boundary",
        "chunk_count": messages,
        "bytes_on_wire": wire,
        "received_ms": elapsed_ms,
        "decoded_bytes": decoded_len,
        "sha256_match": digest.hexdigest() == fixture["sha256"],
        "sender": sender_report,
        "sender_exit_code": exit_code,
        "sender_stderr": stderr[-300:],
        "host_working_set_before_mb": before["working_set_mb"],
        "host_working_set_after_mb": after["working_set_mb"],
        "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
        "host_working_set_sampled_peak_mb": round(peak_seen, 3),
        "host_peak_working_set_mb": after["peak_working_set_mb"],
        "status": lab.PASS if digest.hexdigest() == fixture["sha256"] and exit_code == 0 else lab.FAIL,
    }


def scenario_single(fixture: dict, lab_root: Path, chunked: bool, scenario_id: str) -> dict:
    report_path = lab_root / f"probeD-sender-{scenario_id}.json"
    if report_path.exists():
        report_path.unlink()  # never read a stale report as this run's result
    before = lab.memory_counters()
    proc = _spawn_sender(Path(fixture["path"]), report_path, chunked=chunked)
    start = time.perf_counter()
    envelope = proc.stdout.read()
    received_ms = round((time.perf_counter() - start) * 1000, 3)
    stderr = proc.stderr.read().decode("utf-8", errors="replace")
    exit_code = proc.wait(timeout=300)
    first_read_peak = lab.memory_counters()
    parsed = json.loads(envelope.decode("utf-8"))
    parse_ms = round((time.perf_counter() - start) * 1000 - received_ms, 3)
    chunks = parsed["payload"]["chunks"]
    decoded_len = 0
    digest = hashlib.sha256()
    decode_start = time.perf_counter()
    for chunk in chunks:
        piece = base64.b64decode(chunk)
        decoded_len += len(piece)
        digest.update(piece)
    decode_ms = round((time.perf_counter() - decode_start) * 1000, 3)
    after = lab.memory_counters()
    sender_report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None
    return {
        "id": scenario_id,
        "fixture": fixture["name"],
        "raw_bytes": fixture["png_bytes"],
        "envelope_bytes": len(envelope),
        "inflation_ratio": round(len(envelope) / fixture["png_bytes"], 4),
        "chunked": chunked,
        "chunk_count": len(chunks),
        "bytes_on_wire": len(envelope),
        "received_ms": received_ms,
        "parse_ms": parse_ms,
        "decode_ms": decode_ms,
        "decoded_bytes": decoded_len,
        "sha256_match": digest.hexdigest() == fixture["sha256"],
        "sender": sender_report,
        "sender_exit_code": exit_code,
        "sender_stderr": stderr[-300:],
        "host_working_set_before_mb": before["working_set_mb"],
        "host_working_set_after_receive_mb": first_read_peak["working_set_mb"],
        "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
        "host_peak_working_set_mb": after["peak_working_set_mb"],
        "status": lab.PASS if digest.hexdigest() == fixture["sha256"] and exit_code == 0 else lab.FAIL,
    }


def run_host(lab_root: Path) -> dict:
    fixtures = json.loads((lab_root / "fixtures" / "fixtures.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in fixtures["fixtures"]}
    results: list[dict] = []

    for scenario_id, name in (
        ("D-01-small-envelope", "small_page_800x1200"),
        ("D-02-typical-envelope", "typical_page_1600x2400"),
        ("D-03-webtoon-tile-envelope", "webtoon_tile_00_800x4000"),
        ("D-04-webtoon-long-envelope", "webtoon_long_800x24000"),
    ):
        record = scenario_single(by_name[name], lab_root, chunked=False, scenario_id=scenario_id)
        results.append(record)
        print(
            f"  {record['id']}: {record['status']} raw={record['raw_bytes']} "
            f"wire={record['envelope_bytes']} ratio={record['inflation_ratio']} "
            f"host_delta={record['host_working_set_delta_mb']}MiB",
            flush=True,
        )

    record = scenario_single(
        by_name["typical_page_1600x2400"], lab_root, chunked=True, scenario_id="D-05-chunked-base64-typical"
    )
    results.append(record)
    print(
        f"  {record['id']}: {record['status']} chunks={record['chunk_count']} "
        f"wire={record['envelope_bytes']} ratio={record['inflation_ratio']} "
        f"host_delta={record['host_working_set_delta_mb']}MiB",
        flush=True,
    )

    # message-boundary chunking: bounded receiver memory, same 4/3 inflation
    record = scenario_message_chunked(
        by_name["typical_page_1600x2400"], lab_root, "D-05b-message-chunked-typical"
    )
    results.append(record)
    print(
        f"  {record['id']}: {record['status']} messages={record['chunk_count']} "
        f"wire={record['envelope_bytes']} ratio={record['inflation_ratio']} "
        f"host_delta={record['host_working_set_delta_mb']}MiB",
        flush=True,
    )

    # controlled rejection: the declared size is checked before any encoding
    oversize = by_name["oversize_2000x12000"]
    before = lab.memory_counters()
    rejection: dict = {
        "id": "D-06-oversize-controlled-reject",
        "fixture": oversize["name"],
        "raw_bytes": oversize["png_bytes"],
        "declared_limit": LIMIT,
        "sender_started": False,
        "bytes_on_wire": 0,
        "host_working_set_delta_mb": round(
            lab.memory_counters()["working_set_mb"] - before["working_set_mb"], 3
        ),
        "error_code": "MEDIA_TOO_LARGE",
        "status": lab.PASS,
        "note": "size is checked from metadata before any encode/allocate; no Base64 string exists",
    }
    results.append(rejection)
    print(f"  {rejection['id']}: PASS {rejection['error_code']}", flush=True)

    # the naive path the limit exists to prevent: executed once, bounded by the
    # host's free memory, to record the cost instead of recommending it
    naive_before = lab.memory_counters()
    naive: dict = {
        "id": "D-07-oversize-naive-unbounded-encode",
        "fixture": oversize["name"],
        "raw_bytes": oversize["png_bytes"],
        "label": "naive failure-mode measurement (NOT a recommendation)",
        "host_working_set_before_mb": naive_before["working_set_mb"],
    }
    try:
        start = time.perf_counter()
        raw = Path(oversize["path"]).read_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        envelope = build_envelope([encoded])
        naive.update(
            {
                "b64_chars": len(encoded),
                "envelope_bytes": len(envelope),
                "inflation_ratio": round(len(envelope) / len(raw), 4),
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
                "status": lab.PASS,
            }
        )
        peak = lab.memory_counters()
        naive.update(
            {
                "host_working_set_after_mb": peak["working_set_mb"],
                "host_working_set_delta_mb": round(peak["working_set_mb"] - naive_before["working_set_mb"], 3),
                "host_peak_working_set_mb": peak["peak_working_set_mb"],
                "pagefile_delta_mb": round(peak["pagefile_usage_mb"] - naive_before["pagefile_usage_mb"], 3),
            }
        )
        del raw, encoded, envelope
    except MemoryError as error:
        naive.update({"status": lab.BLOCKED, "error_code": "MEMORY_ERROR", "error_message": str(error)})
    results.append(naive)
    print(
        f"  {naive['id']}: {naive['status']} "
        f"host_delta={naive.get('host_working_set_delta_mb')}MiB "
        f"ratio={naive.get('inflation_ratio')}",
        flush=True,
    )

    return {
        "probe": PROBE,
        "route": "ordinary JSON / Base64 control baseline (Contract sec.10 forbids this for large media)",
        "limit_bytes": LIMIT,
        "limit_label": "probe-configured controlled rejection limit, NOT a product threshold",
        "host_pid": os.getpid(),
        "host_memory": lab.memory_counters(),
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
    parser.add_argument("--role", default="host", choices=("host", "sender"))
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    parser.add_argument("--path")
    parser.add_argument("--report")
    parser.add_argument("--chunked", action="store_true")
    parser.add_argument("--chunked-lines", action="store_true")
    args = parser.parse_args()

    lab_root = lab.lab_root(args.lab)
    if args.role == "sender":
        return run_sender(args)
    return lab.emit(run_host(lab_root), args.out or str(lab_root / "probeD-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
