# RUN-BINDING-FIX-1 验证报告（Host 侧 StartRun 携带 provider bindings，零 Core 改动）

- Task：`doc/tasks/RUN-BINDING-FIX-1.md`（team task-34，用户授权 A+B 中的 **A**）
- Branch / worktree：`task/RUN-BINDING-FIX-1` / `G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1`
- Base：卡面 `b993e68bb`；按 DSH 指令为避免过旧 base，分支从当前 HEAD **`146377373`** 创建（`git merge-base` 为同一主线）
- 零 Core 改动：未改 Python Core、未改协议 / Host 契约语义 / 旧壳；未 push / gc / prune

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 接线 | **MET** | Host `HostCommandDispatcher` 的 `library_start_run` 现在恒携带 `overrides.provider_bindings`：默认 `{"ocr":"manga-ocr"}`；未显式给出 `provider_bindings` 时注入；用户显式 `overrides.provider_bindings` **原样优先**（不覆盖、不合并）；其余用户 overrides 保留；通过 `NEWMANGA_RUN_PROVIDER_BINDINGS` 可配置（JSON 对象）或关闭（空 / `off` / `none` / `disabled` / `0`）。真实运行 8/8 页在 models 构建上证明 OCR 不再 `PROVIDER_NOT_CONFIGURED`。 |
| AC2 同构建复验 | **MET** | models 包构建 `2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b` 上整书 8 页复跑：`provider_binding_snapshot_json={"ocr":"manga-ocr"}`，`step_runs` 中 **ocr 3/3 completed、0 条 `PROVIDER_NOT_CONFIGURED`**；链随后停在 **color**（3 条 `PROVIDER_FAILED`），另有 5 页 detect `INVALID_INPUT`（无文字页的既有 Core 语义）。**未把「OCR 通」写成「整链通」**：run 终态仍是 `completed_with_failures`。 |
| AC3 语义测试 | **MET** | 有/无 override 两态：A/B 同构建真实 run（注入 → ocr completed；关闭 → ocr 3/3 `PROVIDER_NOT_CONFIGURED`）；单测覆盖默认值/自定义/关闭/非法配置；参数边界（`overrides` 非对象、`provider_bindings` 非对象 → `INVALID_ARGUMENTS` 且 0 Core 帧）；unknown provider → 真实 run 的 typed 错误 `PROVIDER_UNAVAILABLE`。 |
| AC4 回归 | **MET** | `scripts/test.ps1` **172/172 passed, 0 skipped**（coreclient 55 / host 42 / app 75）；vitest **60 files / 567 tests**；pytest **3F/2746P/9S**（与基线一致，0 新增失败）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；12 条 64-hex pin；`doc/handoffs/RUN-BINDING-FIX-1-handoff.md` 含 Record Decision。 |

## 2. Record Decision：默认绑定与覆盖策略

| 项 | 决定 | 依据 |
|---|---|---|
| 默认值 | `{"ocr":"manga-ocr"}`——冻结 Core 唯一注册的 OCR provider（`provider_id=manga-ocr`） | RUN-OCR-DIAG-1 §2.2：同 sidecar 同数据根只加此绑定 → OCR completed |
| 注入位置 | Host `HostCommandDispatcher.WriteCorePayload` 的 `library_start_run` 分支（**Host 侧**，零 Core 改动）；新增 `RunBindingDefaults` 策略类 | 卡面「Host 侧 StartRun 携带」+ 零 Core 改动路线 |
| 覆盖优先级 | 用户显式 `overrides.provider_bindings`（对象）**完全优先**，不合并、不覆盖；`null` 视为未提供（注入默认）；其余 overrides 键始终保留 | 兼容旧壳调用方；避免悄悄改变用户显式语义 |
| 可配置 / 关闭 | 环境变量 `NEWMANGA_RUN_PROVIDER_BINDINGS`：JSON 对象替换默认；空串/`off`/`none`/`disabled`/`0` 关闭注入 | AC1「允许配置/关闭覆盖」；生产/诊断可关 |
| 配置非法 | 非对象、非字符串 provider id、非法 JSON → `InvalidOperationException`（Host 配置错误，明显失败而非静默改变 run 语义） | 不静默降级 |
| 参数边界 | `overrides` 或 `overrides.provider_bindings` 非对象 → `INVALID_ARGUMENTS`，在**任何 Core 帧发出前**拒绝 | 沿用 Host 命令面边界契约 |
| 不改变的范围 | 不处理 Core 的 `color`（`_StubStyleAnalyzer` 缺 `analyze`）与 detect 0 候选 → `INVALID_INPUT` 语义（属用户授权的 B / CORE-PIPELINE-FIX-1） | 卡面禁止把「OCR 通」写成「整链通」 |

