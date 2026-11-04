# FEA-10 rework r1（DSH，2026-11-04）

状态：**返修记录**（实现方：DSH 集成会话；独立新 head Review 待派）。
输入：`doc/reviews/FEA-10-impl-r1.md`（独立子 agent Review，reviewed_head `a9293458`，changes_requested，1 P0 + 3 P1 + 12 P2）。
依据：`ADJ-2026-11-04-FEA-10-R2`；Task 卡 AC1–AC10；C-08/C-13/C-05/C-04b/M2-C1 rev 2.12。

## Findings 处置

| ID | 级别 | 处置 | 证据 |
|---|---|---|---|
| R-001 | P0 | **已修复**：`validate_prepared_snapshots` 改为执行段强白名单 + 非执行段过滤，补真实 `typeset.stroke_enabled/auto_font_size` 等冻结键；合法用户设置不再使 Prepare 失败；执行段白名单外键仍 fail-closed。 | `test_prepared_run.py::test_prepared_settings_filter_non_execution_sections_and_reject_unknown_execution_keys` |
| R-002 | P1 | **已修复**：`run_binding_available` 接受 `provider_id`/`provider_profile_id`/`id` 三形状；freeze 对 Mapping binding 规范化写入 `provider_id`。 | `test_prepared_run.py::test_mapping_binding_shapes_stay_available_at_plan` |
| R-003 | P1 | **已修复**：fallback 指向未注册/未 typed provider 时，freeze/validate 统一抛 `RUN_SNAPSHOT_INCOMPLETE`，不再泄漏 TypeError/UNKNOWN。 | `test_prepared_run.py::test_untyped_fallback_fails_closed_with_frozen_error_code` |
| R-004 | P1 | **已修复（Host+Core）**：`RunPayloads.PrepareRun` 注入与 StartRun 相同的 Host 默认 provider_bindings（用户显式 binding 优先、环境可禁用）；Core Prepare 继承 StartRun 的 `provider_profiles` 门径；本地 provider（manga-ocr/paddle/korean OCR）获得 typed 快照，默认 `{"ocr":"manga-ocr"}` 可 Prepare；新增 Host 单测断言 Prepare/StartRun payload 的 binding 集合一致。 | `test_default_local_ocr_binding_is_typed_replayable`；`RunControllerTests.PreparedRunPayload_CarriesTheSameHostDefaultBindingsAsStartRun` |
| R-005 | P2 | **部分修复**：本地 provider 现有 typed 快照与 resolve 版本校验（manga-ocr/paddle 类型）；其余本地/provider 类型仍 fail-closed。剩余覆盖登记为债务 `DEBT-FEA10-R005`。 | AC-MATRIX rework 节 |
| R-006 | P2 | **未修（登记债务 DEBT-FEA10-R006）**：StartRun 对「支持类型但配置不完整」提前 fail-closed 的行为变化未加兼容分支；已在 AC-MATRIX 披露。 | AC-MATRIX rework 节 |
| R-007 | P2 | **未修（登记债务 DEBT-FEA10-R007）**：AC6 的 `is_terminal` 仍无生产消费者；AC6 结论限定为 Python projection/DB 层（AC-MATRIX 已注明）。 | AC-MATRIX |
| R-008 | P2 | **已修复**：`Fea10RunIpcTests` 证据改写到隔离 workspace 的 `root/real-ipc.txt`，不再写 tracked `verification/FEA-10/ipc/real-ipc.txt`。 | `Fea10RunIpcTests.cs` |
| R-009 | P2 | **已修复（rework r2 复核）**：AC-MATRIX/Handoff 的 warnings 计数修正为 4；DELIVERY-MANIFEST 在最终 head 提交前重新生成并记录 `excluded_docs`（RR-02）。 | `verification/FEA-10/AC-MATRIX.md`、`DELIVERY-MANIFEST.json` |
| R-010 | P2 | **已修复（口径）**：AC9 的「0 域外」明确限定为 Owner 字节；DSH 治理指针文件为 Integrator 单点编辑并在 AC-MATRIX 单列。 | AC-MATRIX rework 节 |
| R-011 | P2 | **未修（登记债务 DEBT-FEA10-R011）**：Host 候选缓存清理/上限未改。 | AC-MATRIX |
| R-012 | P2 | **已处理（文档化差异）**：InMemory 适配器与 SQLite seam 的 pause/cancel 语义差异显式标注；等价 seam 由 AC5 故障注入覆盖；既有 pipeline 测试保持绿（不恢复会破坏已发布测试语义）。 | `store.py` 注释 + `test_commit_zero_write.py` |
| R-013 | P2 | **未修（登记债务 DEBT-FEA10-R013）**：crash_restart 项仍为恢复放弃断言；AC5 结论已按 seam 层限定。 | AC-MATRIX |
| R-014 | P2 | **已修复**：认证材料键扫描限定 `provider_bindings`（递归）与 settings 段浅层；glossary 词条 `token` 不再误拒；provider_bindings 走私仍拒绝。 | `test_glossary_term_named_token_is_not_treated_as_authentication_material` |
| R-015 | P2 | **未修（登记债务 DEBT-FEA10-R015）**：commit_step 的 source lease 错误仍归并为 db_failed。 | AC-MATRIX |
| R-016 | P2 | **未修（登记债务 DEBT-FEA10-R016）**：preview 异常仍统一 unavailable。 | AC-MATRIX |

