# P02 Stage A r4 exact-commit 复跑（Codex）

更新时间：2026-10-09（Asia/Shanghai）。本报告记录 Codex 对 Antigravity 固定提交的独立复跑；不替代 DSH Review、Codex Integration Gate，也不代表 P02 产品 Task 完成。

## 固定对象

- Base=`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Delivery HEAD=`cc1bd7505f3fc48079db7ea2719040e77a8c58dd`
- Expected tree=`d2569f6c4854c05e18cf22fa363397525962eec8`
- Parent=`5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e` (r3)
- Frozen scope SHA-256=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- Owner branch=`agent/antigravity/P02-real-webview-harness`, clean after delivery.
- Two new detached exact-HEAD worktrees were created separately (after confirming their paths absent/unregistered) to run each mode from a clean starting checkout:
  - ProbeOnly: `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-probe`
  - Full Stage A: `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-full`
- Both environment probes observed clean source HEAD/tree exactly matching `cc1bd750` / `d2569f6c`; no build outputs existed. The full runner's later harness report marks `is_clean_worktree=false` because verification outputs were generated during that same run; all six `key_execution_inputs_sha256` values were independently recomputed and matched the exact committed input bytes.

## Exact commands and outcomes

| Run | Command | Exit | Result |
|---|---|---:|---|
| ProbeOnly | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1 -ProbeOnly` | 0 | Env + static source probe PASS; its dedicated log contains steps 1–2 only and no Stage A harness step. |
| Full Stage A | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1` | 0 | PRE-01/02/03 PASS; AC1–AC6 BLOCKED/null; FAIL=0, NOT_RUN=0. |
| whitespace | `git diff --check 5de8d44c784cbd20b23bcd41a8f1a7258c7addff cc1bd7505f3fc48079db7ea2719040e77a8c58dd` | 0 | No diagnostics. |

stdout/stderr/exit artifacts for the two runners are in `r4-exact-probeonly.*` and `r4-exact-full.*`. The diff-check outputs are `r4-exact-diff-check.stdout.log`, `.stderr.log`, `.exit`. Each command writes into a separate worktree; artifacts are preserved.

The exact Full Stage A generated `p02-harness-results.json` reports source HEAD/tree=`cc1bd750` / `d2569f6c`, stage=`STAGE_A_SAFE_FOUNDATION_R4`, with:

```text
PRE-01 PASS / EXIT=0
PRE-02 PASS / EXIT=0
PRE-03 PASS / EXIT=0
AC1–AC6 BLOCKED / exit_code=null
```

Input hash verification (all `match=true`):

- `verification/P02/harness/workbench_cdp_harness.py`: `d723e3cce8fdedc1a7de3b6b78af0a291e9074958abccef25349d71dd2719d33`
- `verification/P02/probes/env_identity_probe.py`: `af0c8717d7aa336a97a3ae54d8565c28b8ff693ba973e3b2f5d7c3c5aea4897b`
- `verification/P02/probes/static_control_probe.py`: `4d26b9e4d9f8cfe669d74221cac70db958b9570f76f64b0d93f217ec31f01dcb`
- `verification/P02/run-webview.ps1`: `d25b86c19355596afcd069cf0b0c2b8f8cf1faaa4f458c30673db429a78d9c2a`
- `verification/P02/fixtures/workbench_synthetic_data.json`: `c994d60205675abb4879a7b234288d54d74340895a5ac830bd88a738570ac894`
- `apps/desktop/frontend/e2e/workbench_driver_protocol.ts`: `cbd634309509e7e4db0922b28c1a1e62a9c9e98c9673b82686f4925dbb9dadbd`

Generated Full-run artifact SHA-256:

- `p02-harness-results.json`: `5D54723AC7D2037AD76300862D646655BADA200AF4E0A27D74F5A0FCCE7452C3`
- `env-identity-report.json`: `BB58096AB1A58012434B78CD202E44AAF8F6B11387905CEDCFBF13F464D9BA4D`
- `static-control-report.json`: `FFA6DEE7735CD45D4FE54132ACC8FBB642975FE137C528C9624A103003D7AF42`
- `probe-execution-full.log`: `14DF04524458633761B67031281C3420E850592E6A64B5AD858AFF1F52A66EC7`
- `probe-execution-probeonly.log`: `C19D2CB2FF04236A5EFD86D4AFC1A46DC4A57F3ECD3C89E02F0036C93D943BE9`
- Both dedicated mode logs have no UTF-8 BOM and no CRLF; pure LF verified from bytes.

## Boundaries

- These are Stage A preflight checks only. No Cargo/Tauri/sidecar build, Vitest, GUI, WebView2 interaction, keyboard/focus input, timing exercise, or runtime computed-color extraction was performed.
- AC1–AC6 remain blocked by the hard build barrier and missing independently registered/reviewed scratch build inputs.
- The two detached validation worktrees remain preserved; no cleanup was performed.
