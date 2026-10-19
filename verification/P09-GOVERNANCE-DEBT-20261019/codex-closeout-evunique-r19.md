# GOV-EVIDENCE-UNIQUE-1 Closeout 裁定 r19

- 日期：2026-10-20
- 裁定者：Codex（Lead / Architect / Integrator）
- 当前主 checkout：`G:\CODEX\New Manga`
- branch：`antigravity/P09-AC3-DELETE-HARDEN-1`
- 当前 HEAD：`69952f5a79e8921898ef26a9f567f22d4c81fb40`
- 本裁定唯一新增文件；不修改 Task、Plan、STATUS、Review、既有 verification 或其他路径。

## 结论

**建议终态：`done`。** AC1–AC4 已达成；AC5 的剩余工作是 Task/Plan 生命周期记录、证据与资源核销、head/integration 字段和治理核验。全局与 Task-scoped checker 本轮均 PASS，Task 检查有 2 warnings。目录证据、Handoff、四轮 Review、只读核验及本报告构成 closeout 依据。

7 个不存在的候选文件、19 个 `EVIDENCE_GAP` 和两个来源 Task 的 0 勾选异常，均是本 Task 按冻结范围核验后**记录的发现/限制**，不是本 Task 承诺修复的未完成 AC：AC1/AC2 明确要求报告候选存在性、覆盖缺口和不确定性；AC3 明确限定只读，禁止改来源 Task、补 pin 或处置文件。不得把这些发现改写成 PASS 或抹除。它们不阻止 `done`，但其中来源 Task checklist 不一致应作为独立文档维护债项另行登记。

### 2.1 发现的性质与后续

- **7 项缺失**：只证明候选清单中的仓库相对路径不存在；不能证明仓外无副本，也不能证明来源 Task 的 AC 未完成。它们是核验结果，不是 GOV-EVIDENCE-UNIQUE-1 的未完成工作。**不追查仓外副本，不回溯重建历史证据。** 只有未来某个具体发布/验收 Gate 明确依赖其中某项时，才按新授权建立任务核实。
- **19 项 `EVIDENCE_GAP`**：严格表示冻结的 61 项候选集没有覆盖对应 AC 的文件级证据，不等于原 Task 没有任何证据，更不等于 AC 未实现。它们是本次覆盖核验产出；**不建立统一的历史证据补齐 Task，不回溯补造/补采原始运行证据**。新需求或当前 Gate 若确需证明某行为，应在新架构下对该行为建立新验收任务和新证据。
- **`EXPORT-REVEAL-1` 0/7、`P15` 0/6**：维持来源 Task `status: done` 和 checklist 原状。本轮不得由 Codex 直接补勾，也不据 checklist 空白单独重判 done；空白不能证明 AC 未满足。由各来源 Owner 按原 AC 和各自 Canonical Evidence 逐项核实后回填真实结果，再由 Codex 复核：`EXPORT-REVEAL-1` Owner=Codex；`P15` Owner=ZCode。当前不够授权/证据直接更改它们。应登记一个后继的来源记录维护 Task（两份来源文档作为范围），明确不得改写历史 Review/pin、不得把 `BLOCKED`/`NOT_RUN` 标成通过；若逐项核实发现实质未满足，再另行提请 Codex按当前授权流程重判状态/立修复 Task。**Codex 本次不直接修改这两份 Task。**

故本轮对 7 项与 19 项的裁定是**不追历史、不留成“本 Task 未完成债”**；对 2 个来源 Task 的空 checklist 则是**留一项独立、有限的记录维护债**，不改变本 Task 的 done 资格。

## 2.2 Head 三元组与集成字段

| 字段 | closeout 值 | 依据 |
|---|---|---|
| `reviewed_head` | `ef4aadfee`（`ef4aadfee...`） | r4 Review 的精确 `reviewed_head`；Review 绑定值不得因后续 pin/bookkeeping 修正而改写。 |
| `delivery_head` | `3b62f793780defd70c092329e64ebb6b097a84be` | 保持交付 Handoff 与原始固定交付的标识。后续 5 个提交是 Review 修正/复核及 closeout 元数据，不重定义交付包的身份；按 r16 区分被审目标与后续主线历史。 |
| `integration_source_head` | `3b62f793780defd70c092329e64ebb6b097a84be` | Task 在主 checkout 直接执行，无独立来源分支/worktree；来源固定为该交付 head。 |
| `integration_commit` | `69952f5a79e8921898ef26a9f567f22d4c81fb40` | 本 Task 没有 merge/cherry-pick。为满足 DONE checker 非空约束，登记当前主线中最终修正和 closeout 状态所依据的实际集成后主线 HEAD；不得声称这是 merge commit。 |

