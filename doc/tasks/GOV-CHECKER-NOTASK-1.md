---
id: GOV-CHECKER-NOTASK-1
title: 治理检查器显式无当前任务状态
kind: governance
governance_version: 3
status: done
approval: ZCode session sess_ed894fec-18b7-40b8-9e6d-f927d8f2f031；doc/reviews/GOV-CHECKER-NOTASK-1-zcode-release-2026-11-11.md
suggested_owner: codex
owner: codex
reviewer: ZCode 独立会话 sess_4edfc1ab-c2eb-4669-836f-aeb99a0a7bd8（未参与实现）
depends_on:
  - FEA-15-PIN-POLICY-1
base_commit: 0201dc9612faa9eea9104b8e0568414e4a7bad5a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 62ab6b735961359b8a29984484033747b221fee4
delivery_head: 21ce0f24f2c4b0a153f85163eadc64b36b7bf72b
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-CHECKER-NOTASK-1
allowed_paths:
  - tools/governance/check.ps1
  - doc/tasks/GOV-CHECKER-NOTASK-1.md
  - doc/reviews/GOV-CHECKER-NOTASK-1-*.md
  - doc/handoffs/GOV-CHECKER-NOTASK-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/GOV-CHECKER-NOTASK-1/**
---

# GOV-CHECKER-NOTASK-1：治理检查器显式无当前任务状态

## 来源与目标

依据 [ZCode 释放裁决](../reviews/GOV-CHECKER-NOTASK-1-zcode-release-2026-11-11.md) 和 FEA-15-PIN-POLICY-1 Addendum，修复 default checker 不识别明确空窗的缺口。§4.4 基线经 [ZCode 独立裁决 v2](../reviews/GOV-CHECKER-NOTASK-1-zcode-baseline-adjudication-2026-11-11.md) 认定充分；实施必须符合其中白名单、路径排除、指针优先与 T1–T8。

## Acceptance Criteria

- [x] **AC1 空窗正例**：现行明确空窗声明下 default 检查 EXIT 0，记录历史两条错误消失。 <<MET>>
- [x] **AC2 反例与判别力**：终态指针、不存在路径、缺失当前 Task 行保持失败；合法非终态指针行为与基线一致；显式 TaskPath 对 done 且 integration_commit pending 保持失败；隔离变异使缺失行和路径形态反例分别错误变绿，再逐字节恢复并验证复红、空窗正例仍绿，记录 hash 和 EXIT。 <<MET>>
- [x] **AC3 门禁与收口**：空窗 default、本卡 TaskPath、18 pins、API inventory 均 EXIT 0；独立 Review、独立 ZCode 最终裁决、BLOB pin、STATUS/Plan/Ledger/Closeout 全部完成。 <<MET>>

## 允许修改范围

仅 frontmatter 的 allowed_paths；场景构造位于 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/`，不污染主树。

## 禁止范围

禁止改变其他 checker 判定语义、`-TaskPath`、终态指针拒绝、integration_commit、ledger、READY、预算或 r194 双基准语义；禁止改其他治理工具、模板、`.gitattributes`、历史 pin、冻结契约、产品源码、Schema 或依赖；禁止资源清理和 push。缺失或歧义声明不能作为空窗放行。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 隔离场景矩阵、变异与 SHA-256；`pwsh -NoProfile -File tools/governance/check.ps1` | Windows；基线 `eb06df0`、实现 `21ce0f2` | 基线、边界与实现后矩阵 EXIT 0；31/31 断言及两种变异恢复通过；终态和 pending 样本有额外错误，见 README。 | 基线及 `implementation-run-21ce0f2-r3.log` |
| AC3 | default 与 `-TaskPath`、`verify_pins.ps1`、`python tools/generate_api_inventory.py --check` | clean 活动指针 HEAD `b76c4ab`；dirty 空窗候选 HEAD `05d1f5c` | 两次四项均 EXIT 0；独立 Review ACCEPT，ZCode 终裁有条件批准；提交后 clean HEAD 复跑另行实测。 | `delivery-gates-b76c4ab.log`、`closeout-gates-05d1f5c-G1.log`、Review/终裁 |

## 依赖、风险与阻塞

依赖 FEA-15-PIN-POLICY-1 done。基线和边界样本不足时暂停实现；若反例矩阵不能保持既有 fail-closed 语义，则停止并保留 `-TaskPath` workaround。R-001 不在本卡范围。

## 交付与运行记录

- Handoff：`doc/handoffs/GOV-CHECKER-NOTASK-1-21ce0f2.md`；Review：`doc/reviews/GOV-CHECKER-NOTASK-1-zcode-review-2026-11-11.md`，独立 session `sess_4edfc1ab-c2eb-4669-836f-aeb99a0a7bd8`，reviewed HEAD `4231469b972d0c2be086c6b077b6150c90a5d3d6`，ACCEPT，F-1/F-2 待 Integrator 裁决、F-3/F-4 已登记；实际测试见表。
- 释放裁决 session：`sess_ed894fec-18b7-40b8-9e6d-f927d8f2f031`；独立 Review 和最终裁决使用不同于实现及彼此的上下文。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| release | 任务释放与范围 | doc/reviews/GOV-CHECKER-NOTASK-1-zcode-release-2026-11-11.md | 259fb7c1a1d76f41802c29688e3b28c18db82378 | 6066a7afd5331284cf42349dfedc5bb8ccc5219fbd21dad58f30a2dd6b770c77 | CANONICAL |
| baseline-log | AC2 实施前样本 | verification/GOV-CHECKER-NOTASK-1/baseline-run-eb06df0-blob.log | 9610df47438da0c2f5f9d98f72cbdd1e6ffedb1c | 4c6159802ce7691446592a03537ec1d3c92c5d28a8c899095b61006d3b0af23f | SOURCE_PIN |
| baseline-script | AC2 场景生成器 | verification/GOV-CHECKER-NOTASK-1/baseline_matrix.py | 9610df47438da0c2f5f9d98f72cbdd1e6ffedb1c | 5b70d070a1e01e2feea6bd8597eb238cc031db7a721816aa8f3318954c7d17db | SOURCE_PIN |
| evidence-readme | 基线范围与限制 | verification/GOV-CHECKER-NOTASK-1/README.md | 9610df47438da0c2f5f9d98f72cbdd1e6ffedb1c | e6535136b34f0ff253119f347a0aece1024f46db85d37ae56c82c1b786fdd690 | SOURCE_PIN |
| boundary-log | AC2 边界基线 | verification/GOV-CHECKER-NOTASK-1/boundary-run-eb06df0.log | ca7f6f31b740cd09d6853e63683983c4826daf60 | b81b9ab3fb1ac5dd677d8be8e7cbbd7533ce02fcbb87682a31419e0a6ccae563 | SOURCE_PIN |
| boundary-script | AC2 边界生成器 | verification/GOV-CHECKER-NOTASK-1/boundary_matrix.py | ca7f6f31b740cd09d6853e63683983c4826daf60 | d9641c51d27d3b7cdb41f291baefac9344c6b5242d08f7db5aced87976feca2f | SOURCE_PIN |
| boundary-notes | AC2 边界结果 | verification/GOV-CHECKER-NOTASK-1/boundary-notes.md | ca7f6f31b740cd09d6853e63683983c4826daf60 | 8fda726c64ce111a1c2bcdc1b800605ad19f5973e49c8185ef9c28307d52f6e9 | SOURCE_PIN |
| baseline-adjudication | §4.4 与 v2 语法裁决 | doc/reviews/GOV-CHECKER-NOTASK-1-zcode-baseline-adjudication-2026-11-11.md | 79e96c36e66e34c6f8a2f34a3271eea370555e15 | 637f893949036cd35687953a6ea571f099e693ecec887fbbb720ee6e978bd6e7 | CANONICAL |
| implementation-matrix | AC1/AC2 31 场景与变异 | verification/GOV-CHECKER-NOTASK-1/implementation-run-21ce0f2-r3.log | b76c4ab0621b3ec27433727d86078f0958b9d264 | e30febf50364996199a813eececbb2df6243dfe1973ed0dea265ab778accfe36 | CANONICAL |
| implementation-script | AC1/AC2 生成器 | verification/GOV-CHECKER-NOTASK-1/implementation_matrix.py | b76c4ab0621b3ec27433727d86078f0958b9d264 | b0918d4110b4eef721b5f395c5bdb20ba44c780fc925c62df2844ecf8d1e3b85 | SOURCE_PIN |
| implementation-notes | AC1/AC2 适用范围 | verification/GOV-CHECKER-NOTASK-1/implementation-notes.md | b76c4ab0621b3ec27433727d86078f0958b9d264 | 66760aa70e04a1e7cce3ba132450ddea90e5b23920403e03db6bd927d77980e0 | SOURCE_PIN |
| delivery-gates | AC3 交付门禁 | verification/GOV-CHECKER-NOTASK-1/delivery-gates-b76c4ab.log | 869f76b350de8db8e392905379e9dde40c9e1162 | 2895080486d4fe26852d25ab7e8212a28695d90ffcd7370e6b6af42e9dbe66e6 | CANONICAL |
| handoff | 交付与风险 | doc/handoffs/GOV-CHECKER-NOTASK-1-21ce0f2.md | 869f76b350de8db8e392905379e9dde40c9e1162 | 1bdb6647953d9ae62c38db0d9020d187be2809a190a00301072a6c952f15e678 | CANONICAL |
| review | 独立 Review | doc/reviews/GOV-CHECKER-NOTASK-1-zcode-review-2026-11-11.md | 2afe986b6fd61a89a194176b1f5321d0aed6846c | cceacf71ca76382336f1e3366be29ac4fa7accda3e41a43e22db13fd16eeb25d | CANONICAL |
| supplementary-audit | diff 与 evidence 审计 | verification/GOV-CHECKER-NOTASK-1/delivery-audit-2afe986.log | 0bea9c190a1162170f0f16122698fab699230488 | 326627b52edc8466df60abd9c115369da05dfc8dda78f938f74e8fbf5c4c28a3 | SOURCE_PIN |
| resource-manifest | 资源清单与保留建议 | verification/GOV-CHECKER-NOTASK-1/resource-manifest.md | 0bea9c190a1162170f0f16122698fab699230488 | 512725a0398eb01ecfdf32a08d213129fa24cba9cd6cdeda7eb534fcc0041641 | SOURCE_PIN |
| final-adjudication | 独立 ZCode 最终裁决 | doc/reviews/GOV-CHECKER-NOTASK-1-zcode-final-adjudication-2026-11-11.md | 05d1f5cd29cfc860d3ee12166db87136e409eaff | bd9a500f7155511855a83571c5c1ef74820a34f817b61f7edaf8d4039ce9c255 | CANONICAL |
| closeout-gates | AC3 主树 dirty 候选四项门禁 | verification/GOV-CHECKER-NOTASK-1/closeout-gates-05d1f5c-G1.log | 685d3a9e22e7adfb1d032f7b202e5390146e4b05 | fbecc78cdbec32ed8378f84ea7bdbb0e344b99e0f4f9f93651e02385dc92ac06 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | verification/GOV-CHECKER-NOTASK-1/resource-manifest.md | 既有 main 主树；清单记核验时 HEAD，保留 |
| task-env | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无独立环境 |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无外部数据 |
| artifact | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无安装包 |
| temp | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/ | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/ | verification/GOV-CHECKER-NOTASK-1/resource-manifest.md | 三个隔离副本保留；未清理 |
| agent-output | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/ | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/ | verification/GOV-CHECKER-NOTASK-1/resource-manifest.md | 六份初始日志及 G1、过渡 gate 日志保留；后两项 hash 见 Closeout |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无 |

## Closeout Record

- Closeout date / adjudicator：2026-11-11 / ZCode `sess_6f299f99-83a7-4d04-a749-dade19f47d9a`，v2 裁决采信独立 Review；`integration_commit` 为直接 main 交付的集成验证基准 `62ab6b735961359b8a29984484033747b221fee4`，含实现、交付证据和 Review。
- canonical_evidence_status / resource_closeout_status：complete / complete；Review F-1 按 v2 顺序处置，F-2 已以资源清单替换占位，F-3 预算由门禁验证，F-4 证据目录已登记并由 TaskPath 复核。
- 删除、迁移、归档数量/字节数：0；主 worktree、三个隔离副本和原始日志保留。仓外 G1 日志 SHA-256 `8b8d959f82555f83587da84ffbafb8daad7fc602d040fa3ee1c675c5494922d4`；过渡日志路径 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/transitional-gates-685d3a9.log`。
- 过渡日志实际 SHA-256：`27a8baed3e6cc70c11a7b4735130822748e995250d3cfe5cfecafc21aa50c59b`；HEAD `685d3a9e22e7adfb1d032f7b202e5390146e4b05` 时 TaskPath 因 G1 日志尚未登记而 EXIT 1，其余三项 EXIT 0；本 pin 回填消除该暂态，未将其记为 PASS。
- 未关闭项及当前指针清理：STATUS 空窗、Plan done、Ledger 重生成；R-001 保持 open P2，后续 Task 尚未释放。空窗候选和 clean 终态验证见 closeout gate 记录及最终复跑。