## 验证（DSH 实跑）

- `pytest tests/fea10 tests/core tests/pipeline`：**1051 passed**（+4 新回归，无 failed）。
- `pytest tests/providers`：559 passed / 4 skipped。
- `dotnet build`（Release）：0 warning / 0 error。
- `dotnet test`（Release，全量）：见 `logs/dsh/dsh-rework-dotnet2.log`。
- 真实 IPC（`NEWMANGA_FEA10_IPC=1`）：见 `logs/dsh/dsh-rework-dotnet2.log`。
- `check.ps1` PASS（4 warnings）；`verify_pins.ps1` 17/17；范围 0 域外；FEA-09 零 diff（测试重写后恢复）。

## 限制

- 本记录由实现方（DSH）撰写，**不是独立 Review**；`a9293458` 的 Review 结论不适用于 rework head。
- 需派全新上下文 Review 审查 rework head（Codex 19:50 后优先；否则 ZCode/独立子 agent）；approved 后才能 closeout。

## DSH rework r3（2026-11-04，按 FEA-10-final-review-r1 处置）

- 最终 Review（Codex 全新上下文，reviewed_head `5be507e2`）changes_requested：P0=0、P1=3（FR-01/FR-02/FR-03）、P2=5。报告正文见 `doc/reviews/FEA-10-final-review-r1.md`（Codex 只读会话未能落盘，DSH 据其最终回复归档）。
- FR-01（已修复）：认证材料扫描改为「任意位置嵌套键拒绝」，仅 mapping glossary 的**词条名**豁免、词条值继续扫描；settings 快照整体扫描（含 defaults）；`glossary.nested.headers.authorization` 类走私与 `typeset.font_family.headers.authorization` 均拒绝。
- FR-02（已修复）：Canonical Evidence 的 commit 回填为包含 AC-MATRIX 字节的提交（见 Task 卡 EV 行）；DELIVERY-MANIFEST 记录 `excluded_docs` 与生成时 head。
- FR-03（已修复）：新增 `_freeze_fallbacks` helper，mock/local/remote 三类 typed primary 统一冻结 fallback 链；未注册/未 typed fallback 统一 `RUN_SNAPSHOT_INCOMPLETE`。
- FR-04（已修复）：Core Prepare 拒绝 `provider_bindings=null`（存在即须为对象）。
- FR-05（已修复）：accept 后 settings 快照重新 `freeze_snapshot`，不可变。
- FR-06（已修复）：`_redact` 保留 mapping glossary 的词条名（`token` 词条不再被删），值仍 redact。
- FR-07（已修复）：执行段非 Mapping 形状保留并触发 `RUN_SNAPSHOT_INCOMPLETE`（不再静默丢弃）。
- FR-08（已修复）：本文档的 C# 测试名改为实际 `RunControllerNullFakeTests.PreparedRunPayload_CarriesTheHostDefaultBindings`；日志指向实际入库的 `verification/FEA-10/logs/dsh-rework2-*.log` / `dsh-rework3-*.log`。
- 回归：`test_nested_auth_material_in_defaults_and_glossary_values_is_rejected`、`test_local_primary_freezes_its_fallback_chain`、`test_illegal_execution_section_shape_is_rejected`、`test_default_local_ocr_binding_is_typed_replayable` 等。
- 门禁（DSH 实跑，`logs/dsh-rework3-*.log`）：pytest 主套件 **1055 passed**、providers 559/4、build 0/0、.NET **1345/0/75**、真实 IPC 1、check PASS（4 warnings）、pins 17/17、FEA-09 零 diff、范围 0 域外。