r4 的 verdict 是 `APPROVED_WITH_ONE_FIX`，其唯一修复是删除后重算 pin；其后提交 `90377dd22` 核验两表各 3 行并更新 pin，`69952f5a7` 记录 AC4 closed、四轮发现均处理。当前工作提交链是：`c41a40a09`、`0a9e809e2`、`ef4aadfee`、`90377dd22`、`69952f5a7`。Handoff 的 `delivery_head` 描述首个冻结交付；r4 的 Review 固定到后来经修订的 `ef4aadfee`。两者语义不同，不互相覆盖。

## 2.3 Canonical Evidence 与 Resource Manifest

### Canonical Evidence

现有 9 行覆盖 AC1–AC3 和首轮 Review。AC4 的 Review Gate 需要保留完整审查链，closeout 应补登记 **r2、r3、r4 三份**，使 Review 清单为 r1–r4：

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-REVIEW-R1 | AC4 | `doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r1.md` | `c41a40a09` | `a9abc01e6514ddf786476dc369467a29afd787898a07de063f467781da7c83ed` | `CANONICAL` |
| EVID-REVIEW-R2 | AC4 | `doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r2.md` | `0a9e809e2` | `fd3c249116fe87b48b16d379570d29e303425f5c38382deabeed5b1d8bc815d1` | `CANONICAL` |
| EVID-REVIEW-R3 | AC4 | `doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r3.md` | `ef4aadfee` | `b6b55c1c553d2fe05b58ef501c51879e24e7f84d90c57121bd0e1d0dcbc201ad` | `CANONICAL` |
| EVID-REVIEW-R4 | AC4 | `doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r4.md` | `90377dd22` | `8593ce4d75a66a02350de4022445097790ff8385061a9645be26035c379ce752` | `CANONICAL` |

Commits are the commits that introduce each review file. Hashes above were computed from the current on-disk review files. R1–R3 preserve the historical `CHANGES_REQUESTED` outcomes; they are not current approval. R4 is the final Review and is `APPROVED_WITH_ONE_FIX`; subsequent pin recomputation and AC4 closeout resolve its one fix. The checker confirms Task PASS after the already completed pin rehash.

**Inventory discrepancy:** the user/task summary says the evidence directory contains 14 files; current read-only `Get-ChildItem -File` returns 13. This report does not add, remove, or alter evidence files. The registered canonical evidence remains the nine existing rows plus three Review rows; process/input inventories remain governed by existing warning and pins.

### Resource Manifest

本 Task 只读盘点，未创建或处置资源。Resource Manifest 应逐项填入以下处置，不得留空：

| resource_type | disposition / 核实结论 |
|---|---|
| worktree | `NOT_APPLICABLE` — Task frontmatter 为 `worktree: null`；在主 checkout 执行。 |
| task-env | `NOT_APPLICABLE` — 无专用 task environment 创建/登记。 |
| dataset/model/test-material | `NOT_APPLICABLE` — 只读仓库证据文件，无独立数据集、模型或测试材料派生物。 |
| artifact | `NOT_APPLICABLE` — 无新建构建/产品 artifact。 |
| temp | `NOT_APPLICABLE` — 无 Task 临时文件登记或处置。 |
| agent-output | `NOT_APPLICABLE` — 交付材料直接入库至既定 verification/Handoff/Review；没有另行保留的 agent-output 资源。 |
| exchange | `NOT_APPLICABLE` — 无交换目录/文件。 |
| evidence_dir | `PRESERVE_REFERENCED` — `verification/GOV-EVIDENCE-UNIQUE-1/` 为本 Task 的版本化证据与当前 pin 引用；只读保留。 |
| Handoff / Review | `PRESERVE_REFERENCED` — 当前 Handoff、Review 及历史审查链由 Task 生命周期引用；保留。 |

