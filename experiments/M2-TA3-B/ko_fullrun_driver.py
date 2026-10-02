"""M2-TA3-B3-KO-FULLRUN: ko 8-case full-run driver (user ruling 2026-10-02 §7).

Scope (task doc AC1/AC5): the 7 stopped KO-RERUN cases run FULL (K01/K04/K05/
K08/K07/K09/K10) + a CLEAN K02 rerun (fresh data root / temp library by the
runner's per-run tempfile construction; first-run and KO-RERUN K02 stay as
comparison artifacts).  K11/K19 are NOT in this run's case list (K11 keeps the
KO-RERUN result; K19 keeps the F4 registration).

Execution order (small pages first so failures surface early):
  K04 K05 K08 K07 K09 K10 K01  ->  K02 main  ->  K02 rerun-check  ->  similarity

Budget control (AC5, user-endorsed ceiling): every case runs with
``--meter-translation``; after each phase the summary's metering is appended to
the in-repo ledger (verification/M2-TA3-B/phase2/ko-fullrun/budget-ledger.json).
If the cumulative input+output ESTIMATE exceeds CEILING_EST_TOKENS the driver
stops the remaining phases and records a BUDGET_STOP entry (stopping at the
ceiling is the user-approved discipline, not a violation; the number is still
metered and reported).

Outage resilience (KO-RERUN N1 precedent): a minimal endpoint probe runs
before every phase; on failure the driver sleeps PROBE_INTERVAL_S and retries,
up to MAX_PROBES, so a DeepSeek outage window is waited out instead of burning
failed attempts.  Inside a run the production chain's typed fail-closed
semantics remain the outage behaviour (no driver-level retry of regions).

Resume discipline: the runner skips cases whose summary already exists, so a
killed driver can simply be restarted.  The ledger dedupes per (case, phase).

Every runner step keeps its own exit code (1 = pipeline failures, which is
EXPECTED for typed registrations and must NOT abort the chain); only a probe
that never recovers or a runner crash (exit 2 configuration / unhandled)
aborts.  The key enters ONLY via the key file read into TA3B_TRANSLATE_API_KEY
at driver start; it is never printed and scrubbed from every persisted record
by the runner's dump_json.
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

#: paddleocr/paddle live in the dedicated OCR venv, NOT in the runner's own
#: venv.  The first (valid) leg of this run inherited it via the launching
#: shell's PYTHONPATH; the restart leg lost that and produced 6 summaries
#: where every OCR step failed PROVIDER_DEPENDENCY_MISSING with empty text
#: (archived under summaries/invalid-env-2026-10-02-ocr-dep-missing/).  The
#: injection is now a driver-owned invariant instead of an environment
#: accident, and main() refuses to start without it (fail fast, not 6 cases
#: later).
OCR_SITE_PACKAGES = r"G:\CODEX\New Manga.task-envs\M2-TA3-B-ocr\Lib\site-packages"


def runner_env() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    parts = [p for p in existing.split(os.pathsep) if p]
    if OCR_SITE_PACKAGES not in parts:
        parts.insert(0, OCR_SITE_PACKAGES)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def ocr_stack_ok() -> bool:
    """Fail fast BEFORE burning any case (2026-10-02 invalid-env lesson)."""
    probe = subprocess.run(
        [PY, "-c", "import paddleocr, paddle, cv2; print('ocr-stack-ok')"],
        cwd=str(REPO_ROOT), env=runner_env(), capture_output=True, text=True,
    )
    ok = probe.returncode == 0 and "ocr-stack-ok" in probe.stdout
    if not ok:
        log(f"FATAL: OCR stack unusable under the runner env "
            f"(exit={probe.returncode}): {probe.stderr.strip()[:300]}")
    return ok

OUT_MAIN = str(REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "ko-fullrun" / "summaries")
LEDGER = REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "ko-fullrun" / "budget-ledger.json"
SIM_OUT = str(REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "ko-fullrun" / "determinism")
PIX_MAIN = r"G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-fullrun-pixels"
LOG_ROOT = Path(r"G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-fullrun-logs")
KEY_FILE = Path(r"G:\CODEX\New Manga.task-envs\M2-TA3-B\deepseek.key")

ENV_KEY_NAME = "TA3B_TRANSLATE_API_KEY"
CEILING_EST_TOKENS = 2_200_000
#: user ruling backing: ~2.09M (7-case full upper bound) + ~113k K02 clean rerun;
#: case-level exemption record closing ko-rerun-report §7.5 / budget-register R1.
CEILING_BASIS = (
    "user-approved 2026-10-02: 7-case full extrapolation upper bound ~2.09M "
    "est tokens + K02 clean rerun ~113k = 2.2M ceiling (ko-rerun-report §7 "
    "items 1+2; case-level exemption record for phase2-plan.md:192)"
)
#: estimated est tokens per region for the whole chain (2 x 607, the registered
#: UPPER-BOUND model from budget-register.json extrapolation.formula)
EST_PER_REGION_UPPER = 1214
#: K07/K09/K10 have never had a detect measurement (KO-RERUN extrapolation)
UNKNOWN_REGION_UPPER = 400
KNOWN_REGIONS = {"K01": 180, "K02": 93, "K04": 113, "K05": 62, "K08": 60}

MAX_PROBES = 18
PROBE_INTERVAL_S = 600

MAIN_ORDER = ["K04", "K05", "K08", "K07", "K09", "K10", "K01"]


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[driver {utc()}] {msg}", flush=True)


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


def wait_for_endpoint() -> bool:
    for attempt in range(1, MAX_PROBES + 1):
        log(f"probe attempt {attempt}/{MAX_PROBES}")
        if probe_ok():
            return True
        if attempt < MAX_PROBES:
            time.sleep(PROBE_INTERVAL_S)
    log("FATAL: endpoint never recovered within the probe budget")
    return False


def ledger_load() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        "task": "M2-TA3-B3-KO-FULLRUN",
        "ceiling_est_tokens": CEILING_EST_TOKENS,
        "ceiling_basis": CEILING_BASIS,
        "metering_basis": (
            "estimate_tokens (ports/translation/protocol.py, CJK-aware) via the "
            "runner's --meter-translation passthrough proxy; ESTIMATES, and "
            "production retries outside the provider are NOT metered (KO-RERUN r1 R6)"
        ),
        "entries": [],
        "stop": None,
    }


def ledger_entry_exists(ledger: dict, case_id: str, phase: str) -> bool:
    return any(e["case_id"] == case_id and e["phase"] == phase for e in ledger["entries"])


def metering_summary(case_id: str, rerun: bool = False) -> dict | None:
    name = f"qual-{case_id}.rerun.json" if rerun else f"qual-{case_id}.json"
    path = Path(OUT_MAIN) / name
    if not path.exists():
        return None
    summary = json.loads(path.read_text(encoding="utf-8"))
    metering = summary.get("translation_metering")
    if not metering or not metering.get("metered"):
        return None
    return {
        "requests": metering["requests"],
        "input_est_tokens": metering["input_est_tokens_total"],
        "output_est_tokens": metering["output_est_tokens_total"],
        "est_tokens": metering["input_est_tokens_total"] + metering["output_est_tokens_total"],
    }


def ledger_append(ledger: dict, case_id: str, phase: str, exit_code: int | None) -> int:
    """Append (dedupe) the phase's metering entry; return the new cumulative."""
    if ledger_entry_exists(ledger, case_id, phase):
        log(f"ledger already has {case_id}/{phase} -> skip append")
    else:
        metering = metering_summary(case_id, rerun=(phase == "rerun"))
        ledger["entries"].append(
            {
                "case_id": case_id,
                "phase": phase,
                "finished_at_utc": utc(),
                "runner_exit_code": exit_code,
                **(metering or {"requests": 0, "input_est_tokens": 0, "output_est_tokens": 0, "est_tokens": 0,
                                "note": "no metering record in summary"}),
            }
        )
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sum(e.get("est_tokens", 0) for e in ledger["entries"])


