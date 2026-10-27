---
task_id: RUN-BINDING-FIX-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 146377373
delivery_head: 33ddc2804c0ba018b7c0d83df85226e7cc851a09
status: ready-for-integration
---

# Handoff：RUN-BINDING-FIX-1（Host 侧 StartRun 携带 provider bindings，零 Core 改动）

## 交付结果

实现提交 **`33ddc2804c0ba018b7c0d83df85226e7cc851a09`**（branch `task/RUN-BINDING-FIX-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1`；卡面 base `b993e68bb`，按 DSH 指令从当前 HEAD `146377373` 建分支避免过旧 base）；本 Handoff 与任务卡 pin 在后续文档提交中记录。**零 Core 改动**：未改 Python Core、协议/Host 契约语义、旧壳；未 push / gc / prune。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 接线 | **MET** | Host `HostCommandDispatcher.library_start_run` 恒携带 `overrides.provider_bindings`：默认 `{"ocr":"manga-ocr"}`；`NEWMANGA_RUN_PROVIDER_BINDINGS` 可配置/关闭；显式用户绑定原样优先；其余 overrides 保留；非对象 → `INVALID_ARGUMENTS`（0 Core 帧）。 |
| AC2 同构建复验 | **MET** | models 构建 `2b36bfeb…4ec519b`、整书 8 页、Host 命令面：`provider_binding_snapshot={"ocr":"manga-ocr"}`，`step_runs` **ocr 3/3 completed、0 条 `PROVIDER_NOT_CONFIGURED`**；链停在 **color**（3 条 `PROVIDER_FAILED`）；run 终态 `completed_with_failures`。同构建对照（关闭注入）ocr 3/3 `PROVIDER_NOT_CONFIGURED`。**未把「OCR 通」写成「整链通」**。 |
| AC3 语义测试 | **MET** | 有/无 override 两态 + 参数边界 + 覆盖优先级单测；unknown provider (`no-such-provider`) → typed `PROVIDER_UNAVAILABLE`。 |
| AC4 回归 | **MET** | test.ps1 **172/172, 0 skipped**（55/42/75）；vitest **60/567**；pytest **3F/2746P/9S**（无新增）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；13 条 64-hex pin；本 Handoff 含 Record Decision。 |

## Record Decision（默认绑定 / 覆盖策略）

1. **默认值**：`{"ocr":"manga-ocr"}`——冻结 Core 唯一注册的 OCR provider（RUN-OCR-DIAG-1 §2.2 因果验证：只加此绑定，同 sidecar 同数据根 OCR 立即 completed）。
2. **注入位置**：Host `HostCommandDispatcher` 的 `library_start_run` 分支（新增 `RunBindingDefaults` 策略类）。选择 Host 而非 Core：本 Task 是用户授权的「A：零 Core 改动」路线；B（Core 语义小改）另属 CORE-PIPELINE-FIX-1。
3. **覆盖优先级**：调用方显式 `overrides.provider_bindings`（JSON 对象）**完全优先**（不合并、不覆盖）；`null` 视为未提供（注入默认）；其余 overrides 键始终原样保留。目的：兼容旧壳调用方与高级用户，绝不悄悄改写显式语义。
4. **可配置 / 关闭**：环境变量 `NEWMANGA_RUN_PROVIDER_BINDINGS`：JSON 对象替换默认；空串 / `off` / `none` / `disabled` / `0` 关闭注入。生产默认不设即用默认；诊断/对照可关闭。
5. **非法配置**：非对象、provider id 非非空字符串、非法 JSON → `InvalidOperationException`（Host 配置错误，明显失败；不静默降级改变 run 语义）。
6. **参数边界**：`overrides` 或 `overrides.provider_bindings` 不是对象 → `INVALID_ARGUMENTS`，在**任何 Core 帧发出前**拒绝（沿用 Host 命令面边界契约）。
7. **不做的事**：不改 color/detect 的既有 Core 语义；不把 run 终态 `completed_with_failures` 说成成功；不覆盖 Export/Retry 等其它 run 入口（本卡 AC1 只点名 StartRun）。

## 同构建真实运行证据（models 构建，8 页整书）

| 实验 | StartRun overrides | `provider_binding_snapshot` | detect | **ocr** | color | 终态 |
|---|---|---|---|---|---|---|
| A 关闭注入（对照） | 无（env off） | `{}` | completed×3 + INVALID_INPUT×5 | **failed×3 `PROVIDER_NOT_CONFIGURED`** | 未到达 | completed_with_failures |
| B 默认注入（修复） | `{"ocr":"manga-ocr"}` | `{"ocr": "manga-ocr"}` | completed×3 + INVALID_INPUT×5 | **completed×3，0 条 `PROVIDER_NOT_CONFIGURED`** | failed×3 `PROVIDER_FAILED` | completed_with_failures |

