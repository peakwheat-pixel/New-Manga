# P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION — pure selftest run record

## 运行绑定

| 字段 | 值 |
|---|---|
| Task | P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION |
| AC | AC3（本 Task 测试要求第 1 行：source parser + pure selftest） |
| delivery commit（被测源码） | `6420653c1ec8adfcc26da9378072451f921b5930` |
| 分支 / worktree | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` / `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` |
| 运行时 CWD | `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` |
| 命令（原样） | `pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1` |
| Shell | `C:\Program Files\PowerShell\7\pwsh.exe` |
| PowerShell 版本 | `7.6.6` / `Core` / `FullLanguage`（满足 AC3 要求的 7.6.6） |
| OS | `Microsoft Windows 10.0.26300` |
| startedUtc / finishedUtc | `2026-10-13T21:06:08.8266122Z` / `2026-10-13T21:06:10.5799458Z`（本地 2026-10-14 05:06 +0800） |
| exit code | `0` |

被测文件（delivery commit `6420653c` 内）：

| 文件 | SHA-256 |
|---|---|
| `tools/p02/p02-new-time-baseline.ps1` | `bf9f69cfb291c6e7609a861821fc458c32c7a3c7ad93898953e3ad2db26d567a` |
| `tools/p02/p02-new-time-baseline-selftest.ps1` | `26c5f50ec3c7cd447a7bc116b1038ae57777fcda38e3b95e74232a2acaf2f73f` |

selftest SUMMARY-JSON 内 `collectorSha256` 与上表 collector SHA-256 一致，证明本次运行针对的就是 delivery commit 的源码内容。本 Task 仅此一次 selftest 运行。

## 结果

| 指标 | 值 |
|---|---|
| assertsPassed | 220 |
| assertsFailed | 0 |
| assertsSkipped | 7（逐项见下；不计 PASS） |
| exit | 0（`assertsFailed > 0` 时才非零） |
| summary revision | `i2-r3+ac3-branch-res+ac3-helper-value-shape` |

其中新增（本 Task）helper 输出形状回归断言 8 条全部 PASS：

- `helper-shape-producer-function-found`
- `helper-shape-exactly-two-producer-constructions`
- `helper-shape-both-constructions-value-wrapped`
- `helper-shape-no-legacy-unwrapped-output`
- `helper-shape-success-path-value-envelope`
- `helper-shape-exception-path-value-envelope`
- `helper-shape-consumers-read-value-envelope`
- `helper-shape-json-pointers-target-value-envelope`

原 assertions 未减少（diff 仅新增断言与注释；原 7 项 skip 原样保留）。

## SKIP 项及原因（原样保留，单列）

1. `live-collector-run` — Task: live collector execution is NOT authorized in this Owner delivery round; requires Codex freeze of commit/hash/argv/CWD/RunId/targets plus AC2/AC3 gates first.
2. `live-git-child` — Forbidden here: no git child process during the pure selftest; git argv builders are verified as pure functions.
3. `live-whoami-child` — Forbidden here: no whoami child during the pure selftest; identity comparison stays a documented live-scope check.
4. `live-registry-acl-profile-getter` — Forbidden here: no registry/ACL/profile API at all in this Task scope (read or write).
5. `executor-dynamic-process-enumeration` — Forbidden scopes: attempt6 executor (never referenced/read/executed), Toolhelp/Process32*/Get-Process enumeration — all NOT_RUN by Task forbidden scope.
6. `x6-post-run-review-build-cargo-ac-sandbox` — Forbidden scopes: X6, post-run Review, Build/Cargo, product AC1-AC7, Windows Sandbox — later Gates, never released by this Task; all NOT_RUN.
7. `historical-input-access` — Forbidden scopes: no H1/P2-1 historical input, conclusion, finding or missing-source record is read, rewritten, backfilled or re-awarded; history isolation is enforced statically.

## 证据文件

| 文件 | SHA-256 |
|---|---|
| `selftest-20261014T0506+0800-stdout.log`（255 行，含完整 assert/skip 日志与 SUMMARY-JSON） | `f242304ec8090bfcfda6530895d3cf111c15d86fcaa595cb9539fb75a50298f9` |
| `selftest-20261014T0506+0800-stderr.log`（空文件，0 字节） | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`（空字节流 SHA-256） |

## 未运行项（本 Task 冻结边界）

未运行 live collector、任何新 RunId、git/whoami child、X6、post-run Review、Build/Cargo、产品 AC1–AC7、Windows Sandbox；未读取或改写任何 H1/P2-1 历史输入或结论。selftest fixtures 写入 `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261014-050608-pure-selftest/`（selftest 自身固定行为，保留供 Review）。

本目录中 Codex 的既有 `zcode-preflight-*` untracked 文件不属于本次交付，保持原样、未纳入提交。
