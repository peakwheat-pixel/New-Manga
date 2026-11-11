---
task_id: FEA-15-PIN-POLICY-1
adjudicator: ZCode CLI 独立上下文
adjudication_session_id: sess_39001b09-6b67-417a-b81d-85f3e62ec80d
adjudication_mode: plan（只读）
review_session_id: sess_08fc30ae-10e9-48c5-8029-c3adb02fe9a5
base_commit: 4efc592d12c25b8be33502f53c9270ad0597adfd
delivery_head: 359d09dffc489c8762727cf69b778cba6f432843
adjudication_input_head: a3db215b72a5665988e82a9d33804169af3b9375
decision: ACCEPT_ALL_FOUR_PROPOSALS
---

# FEA-15-PIN-POLICY-1 最终 ZCode Adjudication

## 裁决身份与输入

- 最终裁决者：ZCode 独立 CLI 新会话 `sess_39001b09-6b67-417a-b81d-85f3e62ec80d`。此 ID 由 CLI JSON wrapper 的 `sessionId` 字段取得；ZCode 正文因 plan mode 无法自省，但实际会话 ID 已回填。
- 未复用 Task release session `sess_236d9541-8358-45f0-9318-4844a86a767e` 或独立 Review session `sess_08fc30ae-10e9-48c5-8029-c3adb02fe9a5`。
- base `4efc592d12c25b8be33502f53c9270ad0597adfd`；政策提案 delivery head `359d09dffc489c8762727cf69b778cba6f432843`；裁决输入 main HEAD `a3db215b72a5665988e82a9d33804169af3b9375`。
- 补证 clean HEAD `d26c43c76576b0f514530874fc9cb04f016674e6` 的五项 gate 日志 `delivery-gates-d26c43c.log` 已登记；其生成 HEAD、clean 状态、EXIT 与本 Task card pin 一致。

## 核验摘要

| 项目 | 裁决输入与结果 |
|---|---|
| Inventory / delta | `5,376` 行；`+26 / -0 / changed 0`；增量为上游 24 行 + 本 Task 2 行；`WORKTREE +16 / MIXED +10`。 |
| 互斥 basis / 异常 | `3,467 + 327 + 1,009 + 573 = 5,376`；573 由 `160 + 293 + 68 + 47 + 3 + 2` 构成且是观察分类，不是 corruption 清单。 |
| r194 matrix | `4,803` modeled match / `573` modeled nonpass；这是 inventory predicate model，非逐行执行 `check.ps1`。 |
| 样本 / limitation | BLOB text、WORKTREE text、MIXED_EOL text、BINARY PNG；legacy `class` parser limitation 在多份文档披露。 |
| R-001 / NOT_RUN | R-001 保留 open P2；clone dry-run、pytest/.NET、Linux fresh clone、renormalize、迁移及 checker/template 改动均未宣称 PASS。 |
| 补证 gates | `d26c43c` clean HEAD 的 default/current/prior TaskPath、18 pins、API 五命令均 `EXIT=0`，各 check 有 3 条既有 warning。 |

裁决会话处于 plan mode，Bash 被拦截；它未独立重算 Canonical Evidence SHA、未执行 `git ls-tree` 或亲跑门禁。裁决依据为多载体一致性、已提交日志和 Review 报告；该限制不冒充独立机器复核。Codex 在 `a3db215` 上另行只读核验当时卡面 28 条 Canonical Evidence：路径存在、SHA 一致、所有非空 commit 均包含对应路径。该本机审计不代表 ZCode 会话亲自执行。

## 四项最终裁决

### 1. 新 pin 默认基准：接受 `BLOB`

仓库内新 Canonical Evidence pin 默认对准表内 commit 中路径的精确 Git blob 字节：先提交证据，再对 `git cat-file blob <commit>:<path>` 取 SHA-256。文本不隐式转换 EOL；二元文件不解码、不重压缩，使用相同字节算法。仓外原始输入使用明确的外部 basis；无法读取时记 `NOT_RUN` 或 `BLOCKED`。`WORKTREE` 仅限明确声明并解释环境可复现性的例外。此口径在本裁决入库并由 Task 卡 pin 后，对治理和人工登记要求生效。

