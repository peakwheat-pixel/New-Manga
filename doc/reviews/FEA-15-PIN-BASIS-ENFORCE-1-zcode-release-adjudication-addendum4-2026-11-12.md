---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode 原始释放 Integrator 会话（主裁决及 Addendum 1–3 同源）
session_id: sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58
turn_id: turn_391d1a6b-6e08-4bba-b0b8-f80f32a68e0d
reviewed_head: bdbc58b541341f3059f5ff8f37017a45cb46b245
decision: ACCEPT_ONE_TIME_BASELINE_TRANSITION
---

# 释放 Addendum 4：一次性基线转接与停止门解除

2026-11-12，原始释放会话对 [AC1 停止条件独立裁决](FEA-15-PIN-BASIS-ENFORCE-1-ac1-delta-stop-adjudication-2026-11-12.md)（`ADJUDICATION_STOP`，session `sess_e951752d-de8c-4afe-aee2-964d2bc47ecb`）作出处置。结论：**接受一次性基线转接（ACCEPT）**。正式 delta `+62 / -0 / CHANGED=2` 按独立报告归因冻结为已解释衔接；程序性 STOP 解除；AC1c 恢复执行。本 Addendum 不授权任何实现提交、不改写任何历史文件、不关闭 R-001。

## 1. 裁决身份与输入

- 裁决者为主裁决及 Addendum 1/2/3 的同一原始释放会话，未参与实现；独立 STOP 裁决由未参与本 Task 的 fresh ZCode 会话出具，两者满足上下文独立。
- 输入：主裁决与 Addendum 1–3（已入库）、Task 卡（`blocked`，证据 commit `411309ca…`）、verification README、正式 delta JSON 全文、独立 STOP 裁决报告。主仓 HEAD `bdbc58b541341f3059f5ff8f37017a45cb46b245` 由 Owner 提供；本会话 plan mode 未运行 Git，未做 rev-parse 级核验，依文件级证据裁决。
- 本会话独立核验：2df 工作树中 `FEA-15-PIN-POLICY-1` 卡 Canonical Evidence 表头已为纯 `class`、`release-gates` 行 `ac_gate` 现值为 `AC3 release gates`、两行 `pin_sha256`（`3912a32c…`、`18258a64…`）与 delta after 值一致；`pin-basis-impact-plan.md` §2 预登记了 parser 对带括号表头不捕获的 limitation（即 before 侧 class 为空的文档成因）；四个关键历史文件工作树 SHA 与 PIN-POLICY-1 卡 pin 对账一致（本会话前轮亲测）。采信：`d26c43c76576b0f514530874fc9cb04f016674e6` diff 归因与三生成器跨 HEAD blob 一致性（独立裁决 git 交叉核对）；A clone 测量前 clean（测量日志与 inventory 环境字段）。

## 2. 事实认定

1. Reproduction anchor `EXIT=0`，输出与历史 `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323` 逐字节一致——生成器、输入与环境复现链完好。
2. `CHANGED=2` 两行均为 `FEA-15-PIN-POLICY-1` 卡既有行：`release-adjudication`（class `""`→`CANONICAL`）与 `release-gates`（class `""`→`CANONICAL`、`ac_gate` `AC3 release baseline`→`AC3 release gates`）。两行 identity 与 `pin_sha256` 均不变。成因：`d26c43c…`（PIN-POLICY-1 收口 pinbackfill）将表头 `class (CANONICAL / SOURCE_PIN)` 改为 `class`，使冻结解析器从误读为空变为正确读取；同 commit 修订了 `release-gates` 的 `ac_gate` 措辞。该 commit 是已入库的前序收口操作，非本 Task 期间未授权改动。
3. `ADDED=62` 归因闭合：`FEA-15-PIN-POLICY-1` 31、`GOV-CHECKER-NOTASK-1` 18、`GOV-REFINCIDENT-1` 13；`REMOVED=0`。
4. 补充披露（本 Addendum 新增）：delta 的 `basis_count_delta` 大幅漂移（`WORKTREE -330`、`MIXED -382`、`BLOB +422`、`UNRESOLVED_COMMIT +271`、`INCONSISTENT +81`）远超 62 新行的贡献，成因是 A clone 为 fresh checkout、其工作区 EOL 字节与 e9f 开发主树不同，导致既有行在 `MIXED/WORKTREE` 与 `BLOB/UNRESOLVED_COMMIT/INCONSISTENT` 间重分类。该漂移是环境敏感的观察量摆动，`UNPINNED=293` 等与 worktree 无关的类别零变化佐证此解释；不构成历史行变化，亦不构成损坏证据。**`basis` 字段不得用于任何跨环境不变性断言。**

## 3. 裁定一：基线层级

- `e9f7bb1b…` 的 5,376 行 inventory（入库 `pin-inventory.json`）为不可改写历史快照，仅作历史对照锚，永不更新。
- 本 Task 在固定 `2df8db7a4d19b591e919ecc6e8f8651167800ef0` A clone 复测的 `pin-inventory-2df8db7.json`（5,438 行，SHA-256 `3c6e39a2…`）冻结为本 Task **唯一后续历史不变性基线**。Task 卡 frontmatter `base_commit d8b9b208…` 是实现分支基点，与 A clone 历史基线 `2df8db7…` 并存不混用。

## 4. 裁定二：history transition ledger

本次 `+62 / -0 / CHANGED=2` 整体冻结为**一次性衔接**，Owner 须在 `verification/FEA-15-PIN-BASIS-ENFORCE-1/history-transition-ledger.md`（允许集内新文件）登记下表，且 Addendum 与后续证据引用时**必须原样保留 `CHANGED=2`，不得表述为 0、无变化或「已修复」**：

