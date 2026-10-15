---
task_id: ARCH-DOC-REBASELINE
title: 新架构需求、验收及输出格式映射Gate
reviewer: DeepSeek Harness（非作者；Owner=Antigravity、contributor=Codex，Reviewer 独立成立）
owner: Antigravity（AUTO_SELECT 路由；原登记 Codex 转为 contributor）
base_commit: 4ef92f3daa527adac752b8fc52d492176697a292
delivery_head: 702081442d44f74310f7ae9ae7cc412479f0766a
reviewed_head: 702081442d44f74310f7ae9ae7cc412479f0766a
review_worktree: G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE
base_worktree: G:/CODEX/New Manga（用户 dirty 文档留在此处，未被覆盖）
date: 2026-10-15
mode: 只读审查 + 独立 hash 复核；未修改实现与文档；未运行产品代码/构建/GUI/模型
object_binding: VERIFIED
architecture_axis: PASS
verification_axis: PASS（AC1–AC6 证据形态与范围；AC7 消费方裁决待做）
decision: approved_with_conditions
decision_scope: 映射证据、source pin 与范围合规通过；AC1–AC3 维持 Owner 的 PARTIAL（未决项明确）、AC4–AC6 维持 NOT_RUN；集成与逐消费者裁决未完成，不得据此把 Task 标 done
---

# ARCH-DOC-REBASELINE 独立 Review（R1）

## 0. 审查对象与方法

- 对象：`codex/arch-doc-rebaseline` 分支 `4ef92f3d..70208144`（Owner=Antigravity）。
- Reviewer 实际执行 Git 与 SHA-256 复核，`object_binding=VERIFIED`。

### 0.1 本轮实际执行

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 4ef92f3d HEAD` | 15 个文件，**全部落在冻结 allowlist**（5 个文档 + Task + Handoff + 8 个证据文件）；无越界 |
| **source pin 真实性** | 解析 `verification/ARCH-DOC-REBASELINE/source-pins.json` 的 `pinned_files`，对 `G:/CODEX/New Manga` 工作区逐项重算 SHA-256 | **10/10 一致，0 mismatch**（记录的确是主仓**未提交工作区**版本） |
| 主仓未被触碰 | 对 6 个相关文档的 status + 内容 hash | 6 个文档**仍为 `M`（用户 dirty）**；main HEAD 与 dirty 计数未变 |
| 文档改动量 | `git diff --stat 4ef92f3d HEAD -- doc/02,05,07,08,13` | 5 文件、+25/−14 —— 属"分类标记 + 映射说明"级增量，非重写 |
| 证据完整性 | 列 `verification/ARCH-DOC-REBASELINE/**` | AC1–AC6 各一份对照报告 + `rebaseline-summary.md` + `source-pins.json`；Handoff 6939 B |
| 证据形态抽查 | 读 AC1 覆盖表与 summary | 逐份覆盖 + 正式来源 + 消费 Gate，非"文件存在"式空洞证明 |

## 1. AC 逐项结论（与 Owner 自报一致）

| AC | Owner 结论 | Reviewer 判定 | 说明 |
|---|---|---|---|
| AC1 | PARTIAL | **接受（PARTIAL）** | 01–08 逐份覆盖与 AD-001 映射已建立；未决项明确留 P09（组件实现/IPC 测试） |
| AC2 | PARTIAL | **接受（PARTIAL）** | 六维度跨文档一致性对照已产出；未决语义一致性由 P09 消费时确认 |
| AC3 | PARTIAL | **接受（PARTIAL）** | 四一级页面/默认书架/基础 Reader/延期项核对完成；四页设计需 ZCode 独立 Task，不以文档替代 |
| AC4 | NOT_RUN | **接受（NOT_RUN）** | 仅建立证据责任（样本/真值/阈值/version/device/model/endpoint），真实质量证据留 P18 |
| AC5 | NOT_RUN | **接受（NOT_RUN）** | 仅建立旧 stack-specific 条目与新证据 Gate 的对应，实测留 P20 |
| AC6 | NOT_RUN | **接受（NOT_RUN）** | P08-FMT 5 格式追踪表已建立，实际格式验收留 P16/P17 |
| AC7 | 未完成 | **未完成** | 固定 head 非作者 Review 由本文件完成；Codex 集成、逐消费者裁决与 closeout 待做 |

无把历史 PySide6/QML PASS 迁移到新栈的表述；无产品范围扩大或阈值下调。

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P2（集成前置）** | 主仓 `doc/02/05/07/08/13`（及 01/03/04/06/AD-001）当前均为**用户未提交 dirty** 版本；而本分支基于 `4ef92f3d` 的**已提交**版本。两者内容不同，直接集成会造成用户未提交修改与分支更新的合并冲突，且分支产出**未包含**用户 dirty 内容 | 集成前必须由用户/Coordinator 裁定合并策略（例如：把用户 dirty 内容作为基线在新分支重建，或明确以本分支覆盖并备份用户版本）；**禁止**在未裁定前覆盖主仓文档 |
| F2 | P3 | source-pins 记录的是主仓 dirty 版本指纹（已复核真实），但集成后该 pin 指向的字节可能随用户提交而变化 | closeout 时在证据中说明 pin 的时点语义，不回写原始记录 |
| F3 | P3 | AC1–AC3 判 PARTIAL 的"组件实现/IPC 测试"责任已指向 P09，但 P09 自身的释放尚未冻结 | 保持本 Task 不 done；P09 释放时引用本 Task 证据作为 Gate 输入 |
| F4 | P4 | 证据为 8 个独立 Markdown，无索引 | 不阻塞；可在后续任务补齐导航 |

## 3. 条件

- **C1**：按 F1，集成前先裁定"主仓 dirty 文档 vs 分支文档"的合并策略；主仓用户版本必须先有备份或提交，才允许任何覆盖动作。
- **C2**：AC7 的逐消费者裁决（P09/P18/P20/P16/P17）按消费者分别进行；本 Task 保持 `ready`/不 `done`，直到至少 P09 消费 Gate 明确接受 AC1–AC3 证据。
- **C3**：closeout 时登记证据 pin（含本 Review、`70208144`、source-pins 的时点语义）与 Resource Manifest。

## 4. 能力边界

- 本 Review 仅覆盖文档映射证据与范围合规；不代表 P09/P18/P20/P16/P17 的消费者 Gate 结论。
- 所有 hash/Git 结论由 Reviewer 在 live 环境实际执行；未运行产品代码、构建、GUI、模型或真实 Core。
- 主仓用户 dirty 内容、既有 worktree 未触碰；未 push、未删除。Reviewer 未修改被审分支或主仓任何文件。
