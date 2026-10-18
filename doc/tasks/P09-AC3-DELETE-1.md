---
id: P09-AC3-DELETE-1
title: 项目级永久删除（Core 硬删除）与 P09 AC3 源文件零改动回补
kind: feature
governance_version: 2
status: ready
approval: user_ruling_20261018_create_p09_ac3_delete
blocked_by: null
suggested_owner: Antigravity（ZCode CLI 不可用，按项目故障转移顺序）
owner: Antigravity
reviewer: Codex（非作者；同时负责先冻结本 Task 需要的新契约）
depends_on: [P09]
base_commit: baf4ec90c
branch: null
worktree: G:/CODEX/New Manga（真实工作流验证须在隔离环境执行；执行方写 verification/P09-AC3-DELETE-1/**、本 Task、doc/handoffs/P09-AC3-DELETE-1-*.md）
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P09-AC3-DELETE-1
---

# P09-AC3-DELETE-1：项目级永久删除与 P09 AC3 回补

## 来源与依据

- 用户裁决（2026-10-18）：就 `P09` 的 AC3 残留缺口**立即另立本 Task 补齐**（不等待未来功能）。
- 缺口事实（`P09` 的 AC3 = `AC-IMPORT-002` [P0]「源文件零修改」）：
  - ✅ 已实测通过：两个隔离源样本在**导入、软删除、Page 级永久清理、真实 `TRANSLATE_ALL` / `REINPAINT_REGION` / `RERENDER_SINGLE`** 后 hash 完全相同（证据 `verification/P09/evidence/AC3-source-hashes.json`、`37-ac3-workflow-source-hashes-final.txt`）。
  - ❌ **BLOCKED**：**"项目级永久删除"路径无法验证** —— `LibraryService.delete_book` 仅**软删除**，`TrashService.purge_batch` 仅 **Page 级**；Core **不存在**项目级永久删除，且 P09 的授权路径不允许为验证它而新增功能。
- 因此本 Task = **先实现该功能（含源文件保护），再回补 P09 的 AC3 验证**。

## Acceptance Criteria

- [ ] AC1：**契约先行（阻断性）**——若实现需要**新增或修改** IPC 命令、请求/响应 Schema 或错误码，**必须**先由 Codex 在本 Task 中明确冻结契约（命令名、入参、返回、错误语义、ACL 白名单），并在 `doc/**` 留下冻结记录；**契约未冻结前不得实现**。若可复用既有命令完成，须写明复用的是哪条命令与为何足够。
- [ ] AC2：**项目级永久删除可用**——提供"永久删除项目"操作：硬删除该项目的 DB 行（book/chapter/page 及其关联），并回收其 **Managed Copy** 与派生资源；软删除（`delete_book`）与 Page 级 purge 的既有语义**不得改变**。
- [ ] AC3：★ **源文件零改动（P0）**——永久删除项目后，**项目源目录内的源文件 hash 完全不变**（与删除前逐文件比对）；用 P09 同款隔离样本与真实工作流验证，产出可比对报告。
- [ ] AC4：**无残留**——删除后：DB 无该项目残留行；Managed Storage 与派生/缓存目录**无孤儿文件**（给出清理前后文件数与字节数）；`core` 日志与 GC 路径无错误。
- [ ] AC5：**误删防护与语义区分**——永久删除与软删除在 UI/契约层语义清晰（永久删除须显式确认、不可从回收站恢复）；不提供隐式触发路径。
- [ ] AC6：**回补 P09 AC3**——把该路径证据并入 `verification/P09/evidence/**` 与 `P09.md` 的 Canonical Evidence；把 `P09.md` 的 AC3 从 `BLOCKED` 更新为**实际达成状态**（若仍有未覆盖路径则如实保留局部限制，并说明剩什么）。
- [ ] AC7：**不回归 P09 已通过项**——导入 / 翻译 / 重修 / 重渲染 / 软删除 / Page 级永久清理的源 hash 零变化结论**不得退化**：复用 P09 的既有验收命令重跑并给出对照。

## 允许修改范围

- Core（`src/**`）中与项目级删除、purge、资源回收相关的实现与测试。
- Tauri 侧与前端**仅在契约冻结后**、且仅限"永久删除"入口与确认交互所需的最小改动。
- `verification/P09-AC3-DELETE-1/**`、本 Task、`doc/handoffs/P09-AC3-DELETE-1-*.md`、以及**契约冻结所必需的** `doc/**` 记录（由 Codex 落笔）。
- `P09.md` 的 AC3 状态与 Canonical Evidence 更新（回补时）。

## 禁止范围

- **契约未冻结前不得**新增/修改 IPC 命令、Schema、错误码、ACL 白名单。
- 不得改依赖版本；不得降低任何既有阈值；不得放宽 `AC-IMPORT-002`（源文件零修改）的判定。
- 不得改变既有软删除 / Page 级 purge 的语义或删除它们的能力。
- 不得用"删掉测试/跳过断言/只改判定口径"来让 AC 通过；源 hash 必须以**磁盘字节**重算。
- 不 push；不动用户 43 项未提交改动（含 `verification/P19/codex-review-r2.md`）；GUI/工作流验证用 `%TEMP%` 隔离根（禁止放 `apps/desktop/src-tauri/target/**`），并保护用户真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 数据。

## 测试要求

planned：永久删除的真实工作流验收（隔离源样本 + 真实 Core assembly）；删除前后**逐文件 hash 对照**；DB 行与孤儿文件核查（清理前后计数）；软删除/purge 语义不回归；P09 既有 AC 重跑对照。全部结论须附原始产物（脚本、日志、时间戳、退出码）。

## 依赖、风险与阻塞

- 依赖：`P09`（提供 AC3 事实、隔离样本与验收脚本）。
- 风险一：**契约变更**是本 Task 最大风险 —— 必须先冻结，否则会污染 58 条命令的请求面与 ACL 白名单。
- 风险二：永久删除属**不可逆破坏性操作**，验证必须全程在隔离根内，且不得对用户真实数据执行。
- 已知阻塞：无（本 Task 即为解除 P09 的 BLOCKED）。

## 交付与运行记录

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决创建本 Task；`status: ready`。
- 第一步建议：由 Codex 先做**契约冻结裁决**（AC1），再释放 owner 实现。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在关闭时同步。
