---
task_id: P19-UI-MANIFEST-VIEW-1
author: dsh
recipient: Codex
base_commit: cf4529297f4e38fcde0bbc51784ec301ddbdeb35
delivery_head: 4543e23a02dd63124940598ead206ed29e71fc81
status: ready_for_review
---

# Handoff：P19-UI-MANIFEST-VIEW-1

## 交付结果

把 `P19-UI-FIX-1` 的 Resource Manifest 引用改成检查器可解析的形式。

```diff
- 见 [`resource-manifest.json`](../../verification/P19-UI-FIX-1/resource-manifest.json)。worktree、构建产物、...
+ 外部清单：`verification/P19-UI-FIX-1/resource-manifest.json`。worktree、构建产物、...
```

原散文中的处置事实**逐字保留**（保留声明、删除 0 项、6 个日志改名、PyInstaller 缓存登记）。
源 JSON **未被修改**（sha256 `b0772d93ab8ed9182497a43e0761f0d4ccc5560768f806ba86eb8048905c4dc2` 前后一致）。

## AC 对照

| AC | 结果 |
|---|---|
| AC1 引用改为可解析形式 | **通过**：`Resource Manifest 引用必须位于 verification/**` 错误消失 |
| AC2 保存对照与证据 | **通过**：`ac2-governance-output.txt`（完整 stdout + 退出码 + 十项逐条）、`ac1-original-section.md` |
| AC3 使该 Task 检查清洁 | **失败**：错误 4 → 10，详见下 |

## AC3 为什么失败（核心事实）

引用一旦可解析，检查器就开始读那份 JSON，于是暴露出**此前被引用格式挡住的 6 个 destination 债务**：

```
Resource 最终路径未验证：Same ignored target/dist locations in this worktree
Resource 最终路径未验证：Same source location
Resource 最终路径未验证：Same shared build environment
Resource 最终路径未验证：Same local cache location
Resource 最终路径未验证：Same main-repository paths
Resource 最终路径未验证：apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017
```

前五个是**同源位置标记**（`Same ...`），语义是「与 `source_path` 相同」，不是路径；
第六个是**当前确实不存在的真实路径**。检查器把它们都当路径 `Test-Path`，必然失败。

Codex r11 裁定：**保留本次修改、不回退**；AC3 记 FAIL；终态 `closed_with_limitations`；
同源语义**另立 Task**（`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`），不 reopen 已集成的
`GOV-RESOURCE-MANIFEST-JSON-1`。

## 验证证据

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 本 Task 检查 | `check.ps1 -TaskPath doc/tasks/P19-UI-MANIFEST-VIEW-1.md` | 见原始输出 | `ac2-governance-output.txt` |
| P19 改后检查 | `check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md` | **10 errors**（改前 4） | 同上 |
| 源 JSON 未变 | sha256 改前改后 | 一致 | `ac1-original-section.md` |

## 明确未做

- 未回退本次引用修改（按 r11）。
- 未修改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 未修改 `tools/governance/`（同源语义属后继 Task）。
- 未改动任何历史证据文件、pin 或资源；未删除/迁移任何东西。

## 已知限制（`closed_with_limitations` 的依据）

1. `P19-UI-FIX-1` 的错误从 4 增加到 10，本 Task **未使其清洁化**；
2. 6 个 destination 债务中，5 个是同源标记（需检查器支持），1 个是真实不存在路径（需单独核实）；
3. `P19-UI-FIX-1` 原有的 3 项历史债务（2 个日志 SHA 不匹配、8 个未登记证据文件）仍未解决。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 4543e23a02dd63124940598ead206ed29e71fc81`。
请重点确认：AC1/AC2 是否真的达成、AC3 的失败是否被如实记录（而非掩盖）、
以及「净变差但保留修改」这个裁定下本 Task 的交付是否诚实、完整。
