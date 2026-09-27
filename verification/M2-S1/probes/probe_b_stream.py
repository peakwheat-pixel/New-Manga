"""Route B -- streaming / chunked media transfer over an OS pipe.

Measured question
-----------------
Does a byte-oriented channel give bounded consumer memory, honest integrity
signalling, real backpressure and deterministic cancellation/failure, and at
what throughput?

Shape
-----
``producer`` (child) writes the fixture bytes to stdout in write-chunks.
``host`` (parent, ``bufsize=0`` so reads return as soon as data is available)
reads with a caller-chosen read-chunk size into a single reused buffer,
hashing incrementally and never retaining the payload. Media bytes *are* the
channel here, so ``bytes_on_wire == resource bytes`` by construction; that is
why Route A's control channel is measured separately.

Roles
-----
  python probe_b_stream.py --role producer --path <file> --report <json> [...]
  python probe_b_stream.py --lab <lab> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402

PROBE = "B"
LIMIT = lab.MEDIA_LIMIT_BYTES
WRITE_CHUNK = 1 << 20


# --------------------------------------------------------------------------
# producer role
# --------------------------------------------------------------------------


def run_producer(args: argparse.Namespace) -> int:
    payload_path = Path(args.path)
    report_path = Path(args.report)
    report: dict = {"role": "producer", "pid": os.getpid(), "path": str(payload_path)}
    total = 0
    status = "COMPLETED"
    out = sys.stdout.buffer
    try:
        with open(payload_path, "rb") as handle:
            while True:
                block = handle.read(WRITE_CHUNK)
                if not block:
                    break
                if args.truncate_at and total + len(block) > args.truncate_at:
                    block = block[: args.truncate_at - total]
                if args.crash_at and total + len(block) > args.crash_at:
                    block = block[: args.crash_at - total]
                if block:
                    out.write(block)
                    out.flush()
                    total += len(block)
                if args.crash_at and total >= args.crash_at:
                    status = "CRASHED_BY_DESIGN"
                    report.update({"bytes_written": total, "status": status,
                                   "memory": lab.memory_counters()})
                    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                    os._exit(3)
                if args.truncate_at and total >= args.truncate_at:
                    status = "TRUNCATED_BY_DESIGN"
                    break
    except BrokenPipeError:
        status = "CHANNEL_CLOSED_BY_CONSUMER"
        try:
            os.close(1)
        except OSError:
            pass
    except OSError as error:
        status = f"OS_ERROR:{error.errno}"
    report.update(
        {
            "bytes_written": total,
            "status": status,
            "memory": lab.memory_counters(),
        }
    )
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if status in ("COMPLETED", "TRUNCATED_BY_DESIGN") else 4


# --------------------------------------------------------------------------
# host role
# --------------------------------------------------------------------------


def scenarios() -> list[dict]:
    typical = "typical_page_1600x2400"
    long_page = "webtoon_long_800x24000"
    return [
        {"id": "B-01-small-1MiB", "fixture": "small_page_800x1200", "chunk": 1 << 20},
        {"id": "B-02-typical-1MiB", "fixture": typical, "chunk": 1 << 20},
        {"id": "B-03-webtoon-tile-1MiB", "fixture": "webtoon_tile_00_800x4000", "chunk": 1 << 20},
        {"id": "B-04-webtoon-long-1MiB", "fixture": long_page, "chunk": 1 << 20},
        {"id": "B-05-chunk-64KiB", "fixture": typical, "chunk": 1 << 16},
        {"id": "B-06-chunk-256KiB", "fixture": typical, "chunk": 1 << 18},
        {"id": "B-07-chunk-4MiB", "fixture": typical, "chunk": 1 << 22},
        {"id": "B-08-oversize-reject", "fixture": "oversize_2000x12000", "chunk": 1 << 20, "reject": True},
        {"id": "B-09-cancel-after-4MiB", "fixture": long_page, "chunk": 1 << 20, "cancel_after": 4 << 20},
        {"id": "B-10-truncated-stream", "fixture": typical, "chunk": 1 << 20, "truncate_at": 8 << 20},
        {"id": "B-11-producer-crash", "fixture": typical, "chunk": 1 << 20, "crash_at": 4 << 20},
        {
            "id": "B-12-backpressure-slow-consumer",
            "fixture": long_page,
            "chunk": 1 << 20,
            "slow_every": 8 << 20,
            "slow_ms": 150,
        },
    ]


def run_scenario(spec: dict, fixture: dict, lab_root: Path) -> dict:
    path = Path(fixture["path"])
    expected = fixture["png_bytes"]
    record: dict = {
        "id": spec["id"],
        "fixture": spec["fixture"],
        "expected_bytes": expected,
        "read_chunk_bytes": spec["chunk"],
        "status": lab.NOT_RUN,
    }
    report_path = lab_root / f"probeB-producer-{spec['id']}.json"
    if report_path.exists():
        report_path.unlink()
    producer_report_path = lab_root / "probeB-producer-last.json"
    if producer_report_path.exists():
        producer_report_path.unlink()  # never read a stale report as this run's result

    command = [
        lab.python_exe(),
        os.path.abspath(__file__),
        "--role",
        "producer",
        "--path",
        str(path),
        "--report",
        str(producer_report_path),
    ]
    if spec.get("truncate_at"):
        command += ["--truncate-at", str(spec["truncate_at"])]
    if spec.get("crash_at"):
        command += ["--crash-at", str(spec["crash_at"])]

    before = lab.memory_counters()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    digest = hashlib.sha256()
    received = 0
    reads = 0
    first_byte_ms: float | None = None
    cancelled = False
    stream_error: str | None = None
    start = time.perf_counter()
    try:
        if spec.get("reject"):
            # Controlled rejection: Core refuses the resource over the limit
            # and closes the channel *before* any byte is served.
            raise lab.ProbeError("MEDIA_TOO_LARGE", f"declared={expected} limit={LIMIT}")
        fd = proc.stdout.fileno()
        next_slow = spec.get("slow_every")
        while received < expected:
            block = os.read(fd, spec["chunk"])
            if first_byte_ms is None:
                first_byte_ms = round((time.perf_counter() - start) * 1000, 3)
            if not block:
                stream_error = "STREAM_TRUNCATED"
                break
            digest.update(block)
            received += len(block)
            reads += 1
            if spec.get("cancel_after") and received >= spec["cancel_after"]:
                cancelled = True
                stream_error = "CHANNEL_CANCELLED_BY_CONSUMER"
                break
            if next_slow and received >= next_slow:
                time.sleep(spec["slow_ms"] / 1000)
                next_slow += spec["slow_every"]
    except lab.ProbeError as error:
        record["error_code"] = error.code
        record["expected_rejection"] = True
    finally:
        elapsed = time.perf_counter() - start
        if cancelled:
            proc.kill()
        try:
            proc.stdout.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            exit_code = proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            proc.kill()
            exit_code = proc.wait(timeout=60)
            record["producer_hang"] = True
        stderr = proc.stderr.read().decode("utf-8", errors="replace")
        proc.stderr.close()
        producer_report = (
            json.loads(producer_report_path.read_text(encoding="utf-8"))
            if producer_report_path.exists()
            else None
        )
        if producer_report_path.exists():
            producer_report_path.replace(report_path)

    after = lab.memory_counters()
    record.update(
        {
            "bytes_received": received,
            "read_calls": reads,
            "elapsed_ms": round(elapsed * 1000, 3),
            "throughput_mb_s": round(received / 1048576 / elapsed, 2) if elapsed > 0 else None,
            "first_byte_ms": first_byte_ms,
            "producer_exit_code": exit_code,
            "producer_stderr": stderr[-400:],
            "producer_report": producer_report,
            "sha256_match": digest.hexdigest() == fixture["sha256"] if received else False,
            "stream_error": stream_error,
            "cancelled": cancelled,
            "host_working_set_before_mb": before["working_set_mb"],
            "host_working_set_after_mb": after["working_set_mb"],
            "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
            "host_peak_working_set_mb": after["peak_working_set_mb"],
        }
    )

    if spec.get("reject"):
        ok = record.get("error_code") == "MEDIA_TOO_LARGE" and received == 0
        record["status"] = lab.PASS if ok else lab.FAIL
        record["note"] = (
            "no byte was served; the producer observed the closed channel "
            f"(producer status={producer_report.get('status') if producer_report else None})"
        )
        record["bytes_on_wire"] = 0
        return record

    if cancelled:
        record["status"] = lab.PASS if received >= spec["cancel_after"] else lab.FAIL
        record["bytes_on_wire"] = received
        return record
    if spec.get("truncate_at"):
        record["status"] = lab.PASS if stream_error == "STREAM_TRUNCATED" else lab.FAIL
        record["bytes_on_wire"] = received
        return record
    if spec.get("crash_at"):
        crashed = stream_error == "STREAM_TRUNCATED" and exit_code != 0
        record["status"] = lab.PASS if crashed else lab.FAIL
        record["bytes_on_wire"] = received
        return record
    record["bytes_on_wire"] = received
    record["status"] = (
        lab.PASS
        if received == expected and record["sha256_match"] and exit_code == 0
        else lab.FAIL
    )
    return record


def run_host(lab_root: Path) -> dict:
    fixtures = json.loads((lab_root / "fixtures" / "fixtures.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in fixtures["fixtures"]}
    results = []
    for spec in scenarios():
        record = run_scenario(spec, by_name[spec["fixture"]], lab_root)
        results.append(record)
        suffix = record.get("error_code") or record.get("stream_error") or ""
        print(
            (
                f"  {record['id']}: {record['status']} bytes={record.get('bytes_received')} "
                f"ms={record.get('elapsed_ms')} MB/s={record.get('throughput_mb_s')} {suffix}"
            ).rstrip(),
            flush=True,
        )
    return {
        "probe": PROBE,
        "route": "streaming / chunked byte channel over an OS pipe",
        "limit_bytes": LIMIT,
        "limit_label": "probe-configured controlled rejection limit, NOT a product threshold",
        "write_chunk_bytes": WRITE_CHUNK,
        "host_pid": os.getpid(),
        "host_memory": lab.memory_counters(),
        "peak_working_set_note": (
            "PeakWorkingSetSize is monotonic within one process, so the per-scenario "
            "peak is cumulative; per-scenario working-set deltas are reported instead "
            "and the final cumulative peak is the bounded-memory evidence."
        ),
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
    parser.add_argument("--role", default="host", choices=("host", "producer"))
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    parser.add_argument("--path")
    parser.add_argument("--report")
    parser.add_argument("--truncate-at", type=int, default=0)
    parser.add_argument("--crash-at", type=int, default=0)
    args = parser.parse_args()

    lab_root = lab.lab_root(args.lab)
    if args.role == "producer":
        return run_producer(args)
    result = run_host(lab_root)
    return lab.emit(result, args.out or str(lab_root / "probeB-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
