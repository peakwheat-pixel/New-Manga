---
task_id: FEA-06-PREREQ-2
reviewer: ZCode（主会话）
reviewer_kind: agent
author: dsh-lead
base_commit: cad5ebde3（卡声明）
reviewed_head: a33778608
decision: approved
counts: { P0: 0, P1: 0, P2: 0 }
---

# FEA-06-PREREQ-2 范围冻结复核 r4（独立上下文；本席位未参与本卡起草/实现）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-2.md`（`proposed`；`approval: pending_review`） |
| reviewed_head | `a33778608`（`docs(handoff): 更新交接材料中的 scope-r3 结果与下一步（r4）`）；`git status --short` 干净；处置 commit 为其父 `a6652022d`（r3 head `df089039c` → 本 head 共 3 commits，仅治理/卡面文档） |
| 审查范围 | **窄面确认**（r3 报告 §4.2 指定）：只核上轮唯一 P1（R3-P1-1）是否闭合 + 指定随修项 R3-P2-3 + 是否引入新问题；r1–r3 已闭合项不重开，其余 P2 只记延续状态 |
| reviewer | **ZCode（主会话）**，DSH 派发（2026-10-31 上下文独立裁决：产出变更的会话不得自审）；未参与 FEA-06-PREREQ-2 的起草、r1–r3 处置修订与任何实现 |
| 日期 | 2026-11-02（被审 head 提交后同日） |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 0** |

> **一句话结论**：上轮唯一阻塞项 R3-P1-1 **实质闭合**——禁止范围（卡 `:79`）原「新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围」的授权残留已删除，改写为与 P6「明确不新增枚举值」、W-11「枚举与签名不变，无需 UNFREEZE」及 C-02 V-07 审查判据完全一致的禁止表述；随修项 R3-P2-3 的 R14 计数措辞已改为「59 不变 / 65 → 67」；STATUS/PLAN 指针（R3-P2-5）已刷新为「待 r4」。卡面 diff 仅此两处、无暗改，禁止范围与 P5/P6/P7 授权边界无新自相矛盾，治理脚本双 PASS、C-02 冻结字节未被触碰。**范围冻结通过、可置 ready 实施。**

---

## 0. 方法与只读声明

- 只读核查被审 head `a33778608`；未修改卡/代码/设计/契约；未 commit/push；本报告为本轮唯一新增文件（落盘于本卡写域 `doc/reviews/FEA-06-PREREQ-2-*.md`）。
- 本轮实测：`check.ps1` → **PASS（3 warnings：10 非终态、STATUS 3028B/29 行 80%、PLAN 3941B/62 行 80%，与 r3 同源无新增；PLAN 字节数微变系指针文字更新所致）**；`verify_pins.ps1` → **PASS（all 15）**，C-02 冻结字节（`bb365ca891a7`）未被触碰——与 W-11「无需 UNFREEZE」的现状一致。
- 阅读：r3 报告全文；本卡全文（行号实测于 `a33778608`）；`df089039c..a33778608` 全量 diff（6 文件、+216/−6）；C-02 修订单 V-07（`:86-91`）与 §5 汇总行（`:125`）；STATUS `:7`/PLAN `:22,:37` 指针；`ThemeMaterial`/`W-9`/枚举关键词全卡检索。

---

## 1. 指定核查项逐项 disposition

### R3-P1-1（禁止范围与 P6/W-11 矛盾）—— **CLOSED**

**旧文**（`df089039c` 卡 `:79`，本轮 `git show` 实证）：

> 不改 ThemeEngine 的既有主题包语义（`newmanga-default` 字节不变；新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围）

**新文**（`a33778608` 卡 `:79`）：

> 不改 ThemeEngine 的既有主题包语义（`newmanga-default` 字节不变；**不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 构造器签名**——Material 走主题层令牌，见 P6/W-11）

**判定依据**：
1. **矛盾源已删除**：原括号子句是 r2 版 P6（加枚举值路径）的配套授权声明，已整句消失，不再是「许可 vs 禁止」冲突。
2. **三处口径一致**：新文本与 P6（`:65`「**明确不新增** `ThemeMaterial` 枚举值、**不改** `ThemeTokenSet` 构造器签名…**不需要契约 UNFREEZE**」）、W-11（`:90`「`ThemeMaterial` 枚举与 `ThemeTokenSet` 签名**不变**，故**无需 UNFREEZE**；若后续确需改公开面，须先出 UNFREEZE 记录再改」）措辞同向，且以「见 P6/W-11」显式交叉引用。
3. **与冻结契约判据对齐**：C-02 V-07 审查判据「`ThemeKind` 枚举值与公开方法签名不得变化」（修订单 `:90`）及 §5 汇总「以本修订单 V-07 为准：**不新增枚举值**」（`:125`）——`ThemeMaterial`/`ThemeTokenSet` 均属 ThemeEngine §4 公开面，新文本与之零冲突。`verify_pins` 15/15 佐证 C-02 冻结字节自 r3 以来无人触碰。
4. **残留扫描**：全卡检索 `ThemeMaterial` 共 4 处（`:65` P6 禁止、`:79` 禁止范围禁止、`:90` W-11 不变、`:63` P5 sink 行不含枚举语义），`W-9` 出现处（`:63/:65/:73/:74`）均为承接标签，**无任何残留表述会诱导实现者新增枚举值**。

