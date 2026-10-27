# RUN-EXPORT-E2E-1 Handoff（Run/Export 命令端到端）

- Task: `doc/tasks/RUN-EXPORT-E2E-1.md`（team task-28）
- Branch: `task/RUN-EXPORT-E2E-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/RUN-EXPORT-E2E-1`
- Base: `171529b5d`（卡面）；实际分支基于释放提交 `04b657131`（含任务卡 + 治理 PASS 状态）
- Delivery head: 见任务卡 Canonical Evidence 的 commit 列
- 未 push；未改 Core 语义、未改 Host 契约语义、未改旧壳、未碰真实用户数据、不伪造运行成功。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 清单与接线 | **MET** | 9 条命令接线（StartRun/ControlRun/ResumeBlockedRun/GetRunSnapshot/GetTaskProjection/RetryFailedTargets/StartExport/CancelExport/GetExportSnapshot），dispatcher 边界校验；无模型 Run 全页 typed `PROVIDER_NOT_CONFIGURED`；集成测试 6 类 typed 错误断言；`command-list.json` |
| AC2 Export 真跑 | **BLOCKED** | 真实调用 typed `EXPORT_INPUT_UNAVAILABLE`（缺 translated 页）+ target_ref 需 host-control `RegisterExportTarget`（HOST-ISSUER 通道未迁移）；无产物、无 SHA、无伪成功：`probe-base.json`/`probe-models.json` |
| AC3 Run 真跑（含模型） | **BLOCKED（部分链）** | models sidecar + BOOK-FIXTURE：StartRun 接受、run 3.1–6.5s 终态 completed_with_failures；页1–3 detect 真实完成 → OCR typed `PROVIDER_NOT_CONFIGURED`；页4–8 detect `INVALID_INPUT`；未到 translate/render：`probe-models.json` + `core-models.stderr.log` |
| AC4 parity/回归 | **MET** | `--check` PASS、快照 sha 未变；24→33 IMPLEMENTED / 42→33 NOT_SUPPORTED；test.ps1 145/145；vitest 60/567；pytest 3F/2739P/9S（0 新增） |
| AC5 门禁 | **MET** | check.ps1 PASS；64-hex pin；本 Handoff + Record Decision §3 |

## 2. 代码改动（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 9 条 Core 绑定（minor=3）；类注释 24→33 |
| `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `WriteCorePayload` 新增 9 个 case（start_run 必填 command/scope/idempotency_key、control_run 可选 key、start_export 六字段校验、export_id 读取等）+ `WriteRequiredStringArray` 辅助 |
| `src/NewManga.App/Shell/ReaderWorkbenchSupport.cs` | S4Wiring：9 条入 wired（14→23），S4-C 账本删除已接线 4 条（NS 9→5） |
| `tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs` | 新增 6 类 typed 错误真实执行断言（INVALID_REQUEST / TARGET_NOT_FOUND / EXPORT_NOT_FOUND） |
| `tests/NewManga.CoreClient.Tests/Commands/CommandParityContractTests.cs` | 33/33 |
| `tests/NewManga.App.Tests/S4ReaderWorkbenchTests.cs` | 23 wired / 5 NS |

## 3. Record Decision（命令面 / 模型依赖边界）

1. **只接 Core-backed 命令**：Run/Export 控制与投影面全部走冻结协议 2.3 minor=3；`library_reveal_export_folder`
   是 host-local OS 行为，保持 NOT_SUPPORTED，不伪造 Core 路由。
2. **StartExport 的 target_ref 属 host-control 通道**：`RegisterExportTarget` 是 HOST-ISSUER-1 grant/session
   信封命令，C# Host 尚未迁移该通道 → 本批只验证 typed 失败路径；不算 IMPLEMENTED 之外的“成功”。
3. **Export 输入语义**：冻结 Core 只导出 **translated** 产物；BOOK-FIXTURE 仅有 original 页，因此真实导出
   必然 `EXPORT_INPUT_UNAVAILABLE`。要闭环 Export，必须先有可运行的翻译/渲染链（见 §4）。
4. **模型依赖边界**：models 包 sidecar 的 detect 已真实用 ONNX 权重跑通（页1–3 completed）；OCR 仍
   `PROVIDER_NOT_CONFIGURED`、页4–8 `INVALID_INPUT`——按“不伪造成功”原则标 BLOCKED，留待单独诊断，
   不在本 Task 改 Core 语义。
5. **回归隔离**：test.ps1 使用私有 `-EvidenceDirectory`（避免与并行任务共享 rerun log），
   证据新鲜副本在 `verification/RUN-EXPORT-E2E-1/evidence/`。

## 4. 遗留 / NOT_RUN

1. AC2 Export 真跑 BLOCKED：需 (a) Run 产出 translated 页；(b) Host host-control grant 通道（HOST-ISSUER）
   迁移；二者都超出本 Task 范围，需 DSH 裁决后续 slice。
2. AC3 OCR/detect 失败待诊断：建议最小单页复现（detect 单页 + OCR 权重解析），单独小 Task。
3. `library_retry_failed_targets` 未构造真实失败重试场景（run 未达可重试态）。
4. 任务卡 `allowed_paths` 未含 `doc/handoffs/**`；本 Handoff 按 AC5 落位，建议 DSH 补该路径。
5. 需独立 Review（Owner 不得自审）。
