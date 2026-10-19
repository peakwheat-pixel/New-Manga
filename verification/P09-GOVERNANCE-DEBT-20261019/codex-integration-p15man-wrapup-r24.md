# GOV-P15-MANIFEST-1 集成裁定 + GOV-PIN-LINEAGE-1 释放评估（r24）

- 日期：2026-10-20
- 裁定者：Codex（Lead / Architect / Integrator）
- checkout：`G:\CODEX\New Manga`
- branch / 当前 HEAD：`antigravity/P09-AC3-DELETE-HARDEN-1` / `7b1cb6a78346b42bb7c23de9bf924117b7c68a21`
- 本文件是本轮唯一写入。未修改 Task、Plan、STATUS、checker、源代码或任何既有 evidence；未执行 Git 写命令，未调用 `coordinator-lease.py`。
- 基线：动手前 `git status --porcelain` 为 1237 行；按 LF 连接后的 UTF-8 状态文本 SHA-256 为 `5d38f7479a2e55b24ddebb282bce3a47a144d3607679f5d22ee1f47bebd92bfc`。目标文件当时不存在。

## 结论摘要

1. **P15 manifest Task 应在集成后验证通过后转 `done`；眼下仍保持 `approved`。** 固定 delivery/review source 是 `2f9d549d5578a50893eabb4572394b4e212f0d87`，当前 checkout 的祖先链包含它；现场未发现独立交付 branch/worktree，提交链也无 merge/cherry-pick。它是在当前分支原地交付的。但 `integration_commit` 不能仅因提交已在当前分支、或为 checker 填非空值就记成当前 HEAD。按 r23 §3，Codex 还须确认当前 checkout 是受控集成目标并完成集成后验证；该验证完成时的**真实完整 HEAD**才可记为 `integration_commit`。不改 checker，不采用 `in_place` 伪枚举，也不把 delivery head 自动等同 integration commit。
2. **此刻的 head 三元组**：`reviewed_head = 2f9d549d5578a50893eabb4572394b4e212f0d87`；`delivery_head = 2f9d549d5578a50893eabb4572394b4e212f0d87`；`integration_source_head = 2f9d549d5578a50893eabb4572394b4e212f0d87`；`integration_commit = null`（待真实集成后验证）。若随后验证通过且期间没有新提交，候选真实值为当前 HEAD `7b1cb6a78346b42bb7c23de9bf924117b7c68a21`，但必须以验证当刻实际 HEAD 回填，不能预填。
3. **GOV-PIN-LINEAGE-1 暂不释放。** 主体可冻结为历史 pin lineage，AC4 选择不改 checker；但来源仅具体确认两个 pin，未给出“另外五个”的身份与提交链，当前不能交付可执行的七项清单。且 Task 仍 `proposed`，Plan/STATUS/owner/reviewer/base/branch/worktree/allowed paths 尚未按释放协议冻结；本轮授权也只允许写本报告。
4. **治理债线还没有完全 closeout，但已进入收尾段，建议完成 P15 closeout 与一个边界清楚的 pin-lineage Task 后转产品主线。** 9 个治理 Task 的状态口径为 8 个 `done`/`closed_with_limitations`、1 个 `approved`。PIN-LINEAGE 不是唯一尚存的 Plan `proposed` 节点：Plan 还保留一个合并的 `RUST-ENV-BASELINE-1 / P07 / P21` proposed 行（P07/P21 标注可选）；它们属于后续工作队列，不等于已确认的治理债。没有证据支持声称“再无任何债”，也不建议为追求全绿而无边界扩大审计。

## 1. GOV-P15-MANIFEST-1：原地集成的诚实表达

### 核验结论

Task frontmatter 的 `branch: null`、`worktree: null`；固定被 Review 的交付提交 `2f9d549d5` 是当前分支 HEAD 的祖先。当前分支最近提交链为：

```text
237c43862 manifest 初次恢复
→ 2f9d549d5 补三项 junction 实测
→ 68e696306 Review / 证据记账
→ e66927a31 r3 Review pin 记账
→ 7b1cb6a78 Task 停在 approved、integration_commit=null
```

