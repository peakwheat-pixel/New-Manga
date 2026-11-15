# 目标 C 三项技术债 — 核实报告（2026-11-16）

- 作者：DSH（Lead / Integrator）
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

**复算证据**（erification/GOAL-C-DEBT-AUDIT-1/audit.log）：全量扫 = 16、精确口径 = 12、差异 = 4。

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