def case_upper_estimate(case_id: str) -> int:
    regions = KNOWN_REGIONS.get(case_id, UNKNOWN_REGION_UPPER)
    return regions * EST_PER_REGION_UPPER


def run_phase(case_id: str, phase: str, extra_args: list[str]) -> int | None:
    """Run one runner invocation with a pre-probe; None = endpoint never recovered."""
    if not wait_for_endpoint():
        return None
    log_path = LOG_ROOT / f"{case_id}{'.' + phase if phase != 'main' else ''}.log"
    log(f"phase {case_id}/{phase}: start (log {log_path})")
    started = time.perf_counter()
    with log_path.open("w", encoding="utf-8") as handle:
        proc = subprocess.run(
            [PY, RUNNER, "--case", case_id, "--out-dir", OUT_MAIN,
             "--pixel-root", PIX_MAIN, "--meter-translation",
             "--determinism-track", "remote", *extra_args],
            cwd=str(REPO_ROOT), env=runner_env(), stdout=handle,
            stderr=subprocess.STDOUT,
        )
    elapsed = round(time.perf_counter() - started, 1)
    log(f"phase {case_id}/{phase}: exit={proc.returncode} elapsed={elapsed}s")
    return proc.returncode


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # key enters via file -> process env (equivalent to the KO-RERUN
    # `export TA3B_TRANSLATE_API_KEY=$(cat ...)` injection); never printed.
    os.environ[ENV_KEY_NAME] = KEY_FILE.read_text(encoding="utf-8").strip()
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    if not ocr_stack_ok():
        return 2

    ledger = ledger_load()
    results: dict = {"driver_started_utc": utc(), "ceiling_est_tokens": CEILING_EST_TOKENS,
                     "phases": {}}
    budget_stopped = False

    def finish(status: str) -> int:
        results["status"] = status
        results["finished_utc"] = utc()
        results["cumulative_est_tokens"] = sum(e.get("est_tokens", 0) for e in ledger["entries"])
        (LOG_ROOT / "driver-result.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        log(f"chain complete: {status} cumulative={results['cumulative_est_tokens']}")
        return 0 if status == "DONE" else 3

    # ---- 7 stopped cases, full (user ruling §7 item 1) ---------------------
    for case_id in MAIN_ORDER:
        if budget_stopped:
            results["phases"][f"{case_id}/main"] = "SKIPPED (budget stop)"
            continue
        if (Path(OUT_MAIN) / f"qual-{case_id}.json").exists() and ledger_entry_exists(ledger, case_id, "main"):
            log(f"{case_id}/main: summary + ledger entry exist -> resume-skip")
            results["phases"][f"{case_id}/main"] = "RESUME_SKIPPED"
            continue
        cumulative = sum(e.get("est_tokens", 0) for e in ledger["entries"])
        projected = cumulative + case_upper_estimate(case_id)
        log(f"{case_id}: cumulative={cumulative} projected_upper={projected} ceiling={CEILING_EST_TOKENS}")
        code = run_phase(case_id, "main", [])
        if code is None:
            ledger["stop"] = {"reason": "ENDPOINT_NEVER_RECOVERED", "at_utc": utc(),
                              "remaining": [c for c in MAIN_ORDER[MAIN_ORDER.index(case_id):]] + ["K02"]}
            LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            results["phases"][f"{case_id}/main"] = "ENDPOINT_NEVER_RECOVERED"
            return finish("ENDPOINT_NEVER_RECOVERED")
        if code == 2:
            results["phases"][f"{case_id}/main"] = "ABORTED(exit2)"
            return finish("ABORTED")
        cumulative = ledger_append(ledger, case_id, "main", code)
        results["phases"][f"{case_id}/main"] = f"exit={code}"
        if cumulative > CEILING_EST_TOKENS:
            log(f"BUDGET_STOP: cumulative {cumulative} > ceiling {CEILING_EST_TOKENS}")
            ledger["stop"] = {"reason": "BUDGET_CEILING_EXCEEDED", "at_utc": utc(),
                              "cumulative_est_tokens": cumulative,
                              "remaining": [c for c in MAIN_ORDER[MAIN_ORDER.index(case_id) + 1:]] + ["K02"]}
            LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            budget_stopped = True

    # ---- K02 clean rerun (user ruling §7 item 2): main + rerun + similarity -
    if not budget_stopped:
        cumulative = sum(e.get("est_tokens", 0) for e in ledger["entries"])
        projected = cumulative + case_upper_estimate("K02") * 2
        log(f"K02: cumulative={cumulative} projected_upper={projected} ceiling={CEILING_EST_TOKENS}")
        code = run_phase("K02", "main", [])
        if code is None:
            ledger["stop"] = {"reason": "ENDPOINT_NEVER_RECOVERED", "at_utc": utc(), "remaining": ["K02"]}
            LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            results["phases"]["K02/main"] = "ENDPOINT_NEVER_RECOVERED"
            return finish("ENDPOINT_NEVER_RECOVERED")
        if code == 2:
            results["phases"]["K02/main"] = "ABORTED(exit2)"
            return finish("ABORTED")
        cumulative = ledger_append(ledger, "K02", "main", code)
        results["phases"]["K02/main"] = f"exit={code}"
        if cumulative > CEILING_EST_TOKENS:
            log(f"BUDGET_STOP after K02 main: {cumulative} > {CEILING_EST_TOKENS}")
            ledger["stop"] = {"reason": "BUDGET_CEILING_EXCEEDED", "at_utc": utc(),
                              "cumulative_est_tokens": cumulative, "remaining": ["K02.rerun", "similarity"]}
            LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            budget_stopped = True

    if not budget_stopped:
        cumulative = sum(e.get("est_tokens", 0) for e in ledger["entries"])
        log(f"K02/rerun: cumulative={cumulative} ceiling={CEILING_EST_TOKENS}")
        code = run_phase("K02", "rerun", ["--rerun-check", "K02"])
        if code is None:
            ledger["stop"] = {"reason": "ENDPOINT_NEVER_RECOVERED", "at_utc": utc(),
                              "remaining": ["K02.rerun", "similarity"]}
            LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            results["phases"]["K02/rerun"] = "ENDPOINT_NEVER_RECOVERED"
            return finish("ENDPOINT_NEVER_RECOVERED")
        if code == 2:
            results["phases"]["K02/rerun"] = "ABORTED(exit2)"
            return finish("ABORTED")
        cumulative = ledger_append(ledger, "K02", "rerun", code)
        results["phases"]["K02/rerun"] = f"exit={code}"
        if cumulative > CEILING_EST_TOKENS:
            log(f"BUDGET_STOP after K02 rerun: {cumulative} > {CEILING_EST_TOKENS}")
            ledger["stop"] = {"reason": "BUDGET_CEILING_EXCEEDED", "at_utc": utc(),
                              "cumulative_est_tokens": cumulative, "remaining": ["similarity"]}
            LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            budget_stopped = True

    if not budget_stopped:
        log("similarity K02: start")
        with (LOG_ROOT / "K02.similarity.log").open("w", encoding="utf-8") as handle:
            proc = subprocess.run(
                [PY, SIMILARITY, "--case", "K02", "--summaries-dir", OUT_MAIN,
                 "--out-dir", SIM_OUT, "--determinism-track", "remote"],
                cwd=str(REPO_ROOT), env=runner_env(), stdout=handle,
                stderr=subprocess.STDOUT,
            )
        results["phases"]["K02/similarity"] = f"exit={proc.returncode}"
        log(f"similarity K02: exit={proc.returncode}")

    return finish("DONE_BUDGET_STOP" if budget_stopped else "DONE")


if __name__ == "__main__":
    raise SystemExit(main())