- B run id：`run-d12f988f25b44021a0546e8903505475`（另一次 gate 复跑 id 记录在 `commands/run-binding-models.json`）；从 Host 路径 run 复制的 `library.db` 由 `tools/check_run_binding.py` 逐 step 断言。
- unknown provider：`{"ocr":"no-such-provider"}` → ocr step typed **`PROVIDER_UNAVAILABLE`**。
- **边界**：color `PROVIDER_FAILED`（`_StubStyleAnalyzer` 缺 `analyze`）与 detect 0 候选 `INVALID_INPUT` 是既有 Core 缺陷/语义，属 B。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 wire 级 | `RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` | 冻结 core_service（AC11 副本） | 请求行含 `"provider_bindings":{"ocr":"manga-ocr"}`（无 overrides / 空 overrides 两态） | `commands/run-binding-wire.json` |
| AC1 显式优先 | `StartRun_KeepsExplicitUserBindings_AndOtherOverrides` | 同上 | `custom-ocr` 原样；其余 overrides 保留；缺省补默认 | `commands/run-binding-overrides.json` |
| AC1 关闭 | `StartRun_DefaultDisabled_OmitsProviderBindings`、`Resolve_*` 单测 | 同上 | env off → 无 provider_bindings；配置非法抛错 | `test/results-coreclient.trx` |
| AC2 真跑 | `ModelsBuild_BookRun_WithInjectedBindings_OcrNoLongerProviderNotConfigured` | models `2b36bfeb…4ec519b`；BOOK-FIXTURE 私有副本 | 8 targets；ocr 3/3 completed；0 PROVIDER_NOT_CONFIGURED；color 3 failed | `commands/run-binding-models.json`、`run-binding-db-check.json` |
| AC2 对照 | `ModelsBuild_BookRun_WithoutInjectedBindings_StillFailsOcrWithProviderNotConfigured` | 同构建；env off | ocr 3/3 `PROVIDER_NOT_CONFIGURED` | `commands/run-binding-baseline.json` |
| AC3 unknown | `ModelsBuild_UnknownProviderBinding_SurfacesTypedProviderError` | 同构建 | typed `PROVIDER_UNAVAILABLE` | `commands/run-binding-unknown-provider.json` |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **172/172**（55/42/75），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2746P/9S | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RUN-BINDING-FIX-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/RUN-BINDING-FIX-1` / `G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1`；delivery head `33ddc2804`。
- 复现：见 `verification/RUN-BINDING-FIX-1/REPORT.md §7`（test.ps1 / check_run_binding.py）。
- 前置：models 包 sidecar（`2b36bfeb…4ec519b`，含 OCR 权重）与 BOOK-FIXTURE 私有副本；test.ps1 在路径存在时自动导出 `NEWMANGA_MODELS_SIDECAR_DIR`，缺失时真跑测试显式 Skip。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 重跑 test.ps1 复核 → 集成 → closeout；注意 `GRANT-ISSUER-1` / `S4-CMD-BATCH-1` 在途，registry 冲突先落地者为准、后落地者 rebase（本卡只改 dispatcher 一个 case + 新增策略类，冲突面小）。

## 下一任务建议（必填）

- Task ID / 标题：**CORE-PIPELINE-FIX-1（B，用户已授权）**——修复 color `PROVIDER_FAILED`（`_StubStyleAnalyzer` 缺 `analyze`）与 detect 0 候选 `INVALID_INPUT` 语义；本卡 A 完成后，OCR 已通，整链剩余阻断点即 B 的范围。
- 推荐 Agent / Reviewer：实现 = Python Core 侧 Agent（未参与本卡）；Reviewer = DSH 指定的未参与实现者（ZCode / Antigravity / Codex）。
- 推荐原因与前置依赖：A 已把「OCR 通」证明清楚，B 才能让 `translate_untranslated` 整链往前走；B 是 Core 语义改动，需用户授权（已有）与独立 Review；与本卡无代码冲突（Core vs Avalonia）。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `33ddc2804`；base `146377373`。
- 允许修改路径：B 任务卡另行冻结（Python `src/**` + Core 测试）；本卡不再修改产品代码。
- 禁止范围：不改本卡已验证的 Host 契约；不 push/gc/prune；不把 OCR 通写成整链通。
- 交付物：B 的 Core 修复 + 证据 + Handoff；本卡 DSH 集成验证结论与 closeout 记录。
- 验证命令与完成 Gate：B 完成后重跑本卡 `verification/RUN-BINDING-FIX-1/tools/check_run_binding.py` 的 models 场景，期望链越过 color（或 color typed 错误消失）；本卡 Gate 为 test.ps1 172/172、vitest 60/567、pytest 3F/2746P/9S、`check.ps1 -TaskPath` PASS、13 条 pin、独立 Review 通过。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 RUN-BINDING-FIX-1（delivery 33ddc2804，walkthrough 见 doc/handoffs/RUN-BINDING-FIX-1-handoff.md 与 verification/RUN-BINDING-FIX-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 13 条 pin（sha256 与文件一致）；抽查 Host dispatcher 的 StartRun overrides 合并优先级（显式 provider_bindings 优先、其余 overrides 保留、env 关闭、INVALID_ARGUMENTS 0 帧）；重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 172/172，注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 C:\Python314\python.exe verification/RUN-BINDING-FIX-1/tools/check_run_binding.py（应 passed=true：models 注入 ocr 3/3 completed 且 0 PROVIDER_NOT_CONFIGURED、color 仍 PROVIDER_FAILED、关闭注入仍 PROVIDER_NOT_CONFIGURED、unknown provider 为 PROVIDER_UNAVAILABLE）；确认报告没有把「OCR 通」写成「整链通」；给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. **color 仍失败**：`PROVIDER_FAILED`（`_StubStyleAnalyzer` 缺 `analyze`）→ CORE-PIPELINE-FIX-1（B）。
2. **detect 0 候选 → `INVALID_INPUT`**（页 4–8 无文字页）→ B 的语义修正范围。
3. **Export/Retry 未注入 bindings**：本卡只覆盖 StartRun；若导出链也需 provider bindings，另开 Task。
4. **配置为 Host 环境变量**：桌面正常启动不设置即默认；设置页开关需后续 UI Task。
5. 需独立 Review（Owner 不得自审）。