## 3. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/Commands/RunBindingDefaults.cs`（新） | 默认/自定义/关闭/非法配置解析；`EnvironmentVariable=NEWMANGA_RUN_PROVIDER_BINDINGS`。 |
| `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `library_start_run` 改用 `WriteStartRunOverrides`：默认注入、显式绑定优先、其余 overrides 保留、参数边界 `INVALID_ARGUMENTS`。 |
| `tests/NewManga.CoreClient.Tests/Commands/RunBindingFixTests.cs`（新，11 项） | 4 个策略单测 + 5 个 frozen-sidecar 契约/边界测试（含 wire 请求行断言）+ 2 个 models 构建真跑：A/B 整书 8 页 + unknown provider typed。 |
| `apps/desktop-avalonia/scripts/test.ps1` | 当 models 包存在时导出 `NEWMANGA_MODELS_SIDECAR_DIR`（真跑测试的显式环境；缺失时测试自动 Skip 并给出原因）。 |

## 4. 真实运行证据（models 构建 `2b36bfeb…4ec519b`，BOOK-FIXTURE 私有副本）

同一构建、同一 8 页书、同一 Host 命令面，仅切换 Host 注入开关：

| 实验 | StartRun 请求 | `provider_binding_snapshot_json` | detect | **ocr** | color | run 终态 |
|---|---|---|---|---|---|---|
| A 关闭注入（对照） | 无 `provider_bindings` | `{}` | completed ×3 + INVALID_INPUT ×5 | **failed ×3：`PROVIDER_NOT_CONFIGURED`** | 未到达 | completed_with_failures |
| B 默认注入（本修复） | `{"ocr":"manga-ocr"}`（请求行已入证据） | `{"ocr": "manga-ocr"}` | completed ×3 + INVALID_INPUT ×5 | **completed ×3，0 条 `PROVIDER_NOT_CONFIGURED`** | failed ×3：`PROVIDER_FAILED` | completed_with_failures |

- run 快照：B run `run-d12f988f25b44021a0546e8903505475`，terminal `completed_with_failures`；任务投影 `step_flow` 显示链推进到 color（`color=failed,...`），OCR 阶段不再是终态失败。
- 逐 step 账本（从 Host 路径 run 的 `library.db` 复制）：`step_counts = {detect:completed×3, ocr:completed×3, color:failed:PROVIDER_FAILED×3, detect:failed:INVALID_INPUT×5}`。
- unknown provider：`{"ocr":"no-such-provider"}` → `provider_binding_snapshot={"ocr":"no-such-provider"}`，ocr step typed 错误 **`PROVIDER_UNAVAILABLE`**（不是笼统失败）。
- **边界声明**：OCR 已通 ≠ 整链已通；color 的 `PROVIDER_FAILED` 是 `_StubStyleAnalyzer` 缺 `analyze` 的既有缺陷，detect 的 `INVALID_INPUT` 是「0 候选」被映射为非法输入的既有 Core 语义，二者都留待 CORE-PIPELINE-FIX-1（B）。

## 5. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 wire 级 | `RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` | 冻结 core_service（AC11 副本） | 请求行含 `"overrides":{"provider_bindings":{"ocr":"manga-ocr"}}` | `commands/run-binding-wire.json` |
| AC1 显式优先 | `StartRun_KeepsExplicitUserBindings_AndOtherOverrides` | 同上 | 显式 `custom-ocr` 原样，其他 overrides 保留；缺省时补默认 | `commands/run-binding-overrides.json` |
| AC2 真实整书 8 页 | `ModelsBuild_BookRun_WithInjectedBindings_OcrNoLongerProviderNotConfigured` | models 包 `2b36bfeb…4ec519b`；BOOK-FIXTURE 私有副本 | 8 targets；ocr 3/3 completed；0 PROVIDER_NOT_CONFIGURED；color 3 failed（链路停在此） | `commands/run-binding-models.json` + `run-binding-db-check.json` |
| AC2 同构建对照 | `ModelsBuild_BookRun_WithoutInjectedBindings_StillFailsOcrWithProviderNotConfigured` | 同构建；`NEWMANGA_RUN_PROVIDER_BINDINGS=off` | ocr 3/3 `PROVIDER_NOT_CONFIGURED`（复现基线） | `commands/run-binding-baseline.json` |
| AC3 unknown provider | `ModelsBuild_UnknownProviderBinding_SurfacesTypedProviderError` | 同构建；binding `no-such-provider` | typed `PROVIDER_UNAVAILABLE` | `commands/run-binding-unknown-provider.json` |
| AC3 逻辑/边界 | `Resolve_*`、`StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame` | 无 sidecar / frozen | 4+1 项；边界 0 Core 帧 | `test/results-coreclient.trx` |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **172/172**（55/42/75） | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest | `cd apps/desktop/frontend && npm test`（主仓；旧壳未改） | 旧壳未改 | **60 files / 567 tests** | `test/vitest.log` |
| AC4 pytest | `PYTHONPATH=src python -m pytest -q`（worktree，未改 Python） | 未改 Core | **3F/2746P/9S**（基线一致） | `test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RUN-BINDING-FIX-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 6. 遗留 / 未关闭项（记录不阻塞）

1. **color 步骤仍失败**（`PROVIDER_FAILED`，`_StubStyleAnalyzer` 缺 `analyze`）→ 属 CORE-PIPELINE-FIX-1（B，用户已授权）；本卡不改 Core。
2. **detect 0 候选 → `INVALID_INPUT`**（页 4–8 无文字插画页）→ 同样是 B 的语义修正范围，本卡未动。
3. **StartRun 之外**：Export / Retry 等其它 run 入口未注入 bindings；如用户希望导出链也携带，需另开 Task（本卡只覆盖卡面 AC1 的 StartRun）。
4. **配置是 Host 环境变量**：桌面应用正常启动时不设置该变量即用默认值；运维/诊断可关闭。若未来需要设置页开关，应作为 UI Task 接 `NEWMANGA_RUN_PROVIDER_BINDINGS` 语义。
5. 需独立 Review（Owner 不自审）。

## 7. 复现

```pwsh
# 1) 全量回归（含 models 构建 A/B 真跑：约 40s 额外）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\RUN-BINDING-FIX-1\evidence

# 2) 逐 step 账本校验（Host 路径 run 的 library.db 副本）
C:\Python314\python.exe verification/RUN-BINDING-FIX-1/tools/check_run_binding.py
```