无需删除、移动或归档任何资源；无用户数据或未知资源需要作物理处置。完成登记后，`canonical_evidence_status: complete` 与 `resource_closeout_status: complete` 才可置位。

## 2.4 Plan / STATUS

Plan 当前节点目标说明过时（仍写“AC7 唯一最终证据判定”），而状态为 `in_progress`。closeout 时应整体替换为：

```text
|GOV-EVIDENCE-UNIQUE-1|GOV-DEBT-CLEANUP-2|done（61 项候选存在性与角色盘点；13 个来源 Task、83 个 AC 覆盖核验；COVERED 3、PARTIAL 17、EVIDENCE_GAP 19、NOT_APPLICABLE 42；只读不改来源 pin；closeout r19）|
```

Plan 当前 3387 bytes / 41 lines，未超 7000 bytes / 64 lines。done 计数应由 **36 增至 37**。READY/in_review 列表无需因本 Task 改变。STATUS 不需改：r15 后 STATUS 不复制 DAG 节点状态，本 Task 不是当前 Active Task P20，也没有改变 Gate。全局 checker 本轮 PASS（1 warning）；Task checker PASS（2 warnings：STATUS 预算提醒及 evidence_dir 未登记过程文件提醒）。

## 2.5 两个来源 Task 的明确后续处置

不直接补勾，不在本 closeout 重判 `done`，不改变任何 AC。Checklist 只能由对应 Owner 基于各自逐项证据回填；若无法核实，保持真实 `BLOCKED`/`NOT_RUN`/未知结果并交 Codex裁定。建议后继 Task 为来源 Task checklist 维护/核实，Owner 需分别协调 Codex 与 ZCode 贡献各自来源文档，Reviewer 由非来源 Owner 担任；本裁定不是该 Task 的释放。若复核发现来源 AC 实质失败，届时由 Codex按证据与治理规则另作状态裁定，并决定是否需修复任务。不可仅因空白 checklist 将已集成功能的 `done` 自动改成 `closed_with_limitations`。

## 2.6 7 项缺失与 19 个缺口：是否留债

本 Task 对这两类结果的交付义务是**识别、准确分类、说明范围限制**，不是替历史 Task 补造证据。没有当前 Gate 明确消费项或证据原件来源时，回溯补齐会混淆历史证据与新运行证据，因此本裁定选择：**不追历史，不为 7 项和 19 项建立统一补齐债**。未来新架构需求若需这些行为的证明，应新建针对当前行为的验收任务、重新运行并产出新证据；不能把新证据伪装成历史 Task 原有记录，也不能改写本次 `EVIDENCE_GAP` 结论。

## Closeout Gate 清单

- AC1–AC4：达成；AC5：由本裁定及拟执行的 Task 元数据/Plan closeout 完成。
- 当前 Task 主体不能在只写本报告的授权下直接设为 `done`；要正式落地，还需由 Codex 按以上裁定更新 Task metadata、Canonical Evidence/Resource Manifest 与 Plan，再运行 checker。**本报告裁定技术终态为 `done`，不宣称尚未发生的文档写入已经完成。**
- 唯一后继建议：建立来源记录维护 Task，限定 `EXPORT-REVEAL-1` 与 `P15` 的 AC checklist 逐项核实/如实回填；不得顺带追查 7 个缺失文件或回填 19 个历史证据缺口。按当前项目角色，来源分别由 Codex、ZCode 核实，Codex 整合，Reviewer 不得审查自己的修改。当前未释放该 Task，需先登记 Plan/STATUS、冻结范围及实际 base/head/workspace。

## Git 状态对比与边界

动手前后均使用 `git status --porcelain --untracked-files=all`。本次写入前状态由命令输出捕获；写入后除本文件唯一新增的 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-evunique-r19.md` 外，其余状态行逐字比较相同；无既存状态行消失或变化。写入前共 **1593** 行，写入后共 **1594** 行（均以本命令实测值为准）。

本次只写本报告；未修改 `doc/**`、`tools/**`、`src/**`、`tests/**`、`.gitattributes` 或既有 verification 文件；未调用 `coordinator-lease.py`，未执行任何 Git 写命令，未移动/删除仓外文件。
