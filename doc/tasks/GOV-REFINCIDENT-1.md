---
id: GOV-REFINCIDENT-1
title: main 引用损坏事故只读调查与证据固化
kind: governance
governance_version: 3
status: done
approval: ZCode session sess_84bc17dc-2b59-4dac-b4ba-46768d80fd97；doc/reviews/GOV-REFINCIDENT-1-zcode-release-2026-11-11.md
suggested_owner: codex
owner: codex
reviewer: ZCode 独立会话 sess_f5cc4af4-be6c-451d-9fad-4a68c4d460f7（未参与实现）
depends_on:
  - GOV-CHECKER-NOTASK-1
base_commit: fa5e58e3fdbd2b53453e55104a7b002d4e57d518
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 6b3cd4e7c502aa9ce7ce2a87c7aa7c51d7ec3750
delivery_head: 9740b6de6ff8b532ab9f43543c92f63c2e9983a1
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 事故入册与证据固化**：原始 incident 文件按 R2 在仓内保全原字节，BLOB SHA 与仓外一致；结构化时间线区分日志声称和复核；事故目录既有文件前后文件集和 SHA 一致，关键副本逐项比较，无法读取项记 NOT_RUN。 <<MET>>
- [x] **AC2 只读取证与环境枚举**：限定范围枚举 Git 版本/config/hook、系统事件、G: USN、相关进程和 dangling 对象；逐项命令、时间、EXIT 或 NOT_RUN；分析 NUL 模式与 loose ref 写入机制且不预设根因。 <<MET>>
- [x] **AC3 假设与恢复建议**：记录假设、支持和反对证据、可复核性及置信度，允许 UNKNOWN；复发监测建议标未实施，记录事故原件与演练恢复前置。 <<MET>>
- [x] **AC4 治理收口**：四项门禁、Task/STATUS/Plan/Ledger、独立 Review、不同独立 ZCode 终裁和资源 closeout 完成，关闭后空窗 default 复验；R-001 保持 open P2。 <<MET>>

## 允许修改范围