### R3-P2-3（R14 计数措辞）—— **CLOSED**

- 旧文：「`R14ContractTests` 的 59/65 计数随主题层键面 +2 同步」（可误读为两计数各 +2）。
- 新文（`:65` 末段）：「`R14ContractTests` 的计数：**59 不变**（全局令牌数不增），**65 → 67**（主题层可覆写键面 +2，即 `Nm.Material.Acrylic.Base/.Tint`）」。
- 与 r3 建议的「59 不变、65→67」完全一致（Base/Tint 只进 `ThemeLayerAllowedKeys` 可选键面、不进 Required 59），且新增了 +2 的键名归属与「全局令牌数不增」的限定，消除了原误读空间。

---

## 2. 新问题扫描（本轮指定：是否引入新自相矛盾或新 P0/P1）

- **暗改检查**：`df089039c..a33778608` 的卡面 diff **仅两处**（`:65` 计数措辞、`:79` 禁止范围），即 R3-P1-1 + R3-P2-3 本身；其余章节（P1–P7、AC1–AC7、W-1…W-11、测试要求表 `:94-100` 五行、allowed_paths、frontmatter）逐行比对无变化。
- **禁止范围 vs P5/P6/P7 授权边界**：新禁止文本的括号内容是对「主题包语义不变」的操作化界定，「Material 走主题层令牌，见 P6/W-11」把 Material 的实现路径显式指向 P6 授权的主题层令牌方案，禁止（公开面）与授权（令牌路径）不再交叠——P5（迁移/双写/sink）、P6（`NmKeys` 常量 + `ThemeLayerAllowedKeys` + 主题包 colors）、P7（fluent-dark 的 `metadata.extra` manifest 条目，`newmanga-default` 字节不变）均可在此边界内无歧义实施。**未发现新的自相矛盾**。
- **变更范围核查**：r3 head → 本 head 共 6 文件——卡（写域内）、r3 报告（写域 `doc/reviews/FEA-06-PREREQ-2-*.md` 内）、STATUS/PLAN（写域内）、`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（§8 进度记录）与 `doc/handoffs/FEA-06-PREREQ-2-session-handoff.md`（新增跨会话交接材料）。后两文件不在本卡 allowed_paths，但属 DSH 治理职权范围内的治理/交接文档（r3 报告 R2-P2-4 亦将 checkpoint 补录视为正确处置，未记越域），沿先例口径不列为 finding，在此如实登记。
- **R3-P2-5（STATUS/PLAN 指针）**：STATUS `:7`「r4 待」、PLAN `:22`「scope-r3 P1×1 已修，待 r4」、PLAN `:37` DAG「待 r4」——与本报告落盘前的事实一致（r4 在途）；该指针随 r4 收口（本报告 approved）再滚动一次即可，非阻塞。

**结论：无新 P0/P1/P2。**

---

## 3. 治理脚本

- `check.ps1` → **PASS**（3 warnings 与 r3 同源：10 非终态 Task、STATUS/PLAN 预算 80% 档；无新增、非本卡阻塞）。
- `verify_pins.ps1` → **PASS（all 15）**：C-01b…C-14 + FEA-01 全部 OK，C-02 冻结字节未动。

---

## 4. 上轮 P2 延续状态（不重开，仅记录）

| ID | r4 状态 | 说明 |
|---|---|---|
| R3-P2-1（P5 sink 传入形态/AC5 工程列举） | OPEN（接受遗留） | P5/AC5 文字未再动；AC4 全量兜底 |
| R3-P2-2（P7/AC7 Validate 语义定界） | OPEN（接受遗留） | 隐式锁定「不改 `ThemeValidator`、只加测试」的最小路径 |
| R3-P2-4（PREREQ-1 卡 `:133` 声明行漂移） | OPEN（接受遗留） | 无事实错误，仅声明行时点快照 |
| R3-P2-5（STATUS/PLAN 指针） | **已处置** | 本 head 已刷新为「待 r4」（§2）；收口时再滚为终态 |
| R2-P2-6（base_commit 刷新） | OPEN（按计划留 release） | 届时刷新为当刻 main head |

---

## 5. 结论

**P0 = 0 / P1 = 0 / P2 = 0 → `approved`。范围冻结通过、可置 ready 实施。**

处置建议：DSH 按 [协作协议 §5.1](../09_COLLABORATION.md) 执行 release 动作——置 `ready`、刷新 `base_commit` 为当刻 main head（R2-P2-6）、STATUS/PLAN 指针滚为「scope-r4 approved / ready」，随后释放实现（`suggested_owner: dsh`）。

## 6. 边界声明

本报告只审**范围/卡面/冻结契约一致性/治理指针**（窄面：R3-P1-1、R3-P2-3 与新引入问题），不实现本卡，不审 PREREQ-2 未来代码；r1–r3 已闭合项与接受遗留的 P2 不重开。对 P6 主题层令牌路径的认可以 C-02 V-07 判据核对为限，不构成对 FEA-06 视觉例外的集成授权（V-05 的 per-scheme 例外仍由其自身判据约束）。`check.ps1`/`verify_pins.ps1` 为只读参考，不替代审查。未修改源码/卡/设计/契约，未 commit/push；行号基于 `a33778608` 实测。
