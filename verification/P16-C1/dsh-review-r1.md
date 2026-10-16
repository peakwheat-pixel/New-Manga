---
task_id: P16-C1
title: Reader/Export IPC 契约修订
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P16-C1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: ff9633b5b09d8a898f92722a728edd3ff14da2d5
declared_delivery_head: 196f50d45bc55eedfae87603b8887fd98ddcbf62
reviewed_head: 356a9fe07f67dd8b0c376d3b6c02c151b4c06f15
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P16-C1-READER-EXPORT-IPC
date: 2026-10-16
mode: 只读审查 + 独立 Git/契约 diff 复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: 冻结契约增量修订（rev 2.0 → 2.1；major 不变）
decision: approved
---

# P16-C1 独立 Review（R1）—— IPC 契约 rev 2.1

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only ff9633b5..HEAD` | **7 个路径，全部在授权范围** |
| **P11 契约完好** | 过滤 `P11_LONG_TASK` | **未被修改** ✅ |
| **P13 已冻结 Run wire 完好** | 读契约确认 rev 2.0 条目与 `StartRun`/`ControlRun`/`GetTaskProjection` 等仍在，且 rev 2.1 头部明示"P13 Run wire 本文零语义变化" | ✅ |
| **产品实现零改动** | 过滤 `^(src\|apps\|packaging)/` | **空** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 本 Task 的阻塞处置 | 读 `decision-blocker.md` 与 Task 中的裁决段 | 见 §2 |

## 1. 契约修订的逐项审查

| 关注点 | 审查结论 |
|---|---|
| **导出写授权（Coordinator 裁决的落实）** | §10.3 定义 `ExportTargetRef`：**不透明、受限的写授权引用，不是路径字符串且不得编码/暴露路径**；**唯一 issuer = 受信 Tauri host**；Host 在用户选择目标后签发并**只**注入可信 host→Core 的 `StartExport`；**React/WebView 不接收** ✅ 与裁决逐条吻合 |
| **引用生命周期** | scope = **一个精确最终输出文件 + 一次 `StartExport` 调用**（含该文件所需的临时 sibling staging 与发布）；签名绑定 host session、单一 grant ID、scope、允许的 `format`、替换授权与**绝对过期时间**；引用仅含不透明 grant ID + host 签名 |
| **Core 侧强制校验** | 任何目标写入**前**必须验证签名/issuer、scope、format、替换授权、未过期、未撤销、未消费，并**原子消费** grant；拒绝面完整：`REF_MALFORMED` / `REF_SIGNATURE_INVALID` / `REF_EXPIRED` / `REF_UNKNOWN_ID` / `REF_REVOKED` / `REF_ALREADY_CONSUMED` ✅ |
| **与既有模式对齐** | 契约明示该模式与 §5/§10 的 `ImportSourceRef` 同源，并说明差异（import 只读可续期；export 单次写授权）——正是裁决要求的"不得发明第二套" |
| **Reader 面（AC1）** | 新增冻结 `GetReaderProjection` / `SaveReadingProgress`；覆盖 Original/Translated 独立进度、RTL/LTR、Webtoon Vertical、一长图一 Page、坐标回映、关闭重开 |
| **Export 面（AC2/AC3）** | `StartExport` 载荷含 `book_id/chapter_ids/ordered_page_ids/format/format_options/stale_policy/target_ref`；五格式（PNG〔按 D1/D2 映射单图〕/ZIP/CBZ/PDF/文本）+ 页序、hash、lineage；`CancelExport`、临时发布清理、**源零写**、`stale_policy` 与 `GetExportHistory` |
| **进度与事件（AC4）** | 新增 `ReadingProgressChanged` / `ExportProgressChanged`，封装为 §3 `Event<T>`、与请求响应共用 JSONL；**仅在进度快照持久化后发出**、只提示重查、**不携带文件路径或 `ExportTargetRef`**、不保证送达/重放/排序 ✅ 与 P13 的事件纪律一致 |
| **版本策略** | rev **2.1**，envelope 为 **major 2 / minor 1**；因**只新增命令与事件、不改既有冻结 wire**，**major 不变**（符合 §3.2 的 minor widening 规则）；并如实声明"不代表签名实现或 Python Runtime 已落地" |
| **授权边界（AC5）** | §12 另行明确授权**未来已释放的 P16** Python IPC Runtime，且**限定在冻结 allowlist**（`src/application/reading/*` 等），排除 React/Tauri/Rust/QML、Legacy、Schema/migration、依赖与其他产品行为 |

## 2. 阻塞与解阻的复核

- Owner 首轮 `BLOCKED_WAITING_EXTERNAL_DECISION` 的依据**成立**：D04 §37 要求选择导出目标、`AC-EXPORT-002` 要求记录输出路径，
  而 §10 规定"前端路径不是写权限"，既有 resource reference 只覆盖 Core 控制的**读**。
- Coordinator 裁决（可信 host 中介）**属架构实现边界**而非产品取舍：产品行为（选择目标、记录路径、完成后打开文件夹）已在 D04 §37 / `AC-EXPORT-002` 冻结；
  且 AD-001 已确立"React 不接触任意 OS 路径"、§5/§10 已有 `ImportSourceRef` 先例（M2-C2 ruled）。
- **复核结论：修订结果与裁决完全一致，未出现"发明第二套授权"或"空转"**。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 6 次）** | `delivery_head` 申报 `196f50d4`（契约冻结提交），实际 HEAD=`356a9fe0`（证据回填提交） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | P3（验证边界） | 签名实现、Python Runtime、格式兼容与 Windows smoke 均 `NOT_RUN`（Owner 已在契约与回答中如实声明） | 属 P16/P17 的实现验收范围；**不得据此宣称产品级导出已可用** |
| F3 | P4 | `ExportTargetRef` 的签名算法/密钥托管未在本契约选定（仅冻结验证义务与拒绝码） | 合理：属实现层选择，P16 实现时需在证据中单列；建议 P16 在迁移/安全边界中说明 |
| F4 | P4 | `§11` 状态表中 `ExportProgressChanged` 由 UNKNOWN 提升为冻结 | 与 AC4 要求一致；记录即可 |

**无 P0/P1/P2 finding。**

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `356a9fe07f67dd8b0c376d3b6c02c151b4c06f15`。
- **C2**：P16 释放时须引用本契约 §10.3，并在实现证据中单列**签名算法/密钥托管**与**grant 消费原子性**的实测（F3）。
- **C3**：本节结论仅覆盖契约与 wire 覆盖；**不代表**任何 runtime 已实现，`P16`/`P17` 的实现与验收仍需各自 Gate。
- 契约内容本身无需返修。

## 5. 能力边界

- 本 Review 覆盖契约文本、范围合规、裁决落实情况与版本策略；未重跑任何 runtime 测试（本 Task 无代码）。
- 所有 Git / 契约结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
