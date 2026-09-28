# M2-AC3 Provider Fail-closed Acceptance — Verification Results

- Owner: ZCode（本会话亲自实现）
- Task: [doc/tasks/M2-AC3.md](../../doc/tasks/M2-AC3.md)（纯验收，产品代码零改动）
- Base: `319c5e4b`（release commit `7e88de4b`）
- Branch: `agent/zcode/M2-AC3-provider-fail-closed`
- Worktree: `G:/CODEX/New Manga.worktrees/M2-AC3-zcode`
- Environment: Windows 11 x64 · Git Bash · Python 3.12.3（`G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`，下称 `$py`）· pytest 9.1.1

## 测试要求矩阵（Task §测试要求 → 实际结果）

| 场景/AC | 命令（worktree 根目录） | 结果 | 证据 |
|---|---|---|---|
| AC1–AC5 场景族 | `$py -m pytest tests/m2_acceptance/test_provider_fail_closed.py -v` | **executed：8 passed，EXIT=0** | [raw/pytest-provider-fail-closed-v.log](raw/pytest-provider-fail-closed-v.log) |
| 回归：m2_acceptance 既有套件 | `$py -m pytest tests/m2_acceptance -q` | **executed：23 passed**（既有 15 + 新增 8，零回归），EXIT=0 | [raw/pytest-m2-acceptance-regression.log](raw/pytest-m2-acceptance-regression.log) |
| 范围与空白 | `git diff --check 319c5e4b..<delivery-head>` | **executed：EXIT=0**（delivery-head=交付 tip，见 Handoff） | [raw/git-diff-check.log](raw/git-diff-check.log) |

日志头部记录了运行时的 shell、解释器版本与固定 HEAD。所有 skip：无（0 skipped）。

## 场景 → AC 映射（8 场景全部 PASS）

| 场景 | AC | 判别对象 | 判定 |
|---|---|---|---|
| `test_ac1_zero_config_detect_fails_closed_without_fabricated_regions` | AC1 | 零配置生产装配（无 binding、无 docTR 权重）→ page-level run 在 detect 能力缺口 typed 失败（`PROVIDER_NOT_CONFIGURED`，detail 指名 "weights are not installed"）；零 Region / 零 candidate / 零新 managed 文件 | **PASS** |
| `test_ac1_missing_binding_fails_closed_with_typed_slot` | AC1 | region-level OCR 无 binding → `_chain` 抛 typed `PROVIDER_NOT_CONFIGURED`，detail 含 `no provider binding configured for step 'ocr'`；region 文本与 current 指针不变、零半成品 revision | **PASS** |
| `test_ac1_dangling_binding_reports_unavailable_not_silent` | AC1 | binding 指向未注册 id → resolve 阶段 typed `PROVIDER_UNAVAILABLE`，detail 含 `no provider registered as 'm2ac3-ghost-ocr'`（与网络失败、未配置 binding 三者可区分）；零半成品 | **PASS** |
| `test_ac2_network_failure_typed_and_existing_results_intact` | AC2 | transport 注入（fixture provider 每次调用抛 `ProviderTimeout`）→ typed `PROVIDER_TIMEOUT` ≠ `PROVIDER_NOT_CONFIGURED`，detail 带 provider id；人工译文、translation lock、manual_edited、pinned revision、revision 计数、current 指针全部原样 | **PASS** |
| `test_ac3_partial_failure_run_boundary_is_honest` | AC3 | 双页 run：A 页 provider 成功 / B 页 transport 失败 → run=`COMPLETED_WITH_FAILURES`、task 边界可查询（A=COMPLETED/B=FAILED）；A 落恰好 1 条新 revision 且 current 在其上、B 零 revision 零伪文本、B 的 typed detail 按页可诊断 | **PASS** |
| `test_ac4_source_files_untouched_across_failure_runs` | AC4 | 连续两个失败 run（无 binding → 悬空 binding）后：源文件 bytes/size/mtime_ns/目录清单不变；managed copy 字节与源逐字节一致（无部分写入） | **PASS** |
| `test_ac5_reassembly_after_failure_preserves_run_truth` | AC5 | 失败 run 后同 data root 全量重装配（进程重启等价）：run 状态、task FAILED + typed error_code、step error_code/detail 全部持久可查询；region 零回写 | **PASS** |
| `test_ac5_retry_after_fix_leaves_no_duplicates_or_dangling` | AC5 | 网络失败 run → 重装配 → binding 修复为 mock provider → 重试 run=`COMPLETED`；旧 run 保持 `COMPLETED_WITH_FAILURES` 不复活；revision 序列 `[1,2]` 连续无重复、current 在最新且携带 provider 文本——失败 +1 成功 = 恰好 origin + result | **PASS** |

## 判别力（先红验证，两次 mutation，复现命令见 [discrimination-mutations.md](discrimination-mutations.md)）

- **M1（状态伪造）**：`_aggregate_run` 吞掉 `FAILED` 分支 → `test_ac2_network_failure_typed_and_existing_results_intact` **红**（`test_provider_fail_closed.py:404` run 状态断言）。
- **M2（typed 错误被替换为 generic）**：`_fail_step` 将 `step_run.error_code` 硬编码为 `"STEP_FAILED"` → 同场景 **红**（`test_provider_fail_closed.py:413` typed code 断言）。
- 两次验证后 `git checkout -- src/application/tasks/service.py` 还原，`git status --porcelain src/` = 0 行（零残留）。产品代码在本 Task 交付中零改动。

## NOT_RUN / BLOCKED

- **Qt/WebView2 读面的错误呈现**（错误如何在 UI 呈现）：NOT_RUN——headless 验收装配不可达（与 M2-AC2 的 Qt provider 读面 NOT_RUN 同因），登记为后续 E2E slice 输入。Task AC1 的"页/run 状态如实"断言落在 Core 层 run/task/step 持久状态上，已 PASS。
- 其余无 FAIL / BLOCKED。

## 范围核查

- Owner 变更路径：`tests/m2_acceptance/test_provider_fail_closed.py`（新增）、`doc/tasks/M2-AC3.md`、`verification/M2-AC3/**`、`doc/handoffs/M2-AC3-owner-delivery.md`——全部在 Task 允许范围内。
- `src/**`、`apps/**`、`doc/contracts/**`、既有验收套件（`test_acceptance_loop.py` / `test_data_integrity.py`）：零改动（mutation 验证的临时改动已还原并复核）。
