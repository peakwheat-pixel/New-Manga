---
id: GOV-REFINCIDENT-1
title: main 引用损坏事故只读调查与证据固化
kind: governance
governance_version: 3
status: ready
approval: ZCode session sess_84bc17dc-2b59-4dac-b4ba-46768d80fd97；doc/reviews/GOV-REFINCIDENT-1-zcode-release-2026-11-11.md
suggested_owner: codex
owner: codex
reviewer: 独立 ZCode 会话（未参与实现，session 待指派）
depends_on:
  - GOV-CHECKER-NOTASK-1
base_commit: fa5e58e3fdbd2b53453e55104a7b002d4e57d518
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-REFINCIDENT-1
allowed_paths:
  - doc/tasks/GOV-REFINCIDENT-1.md
  - doc/reviews/GOV-REFINCIDENT-1-*.md
  - doc/handoffs/GOV-REFINCIDENT-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/GOV-REFINCIDENT-1/**
---

# GOV-REFINCIDENT-1：main 引用损坏事故只读调查与证据固化

## 来源与目标

依据 [ZCode 释放与 R2 裁决](../reviews/GOV-REFINCIDENT-1-zcode-release-2026-11-11.md)，调查已恢复的 main loose ref 41 字节 NUL 事故，固化证据并区分事实与假设。`GOV-CHECKER-NOTASK-1` 为时序和仓外证据目录依赖，非因果依赖。根因允许 `root_cause_unknown_with_evidence`，不得凭时间关联断言因果。

## Acceptance Criteria

- [ ] **AC1 事故入册与证据固化**：原始 incident 文件按 R2 在仓内保全原字节，BLOB SHA 与仓外一致；结构化时间线区分日志声称和复核；事故目录既有文件前后文件集和 SHA 一致，关键副本逐项比较，无法读取项记 NOT_RUN。 <<PARTIAL: 仓外初步快照已取，仓内证据待登记>>
- [ ] **AC2 只读取证与环境枚举**：限定范围枚举 Git 版本/config/hook、系统事件、G: USN、相关进程和 dangling 对象；逐项命令、时间、EXIT 或 NOT_RUN；分析 NUL 模式与 loose ref 写入机制且不预设根因。 <<PARTIAL: 部分只读取证已执行，摘要和逐项核验待完成>>
- [ ] **AC3 假设与恢复建议**：记录假设、支持和反对证据、可复核性及置信度，允许 UNKNOWN；复发监测建议标未实施，记录事故原件与演练恢复前置。 <<PARTIAL: 尚未形成最终分析>>
- [ ] **AC4 治理收口**：四项门禁、Task/STATUS/Plan/Ledger、独立 Review、不同独立 ZCode 终裁和资源 closeout 完成，关闭后空窗 default 复验；R-001 保持 open P2。 <<PARTIAL: 尚未执行收口>>

## 允许修改范围

仅 frontmatter allowed_paths；仓外新输出仅写 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/`。原始系统事件及进程数据只留仓外，仓内摘要脱敏。

## 禁止范围

不得改既有事故文件、引用、Git 配置/hooks/objects，禁止 gc/prune/repack、清理/归档/迁移资源、push、提权、修改治理工具/模板/历史 pin/契约/源码/Schema/依赖；正常 Task 文档 commit 所需 Git 写入除外。禁止对原字节 incident 副本 renormalize、普通 `git add`、checkout/restore/clean/stash pop 覆盖；仅按 R2 经预演的一次性 `git -c core.autocrlf=false add` 入库。监测工具只建议不实施。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 复算前后文件集、原件/副本 hash，校验 commit BLOB | Windows；保留事故目录 | 部分已执行；仓内 BLOB 校验 NOT_RUN | 仓外 investigation |
| AC2/AC3 | 限定事件/环境只读查询，假设分层 | 权限不足项不得提权 | 部分已执行；USN NOT_RUN（非管理员） | 仓外 investigation；仓内摘要待生成 |
| AC4 | default、TaskPath、pins、API；独立 Review/终裁 | 交付及收口 HEAD | NOT_RUN | 待生成 |

## 依赖、风险与阻塞

原件 hash 不一致或活跃持续损坏源证据出现时停止并保留现场；只读查询权限不足记 NOT_RUN。R2 原字节入库若隔离 V1/V2/V3 不满足则采用 ZIP 容器替代条款；fresh checkout 工作区字节不得无条件承诺。事故根因 UNKNOWN；不清理 479 条 dangling 对象。

## 交付与运行记录

- ZCode release session `sess_84bc17dc-2b59-4dac-b4ba-46768d80fd97`；R2 隔离预演见仓外 `investigation/rehearsal-crlf/run.log`。
- Handoff / Review：尚无。执行结果须区分日志声称、已复核和 NOT_RUN。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | 待关闭 | 既有 main 主树，待核验 |
| task-env | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无独立 task-env |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无外部数据集 |
| artifact | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无安装包 |
| temp | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/ | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/ | 待关闭 | 事故原件及 investigation 保留 |
| agent-output | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/ | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/ | 待关闭 | 新取证输出和隔离预演保留 |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无 |

## Closeout Record

- Closeout date / adjudicator：待关闭。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：待关闭；当前无操作。
- 未关闭项及当前指针清理：待关闭。
