# RELEASE-REPACK-2 tools

## run_full_chain_probe.py (AC2/AC3)

Drives the freshly repacked models `core_service.exe` over the real wire:
`StartRun(translate_untranslated)` on BOOK-FIXTURE with
`overrides.provider_bindings = {"ocr": "manga-ocr", "translate": "identity-translation"}`, while a
second thread polls `GetTaskProjection` every 100 ms (projection-fresh topology). It records the
final task projection, per-step-type wall-clock durations (from `CurrentPageStepChanged` frames),
and queries the run DB for `step_runs` counts, stuck `running` rows, regionless `INVALID_INPUT` rows
and `PROVIDER_NOT_CONFIGURED` rows.

```powershell
python verification/RELEASE-REPACK-2/tools/run_full_chain_probe.py \
  --sidecar <models-bundle>/core-sidecar \
  --out <task-env>/full-chain-run.json
```

## AC3 source-topology regression

`verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py scheduler projection-fresh`
is run with `NEWMANGA_EVIDENCE_DIR` pointing at this task env; verdict must be PASS with
`stuck_running=0` and `regionless_invalid_input=0`.