当前 checkout 的唯一包含分支为 `antigravity/P09-AC3-DELETE-HARDEN-1`。结合本 Task 没有 delivery branch/worktree 元数据、上述连续提交链以及“直接在主 checkout 完成”的交付事实，裁定：**没有独立交付分支/worktree；无 merge/cherry-pick；交付已原地落在当前集成 checkout。** 这证明集成来源提交已经包含在 checkout 中，但不替代集成后验证。

### `integration_commit` 处置

- 不填 `in_place`：checker 只把非空值当作“有 integration commit”，该字符串不能提供 Git commit 身份，也会扩展字段 schema。
- 不因 DONE checker 必须非空而让它永久 `null`：协议 §4 明确 `done` 前要完成集成、验证和 closeout；“原地集成”是有效集成方式。
- 不立即填 `7b1cb6a78`：它是当前观察到的 HEAD，尚未由本次 Codex 完成集成后验证；仅记录 HEAD 会重演 r23 所禁止的占位行为。
- **采用 r23 §3 已给出的原地集成口径**：完成验证后，填验证完成时的真实完整 HEAD，并在 Closeout 写明没有 merge/cherry-pick、approved source 已在受控目标祖先链、验证命令/结果/时间及 HEAD。若验证中产生新提交，记验证后实际 HEAD。只有发生真实集成与验证后才更新 Task/Plan 状态。

### 集成后验证与 Plan 文本

验证建议至少包括：核对 `2f9d549d5` 的祖先包含关系和本 Task 允许 diff；运行 Task-scoped 与全局 `tools/governance/check.ps1`；单独核对 P15：manifest 缺失错误确已消失，预期仅余 `SettingsPage.test.tsx` 的既有时间性 pin 失配，并通过 `git log` 确认其后续变更提交。记录完整输出、exit code 与实际验证 HEAD。P15 的预期遗留项不得报成 P15 全绿；它由 PIN-LINEAGE 范围承接。正式 closeout 是否可 DONE 仍取决于 Task 自身的检查器 Gate、证据/资源核销和协作协议 §4。

验证完成前，Plan 应使用 r23 §5 的完整 `approved / integration pending` 行：

```markdown
|GOV-P15-MANIFEST-1|GOV-SOURCE-RECORDS-1|approved（AC 4/4 MET；重建 P15 Resource Manifest，worktree + 3 个实测 junction；Antigravity Review r3 APPROVED；等待 Codex 原地集成后验证及 evidence/resource closeout）|
```

验证及 closeout 全部通过后才替换为终态行：

```markdown
|GOV-P15-MANIFEST-1|GOV-SOURCE-RECORDS-1|done（AC 4/4 MET；重建 P15 Resource Manifest，worktree + 3 个实测 junction；Antigravity Review r3 APPROVED；SettingsPage.test.tsx 历史 pin 由 GOV-PIN-LINEAGE-1 承接）|
```

Plan 当前 done 计数为 40；正式变成 `done` 后增至 41。STATUS 当前 Active Task 是 P20，不因 P15 closeout 改写 Active 指针。r23 的推荐/允许路径正确；本次没有执行这些 lifecycle 写入。

## 2. GOV-PIN-LINEAGE-1：释放裁定、AC 与对象清单

### 是否释放、Owner/Reviewer

**目前不释放；保持 `proposed`。** 解锁条件：

1. GOV-P15-MANIFEST-1 完成 Codex 原地集成后验证、evidence/resource closeout，并经正式 lifecycle 写入为 `done`；其依赖及基线随之可冻结。
2. 对七个候选 Task/pin 做独立 inventory：确定每行 Task ID、evidence_id、path、原 commit、原 SHA、该 commit 处 hash、当前 hash、后续修改提交完整 hash/日期、是否确属授权的时间性演进；排除 pin 从始即错、工作树未提交修改、CRLF/EOL-only 变化及其它类问题。必须先得到确定的七项，再把范围写回 Task。
3. 对 AC4 冻结本裁定所选的 **(c) 不修改 checker**，并记录后果：历史 hash mismatch 在相关 Task-scoped check 里仍是 error；lineage 说明保存历史意义，不会让当前字节 hash 检查自动变绿。GOV-PIN-LINEAGE-1 不以“修 checker / 清除旧红项”为目标，不重算原 pin。当前已有的四个 PASS 范围不会因仅追加 Task 正文 lineage 而改变；两项已知失配对应 Task 的 checker 仍保留原错误，不能声称它们 PASS。
4. 由 Codex 完成 Task、Plan DAG/READY、STATUS 待派指针、完整 base、branch/worktree、allowed paths 和资源边界登记，并通过任务/全局权威 checker 后再派发。proposed 文件本身不能开工。

