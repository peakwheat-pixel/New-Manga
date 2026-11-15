# 目标 C 三项技术债 — 核实报告（2026-11-16）

- 作者：DSH（Lead / Integrator）
- **v2 更正（2026-11-16，本卡 r1 阶段自纠）**：第 3 项的初版结论「可归因闭合 = 0」**用错了口径**。
  本文用的是 <<BLOCKED>> 标记（12 处），但目标 C 指的是
  verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md 的 **72 条 AC 级判定**，
  其中 **RERUN + DOC + IMPL = 41 条判为「可由 Agent 闭合」**。正确数字见 §3 的 v2 节。
- 基线：`1f3bd0d84`
- 范围：只核实目标 C 明文列出的三项债务，给出**可闭合项的实际数量**；不改变任何 Gate

## 三项债务逐项结论

| # | 债务（目标 C 原文） | 结论 | 依据 |
|---|---|---|---|
| 1 | `doc/tasks` 控制字符损坏修复 | ✅ **已清零** | `DOC-CTRLCHAR-FIX-1`（`1f3bd0d84`）：37 文件、TAB 33 处 → `t`、孤立 CR 20 处删除；修复后残留 **0** |
| 2 | `check.ps1` 历史终态卡 AC 豁免 | ✅ **已实现** | `check.ps1:853-854` 的 `$htmlAcStyle` / `$historicalAcExempt`；`09_COLLABORATION.md` §4.3.1 有文档 |
| 3 | AC blocked 项中可归因闭合项 | ⚠️ **实际可闭合数 = 0** | 见下节 |

## 第 3 项：blocked AC 的真实分布

### 统计口径的修正（重要）

历史上这个数字被记为「64」。按 doc/tasks 全量扫描 <<BLOCKED: 得 **16 处**，但其中 **4 处**是**说明文字误匹配**（不是 AC 行）：

- FEA-15-PIN-POLICY-1.md:52 是一句**语法说明文字**（它引用了 <<MET>> / <<PARTIAL: 原因>> / <<BLOCKED: 原因>> 这套标记语法，本身不是 AC 行）；
- 另 3 处为同类引用（卡面或 Closeout 里复述标记语法）。

**复算证据**（verification/GOAL-C-DEBT-AUDIT-1/audit.log）：全量扫 = 16、精确口径 = 12、差异 = 4。

按**精确口径**（行首 `- [ ] **AC` + `<<BLOCKED: …>>`）统计得 **12 处**。

### 12 处的分类

| 卡 | 处数 | 卡状态 | 阻塞原因 | 能否由 Agent 独立闭合 |
|---|---|---|---|---|
| `GOV-PIN-LINEAGE-1` | **6** | `closed_with_limitations` | "r27 撤回原方案、r28 停止改造，本 Task 未实施任何 AC" | **已合规**：历史卡用 `<!-- blocked: … -->` 形式（§4.3.1 豁免），**无需改动** |
| `GIT-CLEAN-CORE-ENV-2` | 3 | `proposed` | V2–V5 具体定义与可用环境尚未给出；未释放、禁止 ACL 写入；环境与窄运行命令待冻结 | **不能**：需先冻结环境定义 |
| `GIT-CLEAN-PUBLICATION-1` | 1 | `in_review` | Core 三组参数失败、旧 icacls 错误码未知 | **不能**：需修测试/环境 |
| `GIT-CLEAN-RUST-ISOLATION-1` | 1 | `in_review` | peak0 未达 32，容量接受/拒绝路径未验证 | **不能**：需性能达标 |
| `REAL-TRANSLATE-PROVIDER-1` | 1 | `done` | **OpenCode 额度耗尽**（free=429 / paid=402），3 页真实 HTTP 429 → typed `PROVIDER_RATE_LIMITED` | **不能**：属**外部账号/额度** ⇒ 应归 **HUMAN-REQUIRED** |

### 结论

**可归因闭合项 = 0。**

- 6 处**已是合规形态**（历史卡 HTML 注释），不需要"闭合"也不需要"修复"；
- 5 处是**真实技术阻塞**（环境冻结 / 测试失败 / 性能未达标），不是文档问题；
- 1 处是**外部账号额度**，按目标 D 应登记为 HUMAN-REQUIRED。

