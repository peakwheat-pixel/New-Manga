# RUN-EXPORT-E2E-1 报告：Run/Export 命令端到端验证

- Task: `doc/tasks/RUN-EXPORT-E2E-1.md`（team task-28）；Branch/Worktree: `task/RUN-EXPORT-E2E-1` /
  `G:/CODEX/New Manga.workspace/worktrees/RUN-EXPORT-E2E-1`；卡面 Base `171529b5d`，实际基于释放提交
  `04b657131`（含任务卡 + 治理 PASS）
- 未 push；未改 Python Core 语义、未改 Host 契约语义、未改旧壳、未碰真实用户数据、未 gc/prune。
- **不伪造运行成功**：AC2/AC3 的真实结果见 §2/§3，未闭环的部分明确标 BLOCKED。

## 0. 结论

| AC | 判定 | 要点 |
|---|---|---|
| AC1 清单与接线 | **MET** | 9 条 Core-backed Run/Export 命令接线（StartRun/ControlRun/ResumeBlockedRun/GetRunSnapshot/GetTaskProjection/RetryFailedTargets/StartExport/CancelExport/GetExportSnapshot），dispatcher 复刻旧壳签名做边界校验；冻结 sidecar 实测：无模型时 Run 全 8 页 `PROVIDER_NOT_CONFIGURED`（typed，不静默）；未知 id 返回 `TARGET_NOT_FOUND`/`EXPORT_NOT_FOUND`；集成测试 6 类 typed 错误断言 |
| AC2 Export 真跑 | **BLOCKED** | 冻结 Core 的 StartExport 前置满足不了：①导出要求 **translated 页产物**，BOOK-FIXTURE 只有 original 页 → typed `EXPORT_INPUT_UNAVAILABLE`；②`target_ref` 需 **host-control RegisterExportTarget grant**（HOST-ISSUER 通道）而 C# Host 尚未实现该通道。两次 probe（base/models）均为 typed 错误，无产物、无伪成功 |
| AC3 Run 真跑（含模型） | **BLOCKED（部分链）** | models 包 sidecar + BOOK-FIXTURE 8 页：StartRun 被接受（`run_id`），run 在 3.1s（模型预热后）/6.5s（冷）终态 `completed_with_failures`；页 1–3 **detect 步骤真实完成**（ONNX 模型），**OCR 步骤** typed `PROVIDER_NOT_CONFIGURED`；页 4–8 detect 即 `INVALID_INPUT`；未到 translate/render，无可见产物。失败步骤/耗时已入证据，未标成功 |
| AC4 parity/回归 | **MET** | `--check` **PASS**（66 命令零漂移）；registry **24→33 IMPLEMENTED / 42→33 NOT_SUPPORTED**（9 条 NOT_SUPPORTED→IMPLEMENTED）；test.ps1 **145/145 passed**；vitest **60/60 文件、567/567**；pytest **3F/2739P/9S**（与基线相同失败集合，0 新增） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision |

## 1. AC1 清单与接线（9 条，全部 Core 路由 minor=3）

| 命令 | 旧壳参数 | Core 路由 | 备注 |
|---|---|---|---|
| `library_start_run` | `command, scope, overrides?, idempotency_key` | `StartRun` | 无模型 → run 行级 `PROVIDER_NOT_CONFIGURED` |
| `library_control_run` | `run_id, action, idempotency_key?` | `ControlRun` | 终态上控制 → typed `INVALID_RUN_TRANSITION` |
| `library_resume_blocked_run` | `run_id` | `ResumeBlockedRun` | 非 blocked → `INVALID_RUN_TRANSITION` |
| `library_get_run_snapshot` | `run_id` | `GetRunSnapshot` | 未知 id → `TARGET_NOT_FOUND` |
| `library_get_task_projection` | `run_id` | `GetTaskProjection` | 步骤级失败/耗时来源 |
| `library_retry_failed_targets` | `run_id, idempotency_key` | `RetryFailedTargets` | 未构造失败重试场景（安全） |
| `library_start_export` | `book_id, chapter_ids, ordered_page_ids, format, format_options, stale_policy, target_ref` | `StartExport` | 真实调用 → `EXPORT_INPUT_UNAVAILABLE` |
| `library_cancel_export` | `export_id` | `CancelExport` | 未知 id → `EXPORT_NOT_FOUND` |
| `library_get_export_snapshot` | `export_id` | `GetExportSnapshot` | 同上 |

