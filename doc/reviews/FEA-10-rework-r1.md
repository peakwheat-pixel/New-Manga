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
| R-009 | P2 | **已修复**：AC-MATRIX 的 ipc 失败历史指向与 check warnings 数（4）修正；DELIVERY-MANIFEST 随 rework head 重新生成。 | `verification/FEA-10/AC-MATRIX.md`、`DELIVERY-MANIFEST.json` |
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