仅 frontmatter allowed_paths；仓外新输出仅写 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/`。原始系统事件及进程数据只留仓外，仓内摘要脱敏。

## 禁止范围

不得改既有事故文件、引用、Git 配置/hooks/objects，禁止 gc/prune/repack、清理/归档/迁移资源、push、提权、修改治理工具/模板/历史 pin/契约/源码/Schema/依赖；正常 Task 文档 commit 所需 Git 写入除外。禁止对原字节 incident 副本 renormalize、普通 `git add`、checkout/restore/clean/stash pop 覆盖；仅按 R2 经预演的一次性 `git -c core.autocrlf=false add` 入库。监测工具只建议不实施。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 复算前后文件集、原件/副本 hash，校验 commit BLOB | Windows；保留事故目录 | 44/44 一致；8/8 关键 hash OK；原件与 BLOB SHA 相同；R2 精确 rm+checkout NOT_RUN，替代 checkout-index 和 fresh clone 已测 | `incident-record.md`、仓外 investigation |
| AC2/AC3 | 限定事件/环境只读查询，假设分层 | 权限不足项不得提权 | System 查询 EXIT 0；USN query/read NOT_RUN（非管理员）；根因 UNKNOWN | `incident-record.md`、`hypotheses.md`、`recurrence.md` |
| AC4 | default、TaskPath、pins、API；独立 Review/终裁 | clean 交付 HEAD `9740b6d`；dirty 收口候选 HEAD `6b3cd4e` | 交付四项 EXIT 0；独立 Review ACCEPT、ZCode 终裁采信；候选四项及 clean 终态复跑按裁决留证。 | `delivery-gates-9740b6d.log`、Review、终裁、后续收口 gate 日志 |

## 依赖、风险与阻塞

原件 hash 不一致或活跃持续损坏源证据出现时停止并保留现场；只读查询权限不足记 NOT_RUN。R2 原字节入库若隔离 V1/V2/V3 不满足则采用 ZIP 容器替代条款；fresh checkout 工作区字节不得无条件承诺。事故根因 UNKNOWN；不清理 479 条 dangling 对象。

## 交付与运行记录

- ZCode release session `sess_84bc17dc-2b59-4dac-b4ba-46768d80fd97`；R2 隔离预演见仓外 `investigation/rehearsal-crlf/run.log`。
- Handoff：`doc/handoffs/GOV-REFINCIDENT-1-9740b6d.md`；独立 Review：`doc/reviews/GOV-REFINCIDENT-1-zcode-review-2026-11-11.md`，session `sess_f5cc4af4-be6c-451d-9fad-4a68c4d460f7`，reviewed HEAD `3cc94ea7066e3ee4a7845fec533a20366a6235b6`，ACCEPT；P3-1/P3-2 文档澄清提交 `1fa6677f740a99826f2044c64d8baaec82a32f0d`，待 Integrator 处置。执行结果区分日志声称、已复核和 NOT_RUN。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| release | 任务释放及 R2 字节裁决 | doc/reviews/GOV-REFINCIDENT-1-zcode-release-2026-11-11.md | ee3f0ace6a50bc05d36fc1cf951cb199ceca121e | 55e2ba6ddaae3fe316605a82b4fac2bd94cc1e86a0b2b2ad952d809ff2232b7d | CANONICAL |
| incident-original | AC1 原字节事故记录 | verification/GOV-REFINCIDENT-1/incident.txt | 48c250fa6b8ae7cf2332944dae5be10c3c1d1c83 | 72456c6d002a6799e483221c7c1b9df69723a64faa18c9868e355cae86f53970 | CANONICAL |
| incident-record | AC1/AC2 时间线与来源 | verification/GOV-REFINCIDENT-1/incident-record.md | 1fa6677f740a99826f2044c64d8baaec82a32f0d | 650b618d13948515bbe4dd6559233a2cea918cb693b71bf0723c1956dd8c6139 | CANONICAL |
| nul-analysis | AC2 NUL 模式分析 | verification/GOV-REFINCIDENT-1/nul-pattern-analysis.md | b565218c828df982ad151d5a9370909d5d1937cb | a9e1ec730a0bd9024779a7c972580c28ab5f0aa89ae7ccd05abc99a6cf28a01c | CANONICAL |
| hypotheses | AC3 假设及证据等级 | verification/GOV-REFINCIDENT-1/hypotheses.md | b565218c828df982ad151d5a9370909d5d1937cb | 4ab9b1fd58124258820950c4722ba5642381a8c3f0a4322ee15c4476bad57537 | CANONICAL |
| recurrence | AC3 未实施建议 | verification/GOV-REFINCIDENT-1/recurrence.md | b565218c828df982ad151d5a9370909d5d1937cb | 9daf69910461574c36e294087976c19a14ea4d9657ea2558226e9597d2123c24 | CANONICAL |
| readme | 限制与证据索引 | verification/GOV-REFINCIDENT-1/README.md | e3e7deebc5b061bd21052c7843ffa04de610ac24 | d4d63f0a6b68c17639069b1afe6d0b2aa2c4903d580b4911af90b336f76a0ff1 | SOURCE_PIN |
| resources | 资源清单 | verification/GOV-REFINCIDENT-1/resource-manifest.md | 9740b6de6ff8b532ab9f43543c92f63c2e9983a1 | ce205870ed9baad067eced366007da0ff7955696ddf2b17f7a8e14471e48151f | SOURCE_PIN |
| delivery-gates | AC4 活动状态交付门禁 | verification/GOV-REFINCIDENT-1/delivery-gates-9740b6d.log | df5a104156550e6422e8ea97947038ddddc53c92 | 2c244ac420728c8422b031fe6c24d8824a9cc418c35b71248c31c6b90b234808 | CANONICAL |
| handoff | 交付与限制 | doc/handoffs/GOV-REFINCIDENT-1-9740b6d.md | df5a104156550e6422e8ea97947038ddddc53c92 | 89e7adbbf19f063c9e59b9791a493744b204668a1240a20568a16e41a57a54aa | CANONICAL |
| review | 上下文独立 Review | doc/reviews/GOV-REFINCIDENT-1-zcode-review-2026-11-11.md | 12ddbcb968fedc203d69f1289fd23b8e6beacf5c | 8122cf24bcf61db687f11cca72d83460258a620c937ebd3c9f863f34f6ae313c | CANONICAL |
| final-adjudication | 独立 ZCode 终裁 | doc/reviews/GOV-REFINCIDENT-1-zcode-adjudication-2026-11-11.md | 6b3cd4e7c502aa9ce7ce2a87c7aa7c51d7ec3750 | c8c4a4e918d19b5cc4d81ca6e027b2f87c0f9a7fb13c873f6829fae876340e45 | CANONICAL |
| final-gates | AC4 clean 终态四项门禁 | verification/GOV-REFINCIDENT-1/delivery-gates-final-cfa1866.log | 99d53d4a06c008b7290d810b20e15fa9d19f2451 | e14ad539d3282d063ad0a13ed7327d1bf7a75bb595487f3aa31d32d27173cdbd | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | verification/GOV-REFINCIDENT-1/resource-manifest.md | 既有 main 主树，保留 |
| task-env | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无独立 task-env |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无外部数据集 |
| artifact | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无安装包 |
| temp | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/ | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/ | verification/GOV-REFINCIDENT-1/resource-manifest.md | 事故原件及 investigation 保留 |
| agent-output | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/ | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/investigation/ | verification/GOV-REFINCIDENT-1/resource-manifest.md | 新取证输出和隔离预演保留 |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无 |

## Closeout Record

- Closeout date / adjudicator：2026-11-11 / ZCode 独立 session `sess_937b1456-117c-4a3d-b28b-2da4e53abff6`；`integration_commit` 指向直接 main 交付的终裁采信点 `6b3cd4e7c502aa9ce7ce2a87c7aa7c51d7ec3750`，并非 merge commit。
- canonical_evidence_status / resource_closeout_status：complete / complete；独立 Review ACCEPT，P3-1/P3-2 由提交 `1fa6677f740a99826f2044c64d8baaec82a32f0d` 澄清并经终裁关闭。
- dirty 收口候选 HEAD `6b3cd4e7c502aa9ce7ce2a87c7aa7c51d7ec3750` 的 default、done TaskPath、pins、API 四项实测均 EXIT 0；仓外 `investigation/gates-B-candidate-6b3cd4e.log` SHA-256 `d1d79eab3aa0597d7c278b97de01e8dd96cb7f6e2f68f3ee6b2e62dd1962d404`。候选测试后本条摘要追加，不改 gate 规则。
- clean 终态 HEAD `cfa18664d4a393e564399fa72129f9e284f4da75` 四项 EXIT 0，日志在 `99d53d4a06c008b7290d810b20e15fa9d19f2451` 独立提交；该提交后未回填时 TaskPath 因新日志未登记而 EXIT 1，default 和 pins EXIT 0，仓外 `investigation/gates-C-99d53d4.log` SHA-256 `c212217b7e2aa98bf485d28fb505f782cc986a14f5e72801199aa94779dddb6b`。本回填提交登记日志以消除暂态，随后 clean HEAD 四项复跑结果留仓外。
- 删除、迁移、归档数量/字节数：0；主 worktree、事故原件、仓外调查及隔离副本均保留。
- 未关闭项及当前指针清理：根因 `root_cause_unknown_with_evidence`；USN query/read、精确 rm+checkout、跨环境 checkout 保持 NOT_RUN；原文默认 diff-check CRLF limitation 见 README；R-001 保持 open P2 未释放。STATUS 空窗、Plan done、Ledger 重生成；候选和 clean 终态门禁按裁决记录。