无法据当前工具状态确认 Antigravity 的实时可用性：本机可见 `agy.exe`，但没有可验证的空闲/认领状态或活跃任务信息。释放时优先检查 Antigravity 可认领性；若不可用，按本项目故障转移顺序转给 **ZCode**。Reviewer 建议 **DSH**：DSH 做过 Owner 不构成对自己工作的自审，因为本 Task 的 Owner 另由 Antigravity 或 ZCode 承担，DSH 不审查自己实现。若实际 Owner 改为 DSH，则 Reviewer 必须另选非作者（优先 Antigravity/ZCode 中可用且未参与实现者）。Qoder 不参与。

### 重写后的可执行 AC（释放前替换 Task 原 AC）

- [ ] **AC1 — 冻结历史失配 pin 清单。** 在 `verification/GOV-PIN-LINEAGE-1/` 建立逐项 inventory；范围恰为 AC2 核实出的七个 Task/pin（不是“七个 Task”与“七行 pin”混用）。每项记录 Task/evidence_id、路径、原 pin commit/full SHA-256、该 commit 处文件 SHA-256、当前 SHA-256、工作区与 HEAD 状态、分类和来源。只纳入“原 pin 在 pinned commit 准确、之后由可定位提交合法修改，故当前文件演进”的时间性失配；明确排除原 pin 错误、未提交改动、EOL-only 失配和证据不足项。若核实数量不等于七，停止并由 Codex重新裁定范围，不能凑数。
- [ ] **AC2 — 证明后续演进。** 对 AC1 每项读取 Git 历史及必要的内容差异，记录使该路径首次偏离原 pin 字节的后续提交完整 hash、日期、提交/变更说明和影响摘要；证明原 pin 在原 commit 中匹配，并说明后续修改与当前 hash 的对应关系。无法证明授权/时间因果的项标为 `UNRESOLVED`，不写成已确认 lineage。
- [ ] **AC3 — 追加 lineage，保留历史事实。** 仅对 AC2 已确认项，在对应 Task 的 Canonical Evidence 表旁追加可定位的 lineage/supersession 记录，列出原 evidence_id、commit、原 SHA、后续变更 commit/date、当前内容 SHA 及结论“原 pin 对当时提交有效、路径内容后来演进”。严格不改表内六列、不覆盖/重算原 pin、不改证据文件；当前 Gate 确需现行内容时，先获 Task 明确授权，再以新 evidence_id 增加当前内容 pin。
- [ ] **AC4 — checker 处置与影响证明。** 采用“不改 `tools/governance/check.ps1`”。说明 lineage 注记不豁免当前 SHA 比对，相关历史 Task 的 mismatch 仍会 FAIL；保存受影响 Task-scoped check 的错误集合与四个基线 PASS Task 的 before/after 对照，证明本 Task 没有扩大/改变 checker 行为、没有隐藏错误或改变任何既有状态。若实施中发现只有改 checker 才能满足新增需求，暂停并交 Codex另行冻结契约/授权，不得在本 Task 中自行扩范围。
- [ ] **AC5 — 独立交付与审查。** Owner 提交 inventory、变更摘要、每项 Git 追溯证据、Task 注记 diff、验证结果、Handoff 与固定 delivery head；运行 Task-scoped 和授权要求的全局只读治理检查并保留 stdout/stderr/exit code。Reviewer 针对固定 head 独立核对七项清单与提交链，抽查原 pin 未被改写，且 Owner 与 Reviewer 不同；Codex 对 findings 完成集成及 closeout 裁定。

