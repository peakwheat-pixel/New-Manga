# DETECT-TILING-1 Closeout 裁定（r36）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
范围：仅 adjudicate `DETECT-TILING-1` 的 P1-2(d)、会话授权边界、AC2 `SEC-FMT-005` 缺口及建议终态。本文件不改 Task、STATUS、REBASELINE_PLAN、源代码、测试或既有证据。

## 裁定摘要

1. **追认 P1-2(d)，并将合成 JPEG 的适用范围明确限制为“JPEG 格式的预解码拒绝路径证据”。** 合成样本可补足 JPEG 格式分支的拒绝/内存观测；它不代表真实超大漫画素材，也不证明真实超大页的检测质量。记录 limitation，不要求为本次 AC4 追补不存在于 `test-materials` 的真实超限 JPEG。
2. **会话指令“按推荐自行裁决”是对选择权的明确委托，不仅是免于向用户提问。** 用户有权作该验收口径决定，因而可将决定委托给执行者；本项目规则没有规定此类裁定不得委托。阶段记录已将选择归于该用户指令，本次由 Codex 作正式追认并明确边界。故不将这次选择定性为越权或过程缺陷。今后涉及标准口径变更，仍须在 Task/权威裁定中明确授权与追认，不能仅依执行者自行偏好。
3. **AC2 的 `SEC-FMT-005` 映射已完成，判定仍为 `PARTIAL`。** 可用物理内存检查是原有且独立的缺口，不因选择固定像素限制路线而消失。决定另立后续 `DETECT-MEMORY-GUARD-1`，由 Codex 在另一个获准的 Task 生命周期中冻结动态内存策略；本裁定不释放其实现，也不把该要求豁免为永久 limitation。
4. **建议 `DETECT-TILING-1` 以 `closed_with_limitations` 收口，不设为 `done`。** P1-2(d) 不再阻断关闭；AC4 按本裁定可计为已完成，但 Task 仍不满足全部 AC 均通过的 `done` 条件，且 `SEC-FMT-005` 明确为 `PARTIAL`。本文件只是 adjudication，不更改权威状态；Task、STATUS、Plan、AC 标记、资源 closeout 与 checker 尚须按协作协议另行完成后，状态才生效。

## 1. P1-2(d)：AC4 的合成 JPEG

### 证据与适用范围

`doc/tasks/DETECT-TILING-1.md` 原 AC4 要求使用 `test-materials` 中既有超限样本，至少一个 PNG 和一个 JPEG。执行记录说明已筛查其中 34 个 JPEG，均未超过 `MAX_DETECT_PIXELS`；真实超限 JPEG 不存在。补充样本是在 workspace 生成的 `5000×4000` RGB JPEG，`20,000,000 px`，sha256 为 `84592ff425ae348313ef202230d59583ef727cada9aca55027dfcc1f800bee5f`，路径为 `G:\CODEX\New Manga.workspace\DETECT-TILING-1\synthetic\oversized-5000x4000.jpg`，未入库。

现有记录给出的实测为：真实 PNG `690×62133`、`42,871,770 px`，拒绝峰值 `141.7 MB`，完整解码峰值 `479.8 MB`；合成 JPEG `5000×4000`、`20,000,000 px`，拒绝峰值 `53.2 MB`，完整解码峰值 `242.2 MB`。数值按 `verification/DETECT-TILING-1/stageA-remeasurement-20261020.md` 的绝对 Peak Working Set 口径引用；这两轮 Review 没有独立重跑内存实验。

合成 JPEG 的结果能支持 JPEG 格式请求经过同一拒绝机制、在像素解码前被拒绝，并提供该样本的内存对照。它不能支持真实漫画页的图像内容表现、检测质量或真实素材分布结论。因此，本次追认只接受其作为 AC4 的 JPEG 格式拒绝路径部分，不把它表述成真实素材验收。

### 决定

