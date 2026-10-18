# F-001 关闭记录（框架，待 Codex 定稿后填实）

**状态**：框架已就绪，等 `codex-rev211-result.md` 落盘后填入契约定稿信息并提交。

裁决依据：**用户 2026-10-19 选择方向 A** —— 认定 `P09-AC3-DELETE-HARDEN-1` 的 AC1 原文「注册到 Tauri production command 与 `generate_handler!`」**构成对该命令的授权**，据此补契约冻结并关闭 F-001。

---

## 1. F-001 的性质（回顾）

Codex R1 复审指出（`verification/P09-AC3-DELETE-HARDEN-1/codex-review-r1.md`）：实现 AC1 引入了 IPC 命令 `library_list_recycle_bin_books`，而该命令**未在 M2-C1 契约中冻结**，与本 Task 禁止范围「不新增未冻结的 IPC 命令」冲突。

**本会话进一步的侦察结论**（`f001-disposition-options.md`）：冲突的根源是**同一份 Task 的两条要求互斥** ——
- AC1 明文要求注册该命令；
- 禁止范围明文禁止新增未冻结命令；
- 且契约 rev 2.10 中经全文检索**确无任何 recycle bin 条目**，即该命令在写 AC1 时并不存在。

**因此这不是实现越界，而是 Task 定义层面的冲突**，需要的是范围裁决而非代码返修。

## 2. 处置（方向 A）

| 步骤 | 内容 | 状态 |
|---|---|---|
| 1 | Codex 定稿契约 **rev 2.11**，冻结 `library_list_recycle_bin_books`（Tauri production）与 `ListRecycleBinBooks`（Core） | ⏳ 进行中（job `pwsh-7388e9b6ac60425f`）|
| 2 | 本 Task 记录 **implementation scope release 与 allowlist** | ⏳ 待填（见 §3）|
| 3 | 关闭 F-001 | ⏳ |
| 4 | 固定新 head，送 Codex 第二轮复审（R2） | ⏳ |

## 3. Implementation Scope Release / Allowlist（待填）

> 本节将记录：契约 rev 2.11 的定稿提交、冻结的命令名称与形状、以及「AC1 措辞即授权」这一裁决在 Task 层面的落地表述。**待 Codex 结果落盘后填入**。

**占位字段**：

| 字段 | 值 |
|---|---|
| 契约 rev | 2.11（待定稿）|
| 契约定稿提交 | 待填 |
| Tauri command | `library_list_recycle_bin_books` |
| Core command | `ListRecycleBinBooks` |
| 命令形状 | `{}` → `BookSummary[]`（仅软删除集合）|
| 协议 minor | `10` → `11`（以 Codex 定稿为准）|
| 授权依据 | AC1 原文「注册到 Tauri production command 与 `generate_handler!`」+ 用户 2026-10-19 方向 A 裁决 |

## 4. 为什么方向 A 而非 B

**方向 B（回退命令）会使 AC1 不完成** —— AC1 是本 Task 的第一条明文验收标准，而冲突的成因不在实现方（两条互斥要求由同一份 Task 同时给出）。此外 Codex R1 已**独立确认**该命令的路由事实成立、数据源正确（从软删除集合读取，非可见列表）。

**方向 A 不改动任何已工作的代码**，只补齐契约使其与实现一致。

## 5. 边界

**本文件目前是框架，不是完成记录**：未声称 F-001 已关闭，未声称契约已修订。契约文件此刻仍为 **rev 2.10**。待 Codex 定稿落盘后，本文件将被补实并作为 F-001 关闭的 Canonical Evidence。
