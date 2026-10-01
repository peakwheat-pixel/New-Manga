"""M2-TA3-B2-KO-RERUN: K11 minimal-set driver (API-outage resilient).

Runs the K11 minimal execution set automatically once the DeepSeek endpoint
responds again, so the recovery window is not missed while the operator
polls.  Steps (each is the production qualification runner, unmodified
semantics):

  0. probe   : one minimal chat completion; on timeout/exception sleep
               PROBE_INTERVAL_S and retry, up to MAX_PROBES times.
  1. K11 main pass          -> ko-rerun/summaries/qual-K11.json
  2. K11 sfx-policy probe   -> ko-rerun/summaries-sfx/qual-K11.sfx-translate.json
       (settings["sfx"]["policy"]="translate" through the production
        re-assemble sequence; independent pixel root so the main-pass
        export PNG is not clobbered)
  3. K11 determinism rerun  -> ko-rerun/summaries/qual-K11.rerun.json
       (main pass summary already exists -> main loop skips; only .rerun runs)
  4. similarity gate        -> ko-rerun/determinism/K11-similarity.json

Every runner step keeps its own exit code (1 = pipeline failures, which is
EXPECTED for typed registrations and must NOT abort the chain); only a
probe that never recovers or a runner crash (exit code 2 configuration /
unhandled) aborts.  All output goes to the log; nothing here prints or
persists the API key.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
RUNNER = str(REPO_ROOT / "experiments" / "M2-TA3-B" / "run_qualification.py")
SIMILARITY = str(REPO_ROOT / "experiments" / "M2-TA3-B" / "ko_rerun_similarity.py")

OUT_MAIN = str(REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "ko-rerun" / "summaries")
OUT_SFX = str(REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "ko-rerun" / "summaries-sfx")
PIX_MAIN = r"G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-rerun-pixels"
PIX_SFX = r"G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-rerun-pixels-sfx"
LOG_ROOT = r"G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-rerun-logs"

ENV_KEY_NAME = "TA3B_TRANSLATE_API_KEY"
MAX_PROBES = 12
PROBE_INTERVAL_S = 600


def log(msg: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%SZ")
    print(f"[driver {stamp}] {msg}", flush=True)


def probe_ok() -> bool:
    key = os.environ.get(ENV_KEY_NAME)
    if not key:
        log("FATAL: env key missing")
        return False
    body = json.dumps(
        {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "reply with the single word: ok"}],
            "max_tokens": 8,
            "temperature": 0,
        }
    ).encode()
    req = request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
    )
    try:
        with request.urlopen(req, timeout=70) as resp:
            data = json.loads(resp.read())
            log(f"probe OK: {data['choices'][0]['message']['content'][:20]!r}")
            return True
    except Exception as exc:  # noqa: BLE001
        log(f"probe FAIL: {type(exc).__name__}: {str(exc)[:100]}")
        return False


def run_step(name: str, cmd: list[str]) -> bool:
    log(f"step {name}: start")
    started = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=os.environ.copy())
    elapsed = round(time.perf_counter() - started, 1)
    log(f"step {name}: exit={proc.returncode} elapsed={elapsed}s")
    return proc.returncode != 2  # only configuration errors abort the chain


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    results: dict[str, object] = {"driver_started_utc": datetime.now(timezone.utc).isoformat()}

    for attempt in range(1, MAX_PROBES + 1):
        log(f"probe attempt {attempt}/{MAX_PROBES}")
        if probe_ok():
            results["probe_attempts"] = attempt
            break
        if attempt < MAX_PROBES:
            time.sleep(PROBE_INTERVAL_S)
    else:
        log("FATAL: endpoint never recovered within the probe budget; chain NOT started")
        results["status"] = "ENDPOINT_NEVER_RECOVERED"
        (Path(LOG_ROOT) / "K11-driver-result.json").write_text(
            json.dumps(results, indent=2) + "\n", encoding="utf-8"
        )
        return 3

    steps = {
        "k11_main": [
            PY, RUNNER,
            "--case", "K11",
            "--out-dir", OUT_MAIN,
            "--pixel-root", PIX_MAIN,
            "--meter-translation",
        ],
        "k11_sfx_translate": [
            PY, RUNNER,
            "--case", "K11",
            "--out-dir", OUT_SFX,
            "--pixel-root", PIX_SFX,
            "--meter-translation",
            "--sfx-policy", "translate",
            "--suffix", ".sfx-translate",
        ],
        "k11_rerun": [
            PY, RUNNER,
            "--case", "K11",
            "--rerun-check", "K11",
            "--out-dir", OUT_MAIN,
            "--pixel-root", PIX_MAIN,
            "--meter-translation",
        ],
        "k11_similarity": [
            PY, SIMILARITY,
            "--case", "K11",
        ],
    }
    aborted = False
    for name, cmd in steps.items():
        if aborted:
            results[name] = "SKIPPED (previous step aborted)"
            continue
        ok = run_step(name, cmd)
        results[name] = "ok" if ok else "ABORTED(exit2)"
        aborted = not ok

    results["status"] = "DONE" if not aborted else "ABORTED"
    results["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (Path(LOG_ROOT) / "K11-driver-result.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    log(f"chain complete: {results['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
