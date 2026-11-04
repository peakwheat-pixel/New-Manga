---
task_id: FEA-10
reviewer: DSH 独立子 agent（父会话 session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4 派发；全新只读上下文，未参与实现/返修）
reviewer_kind: subagent
author: Codex（r1）/ ZCode（r2 续作）/ DSH（r2 集成收尾）
base_commit: aa7bcd6161be5df07e2b8bf546600fec04af038f
reviewed_head: a92934585088fe75ce8ec53452a67c0a72496d31
decision: changes_requested
---

# Review：FEA-10 实现（独立实现 Review，r1）

## 0. 审查者身份与来源

- 身份：DeepSeek Harness 主会话（session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）派发的**独立子 agent**，全新只读上下文；本会话未参与 FEA-10 的实现、r1/r2 返修或证据生成，也未参与 DSH r2 收尾。
- 审查对象：Task 卡 `doc/tasks/FEA-10.md`（AC1–AC10、验证矩阵、实施记录、Canonical Evidence）、交付 `aa7bcd6 → a9293458` 的全部生产/测试/证据字节、阶段提交 `25ba7cb2`、Handoff、AC-MATRIX、`ADJ-2026-11-04-FEA-10-R2`、冻结契约（C-08/C-13/C-05/C-04b、`M2-C1_TYPED_IPC_CONTRACT.md` rev 2.12）。
- `reviewed_head`：`a92934585088fe75ce8ec53452a67c0a72496d31`；`delivery_head` 与之一致；`main` 工作树干净（审查开始时 `git status --porcelain` 为空）。
- 只读约束：未修改生产代码/测试/证据/契约，未 commit/push。唯一写入是本文件；测试与探针只在 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/review-9f3c1b7a/` 下创建，TEMP/TMP 亦指向该目录，未写系统 AppData。

## 1. 结论

**changes_requested（不可 approved / 不可 closeout）。**

r2 的主体机制是真实存在的：Prepare/Accept 两阶段、quartet digest、BEGIN IMMEDIATE 内重读、candidate-only 提交、durable receipt、真实 Core stdio 重启重放、按 provider 类型 fail-closed 的 typed 快照，以及 AC3 的 `freeze_request/complete_frozen` 同源 builder，均有代码与可复跑测试支撑；冻结契约、FEA-08/09 证据、共享组合根未改，pins 17/17，check PASS（本会话复跑）。

但存在 **1 个 P0（valid settings 使 Prepare 整体不可用）**、**3 个 P1（合法 binding 形状被误 BLOCKED、fallback 链泄漏 TypeError 破坏冻结错误码、Prepare/Accept 不携带 StartRun 的默认 binding/P15 快照）**；AC2 与 AC8 的 MET 声明不能成立，AC4/AC5/AC6 的声明存在边界/证据夸大。上述 P0/P1 修复并重新跑门禁前，不得进入 DSH 最终集成/关闭。

## 2. 审查范围与方法

- 代码：`git diff aa7bcd6161be5df07e2b8bf546600fec04af038f a92934585088fe75ce8ec53452a67c0a72496d31`（83 文件，含 r1+r2）；逐文件核读 `src/application/tasks/{service,store,projection}.py`、`src/infrastructure/{providers/{registry,handlers,openai_client,translation_openai},sqlite/pipeline,pipeline/{assembly,executor}}.py`、`src/bootstrap/{core_service,core_assembly}.py`、`src/ports/translation/protocol.py`、`apps/desktop-avalonia/**` 的 C# 改动与新增测试。
- 对照：C-08 冻结条款 SC-R01–R09（`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`）、C-08 冻结记录、C-13、C-05、C-04b、M2-C1 rev 2.12 §5.5（PreparedRun/3 错误码）、ADJ-2026-11-04-FEA-10-R2 的 AC2/3/4/6 完成口径与三文件窄改授权。
- 证据：抽查 `verification/FEA-10/logs/**`、`AC-MATRIX.md`、`DELIVERY-MANIFEST.json`、`RESOURCE-MANIFEST.json`（总量与抽样）、`changed-files.txt`、`scope*.log`、`ipc/real-ipc.txt`；独立复跑 `check.ps1`、`verify_pins.ps1`、`pytest tests/fea10 -q`；针对可疑边界写只读探针（见 §4 证据列）。
- 未逐个读取 825 个 fixture 资源目录，只核对 manifest 结构与抽样；未重算 6617 行 RESOURCE-MANIFEST 的逐文件哈希（其生成器只读、清单为 PRESERVE_REFERENCED 记录）。

## 3. Findings

> 级别定义：P0 阻断（AC 不能成立/交付不可用）；P1 必修（正确性/冻结契约/生产语义缺陷）；P2 非阻断（证据、边界、可维护性）。所有 finding 状态为 open（本会话不修复）。

| ID | 级别 | 文件:行 | 问题与影响 | 依据（契约/AC） | 修复建议 | 复现/证据 |
|---|---|---|---|---|---|---|
| R-001 | **P0** | `src/application/tasks/store.py:76-93`；对照 `src/bootstrap/settings_sections.py:73-85` | `validate_prepared_snapshots` 用硬编码 8 段 settings 白名单，且键名与冻结 settings 面不一致：合法的 `typeset.stroke_enabled`、`typeset.auto_font_size`（settings 面实际键名）被拒；`providers`、`network` 等实际存在于 `pipeline_defaults.settings_json` 的段被拒。任何带合法用户设置的安装执行 `PrepareRun` 都会抛 `RUN_SNAPSHOT_INCOMPLETE`，新两阶段路径在真实配置下不可用。 | AC2「settings/provider snapshot 为完整可重放值」；ADJ §2.2「强类型白名单落盘（非整字典）」不授权拒绝**合法**冻结设置面；P15/设置节契约 | 把 replay schema 改为从冻结 settings 面派生；对不影响执行的段（providers/network）**过滤**而非拒绝；对执行相关段/键做真正的强类型白名单；为每个冻结 section 各加一条 Prepare 回归。 | 探针：`save_settings_section('typeset', {'stroke_enabled': True})` → `RUN_SNAPSHOT_INCOMPLETE`；`{'auto_font_size': True}` → 同；`providers`/`network` → 同；`ocr.script`/`inpaint.preferred_quality` → Prepare OK。 |
| R-002 | **P1** | `src/infrastructure/providers/registry.py:443-456` | `run_binding_available` 只取 `binding["provider_id"]`。合法的 mapping 形状 `{"id": ...}` / `{"provider_profile_id": ...}`（`PipelineDefaultsService._validate_binding_shape`、`chain_from_binding`、`resolve_binding`、`resolve_for_run` 都支持）在 freeze 后仍无 `provider_id` 键，probe KeyError→False，Run 在 plan 期被误判 `BLOCKED(PROVIDER_UNAVAILABLE)`，永不执行。StartRun 与 Prepare/Accept 都受影响。 | AC4「凭据/版本不可用→blocked」不允许把**可解析**的 provider 误判为不可用；ADJ §2.2 的 typed 快照必须可重放；既有 binding 形状兼容 | 复用 `resolve_for_run` 的三键提取（`provider_id/provider_profile_id/id`），并在 `freeze_run_snapshots` 的 value 中补规范化 `provider_id`；加 mapping 形状的 plan/执行回归。 | 探针（OCR 已 committed 后）：string binding plan=`pending`；`{'provider_id': ...}` plan=`pending`；`{'id': ...}` 与 `{'provider_profile_id': ...}` 均为 `blocked` + `PROVIDER_UNAVAILABLE`。 |
| R-003 | **P1** | `src/infrastructure/providers/registry.py:396-404`；`src/application/tasks/store.py:104-107` | 显式 fallback 链指向未注册/未 typed 的 provider 时，递归 freeze 把 fallback 留成**字符串**；`validate_prepared_snapshots` 对其执行 `fallback["execution"]`，抛 `TypeError: string indices must be integers`（或缺 execution 时 KeyError）。Core 的 `except Exception`（`core_service.py:4713-4722`）把它投影为 `UNKNOWN/internal`，违反 AC2「其余类型 … Prepare fail-closed 抛 `RUN_SNAPSHOT_INCOMPLETE`」。 | AC2 的 fail-closed 错误码；C-08/M2-C1 §5.5 冻结三错误码；ADJ §2.2 二选一 | 在 freeze/validate 中要求每个 fallback 都是含 `execution`+`execution_digest` 的 Mapping，否则抛 `RUN_SNAPSHOT_INCOMPLETE`；对 fallback 的 unsupported 类型同样走该错误码；加 primary+unsupported fallback 的 Prepare 回归（含错误码断言）。 | 探针：注册 `docTR-blob` legacy translation provider，binding `{'provider_id': 'fea10-primary', 'fallback': ['fea10-legacy']}` → `prepare_run` 泄漏 `TypeError: string indices must be integers, not 'str'`（非 PipelineError）。 |
| R-004 | **P1** | `apps/desktop-avalonia/src/NewManga.App/Services/RunContracts.cs:407-415`；`HostController.cs:2097,2110-2123`；`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:242,991-1020`；`src/bootstrap/core_service.py:4584-4588` | Prepare/Accept 与既有 StartRun 不是同一条生产语义：①StartRun 经 `library_start_run` 的 `WriteStartRunOverrides` 注入 Host 默认 `{"ocr":"manga-ocr"}`，而 `PrepareRunAsync` 直接调用 `RunPayloads.PrepareRun`，绕过 dispatcher/默认注入；②Core 只在 StartRun 分支附加 `_p15_settings_snapshot`，Prepare/Accept 不附加。结果：同一 scope 下 StartRun 可用的默认 OCR binding 在 Prepare/Accept 的 Run 中缺失（plan/执行 fail），P15 profile 保护/解析也不覆盖该 Run；真实 IPC 用例只验证 wire 重放、不执行，因此未暴露。 | AC8「生产 assembly Prepare/Accept/commit」；AC1/AC3 的「同一 Run 语义」；C-08 SC-R01/R04；P15 settings 快照的既有 StartRun 语义 | 让 Prepare/Accept 复用 StartRun 的 payload builder 与默认 binding 注入；在 Core 的 Prepare 路径同样附加 P15 快照，并让 prepared 校验接受该键；补一条 IPC 测试：Prepare→Accept→plan/至少一步 commit/或断言与 StartRun 的 binding 集合相同。 | 代码路径核对（HostController 2097 vs 2117；dispatcher 242/991；core_service 4585-4588）；`RunStartRequest` 在 UI 侧为 `overrides=null`（`StudioBatchViewModel.cs:1119`）。 |
| R-005 | P2 | `tests/fea10/test_snapshot_retry.py:184-208`；`src/infrastructure/providers/registry.py:339-341` | AC4 的「本地 provider 版本漂移（冻结 model≠live model）→BLOCKED」只在 **mock-local**（测试 provider）上被证明；真实生产本地 provider（`local-manga-ocr-onnx`/`local-paddleocr`/identity 等）不在 typed 集合内，Prepare 直接 fail-closed，因此生产上没有版本漂移分支。AC-MATRIX/卡中把该分支写成通用结论，证据夸大。 | AC4「凭据/版本不可用→阻塞」；ADJ §2.3 | 在 AC 矩阵/卡中注明「版本分支当前仅 mock-local，生产本地 provider 走 fail-closed」；后续 Task 为真实本地 provider 增加 typed adapter 版本校验，或明确该分支的契约边界。 | 测试只注册 `m2ac1-mock-translate`；`freeze_run_snapshots` 的 typed provider_type 集合不含真实本地类型。 |
| R-006 | P2 | `src/infrastructure/providers/registry.py:388`（freeze 内 `validate_provider_execution`）；`tests/fea10/test_prepared_run.py:110-141` | 「既有 StartRun 兼容不回归」只证明了 unsupported provider_type（freeze 跳过）；对**支持类型但配置不完整**（如空 model、白名单外 `extra_options`）的 binding，`create_run` 本身就会抛 `RUN_SNAPSHOT_INCOMPLETE`，即 StartRun 在验收边界提前失败，而非原有「接受后 plan/执行失败」。这是未披露的行为变化。 | AC2「既有 StartRun 兼容不回归」；ADJ §2.2（fail-closed 限定 Prepare） | 把 typed 执行校验放到 Prepare/Accept 路径，或为 StartRun 增加兼容分支；至少补一条「支持类型+不完整配置的 StartRun」回归并在卡中披露。 | 探针：注册 `openai-compatible` provider（`model=''`）→ `create_run('retranslate_region')` 返回 `RUN_SNAPSHOT_INCOMPLETE`。 |
| R-007 | P2 | `src/application/tasks/projection.py:154-163`；`apps/desktop-avalonia/src/NewManga.ApplicationCore/RunMonitor.cs`（无改动） | AC6 的 `TaskProjection.is_terminal` 是**新增且无生产消费者**的属性（全仓仅 `tests/fea10/test_control_terminal.py` 引用）；「UI 不早于 Core 持久 status」只在 Python projection 层断言，C# RunMonitor/RunStateStore 无改动、无专项回归。AC6 的「真实不变量」目前是测试/辅助性质，不是被生产代码消费的判据。 | AC6；ADJ §2.4「在既有 RunMonitor/RunStateStore 与 Python projection 上验证」 | 明确 AC6 边界（Python projection 专项，C# 结构性说明）；若要求生产消费，接入 GetTaskProjection/UI 终态门控并补 .NET 测试；至少给 `is_terminal` 的真实调用方或标注为测试辅助。 | 全仓 `is_terminal` 搜索：仅 projection 定义与 fea10 测试使用（另有 `PlanDecision.is_terminal` 无关）。 |
| R-008 | P2 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10RunIpcTests.cs:73-77` | 真实 IPC 用例在测试内部写**受版本管理的证据** `verification/FEA-10/ipc/real-ipc.txt`，内容含随机 `Guid` 的 DataRoot。任何后续重跑都会把该文件改成不同路径并污染工作树（与 AC9 证据字节稳定性、可复现性冲突），且证据不是由 harness/日志生成。 | AC9 证据纪律；Task「不得改写证据字节」精神 | 测试写入 workspace fixture；由运行命令/日志记录 DataRoot；或让 harness 生成 `real-ipc.txt` 并在重跑后恢复。 | 测试第 73-77 行 `File.WriteAllTextAsync(... "real-ipc.txt")`；`real-ipc.txt` 为 tracked 文件。 |
| R-009 | P2 | `verification/FEA-10/AC-MATRIX.md:24`；`doc/tasks/FEA-10.md:192,199`；`verification/FEA-10/DELIVERY-MANIFEST.json:2` | 证据陈述不一致：①AC-MATRIX 称 `ipc-r2.log` 保留「首次失败」历史，但该文件只有一次通过（失败历史在 r1 的 `real-ipc.log`）；②卡两处写 r2 `check PASS（3 warnings）`，实际 `governance-r2.log` 与 AC-MATRIX 为 4，本会话复跑亦为 4；③DELIVERY-MANIFEST 的 `head=25ba7cb2`，且 `doc/tasks/FEA-10.md`、`doc/handoffs/FEA-10-handoff.md` 两项哈希与 `a9293458` 的 blob 不一致（清单生成后被再次编辑）。 | AC9 证据/Handoff/EV；模板证据纪律（数字须同处给总数与差值） | 修正 AC-MATRIX/卡中的 3 warnings → 4 与 ipc 失败历史指向；在 `a9293458` 重新运行 `record_delivery.py`（或在清单中记录生成后变更）；如保留旧清单，明确其快照时点。 | `governance-r2.log`：`PASS (4 warnings)`；`ipc-r2.log`：6 行仅一次通过；`git cat-file blob a9293458:...` 的 sha256 与清单不同。 |
| R-010 | P2 | `verification/FEA-10/record_delivery.py:27-40`；`verification/FEA-10/logs/scope.log:35-36`；交付提交含 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/reviews/ADJ-2026-11-04-FEA-10-R2.md` | `record_delivery.py` 用 `git diff`（工作树 vs HEAD）+untracked，r2 时 HEAD=`25ba7cb2`，因此 `changed-files.txt`/`scope.log` 不含 r1 阶段提交中的 DSH 治理指针文件；而完整交付 diff `aa7bcd6→a9293458` 包含这些卡外路径。DSH 作为 Integrator 有权改指针，但 AC9「范围 diff 合规/0 域外」的陈述只对 Owner 的 dirty 字节成立，且卡未列这些 DSH 自有路径。 | AC9；卡 `allowed_paths`/`out_of_scope`；DSH 单点治理指针职责 | 在 Task/AC-MATRIX 中把 AC9 范围限定为 Owner 字节，单列 DSH 指针编辑；或扩展 scope 检查基线为 `aa7bcd6` 并对 DSH 文件显式豁免。 | `git diff --name-only aa7bcd6 a9293458 -- doc/` 含 PLAN/STATUS/ADJ；`git diff --name-only aa7bcd6 a9293458 -- doc/contracts verification/FEA-08 verification/FEA-09 apps/.../App.axaml* apps/.../NewManga.sln` 为空。 |
| R-011 | P2 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:266-305` | Host 候选存储 `_preparedRuns`/`_preparedAttempts` 在接受成功后不移除；已消费候选的完整快照（settings/provider）长期驻留内存；清理只在后续 Prepare 时对「过期且未被尝试」的项进行，且 `ContainsValue` 为 O(n²)。长期运行会无界增长。 | C-08 SC-R04（Host 临时候选直到接受或过期）；资源/内存卫生 | 接受成功/确定失败后移除候选；给 attempt 映射设上限或随候选清理；用 `HashSet`/反向索引避免 O(n²)。 | 第 283 行写入；第 297-305 行接受路径无删除；清理条件见第 279-282 行。 |
| R-012 | P2 | `src/application/tasks/store.py:353-378` | `InMemoryTargetCatalog.commit_step` 删除了 pause/cancel 拒绝，注释称「scheduler honors intent at the next boundary」；但生产 `SqliteTargetCatalog.commit_step` 仍在 seam 拒绝（`sqlite/pipeline.py:963-978`）。确定性测试适配器与生产 seam 语义分叉，使用该适配器的 pipeline 测试不再能验证「pause/cancel 在 seam 阻止 live 写」。 | AC5 ⑨ pause/cancel；既有冻结语义；测试适配器一致性 | 恢复该守卫，或在适配器处明确标注差异并新增等价 seam 测试；不要用删除断言的路径换取测试通过。 | 本会话 diff 对照：store 353-378 与 sqlite 963-978。 |
| R-013 | P2 | `tests/fea10/test_commit_zero_write.py:47-55` | AC5 的 `crash_restart` 项**不调用** `commit_step_result`（只重开 DB 后断言 live 未变、completed 未增、candidate=`abandoned`）；因此它不是「seam 未成功」的断言，而是恢复路径断言；且 AC5 说的「candidate 可诊断/恢复」实际是 abandoned（payload 保留但不可恢复提交）。AC5/卡中「逐项断言 seam 未成功」对该项略夸大。 | AC5 ⑩；C-08 SC-R07/SC-R04 | 在 AC 矩阵中区分「恢复放弃」与「seam 拒绝」；如需要，补一条重开后 commit 抛 `INVALID_RUN_TRANSITION` 的断言（本会话探针已证实该行为）并断言 candidate payload 可诊断。 | 本会话探针：重开后 step=`interrupted`，commit 抛 `INVALID_RUN_TRANSITION`，region 不变、completed=0、candidate=`abandoned`。 |
| R-014 | P2 | `src/application/tasks/store.py:185-195` | `validate_prepared_overrides` 仅按 key 名黑名单（token/password/headers/...）递归拒绝，会把**合法业务键**（如术语表 glossary 的 term `"token"`、设置里的 `"headers"` 字段）误判为认证材料，导致 Prepare 误 fail-closed。 | AC2 敏感面；ADJ §2.2（拒认证材料，不是拒同名词汇） | 限制在会承载认证材料的结构（provider execution/override 的认证字段）上做键名校验；对 glossary/settings 等业务内容采用值类型/引用校验；补一条 glossary `token` 不误拒的回归。 | 代码读：递归 key 名集合无上下文区分。 |
| R-015 | P2 | `src/infrastructure/sqlite/pipeline.py:1018-1021`；`src/application/tasks/service.py:937-940` | commit_step 的 `except Exception` 把 `SourceImportError`（source lease/grant 失效）与任何非预期异常统一转成 `db_failed`，再落为 `DB_FAILED`；`source_lease` 故障的 AC5 测试不断言错误码，用户/诊断无法区分源租约与 DB 故障。 | AC5 ⑤ source lease；错误 taxonomy；诊断可读性 | 在 commit_step 捕获层保留 `PipelineError`/`SourceImportError` 的 typed code（至少区分 source/target/db），并补断言。 | 代码路径；`test_commit_zero_write.py:33-39` 注入 RuntimeError 后仅断言 `status != committed`。 |
| R-016 | P2 | `src/infrastructure/pipeline/executor.py:44-51` | `preview_run` 捕获所有异常并返回 `{"translationPayload": "unavailable"}`，把 provider 未配置/配置错误/源文本缺失等原因混淆为同一「不可用」；UI 无法据此区分「依赖上游输出」「无绑定」「敏感材料/白名单拒绝」。这削弱 Prepare 的可用诊断。 | AC3 preview 语义；AC1 displaySummary/redacted preview | 返回 typed 的 preview 状态（requires_upstream_output / unavailable / provider_missing 等）或至少记录诊断 code；不要吞掉所有异常。 | 代码读：`except Exception: return {... "unavailable"}`。 |

## 4. AC 勾选的独立判断

| AC | 卡上结论（r2） | 我的独立判断 | 理由 |
|---|---|---|---|
| AC1 | MET | **认可 MET（机制）** | 本会话复跑 `test_prepared_run.py`；`PrepareRun` 在 `create_run(_persist=False)` 路径零 DB 写/零执行（trace 断言），`AcceptRun` 在既有 `store.accept` 的 BEGIN IMMEDIATE 内 `validate()` 后写 Run+receipt；quartet digest 与独立哈希一致；过期码/缺失码/零写与 C-08 一致。**前提**：R-001/R-004 使该机制在真实配置下无法完成 Prepare/Accept，故 AC1 的「可用性」需与 AC2/AC8 一起看。 |
| AC2 | MET | **不认可（NOT MET）** | typed 四类 provider（mock-local/openai-compatible/openai-compatible-vision/local-sakura）的 execution+digest 闭环、敏感面（credential_ref opaque、无 secret、token overrides 拒绝）与 mock/remote 回归成立；但 R-001 证明**合法冻结 settings** 被拒，AC2 的「settings snapshot 完整可重放」不成立；R-003 证明 fallback 链未按冻结 `RUN_SNAPSHOT_INCOMPLETE` fail-closed。另有 R-006 的 StartRun 兼容偏差。 |
| AC3 | MET（ADJ §2.1 限定） | **认可（按限定口径）** | 三文件窄改在 DSH 授权内；`freeze_request`/`complete_frozen`/`request_digest` 让 preview 与 send 共用同一 builder/同一冻结 config；`payloadDigestSend` 取实际发送的冻结字节；transport 拦截测试证明 Prepare preview digest == 实际 POST 内容（`test_preview_and_real_transport_body_use_same_builder_and_pinned_config`）；Accept 后 provider/defaults 漂移下仍发冻结 endpoint/model；wire/冻结契约零改；providers 559/4。上游 OCR 依赖步骤只用 `requires_upstream_output` 标注且不制造正文，符合 ADJ §2.1.3。 |
| AC4 | MET | **认可（附边界）** | 同键重放不新建、新键 retry 建 `source_run_id` 子 Run、失败页子集、接受时重读上下文冻结、旧 run 快照不变；凭据不可解析→plan `BLOCKED(PROVIDER_UNAVAILABLE)`、vault 恢复后 resume 解除；retry 换 provider→新 Run 且旧 run 字节不变，均有真实 SQLite/production assembly 测试。**边界**：版本漂移只在 mock-local 上成立（R-005）；「新配置差异确认」在实现上是「显式 retry 即确认」的新 Run，没有独立差异披露/确认步骤，AC 文字略强于证据。 |
| AC5 | MET（seam 层） | **认可（seam 层，附边界）** | 17 项故障矩阵在 production SQLite assembly 上逐项断言 `regions.text_json`/`current_revision_id`/`region_revisions` 行数不变、completed step count 不增、candidate 可诊断；成功路径单 BEGIN IMMEDIATE/单 COMMIT；多 Region 编辑 apply 与 step seam 分别使用既有 candidate 存储，未混用。**边界**：R-012 适配器分叉、R-013 crash_restart 不尝试 commit、R-015 source lease 错误码、Windows 原生 lease 未跑（已在 Handoff NOT_RUN 披露）。 |
| AC6 | MET | **认可（Python/DB 层，附边界）** | 控制请求持久化≠状态改变（pause/stop 后 status 仍 running、`*_requested` 落库）；调度器边界后 projection 才报 paused/cancelled；四终态共同不变量+completed/completed_with_failures 附加判据+非法组合拒绝；同 DataRoot/DB 重开 Core 复读 PAUSED 与请求位。**边界**：R-007（`is_terminal` 无生产消费者、C# 未专项、UI 级未验证）。 |
| AC7 | MET | **认可** | same-key receipt 优先于过期/配置读取；丢 ACK 重放找回原 run；异 fingerprint `IDEMPOTENCY_KEY_REUSED`；同 request_id 不同 key 建两个 Run；`restart_core.py --stop/--start` 两进程同 DB 与真实 stdio Core 进程重启重放（`Fea10RunIpcTests`）都通过；只覆盖冻结带 key 操作，不新增按 request 查询。 |
| AC8 | MET | **不认可（PARTIAL）** | 生产 assembly + 真实 stdio Core/client IPC 存在，build 0/0、.NET 1344/0/75 不减少、pytest 1047、真实 IPC 1 passed（日志与 DSH 日志一致）；但 R-004 证明 Prepare/Accept 不携带 StartRun 的默认 binding/P15 快照，真实 IPC 又只测 wire 重放不执行，因此「生产 assembly Prepare/Accept/commit」只对 mock/remote 测试装配成立，对 UI 默认路径不成立。 |
| AC9 | BLOCKED | **认可 BLOCKED（范围/证据措辞需修正）** | 冻结 pins 17/17（本会话复跑 PASS）、C-05/C-15/C-16/C-07/C-08/C-13/C-04b 字节未改、FEA-08/09 证据零 diff、共享组合根未改、check PASS（4 warnings）。但 R-009/R-010 的清单/警告数/scope 基线/DSH 指针路径需修正；独立 Review 即本文件，仍需 findings 处置与 DSH 集成。 |
| AC10 | MET | **认可** | 无新依赖/模型/未冻结 Schema；PrepareRun/AcceptRun 是 M2-C1 rev 2.12 已登记 wire 2.12（PREREQ-1），实现补齐 dispatch 属本卡授权；共享组合根（App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln）零改动；source 校验复用既有 `SourceReadGrantRegistry`；fixtures 合成数据，r2 TEMP/TMP 指向 workspace。 |

## 5. 独立验证记录

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 仓库状态 | `git rev-parse HEAD`；`git status --porcelain` | HEAD=`3e01fae8`（delivery a9293458 + docs 3e01fae）；工作树干净 | 本会话输出 |
| 交付 diff | `git diff --stat aa7bcd6 a9293458`；`git show --stat 25ba7cb2/a9293458` | 83 文件；r1/r2 阶段提交与卡/Handoff 描述一致 | 本会话输出 |
| 冻结/范围 | `git diff --name-only aa7bcd6 a9293458 -- doc/contracts verification/FEA-08 verification/FEA-09 <组合根路径>` | 空（冻结契约、FEA-08/09 证据、组合根未改） | 本会话输出 |
| Pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT=0；17/17 PASS | 本会话输出 |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT=0；PASS (4 warnings)（非卡中 r2 段落的 3 warnings） | 本会话输出 |
| FEA-10 测试 | `TEMP/TMP=G:/CODEX/New Manga.workspace/FEA-10/fixtures/review-9f3c1b7a C:/Python314/python.exe -m pytest tests/fea10 -q -p no:cacheprovider` | **44 passed，EXIT=0** | 本会话输出 |
| AC2 settings 探针 | `save_settings_section('typeset', {'stroke_enabled': True})` 等后 `prepare_run` | `RUN_SNAPSHOT_INCOMPLETE`（R-001） | `fixtures/review-9f3c1b7a/probe9.py` 输出 |
| AC2 binding 探针 | `{'id': ...}` / `{'provider_profile_id': ...}` 后 `prepare_run`+`plan_run` | Prepare OK 但 plan=`blocked(PROVIDER_UNAVAILABLE)`（R-002） | `probe2.py` 输出 |
| AC2 fallback 探针 | primary typed + `fallback: ['fea10-legacy']`（docTR-blob） | 裸 `TypeError`（R-003） | `probe.py` 输出 |
| AC5 crash_restart 探针 | 重开同一 DB 后 `commit_step_result` | `INVALID_RUN_TRANSITION`；region 不变、completed=0、candidate=`abandoned` | `probe7.py` 输出 |
| 证据抽样 | 读 `python-main-r2.log`、`provider-regressions-r2.log`、`fault-matrix.log`、`dotnet-*-r2.log`、`ipc-*.log`、`governance-r2.log`、`pins-r2.log`、`scope*.log`、DSH `dsh-gates-r2.log` | 1047 passed；559/4；17 passed（名称逐项）；1344/0/75（各程序集求和一致）；IPC 1 passed；check 4 warnings；pins 17/17 | 日志原文 |
| Delivery manifest | 逐文件 SHA-256 对比 | 29 项中 2 项（Task/Handoff）与当前树不一致；`head=25ba7cb2`（R-009） | 本会话脚本输出 |
| .NET build/test、真实 IPC | **NOT_RUN（本会话）** | 不重跑：`Fea10RunIpcTests` 会在测试内改写 tracked 的 `verification/FEA-10/ipc/real-ipc.txt`，.NET 全量会重写 FEA-09 `wire-redacted.ndjson`（r1/r2 已多次发生），不符合本 Review 的只读约束；仅核对提交日志与 DSH 日志的一致性 | `Fea10RunIpcTests.cs:73-77`；`verification/FEA-09/logs/wire-redacted.ndjson` r2 重写记录 |
| Windows 系统级 source lease、真实外网 provider/模型、原生 UI 端到端点击 | NOT_RUN | 与 Handoff NOT_RUN 一致；seam 注入测试不能替代系统级验收 | Handoff §r2 NOT_RUN 1/2/4；AC-MATRIX |

**证据真实性结论**：未发现「未跑冒充跑过」的迹象——r2 主套件/providers/逐文件/构建/.NET/真实 IPC/check/pins/scope 的日志均带命令与 EXIT，r1 的失败历史（`real-ipc.log` 的 INVALID_RUN_TRANSITION、`dotnet-build-final.log` 的 EXIT=1、并发 build 失败）保留未改写；DSH 的 `dsh-gates-r2.log` 还保留了当时的 check FAIL（AC-MATRIX pin 更新前）与 FEA-09 diff，说明失败历史可见。问题在于**结论性证据的措辞/时点**（R-009/R-010）与 IPC 测试写 tracked 证据（R-008），不是伪造。

## 6. 对 DSH 的处置建议

1. **先修 R-001/R-003**（同属 AC2 的 Prepare 边界），再修 R-002/R-004（AC4/AC8 生产语义）；每项加针对性回归（合法 settings 各 section、mapping binding、unsupported fallback 错误码、Prepare/Accept 与 StartRun 的 binding 集合一致）。
2. R-001 修复后须重跑 `tests/fea10 tests/core tests/pipeline` + 全量 .NET build/test + 真实 IPC；并重新生成 `DELIVERY-MANIFEST`/`changed-files`/`scope`（以新的 delivery head 为基线），修正 AC-MATRIX 的 ipc 失败历史与 `3 warnings`。
3. R-008 的 IPC 证据写入应在修复时一并移出仓库；否则 DSH 每次重跑都会弄脏工作树。
4. R-012/R-013/R-015 属 seam 语义/测试强度问题，建议在本次返修中一并处理（R-012 是生产/测试适配器分叉，优先级接近 P1）。
5. 本 Review 只对 `a9293458` 有效；修复后必须在新 head 上重新派发独立 Review（或由 DSH 按处置规则复审本文件 findings 并记录新 head），不得把本文件当作新 head 的批准。
6. 不 push；不 closeout；AC9 的独立 Review 现在完成的是「发现并请求返修」，不是 approved。

## 7. 复审边界

- 本文件不构成对 `a9293458` 之后任何 head 的批准；若 DSH 在修复中改动生产/测试/证据，须重新执行独立 Review。
- 未审到：真实 Windows 源租约/原生 UI 点击/真实外网模型质量/825 个 fixture 的逐目录内容；这些在 Handoff 已列为 NOT_RUN，本 Review 沿用该边界。