### 2. 既有 pin：接受保留、分类、逐项授权

不批量迁移既有 5,376 行、不改历史 hash。573 异常为互斥观察集，不代表 corruption、无效或待迁移；逐项处置须有单独 Task、引用核查与证据。因 legacy `class` parser limitation，后续不能用历史 `class_counts` 作语义依据；需先修复/替代解析器并独立复算。

### 3. r194 双基准语义：接受分阶段收敛方案

当前不改 `check.ps1`：旧六列表格式继续遵循现行 OR 语义。后续可在另行释放的 successor Task 中冻结显式 `sha256_basis` 字段及值域，新七列强制 `BLOB`、`WORKTREE` 或 `EXTERNAL_SHA256`；旧格式兼容、旧 pin 暂不迁移。该字段名/值域须在 successor Task 释放时最终冻结，本裁决不授权改模板、checker 或历史表。

### 4. R-001：接受保留 `open P2` 并转交

不关闭、不改历史 hash。当前工具和表格无法证明每条历史记录的作者 basis；关闭条件在显式 basis 工具面形成前尚不可达。R-001 后续转交获释放的 basis enforcement Task；若复算与上游 Review 不符、路径缺失或触及受保护历史，应保持/重开并停止变更。

## Review 发现处置

- **发现 1（P3，pinbackfill 后缺 clean-head gates）：关闭。** `delivery-gates-d26c43c.log` 记录 clean HEAD `d26c43c76576b0f514530874fc9cb04f016674e6` 上五项命令全 `EXIT=0`，18/18 pins、API 86，并已登记为 Canonical Evidence。
- **发现 2（P3，Handoff 的 “clean main” 描述未注明 6 个生成输出 untracked）：非阻断 limitation，不要求返修 Handoff。** Closeout Record 必须明确：“Handoff 中 `e9f7bb1` 处 ‘clean’ 指 tracked clean；当时 6 个生成输出 untracked 在场，以 `delivery-gates-e9f7bb1.log` 的 `STATUS_BEFORE` 为准。”
- **发现 3（P4，preliminary run log 是回溯整理）：非阻断 limitation，无需返修。** 该过程日志自披露来源且已被 delivery 版 supersede；后续数据引用以 delivery 版为准。

## AC 状态与政策生效

- AC1：`MET`。Inventory、delta 与提案完成最终裁决。
- AC2：`MET`。影响面方案完整，NOT_RUN 和禁止实施范围保留。
- AC3：`MET`。Review `ACCEPT`、治理门禁有记录、发现 1 已补证、发现 2/3 分类并由本裁决处置。
- 政策的治理/人工登记要求在本裁决报告入库并由 Task 卡 pin 后生效。机器强制不立即生效：须待 successor Task 独立释放、实现、上下文独立 Review 与集成验证通过。
- 不追溯既有 pins，不改变 r194 当前 checker 行为。接受提案不授权修改 checker、template、`.gitattributes`、历史 pins、契约、源码、Schema、依赖或资源；不授权 push。

## Task 收口与后续边界

Task 可进入 `done`。收口应将三个 AC 设为 `MET`、更新 Closeout Record、登记 resource closeout、同步 STATUS/REBASELINE_PLAN/TASK_LEDGER/checkpoint，并在 done 状态复跑五项 gates 留证。

`FEA-15-PIN-BASIS-ENFORCE-1` 仍只是候选名称，不是已释放 Task。本裁决不释放 successor，也不代行 DSH 的范围冻结。后续未知项（160 条 `INCONSISTENT` 的根因、47 个外部路径可达性、Linux fresh clone 表现、显式 basis checker 的跨平台行为）留给另行释放 Task 实测。