## DSH rework r4（2026-11-04，按 FEA-10-final-review-r2 处置）

- 第 4 轮 Review（Codex，reviewed_head `e23b01a9`）：changes_requested，P0=0/P1=2（F2-01/F2-02）+P2=2（F2-03/F2-04）。报告 `doc/reviews/FEA-10-final-review-r2.md`。
- F2-01（已修复）：glossary 词条名豁免改为**路径绑定**——仅 `translate.glossary` 的 mapping 词条名豁免一层，词条值与任何其他路径（`typeset.font_family.glossary`、`translate.glossary.outer.glossary`）不再获得豁免；`_redact` 同步路径化。新增回归 `test_renested_or_misplaced_glossary_does_not_restore_the_exemption`。
- F2-02（已修复）：Task 卡 Canonical Evidence 的 commit 精确回填为包含 AC-MATRIX `2d264224…` 的提交（见 EV 行）；manifest 继续记录 `head`/`excluded_docs`。
- F2-03（已修复）：本轮门禁日志（`logs/dsh-rework4-*.log`）逐次记录完整 COMMAND、shell、TEMP/TMP 与 EXIT；历史不完整日志保留不改写。
- F2-04（已修复）：旧导航的历史条目保留原字节，但在当前导航中标注其失效/被替代，指向实际用例 `RunControllerNullFakeTests.PreparedRunPayload_CarriesTheHostDefaultBindings` 与实际日志路径。
- 门禁（实跑）：pytest tests/fea10 **53 passed**、主套件 **1056 passed**、providers 559/4、build 0/0、.NET 1345/0/75、真实 IPC 1，均 EXIT=0；check PASS、pins 17/17、FEA-09 零 diff、范围 0 域外。

## DSH rework r5（2026-11-04，按 FEA-10-final-review-r3 处置）

- 第 5 轮 Review（Codex，reviewed_head `b218b52e`）：changes_requested，P0=0/P1=1（F3-01：嵌套 translate.glossary 可重新获得词条名豁免）。F2-02/F2-03/F2-04 已闭合。
- F3-01（已修复）：豁免只在 `translate.glossary` 且**全部词条值为标量文本**时生效；任何嵌套对象/列表词条值都会消耗豁免、内部 glossary 不再豁免；`_redact` 同步。新增回归 `test_glossary_exemption_cannot_be_regained_by_nesting`。
- 门禁（实跑，`logs/dsh-rework5-*.log`）：fea10 54 passed、主套件 **1057 passed**、providers 559/4、build 0/0、.NET 1345/0/75、真实 IPC 1、check PASS、pins 17/17、FEA-09 零 diff。