AC 的授权路径因此限于精确七项所涉 Task 的 Canonical Evidence 表旁、`verification/GOV-PIN-LINEAGE-1/`、Task/Handoff/Review 生命周期文件；**不包括** `tools/governance/check.ps1`、证据原文件、P15 manifest 或其它历史 Task 元数据。正式释放时按准确七项路径冻结 `allowed_paths`，不要把所有 `doc/tasks/**` 宽泛授权。

### 目前能确认的清单边界（不得冒充七项最终 inventory）

| 状态 | Task / pin | 当前可核实事实 |
|---|---|---|
| 已确认候选 1 | `EXPORT-REVEAL-1` / `M2-C1_TYPED_IPC_CONTRACT.md` | Task 与 r20 点名；原 pin 在交付后契约演进到 rev 2.11。完整后续提交链及日期仍应由实现者用 Git 重核。 |
| 已确认候选 2 | `P15` / `apps/desktop/frontend/src/settings/SettingsPage.test.tsx`（evidence `E6`） | Task、Handoff、r3 Review 与 `sha-mismatch-evidence-chain.md` 点名；后续提交 `528c6289c` 修改。原 pin 在 commit `e5f1a719bdaf482da027498671490c585a376bd3` 处匹配。 |
| 未识别候选 3–7 | 尚无可由指定来源核实的 Task/evidence_id/path 清单 | r20 只说“另外 5 个 Task”；r21 要求独立 inventory。`sha-mismatch-evidence-chain.md` 是 102 行异类 hash 差异调查，含 `pin_differs_at_commit`、未提交修改等情况，不能据此任挑五项补数。 |

因此交付方“7 处”目前不能独立确证为七行，也不能确证其余五行确属合法时间性演进。此点是**释放 blocker**，不是把 AC 降低成“待调查后自行决定”。Task 初始材料列出的两项可作为已知候选，释放前的只读 inventory 必须把其余五项补成明确身份，否则保持 proposed。

## 3. 本轮治理线收尾判断

**可以开始收尾，但还不能宣布治理债已全部干净。** 顺序建议是：先完成 P15 Task 的正式原地集成 closeout；再按上述严格边界完成 PIN-LINEAGE（仅在七项清单确证并冻结后释放）；该 Task closeout 后，把精力转回 `ARCH-DOC-REBASELINE`、P20 等产品主线。无需继续对全仓所有 SHA mismatch 做无限扩面审计。

“九个治理 Task 已终态”的计数把当前 P15 `approved` 也算入已处理；严格按协作协议，它不是终态，仍待 `done`。Plan 中除 PIN-LINEAGE 外，还有 `RUST-ENV-BASELINE-1 / P07 / P21` 合并 proposed 行，且 STATUS 另列 RUST proposed；这是一条不同性质的计划工作，不是本轮已识别的治理债清单。PIN-LINEAGE 之后**不会自动证明全仓没有未知问题**，但如果七项 lineage 按边界收口、P15 正式 done、现有 Gate 与当前 Plan 一致，就没有依据继续把这条特定治理债线扩大。剩余收益预期递减，应转产品主线；出现新的具体 Gate 失败/证据时再立窄任务。

## 4. 动手后工作区状态

写入后 `git status --porcelain` 为 1238 行，状态文本 SHA-256 为 `58906ede3d8121d3237d1fbcc190c6faf842a6cafcc7d4337fd2da0241fb5269`。剔除唯一新增项 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-integration-p15man-wrapup-r24.md` 后，剩余 1237 行，SHA-256 为 `5d38f7479a2e55b24ddebb282bce3a47a144d3607679f5d22ee1f47bebd92bfc`，与动手前完全一致。没有归因、整理或清理任何原有 dirty/untracked 内容。

## 下一步

先由 Codex按协作协议完成 P15 的原地集成后验证和正式 closeout；随后做一份只读、逐项有 Git 证据的 PIN-LINEAGE inventory，确证完整七项并在具备实际 Owner/Reviewer 与工作区的条件下重新冻结/释放 Task。该 Task 仍 proposed 时不得派发实现。