**这是如实结论，不是"清零失败"的借口** —— 目标 C 的这项债务在字面上是「blocked 项中**可归因**闭合项」，
核实结果是**没有可归因于 Agent 的部分**。

## 附带发现：3 个 warning 都不是技术债

`check.ps1` 当前 3 个 warning：

| warning | 性质 |
|---|---|
| 存在 11 个非终态 Task | **正常状态**（有 11 张卡在做），检查器明确说「状态字段不能证明活性，不得据此批量关闭」 |
| `doc/STATUS.md` 已达到预算 80%（3178 bytes / 27 lines） | **容量约束**，不是债；但继续加内容会超预算 |
| `doc/REBASELINE_PLAN.md` 已达到预算 80%（6960 bytes / 63 lines） | 同上 |

⇒ 目标 C 若以「`check.ps1` warning 归零」为判据，会**误把正常状态和容量约束当成债**。
合理的判据是本文第 1、2 项的结论 + 第 3 项的「可闭合=0」。

## 后续建议（不在本报告范围内执行）

1. `REAL-TRANSLATE-PROVIDER-1` 的 AC3 应在 HUMAN-REQUIRED 清单里显式登记（外部账号/额度）；
2. `GIT-CLEAN-*` 三条线（CORE-ENV-2 / PUBLICATION-1 / RUST-ISOLATION-1）需要各自的环境/性能前置，
   应作为独立 Task 释放，不是文档修复；
3. `FEA-15-PIN-POLICY-1:52` 这类**说明文字误匹配**，若希望统计口径干净，可在正则侧加「必须是行首 AC 行」
   的约束（本次已用精确口径复核，未改文件）。


---

## 3-v2. 第 3 项的**正确**口径与数字（本卡自纠）

### 两套口径必须区分

| 口径 | 数字 | 含义 |
|---|---:|---|
| <<BLOCKED: …>> 标记（行首 AC 行） | 12 | **当前卡面**上仍标 blocked 的 AC |
| classification-v2.md AC 级判定 | **72** | 历史一次性全量判定（verification/AC-BLOCKED-CLASSIFY-1/） |

初版本报告只用了第一套口径，因此得出「可归因闭合 = 0」——**这是错的**。

### 72 条的分类（classification-v2.md 实测）

| 分类 | 条数 | 是否 Agent 可闭合 |
|---|---:|---|
| ARCHIVE | 13 | 否（AC 对象在当前架构不存在） |
| WITHDRAWN | 9 | 否（方案撤回） |
| RERUN | 10 | **是** |
| DOC | 9 | **是** |
| IMPL | 22 | **是** |
| MECHANISM_NA | 4 | 否（要求本身不适用） |
| HUMAN | 5 | 否（见 HUMAN-REQUIRED 清单） |
| **合计** | **72** | — |

⇒ **可由 Agent 闭合 = RERUN + DOC + IMPL = 41 条。**

### 这 41 条现在的状态

41 条分布在 **19 张卡**，且**全部位于已终态卡内**：

| 卡状态 | 条数 |
|---|---:|
| done | 38 |
| closed_with_limitations | 3 |
| 非终态卡 | **0** |

涉及卡（按条数降序）：FEA-04 8、TASK-056 5、V11R-B-5 4、MICA-FIX-1 3、
GATE3-COVERAGE-MATRIX 3、V11R-B-4 2、FEA-07-AC5-NATIVE-1 2、
GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 2、M2-REGION-RETYPE-CORE 2，其余 10 张各 1 条。

### 为什么它们没被 check.ps1 报错

正是**目标 C 第 2 项**的机制：$historicalAcExempt（check.ps1:853-854）对历史终态卡
的未勾 AC 予以豁免。⇒ 第 2 项与第 3 项是**耦合**的：豁免让这些 AC 不进 gate，但它们仍**未闭合**。

### 结论（更正后）

- 第 3 项的**真实数字是 41 条**，不是 0；
- 这 41 条**全部在终态卡内**，因此不会被 check.ps1 拦住，也不会阻塞任何 gate；
- 它们是否**仍需实施**，需逐条判断（有些可能是历史架构的 live gap，如 FEA-04 的 8 条
  「范围冻结完成、实现未开始」；有些可能已被后续工作覆盖，如 V11R-D-1 AC8 的旧样式退役）；
