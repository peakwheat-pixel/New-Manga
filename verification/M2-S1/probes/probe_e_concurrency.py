"""Probe E -- concurrency / capacity across the candidate routes (AC3).

The three routes have different sharing economics, so they are exercised with
the same shape: N concurrent consumers of a ~10 MiB resource.

* E-A  Route A (capability token + file read): N host threads over *one* Core
       control channel; the control plane is serialised by a lock while the
       out-of-band file reads run in parallel.
* E-B  Route B (streaming pipe): N producer processes, one pipe each, read by
       N host threads.
* E-C  Route C (named section): N reader *processes* map the *same* section,
       which is the case shared memory is supposed to win -- one copy, N
       consumers.

Run: python verification/M2-S1/probes/probe_e_concurrency.py --lab <lab> --out <json>
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402
import probe_a_token as pa  # noqa: E402

PROBE = "E"
LIMIT = lab.MEDIA_LIMIT_BYTES
PROBES_DIR = Path(os.path.abspath(__file__)).parent
TILE_FIXTURES = [f"webtoon_tile_{index:02d}_800x4000" for index in range(6)]


class LockedChannel:
    """Serialise the JSON control channel; the file reads stay parallel."""

    def __init__(self, channel) -> None:
        self._channel = channel
        self._lock = threading.Lock()

    def request(self, **payload) -> dict:
        with self._lock:
            return self._channel.request(**payload)


# --------------------------------------------------------------------------
# E-A: route A concurrency
# --------------------------------------------------------------------------


def route_a(lab_root: Path, placed: dict, by_name: dict, consumers: int) -> dict:
    secret = os.urandom(32)
    env = dict(os.environ)
    env["M2S1_TOKEN_SECRET"] = secret.hex()
    scope = lab_root / "probeA" / "scope"
    channel = pa.CoreChannel(
        [lab.python_exe(), str(PROBES_DIR / "probe_a_token.py"), "--role", "core",
         "--lab", str(lab_root), "--scope", str(scope)],
        env,
    )
    locked = LockedChannel(channel)
    assert locked.request(op="ping")["ok"]

    names = [TILE_FIXTURES[index % len(TILE_FIXTURES)] for index in range(consumers)]
    tokens: list[str] = []
    for index, name in enumerate(names):
        minted = locked.request(
            op="mint", rid=f"conc-{index}", rel=placed[name]["rel"], ttl_seconds=300
        )
        tokens.append(minted["ref"])

    errors: list[str] = []
    # Per-worker slots, summed after join: a shared `total += size` from
    # several threads is a lost-update race (measured during development, see
    # verification/M2-S1/02-evidence-manifest.md section 4).
    delivered = [0] * consumers

    def worker(index: int) -> None:
        try:
            resolved = locked.request(op="resolve", ref=tokens[index])
            if not resolved["ok"]:
                errors.append(f"{index}:{resolved['error_code']}")
                return
            path = Path(resolved["path"])
            digest = lab.sha256_file(path)
            if digest != placed[names[index]]["sha256"]:
                errors.append(f"{index}:SHA_MISMATCH")
                return
            delivered[index] = path.stat().st_size
        except Exception as error:  # noqa: BLE001
            errors.append(f"{index}:{type(error).__name__}")

    before = lab.memory_counters()
    threads = [threading.Thread(target=worker, args=(index,)) for index in range(consumers)]
    start = time.perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    elapsed = time.perf_counter() - start
    after = lab.memory_counters()
    channel_info = channel.close()
    total_delivered = sum(delivered)
    return {
        "id": f"E-A-route-A-consumers-{consumers}",
        "consumers": consumers,
        "resource": "webtoon_tile (rotating over 6 tiles)",
        "bytes_delivered": total_delivered,
        "expected_bytes": sum(
            placed[TILE_FIXTURES[index % len(TILE_FIXTURES)]]["bytes"] for index in range(consumers)
        ),
        "errors": errors,
        "control_requests": consumers * 2 + 1,
        "elapsed_ms": round(elapsed * 1000, 3),
        "aggregate_mb_s": round(total_delivered / 1048576 / elapsed, 2) if elapsed else None,
        "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
        "host_peak_working_set_mb": after["peak_working_set_mb"],
        "core_channel": channel_info,
        "status": lab.PASS
        if not errors and total_delivered == sum(
            placed[TILE_FIXTURES[index % len(TILE_FIXTURES)]]["bytes"] for index in range(consumers)
        )
        else lab.FAIL,
    }


# --------------------------------------------------------------------------
# E-B: route B concurrency
# --------------------------------------------------------------------------


def route_b(lab_root: Path, by_name: dict, consumers: int) -> dict:
    report_dir = lab_root / "probeE"
    report_dir.mkdir(parents=True, exist_ok=True)
    names = [TILE_FIXTURES[index % len(TILE_FIXTURES)] for index in range(consumers)]
    processes = []
    digests: list[str] = [""] * consumers
    received = [0] * consumers
    errors: list[str] = []

    def reader(index: int, proc: subprocess.Popen) -> None:
        import hashlib

        digest = hashlib.sha256()
        total = 0
        fd = proc.stdout.fileno()
        while True:
            block = os.read(fd, 1 << 20)
            if not block:
                break
            digest.update(block)
            total += len(block)
        digests[index] = digest.hexdigest()
        received[index] = total

    before = lab.memory_counters()
    start = time.perf_counter()
    for index, name in enumerate(names):
        report = report_dir / f"e-b-producer-{consumers}-{index}.json"
        if report.exists():
            report.unlink()  # never read a stale report as this run's result
        proc = subprocess.Popen(
            [lab.python_exe(), str(PROBES_DIR / "probe_b_stream.py"), "--role", "producer",
             "--path", by_name[name]["path"], "--report", str(report)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        processes.append((name, proc, report))
    threads = [
        threading.Thread(target=reader, args=(index, proc))
        for index, (_name, proc, _report) in enumerate(processes)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for index, (name, proc, _report) in enumerate(processes):
        exit_code = proc.wait(timeout=300)
        if exit_code != 0 or digests[index] != by_name[name]["sha256"]:
            errors.append(f"{index}:{name}:exit={exit_code}")
    elapsed = time.perf_counter() - start
    after = lab.memory_counters()
    return {
        "id": f"E-B-route-B-consumers-{consumers}",
        "consumers": consumers,
        "bytes_delivered": sum(received),
        "errors": errors,
        "elapsed_ms": round(elapsed * 1000, 3),
        "aggregate_mb_s": round(sum(received) / 1048576 / elapsed, 2) if elapsed else None,
        "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
        "host_peak_working_set_mb": after["peak_working_set_mb"],
        "status": lab.PASS if not errors and sum(received) > 0 else lab.FAIL,
    }


# --------------------------------------------------------------------------
# E-C: route C named-section concurrency
# --------------------------------------------------------------------------


def route_c(lab_root: Path, fixture: dict, consumers: int) -> dict:
    work = lab_root / "probeE"
    work.mkdir(parents=True, exist_ok=True)
    name = f"Local\\m2s1-conc-{os.getpid()}-{os.urandom(4).hex()}"
    payload = Path(fixture["path"]).read_bytes()
    handle = lab.create_section(len(payload), name=name)
    pointer = lab.map_section(handle)
    ctypes.memmove(ctypes.c_void_p(pointer), payload, len(payload))

    processes = []
    before = lab.memory_counters()
    start = time.perf_counter()
    for index in range(consumers):
        report = work / f"e-c-reader-{consumers}-{index}.json"
        if report.exists():
            report.unlink()  # never read a stale report as this run's result
        processes.append(
            (
                report,
                subprocess.Popen(
                    [lab.python_exe(), str(PROBES_DIR / "probe_c_section.py"), "--role", "named_reader",
                     "--report", str(report), "--name", name,
                     "--size", str(len(payload)), "--expect-sha", fixture["sha256"]],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ),
            )
        )
    errors: list[str] = []
    matches = 0
    for index, (report, proc) in enumerate(processes):
        code = proc.wait(timeout=600)
        data = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
        if code == 0 and data.get("sha256_match"):
            matches += 1
        else:
            errors.append(f"{index}:exit={code}:{data.get('status')}")
    elapsed = time.perf_counter() - start
    after = lab.memory_counters()
    lab.unmap_section(pointer)
    lab.close_handle(handle)
    return {
        "id": f"E-C-route-C-consumers-{consumers}",
        "consumers": consumers,
        "resource_bytes": len(payload),
        "bytes_read_by_consumers": matches * len(payload),
        "copies_of_payload_in_section": 1,
        "matches": matches,
        "errors": errors,
        "elapsed_ms": round(elapsed * 1000, 3),
        "aggregate_mb_s": round(matches * len(payload) / 1048576 / elapsed, 2) if elapsed else None,
        "host_working_set_delta_mb": round(after["working_set_mb"] - before["working_set_mb"], 3),
        "host_peak_working_set_mb": after["peak_working_set_mb"],
        "status": lab.PASS if not errors and matches == consumers else lab.FAIL,
    }


def run_host(lab_root: Path) -> dict:
    fixtures = json.loads((lab_root / "fixtures" / "fixtures.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in fixtures["fixtures"]}
    seeded = pa.seed_scope(lab_root, lab_root / "fixtures")
    placed = seeded["placed"]
    unavailable = [name for name in TILE_FIXTURES if name not in placed]
    if unavailable:
        return {"probe": PROBE, "status": lab.BLOCKED, "reason": f"missing fixtures: {unavailable}"}

    results: list[dict] = []
    for consumers in (1, 2, 4, 8):
        record = route_a(lab_root, placed, by_name, consumers)
        results.append(record)
        print(
            f"  {record['id']}: {record['status']} bytes={record['bytes_delivered']} "
            f"ms={record['elapsed_ms']} aggMB/s={record['aggregate_mb_s']} errors={record['errors']}",
            flush=True,
        )
    for consumers in (1, 2, 4):
        record = route_b(lab_root, by_name, consumers)
        results.append(record)
        print(
            f"  {record['id']}: {record['status']} bytes={record['bytes_delivered']} "
            f"ms={record['elapsed_ms']} aggMB/s={record['aggregate_mb_s']} errors={record['errors']}",
            flush=True,
        )
    for consumers in (1, 2, 4, 8):
        record = route_c(lab_root, by_name["typical_page_1600x2400"], consumers)
        results.append(record)
        print(
            f"  {record['id']}: {record['status']} matches={record['matches']}/{consumers} "
            f"ms={record['elapsed_ms']} aggMB/s={record['aggregate_mb_s']} errors={record['errors']}",
            flush=True,
        )

    return {
        "probe": PROBE,
        "route": "concurrency / capacity comparison",
        "limit_bytes": LIMIT,
        "logical_processors": os.cpu_count(),
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
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--out")
    args = parser.parse_args()
    lab_root = lab.lab_root(args.lab)
    return lab.emit(run_host(lab_root), args.out or str(lab_root / "probeE-result.json"))


if __name__ == "__main__":
    raise SystemExit(main())