**追认并记 limitation。** AC4 目的在本次收窄后的 Task 中是验证拒绝路径；拒绝判定取决于头部尺寸及像素策略，不依赖 JPEG 图像内容。用合成样本覆盖确实缺少真实样本的 JPEG 格式分支，能够支撑该项有限结论。为了满足该证据目的而补造真实素材会引入新素材/许可问题，且没有必要；若未来要求证明真实超大漫画页可检测，那属于不同目标和新的 Task。

AC4 的终态应记为：**`MET_WITH_LIMITATION`（或仓库允许的等价终态标记）**。限制原文应保留为：

- JPEG 超限拒绝由合成样本验证；没有真实超限 JPEG 可供实测。
- 不证明真实超大漫画页的检测质量；当前超限页面仍被拒绝，真实页检测链未完成。

`doc/tasks/DETECT-TILING-1.md` 中已登记的尺寸、错误文本、拒绝时机、峰值内存及样本 SHA 是该裁定的事实依据。AC4 原文与证据使用范围的调整须由 Codex 在后续 Task 更新中明确记录；本裁定本身不改写 Task 原文。

## 2. 用户会话指令与项目角色

项目规则将验收口径决定权交给 Codex 或用户。用户在本会话明确要求执行者“按推荐自行裁决”，语义上是把推荐选项的选择委托出去；若将它缩减解释为“只是不必提问”，会忽略“自行裁决”的直接含义。用户的明确授权可在该范围内行使其自身决定权，项目规则未禁止用户委托。

因此，执行者选择合成 JPEG 是**在用户授权范围内作出的决定**，并非越权。由于该选择改变了 AC4 原有“真实/既有样本”的证据范围，仍应有 Codex 权威记录，避免 Task 的规范文本与证据口径不一致；本 r36 即为该追认和范围界定。用户授权不能被泛化为对其它 Task、产品范围或共享契约的概括授权。

## 3. AC2 与 `SEC-FMT-005`

`verification/DETECT-TILING-1/ac2-sec-fmt-005-mapping.md` 对四项要求逐项给出证据与结论：①可用物理内存检查 `NOT_IMPLEMENTED`；②分块或限制 `MET`（走限制分支）；③清晰内存警告 `PARTIAL`；④防止 OOM `PARTIAL`。故 AC2 的工作成果是“逐项映射完成”，并非整个 `SEC-FMT-005` 已满足。AC2 的符合性值保留 `PARTIAL`，不得标为 `MET`。

可用物理内存检查与使用固定尺寸限制是并列要求。它在 r35 选择拒绝路线之前就不存在；本次只是将其确认并留下证据，并非本 Task 撤掉了已有实现。因此该缺口应另立 Task，而非永久留作无后续处置的限制。采纳映射文件提出的方向，建议新建 `DETECT-MEMORY-GUARD-1`，先裁定 Windows 可用内存读取方式、接受/拒绝阈值、固定尺寸限制与动态内存条件的优先级、错误/警告语义及测试，再授权实施。

本裁定未创建该 Task，也未授权代码修改；后续 Task 应由 Codex 走完整生命周期，说明它是 `SEC-FMT-005` ① 的承接者，并处理③/④剩余缺口。Task 被创建并获准前，映射中的 `PARTIAL` 是如实的当前状态。

## 4. Task 状态与 limitation 清单

本 Task 当前定义的五个 AC 可按现有交付和证据评价如下：

| AC | 裁定状态 | 依据 / 边界 |
|---|---|---|
| AC1 预解码拒绝与内存证据 | `MET` | 实现、顺序测试及重测记录；ZCode r1/r2 Review 通过。Review 未重跑测试或内存实验，数值仍是提交方实测记录。 |
| AC2 `SEC-FMT-005` 逐项映射 | `PARTIAL` | 映射文件四项清楚区分；①未实现，③/④部分实现。后续独立 Task 承接。 |
| AC3 RGBA 阈值缺陷登记 | `MET_WITH_LIMITATION` | 缺陷已登记；当前阈值未修改。它不证明 RGBA 峰值内存有界，修复/策略变更待单独授权。 |
| AC4 PNG/JPEG 拒绝实测 | `MET_WITH_LIMITATION` | PNG 用真实样本，JPEG 用合成样本；本 r36 追认有限证据用途。缺真实超限 JPEG及真实超大页质量证据。 |
| AC5 回归与独立审查 | `MET` | 交付记录为 36 tests passed；ZCode r1/r2 为非实施者两轮 Review。Review 属只读，未复跑 pytest。 |