- **本报告不宣称这 41 条已闭合**，也不宣布可全部豁免 —— 需要一张专门的卡逐条处置。
---

## 3-v3. 控制字符修复的范围更正（本卡自纠，重要）

`DOC-CTRLCHAR-FIX-1` 的结论写「`doc/tasks` 控制字符已清零」—— 该结论**只对 `doc/tasks` 成立**。
本轮扫全 `doc/**` 后发现**其它目录仍有控制字符**：

| 文件 | TAB | VT | 孤立CR |
|---|---:|---:|---:|
| `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` | 7 | 4 | 4 |
| `doc/handoffs/CORE-TILE-EMIT-1-handoff.md` | 1 | 2 | 1 |
| `doc/handoffs/DSH-HANDOFF-2026-11-06.md` | 1 | 1 | 0 |
| `doc/handoffs/FEA-04-68c72ba57.md` | 0 | 0 | 1 |
| `doc/handoffs/FEA-09-995d80ca5.md` | 0 | 2 | 2 |
| `doc/handoffs/GOV-EOL-PIN-1-d19e74ab4.md` | 6 | 0 | 0 |
| `doc/handoffs/HOST-RESOURCE-SECURITY-1-handoff.md` | 0 | 1 | 0 |
| `doc/handoffs/M2-C1-zcode-7de1cd2.md` | 7 | 0 | 0 |
| `doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md` | 1 | 0 | 0 |
| `doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md` | 0 | 0 | 1 |
| `doc/plan/FEA-CONTRACT-FROZEN-C09.md` | 0 | 1 | 0 |
| `doc/PUSH_RECORD_2026-10-25.md` | 2 | 0 | 0 |
| `doc/reviews/FEA-06-RESIDUAL-4A-r2.md` | 5 | 0 | 0 |
| `doc/reviews/FEA-11-HOST-AUTH-4-scope-r1.md` | 0 | 1 | 0 |
| `doc/reviews/MAINT-2-C1-BATCH-1-r1.md` | 2 | 0 | 0 |
| `doc/WORKTREE_SAFETY_INVENTORY.md` | 2 | 0 | 0 |

### 为什么没有顺手批量修

抽样后发现 **TAB 的性质在 `doc/` 其它文件里是混合的**：

| 例子 | TAB 的性质 | 能否直接替换 |
|---|---|---|
| `PUSH_RECORD_2026-10-25.md`：`032bb5ad1cf148<TAB>refs/heads/code` | **表格分隔符**（有意义） | ❌ 换成 `t` 会破坏格式 |
| `WORKTREE_SAFETY_INVENTORY.md`：`分支 <TAB>ask/THEME-MACOS` | **被吃掉的 `t`**（`task/`） | ✅ 需还原为 `t` |

⇒ 必须**逐处判断**，不能批量替换。本卡**手工修复 `doc/tasks` 已修**（那批 33 处已逐处确认全是 `t`），
但 `doc/` 其它目录的这批**未修**。

### VT（垂直制表符）的由来

本次核实期间，我自己用 Python 写入报告时，字符串里的 `\v` 被解释成**垂直制表符**，
导致 `verification` 变成 `erification`（3 处，已当场修复）。
⇒ 这解释了历史上 `doc/` 里 VT 的可能来源：**同样的转义事故**。

### 更正后的结论

- 目标 C 第 1 项应表述为：「`doc/tasks/**` 控制字符已清零；`doc/` 其它目录**仍有**控制字符，未修」；
- 这份残余**不阻塞任何 gate**（`check.ps1` 不扫控制字符），属**文档卫生**问题；
- 若要彻底清零，需要一张专门的卡逐处判断（约 16 个文件）。

- 若要彻底清零，需要一张专门的卡逐处判断（约 16 个文件）。

### 硬约束：其中一个文件是 pin 目标

doc/plan/FEA-CONTRACT-FROZEN-C09.md（VT=1）**在 erify_pins 的校验清单内**。
修改它会**直接破坏 pin 审计**（18/18 → 17/18），因此：

- 该文件的控制字符**不得**在未见专门裁决的情况下修改；
- 若要修，必须同时用 git commit 的新 blob 重新锚定 pin，并重跑 erify_pins；
- 本卡**未改任何 doc/plan/** 文件**，erify_pins 仍 18/18。
