"""L-F1-3-PERF-4: wire-level serialisation criterion (NOT a disk benchmark).

Why this exists
---------------
`L-F1-3` asked for a concurrency soak. The three earlier attempts measured *disk* concurrency
and all three were invalid -- this machine has 31.6 GB of RAM and every fixture stayed in the
page cache, so the numbers described memory bandwidth rather than disk. See
`verification/L-F1-3-PERF-1/2/3/README.md`.

The product-relevant question is different and much cheaper to answer:

    `CoreServiceClient._pipeGate` is a `SemaphoreSlim(1, 1)` -- the pipeline is *deliberately*
    serialised (CORE-PIPE-EXCLUSIVE-1) to prevent the response-mismatch class of defect (E-6).

So the criterion is:

    concurrent wall time  ~=  N x single-request latency   => serialisation in effect (PASS)
    concurrent wall time  <<  N x single-request latency   => serialisation lost   (DEFECT)

Plus the correctness half, which is what actually protects users:

    every response must carry the request_id of its own request -- no cross-talk.

This script drives the real `bootstrap.core_service` over stdin/stdout, exactly like
`tests/core/test_core_service.py` does. It uses `core.ping` (no fixture, no disk), so the only
thing being measured is the protocol's behaviour.
"""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

PROTOCOL_NAME = "newmanga.core"
REQUEST_COUNT = 40


def _env(data_root: Path, src_root: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("NEWMANGA_")}
    env["NEWMANGA_DATA_ROOT"] = str(data_root)
    env["PYTHONPATH"] = str(src_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _command(request_id: str) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "version": {"major": 2, "minor": 0},
        "request_id": request_id,
        "command": "core.ping",
        "payload": {},
    }


def main() -> int:
    # tools/perf/<this file> -> parents[2] is the repo root (parents[1] is tools/).
    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"
    data_root = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / ".perf4-data"
    data_root.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [sys.executable, "-m", "bootstrap.core_service"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=_env(data_root, src_root),
        cwd=str(repo_root),
    )

    write_lock = threading.Lock()
    read_lock = threading.Lock()
    failures: list[str] = []

    def send_and_recv(request_id: str) -> float:
        """One request/response round trip. Returns latency in seconds."""
        payload = json.dumps(_command(request_id))
        started = time.perf_counter()
        with write_lock:
            proc.stdin.write(payload + "\n")  # type: ignore[union-attr]
            proc.stdin.flush()  # type: ignore[union-attr]
        with read_lock:
            line = proc.stdout.readline()  # type: ignore[union-attr]
        elapsed = time.perf_counter() - started
        if not line:
            failures.append(f"{request_id}: empty response")
            return elapsed
        response = json.loads(line)
        if response.get("request_id") != request_id:
            # This is the E-6 class of defect: a response delivered to the wrong caller.
            failures.append(
                f"{request_id}: got response for {response.get('request_id')!r}"
            )
        return elapsed

    try:
        # Warm-up: the first request pays module/import cost and would skew the baseline.
        send_and_recv("warmup")
        failures.clear()

        # --- serial baseline -------------------------------------------------------------
        serial_latencies = [send_and_recv(f"s-{i}") for i in range(REQUEST_COUNT)]
        serial_wall = sum(serial_latencies)

        # --- concurrent ------------------------------------------------------------------
        concurrent_latencies: list[float] = [0.0] * REQUEST_COUNT

        def worker(index: int) -> None:
            concurrent_latencies[index] = send_and_recv(f"c-{index}")

        started = time.perf_counter()
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(REQUEST_COUNT)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        concurrent_wall = time.perf_counter() - started

        serial_median = statistics.median(serial_latencies)
        concurrent_median = statistics.median(concurrent_latencies)
        expected_concurrent_if_serial = serial_median * REQUEST_COUNT

        print(f"requests={REQUEST_COUNT} command=core.ping")
        print(
            "SERIAL   wall_s={:.3f} median_ms={:.2f} p95_ms={:.2f}".format(
                serial_wall,
                serial_median * 1000,
                sorted(serial_latencies)[int(0.95 * (len(serial_latencies) - 1))] * 1000,
            )
        )
        print(
            "CONCUR   wall_s={:.3f} median_ms={:.2f} p95_ms={:.2f}".format(
                concurrent_wall,
                concurrent_median * 1000,
                sorted(concurrent_latencies)[int(0.95 * (len(concurrent_latencies) - 1))] * 1000,
            )
        )
        print(f"expected_concurrent_if_serial_s={expected_concurrent_if_serial:.3f}")
        ratio = concurrent_wall / expected_concurrent_if_serial if expected_concurrent_if_serial else 0
        print(f"concurrent_vs_expected_serial_ratio={ratio:.2f}")

        if failures:
            print(f"CORRECTNESS=FAIL ({len(failures)} problems)")
            for problem in failures[:5]:
                print(f"  {problem}")
        else:
            print("CORRECTNESS=PASS (every response carried its own request_id)")

        if ratio >= 0.75:
            print("VERDICT=SERIALISED (concurrent wall approaches N x single latency -- as designed)")
        else:
            print("VERDICT=NOT-SERIALISED (concurrent wall well below N x latency -- investigate)")

        return 0 if not failures else 1
    finally:
        try:
            proc.stdin.close()  # type: ignore[union-attr]
        except Exception:
            pass
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        stderr = proc.stderr.read() if proc.stderr else ""
        if stderr.strip():
            print("--- core_service stderr (tail) ---")
            print(stderr.strip()[-800:])


if __name__ == "__main__":
    raise SystemExit(main())