保留 NOT_SUPPORTED：`library_reveal_export_folder`（host-local OS 行为：打开资源管理器，无 Core 命令，不在本批可验证面）。
逐条旧壳 handler/参数/返回/probe 结果见 `command-list.json`；验证脚本 `tools/run_export_probe.py`。

## 2. AC2 尝试记录（BLOCKED，真实错误）

- 1) 数据前置：BOOK-FIXTURE-1 的 8 页只有 **original** 产物（DB 中无 translated 页）→ `handle_start_export`
  在“translated input unavailable”处 fail-closed。
- 2) 产物目标：`StartExport` 的 `target_ref` 必须是 host-control 通道
  `RegisterExportTarget` 注册过的 grant（签名 grant，HOST-ISSUER-1 §5.7 契约）；C# Host 目前只实现
  应用信封（core_service），未实现 host-control envelope 的 grant 铸造，故无法注册合法 target_ref。
- 实测（`probe-base.json`/`probe-models.json`）：`StartExport` → `EXPORT_INPUT_UNAVAILABLE`（两次一致；
  先于 target_ref 解析），`GetExportSnapshot`/`CancelExport` → `EXPORT_NOT_FOUND`。
- 结论：Export 真跑需要先补齐“Run 产出 translated 页”+“Host host-control grant 通道”两块，超出本 Task
  允许范围（不改 Core 语义/不改 Host 契约语义），如实标 BLOCKED，**未生成任何导出产物、未写 SHA**。

## 3. AC3 Run 真跑记录（含模型，BLOCKED 于 OCR）

| 指标 | 无模型 base sidecar | models 包 sidecar |
|---|---|---|
| StartRun 接受 | 是（run_id, 9.2ms） | 是 |
| 终态 | `completed_with_failures`（1.5s） | `completed_with_failures`（冷 6.5s/热 3.1s） |
| 失败步骤 | 全部 8 页 detect 前即 `PROVIDER_NOT_CONFIGURED` | 页1–3：detect **completed**（真实 ONNX 检测），ocr **failed** `PROVIDER_NOT_CONFIGURED`；页4–8：detect 失败 `INVALID_INPUT` |
| translate/render | 未到 | 未到（无可见产物） |
| 证据 | `probe-base.json` + `core-base.stderr.log` | `probe-models.json` + `core-models.stderr.log` |

**未闭环原因（如实登记，待后续诊断）**：models 包 sidecar 自带 `models/detector/rtdetr-v2-fixed.onnx` 与
`models/ocr/manga-ocr-onnx/`（存在性已核对），detect 已用真实模型跑通；OCR 仍报 `PROVIDER_NOT_CONFIGURED`，
页 4–8 detect 报 `INVALID_INPUT`（可能是并发/会话或权重解析路径问题），本次未改 Core 语义去修，按 Lead
指示标 BLOCKED 并写清哪一步。

## 4. AC4 parity/回归

| 指标 | 前（NS-WIRE-A1 后） | 后（本 Task） |
|---|---|---|
| registry IMPLEMENTED | 24 | **33** |
| registry NOT_SUPPORTED | 42 | **33** |
| Rust 命令面快照 | 66 命令，sha `4c6a4da0…` | 未变（`--check` PASS） |

- `scripts/test.ps1 -EvidenceDirectory <私有>`：**145/145 passed, 0 skipped**（CoreClient 40 / Host 42 / App 63）。
- 旧壳 vitest：**60/60 文件、567/567 用例**。
- pytest：**3 failed, 2739 passed, 9 skipped**（与基线相同失败集合，0 新增）。
- 证据：`parity-update.json`、`parity-check.log`、`evidence/`（parity-contract 33/33、integration-results、
  not-supported-typed-errors、domain-services、wiring、chinese-roundtrip）。

## 5. 遗留 / NOT_RUN

1. **AC2 Export 真跑 BLOCKED**（缺 translated 产物 + host-control grant 通道）；后续 slice 需
   HOST-ISSUER 通道迁移或 Core 侧导出入口方案（需 DSH 裁决）。
2. **AC3 模型链 BLOCKED 于 OCR**：OCR `PROVIDER_NOT_CONFIGURED` 与页 4–8 detect `INVALID_INPUT` 待诊断
   （建议单独小 Task，用最小单页复现，不改 Core 语义）。
3. `library_retry_failed_targets` 未构造真实失败重试（run 未进入可重试态）。
4. `library_reveal_export_folder` 保持 NOT_SUPPORTED（host-local，无 Core 命令）。
5. 需独立 Review（Owner 不得自审）。
