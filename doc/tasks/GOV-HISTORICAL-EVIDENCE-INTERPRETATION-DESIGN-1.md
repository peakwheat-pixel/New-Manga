---
id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1
title: 五项历史证据精确解释与原子保全设计
kind: design
governance_version: 3
status: in_review
approval: user_next_step_20261022_design_only
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1, GOV-BROAD-ROOT-PRESERVATION-IMPL-1]
base_commit: 8274d969706ee99acfdd9e26ae281882f5bbd6c7
branch: codex/gov-historical-evidence-interpretation-design-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1
integration_commit: null
delivery_head: a4fd609b43db745f789251467907cbf69208d2e3
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1
allowed_paths:
  - verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1
  - doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1.md
  - doc/handoffs/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1

## 来源、冻结范围与授权

用户“下一步”（2026-10-22）承接已done研究Handoff；依赖研究R2 49942377b/集成fec50696a与整体保护实现R4 d5d21ff9f/集成a3bba87ce。Codex Owner，DeepSeek Harness独立Reviewer。只设计R25/R26/R27/R28/R32四源五错误的精确身份schema、模板行/围栏边界、NUL原始证据保全解释、原子保护与fail-closed/拒绝矩阵。设计通过不等于实施。

允许有界只读前研究source-facts/report/R2、原四源/P14/P22引用行和必要scanner共享收口；不通扫历史。仅写allowed_paths。禁止改生产工具/实际运行配置/旧Task/Review/NUL/原source/pin/69例外、共享Schema/依赖/产品代码；七历史运行身份继续BLOCKED，不猜TEMP/APPDATA。不得全文件/围栏忽略或去NUL/转码，四源原字节与P09 line227既有保护必须保持。未知作者untracked P22不接管/提交；六旧探针不触碰。

不做真实apply/删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/Legacy。若设计必须改原字节或缩小保护，先列具体对象/证据/影响请求用户裁决；本设计选择全保留，不申请此类变更。

## Acceptance Criteria

- [x] **AC1** 有界复核四源/五完整错误身份/原SHA、NUL/C0与模板上下文；正式12完整identity不变、旧保护集合不减。 <<MET>>
- [x] **AC2** 冻结精确schema/来源与行绑定、整源及原line227保护、三NUL空声明复核、原子发布与审计warning/恢复和拒绝矩阵，严禁通用忽略；binding specimen仅设计、不加载。 <<MET>>
- [x] **AC3** 设计绑定与当前真实来源一致的只读assert校验、EV raw/blob/pin及实际登记、check/diff；planned运行测试不冒称executed，NOT_RUN分列。 <<MET>>
- [ ] **AC4** 固定head DeepSeek非作者Review通过、Codex集成/复验、资源原位保留核销与Task/STATUS/Plan/Handoff/恢复指针一致。 <<PARTIAL: 待审集成>>

## 验证计划

planned：Python -B/UTF8对canonical源字节/当前scan、设计binding字段与真实identity作只读断言；pwsh -NoProfile -File tools/governance/check.ps1；git diff --check。允许纯内存设计数据核对，不写或自清fixture、不试运行设计中的未来helper。运行正负矩阵仅planned；产品/旧127/全资源与句柄盘点NOT_RUN（无实现/处置）。DeepSeek只读/stdout，禁任何temp/探针/fixture/ACL或权限绕过。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/.gitattributes|a4fd609b43db745f789251467907cbf69208d2e3|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/binding-specimen.json|a4fd609b43db745f789251467907cbf69208d2e3|1499ddcfddea281dec45e4ed146499725ea3e1e081ea2412b96829b9af274740|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/checkpoint.md|a4fd609b43db745f789251467907cbf69208d2e3|b6436ac4b82886f466a985f30518c33ea11a3f2bd60c5fcbdaaac46b80c585c2|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/deepseek-review-r1.md|a4fd609b43db745f789251467907cbf69208d2e3|260a15da00359285db7640cc78e89d85ab17f72cc7610712aed782469e3479fd|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/design.md|a4fd609b43db745f789251467907cbf69208d2e3|02d1e9e55ad0021d55481883c7067a2536c294ef03a7628ee3caeb4b1bf2f9b0|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/execution.json|a4fd609b43db745f789251467907cbf69208d2e3|d6cc150df69037988079c844b0ae8eb70f2dfa817753792ff8c9b31efed0ec7d|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/validate_design.py|a4fd609b43db745f789251467907cbf69208d2e3|838348a76c927c12c6c486ca59dca5270033ba98feb9f15f62ffee2512ed398a|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/validation.json|a4fd609b43db745f789251467907cbf69208d2e3|f910cb214386ca5513f1498fcc97aa9db994664c9c8ae226aea448a7927fffaa|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1 | doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1.md | 冻结后创建，原位保留不移除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1 | doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1.md | 设计校验/Review日志和恢复材料保留 |
| env/build/fixture | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |

## 运行与恢复

冻结前main8274d9697，common G:/CODEX/New Manga/.git；Codex epoch9租约有效，先前dsh停止主控写入授权持续。旧作者文件不动，tracked clean；101heads/139WT，创建本Task资源后预计102/140，按r212全保留，父blocked且尚未只剩main。Task来源base和实际branch创建base分别记账；新WT缺untracked源，不替代canonical。可镜像自己的新E/Task/Handoff到main以精确pin/check，不镜像或改写旧源。

实际分支创建base345c86857f6ea80153ead49271e84ff234a4963f，common目录一致，当前102heads/140WT；baseline12错误/1882保护根（含本Task两新资源），四源SHA与已审研究一致，6guard根均已有保护。新E只是设计样本与只读一致性断言，无运行配置/解析器改动；拟议12→7尚未运行。

交付88a8a7b0f/真实Review diff base345c86857f6ea80153ead49271e84ff234a4963f。7EV raw/blob/pin固定；运行配置路径当前不存在、tools差异为空。样本canonical policy SHA-256=3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d（由严格JSON规范化计算，未来实现Task才冻结为代码常量）。设计数据assert/check/diff实际exit0；未来helper/12→7/+6声明/+4warning及T01–T18全NOT_RUN。当前真实12和四源原字节不变，102/140保留，父blocked/r212不变；下一固定head DeepSeek纯只读独审。

R1 DeepSeek approved ac0bd5a74（P0/P1=0）；R2修订集中处理P2快照字段/时点、broad active/no-op适用性，并明确原line227实目标末检及tracking仅用于配置/事实/源文件。未实施生产代码。新交付a4fd609b4/current8EV，canonical样本摘要3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d；设计数据assert再次exit0，原四源/正式12/旧保护不变。固定新head再由DeepSeek只读复审，不用旧批准覆盖新契约。