| identity | 变化字段 | pin_sha256 | 归因 commit | 性质 |
|---|---|---|---|---|
| PIN-POLICY-1 / release-adjudication / doc/reviews/…release-adjudication…md / 0730335f | class `""`→CANONICAL | 3912a32c…（不变） | d26c43c… | 表头纯化后解析器开始正确读取 |
| PIN-POLICY-1 / release-gates / verification/…release-gates-0730335.log / be4efb39 | class `""`→CANONICAL；ac_gate 措辞 | 18258a64…（不变） | d26c43c… | 同上＋同 commit 直接修订措辞 |

此后一切 post 对比（5,438 快照 vs post-implementation inventory）：**历史行硬不变性 = identity 逐行在场（deleted=0）、pin_sha256 逐行不变、changed=0（delta 工具四字段口径）**；本 Task 自证新行单列增量层，不混入历史断言。若出现任何 `changed>0` 或 `deleted>0`：即使 pin_sha256 不变，也须停止并交 ZCode 按本 Addendum 同等标准逐项归因裁断，不得自动放行。`basis`/`basis_counts` 不参与断言（§2.4）。

## 5. 裁定三：停止门解除与 AC1c 恢复

程序性 STOP 即时解除。恢复范围为 AC1c 的 A 侧（A clone @ `2df8db7…`，未变更 checker）：default（预期锚=GOV-REFINCIDENT-1 clean 终态同文案先例）、四个代表历史 TaskPath（AGPL-RELEASE-1 / AD002-FOLLOWUPS-1 / FEA-06-PREREQ-1 / CHAPTER-SELECTOR-1）、18 pins、API、固定边界样本矩阵；命令与口径沿用 `delivery-gates-359d09d.log` 登记集；逐项记录 HEAD/clean/环境/EXIT。

**R0 重新冻结点（对 Addendum 3 的精确化）**：R0 = 本 Addendum 落盘、Task 卡状态恢复（`blocked→in_progress`、AC1 引用更新）及 STATUS 当前指针、Plan 节点确认在场一并提交并入 main 后的 HEAD。B clone 仅在 R0 执行本 Task TaskPath，执行前完成：Task 卡/STATUS 指针/Plan 节点文件级在场断言；`R0..2df8db7` 反向差异全落在释放允许增量集；`tools/governance/**` 与 `doc/templates/**` 逐文件 blob 同一（不得只比 check.ps1）；clean 断言与环境记录。B 不跑 inventory/delta/repro、不写仓内路径。历史 TaskPath 与样本矩阵不得在 B 重复充当基线，也不得在 A 跑本卡 TaskPath（不存在即 N/A，禁止 PASS 化）。

## 6. 裁定四：AC1d 与实现禁令

AC1c A 侧与 B 侧全部实际执行且 EXIT 与预期锚相符后，由**未参与实现、且不同于最终 Review 会话**的 fresh ZCode 会话完成 AC1d 基线确认（输入含：repro anchor、正式 inventory/delta、history transition ledger、A 侧 gates、B 侧 R0 断言与 TaskPath 结果）。**AC1d 通过前禁止任何模板/checker/test 实现提交。** 后续 candidate clone post-change 对照以 R0 为基点；AC4 双 autocrlf 对照与两层断言口径不变。

## 7. 裁定五：长路径裁量与披露义务

A clone 的 clone-local `core.longpaths=true` 被允许：仅改 clone 本地 config，不改变任何 commit/tree/blob、不触碰 `.gitattributes`，不使基线无效。完整记录该配置于全部相关 run log 与 README。保留两项限制并如实登记：首次 checkout 失败的子命令 EXIT 未单独捕获（不呈现为 PASS）；独立裁决时无法读取 A clone 当前 porcelain——AC1c 恢复执行时须补测 `git status --porcelain` 并连同 `core.longpaths` 一并记录。A clone 按清单 `PRESERVE_REFERENCED` 保留。

## 8. 不变式与停止条件（全集重申）

18 frozen pins、`verify_pins.ps1`、历史 Task/Review/Handoff/checkpoint/evidence/pin 字节、`.gitattributes`、renormalize 及 dry-run、冻结契约/Schema/API/产品源码/依赖、`task_ledger.py` 不变；禁止资源清理、gc/prune/repack、push、提权。停止条件：post 对比出现 deleted/changed/无法归因新增；新旧表头不可区分；旧行 checker 判定变化；外部或 EOL 行为异常；`R0..2df8db7` 差异出允许集或治理工具/模板 blob 不一致；B 载体文件级不在场；任何冻结禁区被触及。命中即停、保留现场、交 ZCode 再裁决。R-001 不因本 Addendum 或后续实现自动关闭，仍待最终 Integrator 显式裁定。

## 9. Owner 落盘动作

1. 本文件落盘（`doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md`），回填 turn_id。
2. Task 卡：`blocked→in_progress`，移除 blocked_reason，AC1 更新为引用本 Addendum 的 PARTIAL（已完成 AC1a/衔接冻结；AC1c 恢复执行中），Rolling Checkpoint 追加本裁定。
3. 新建 `verification/FEA-15-PIN-BASIS-ENFORCE-1/history-transition-ledger.md` 登记衔接表。
4. 恢复执行 AC1c A 侧 → 提交证据并 pinbackfill → 冻结 R0（§5 定义）→ B 侧执行 → 报 AC1d。STATUS/Plan 预算纪律不变。