据此，**不应进入 `done`**：协作协议规定 `done` 是技术完成，要求所有已释放 AC 通过，而 AC2 仍为 `PARTIAL`。**建议选择 `closed_with_limitations`**，因为用户当前明确请求 Codex 选择终态处置，且以下限制被显式保留，不伪装为 PASS：

1. `SEC-FMT-005` 在此 Task 范围内为 `PARTIAL`：未实现可用物理内存检查；用户提示不是 memory warning，且没有内存量；没有 `core.detect` 层 `MemoryError` 捕获或临近上限的渐进防护。后续 `DETECT-MEMORY-GUARD-1` 应承接。
2. JPEG 拒绝实测使用合成 JPEG；没有真实超限 JPEG。本证据不证明真实漫画页的检测质量；当前超限真实页仍会被拒绝。
3. `MAX_DETECT_PIXELS` 以 RGB24 推导，但源页可为 RGBA。32 MiB 对应的 RGBA 原始像素平面上限为 `8,388,608 px`；当前门槛未修正。AC3 只完成缺陷登记，不能被理解为已解决，也不得把原始平面换算当作解码器峰值保证。
4. 两轮 Review 静态审查通过但未独立重跑 pytest 或重测内存；36 tests 与内存数值按交付证据记录，不能表述成 Reviewer 独立复现。

`closed_with_limitations` 的效力须通过 Task 的正式 closeout 生效：按 `doc/09_COLLABORATION.md` 更新每个 AC 的 lifecycle 标记及 limitation 原状态/分类，核销 Resource Manifest，填写 canonical evidence/resource closeout，更新 STATUS/Plan 导航，并执行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/DETECT-TILING-1.md`。本文件未执行这些权威状态变更，也未检查/处置资源。

## 5. 状态同步观察与建议下一步

读取时 `doc/STATUS.md` 将 `DETECT-TILING-1` 列为 `ready`，`doc/REBASELINE_PLAN.md` 则列为 `in_review`；Task 自身仍含待追认及待 closeout 字段。状态源彼此不一致，不能从本裁定文件推断 Task 已经关闭。应在正式 closeout 中统一权威状态；不得把 Plan 或 STATUS 的旧值当成此 r36 之后的生效终态。

**下一步建议**：由 Codex 在获准的独立 closeout 写入中，将本裁定登记到 Task 的终态处置表，按 `closed_with_limitations` 完成 AC/证据/资源/导航字段并通过指定 TaskPath 的治理检查；随后提议 `DETECT-MEMORY-GUARD-1`，明确①、③、④的验收范围。两者均不授权直接实现内存策略或修改阈值。

## 来源

- `doc/tasks/DETECT-TILING-1.md`（AC、P1-2(d)、终态处置表、样本数据及 SHA）
- `doc/handoffs/DETECT-TILING-1-dsh-stageA-20261020.md`
- `verification/DETECT-TILING-1/dsh-stageA-zcode-review.md`（r1）
- `verification/DETECT-TILING-1/dsh-stageA-zcode-review-r2.md`（r2）
- `verification/DETECT-TILING-1/ac2-sec-fmt-005-mapping.md`
- `verification/DETECT-TILING-1/ac3-threshold-calibre-defect.md`
- `verification/DETECT-TILING-1/stageA-remeasurement-20261020.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-tiling-stage2-r35.md`
- `doc/09_COLLABORATION.md` §§4–5.1（Task lifecycle、`closed_with_limitations`、下一步任务建议）
