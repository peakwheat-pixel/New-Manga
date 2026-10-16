# P14 独立 Review R1 摘要

- Reviewer：dsh
- Session：`session-cb4e75d6-54a7-4fb2-a901-f7c767fde23f`
- 固定实现提交：`8f3fddcc15e4db55e22e7bde425af168c18bec44`
- Review 结论：`changes_requested`
- Reviewer 未重跑测试；未报告 P0 / P1 边界缺陷。

## Findings 与 Owner 处理

| ID | 级别 | Finding | Owner 处理 |
|---|---|---|---|
| R-001 | P2 | 工作台错误只显示错误码；缺少本地化错误说明、重试操作与 Core 不可用错误卡。 | 复用既有 `parseSemanticError`，工作台错误现在本地化并提供重试；Core 不可用时显示全工作区错误卡。 |
| R-002 | P2 | 暂停/停止缺少中间状态。 | 添加立即可见的“正在暂停/正在停止”；权威快照变更后才显示最终状态，控制等待期间禁用重复操作。 |
| R-003 | P2 | `ExportDialog` 缺少行为测试。 | 新增 DOM 测试覆盖格式与选项、PNG 单页规则、提交取消、忙碌态、取消、进度、历史、打开目录、Escape 与错误重试。 |
| R-004 | P3 | 空 `ListRegions` 状态和 Viewer 分块进度缺失。 | 空 Region 显示“本页暂无 Region”；资源通道回报已取/总块数，Viewer 展示进度。 |
| R-005 | P3 | Toolbar 位置、Task 详情浮层和定位当前页滚动不符设计 §3。 | Toolbar 移到三栏主区下方；Task 详情内容浮动显示；定位页后 PageList 将对应页滚入可见区。 |
| R-006 | P3 | Region Tab 未按顺序循环；G9 未说明 Ctrl+Enter 不可用。 | Tab / Shift+Tab 按 Core 返回的 reading order 循环焦点；G9 原因明确包含 Ctrl+Enter 保持禁用。 |
| R-007 | P3 | 返回 ID 校验未拒绝 `C:` 盘符前缀。 | 响应 ID 复用 `isSafeUiId`；添加 `C:private` 污染响应拒绝测试。 |
| R-008 | P3 | `App.tsx` production startup deny matrix 在 Viewer 外签发并读取 `m2res`，边界证据描述不准确。 | 移除生产启动矩阵中的资源发行/读取与 opaque ID 片段日志；App 测试断言生产启动不调用 `issue_resource_url`；probe / AC1 验收模式明确标为测试路径。 |
| R-009 | P3 | restart/retry 通过本地 fallback 构造虚假 Run snapshot。 | 新 Run 只记录权威返回的 `run_id`，清空旧 snapshot/projection 后重新读取 Core。 |
| R-010 | P3 | Task 与 Handoff 状态不一致。 | `e99be4d` 实现提交仍未修正 Task 状态；随后 AC6 文档收尾将 Task、Handoff 与 checkpoint 统一为 `in_review`，并保留 `canonical_evidence_status: complete`。 |

二次 Review 应对新固定实现提交重新审查；本摘要不构成接收或集成批准。
