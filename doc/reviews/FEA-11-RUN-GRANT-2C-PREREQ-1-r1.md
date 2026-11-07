---
task: FEA-11-RUN-GRANT-2C-PREREQ-1
title: C-06 v1.3 + C-16 v1.6 UNFREEZE 独立 byte-level 复核 r1（mid-run 重复建立；2 pins）
reviewer: DSH fresh subagent（独立上下文；未参与本 UNFREEZE 起草/前轮复核；只读被审字节）
session: f54a7234-2633-410d-8f89-e95298e54e00
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: fresh_subagent_byte_level
date: 2026-11-07
repo: 'G:\CODEX\New Manga'
branch: main
reviewed_head: c1e19ed82dc89a0e42af5e27d9803434794586f1
verdict: changes_requested
---

# FEA-11-RUN-GRANT-2C-PREREQ-1 独立 byte-level 复核 r1

## 结论先行

- **verdict：`changes_requested`**（P0=0 / P1=0 / P2=4 / P3=8）。
- **安全语义实质成立**：v1.3/v1.6 追加句在语义上覆盖「每次新铸新 grant、各自 ≤300s、按当时 facts 重验；不延长既有 `expires_at`、不扩 scope、不撤销后重建、不改选 command/scope、任一页不可授权整请求 typed 拒绝零映射写入」；≤300s 与「不得长期通行证」两锚原文未改；契约字节**未**引入「自动重新授权/恢复入口/长期通行证」语义。**无 P0/P1**。
- **阻断项全部是记录/证据/卡的一致性缺陷，不是契约条款放宽**：①FROZEN-C16 §2 条件行 7 被静默瘦身（删去 `P0=0/P1=0/P2=0/P3=0` 与证据列）、行 8 变成 5 列且把 v1.5 的载体/证据误挂到 v1.6；②载体 §7、卡 I-5 与复核要求引用的 `verification/FEA-11-RUN-GRANT-2C-PREREQ-1/other-16-pins.txt` **不存在**；③卡 I-2/AC-T1 称 C-06「§5 零改动 / 只含 §2.2 一句 + 头部」，但 §5 `:88` 实际新增条件 ⑥（载体 §2.A 已登记）——AC-T1 按字面不可判为 MET。
- **实测 pin 全部正确且可复算**：C-06 `sha256=8cb153d5…`、`git hash-object=9f6bb0e6…`；C-16 `sha256=b8f46fb1…`、`git hash-object=f8f31f55…`；`verify_pins` **18/18 PASS**（重跑）；`check.ps1` 默认 + `-TaskPath` 均 PASS（3 warnings）。
- **diff 面正确**：`git diff --name-only HEAD` 仅 5 个 plan 文件 + 2 个未跟踪路径（载体、证据目录）；C-06/C-16 各 4 个 hunk，与载体 §2.A/§2.B 一一对应；`src/**`、`apps/**`、`tests/**`、`doc/contracts/**` 零改动。
- **P2 修复不改变契约字节**（pin 不变）；P3 中若采纳 R1-005/R1-006 的契约措辞增补，将再次改字节，必须重算 2 pins + delta 复核（见 Verdict 节）。

## 0. 复核快照与方法

| 项 | 实测值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| HEAD | `c1e19ed82dc89a0e42af5e27d9803434794586f1` |
| 工作树状态 | 5 modified（C-06、C-16、FROZEN-C06、FROZEN-C16、矩阵）+ 2 untracked（载体、`verification/FEA-11-RUN-GRANT-2C-PREREQ-1/**`）；本报告写入后新增 1 个 untracked（本文件） |
| 事实来源 | 工作树**最终字节**（未提交 UNFREEZE 包）；历史对比用 `HEAD` 字节 |
| 读取方式 | 只读；未改被审字节/证据/卡/冻结记录；未 `git add/commit/push` |
| 写入 | 仅本文件 `doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r1.md` |

实际执行：`git status/rev-parse/diff/show/hash-object`、`verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、逐文件 `sha256`、`changed-lines.diff` 与实时 `git diff` 的逐字节比较、HEAD blob 的 byte-exact 抽取、16 项不变 pin 抽查（8 项）。

## A. diff 最小性 —— **FAIL（部分）**

**PASS 部分**

| 检查 | 结果 | 证据 |
|---|---|---|
| 文件集只含 C-06/C-16/FROZEN×2/矩阵/载体/证据 | PASS | `git diff --name-only HEAD` = 上述 5 个 plan 文件；`git ls-files --others` = 载体 + `verification/FEA-11-RUN-GRANT-2C-PREREQ-1/**`（7 文件） |
| 无 `src/**`、`apps/**`、`tests/**`、`doc/contracts/**` 改动 | PASS | 同上；`git status --porcelain doc/contracts` 为空；M2-C1 零 diff |
| C-06 改动逐行对应载体 §2.A | PASS（内容面） | 4 hunk：头部 `:3-4`、§2.2 `:43`、§5 `:88`、§6 `:97`；对应载体 `:16-18` |
| C-16 改动逐行对应载体 §2.B | PASS（内容面） | 4 hunk：头部 `:3-4`、§2.4 `:78`、§10 `:244`、记录 `:254`；对应载体 `:21-23` |
| 无未登记改动（契约本体） | PASS | C-06/C-16 的 hunk 之外无 diff；`git diff --numstat`：C-06 5/4、C-16 5/4 |

**FAIL 部分（P2）**

- **FROZEN-C16 §2 条件表被未登记改写**：`HEAD` 行 7 为 `… r8 approved（P0=0/P1=0/P2=0/P3=0）… | ✅ | 载体 CONTRACT-UNFREEZE-2026-11-07-C16-V15.md §6；verification/FEA-11-L-S4-B-PREREQ-1/logs/pins.log |`；工作树行 7（`:50`）只剩 3 列并删去严重度与证据，原证据被误移入新行 8（`:51`）的第 5 列。载体 §2.C（`:26`）只登记「pin/版本/历史 pin/矩阵」，未登记该行改写。→ **R1-001、R1-002**。
- 其余：C-06 §5 `:88` 的 ⑥ 虽在载体 §2.A 登记，却与卡 I-2/AC-T1 的「§5 零改动」冲突（见 F/R1-004）。

## B. 安全语义审查（重点）—— **PASS（实质）；逐字措辞有差（P3）**

### B1 追加句实际字节

- **C-06 §2.2 `:43`（v1.3 追加）**：`Run 非终态期间，Host 可对同一冻结 {command, scope} 重复执行该建立——每次必须重新铸造新 grant（各自 ≤300s、按当时 facts 顺序重新核验）；不得延长既有 grant 的 expires_at、不得扩大 scope、不得在撤销后重建、不得改选 command/scope；任一页不可授权仍整请求 typed 拒绝、零映射写入。`
- **C-16 §2.4 `:78`（v1.6 追加）**：`可在该 Run 非终态期间对同一 {command, scope} 重复调用——每次只绑定当次 live grants；不延长任何 TTL、不改 scope、不绕过撤销；任一页不可授权仍整请求 typed 拒绝、零映射写入。`

### B2 必含子句逐项

| 子句 | C-06 字节 | C-16 字节 | 判定 |
|---|---|---|---|
| 每次新铸新 grant | 「每次必须**重新铸造新 grant**」 | 「每次只绑定**当次 live grants**」 | ✅ 实质 |
| 各自 ≤300s | 「各自 ≤300s」 | 「不延长任何 TTL」（新 grant 的 TTL 由 mint/§2.2 约束） | ✅ 实质 |
| 顺序重验 facts | 「按当时 facts 顺序重新核验」 | 「当次 live grants」+ §2.4 per-page facts（`:90`）不变 | ✅ 实质 |
| 不延长既有 `expires_at` | 「不得延长既有 grant 的 `expires_at`」 | 「不延长任何 TTL」；`:91` 仍「不延长 TTL」 | ✅ 逐字命中 C-06 |
| 不扩 scope | 「不得扩大 scope」 | 「不改 scope」 | ✅ 实质 |
| 不撤销后重建 | 「不得在撤销后重建」 | 「不绕过撤销」 | ✅ 实质 |
| 不改选 command/scope | 「不得改选 command/scope」 | 绑定对象固定为同一 `{command, scope}` | ✅ 实质 |
| 任一页不可授权整请求 typed 拒绝、零映射 | 「仍**整请求 typed 拒绝、零映射写入**」 | 「仍整请求 typed 拒绝、**零映射写入**」 | ✅ 实质 |
| 不构成自动重新授权/恢复入口/长期通行证 | 无该语义 | 无该语义 | ✅（grep 仅见既有否定句与 §2.5 红线） |

**P3（R1-006）**：复核要求/AC-T2 写的「每次新铸新 grant」「不扩 scope」「不撤销后重建」「任一页不可授权整请求…」在字节里分别写作「重新铸造新 grant」「不得扩大 scope」「不得在撤销后重建」「任一页不可授权**仍**整请求…」——语义等价且部分更严，**无放宽**；但按「逐字」口径不成立，需对齐措辞或把 AC-T2 改为语义等价判定。

### B3 三锚

| 锚 | 状态 | 证据 |
|---|---|---|
| dispatch 前 | **锚句原文保留**，但新窗口与首句的时态关系未显式调和 → P3（R1-005） | C-06 `:37/:43/:56`「dispatch 前」；C-16 `:19/:22/:78`「Run dispatch 前」；追加句允许「Run 非终态期间」重复建立（按定义在 Run dispatch 之后）。scope-r1 结论 `:20-24` 与 §1.1 明确以 dispatch 为窗口锚，并警告 0-pin 会把该锚降级为叙述文字 |
| ≤300s | **保留** | C-06 `:40`「≤300 秒」、`:43`「各自 ≤300s」；C-16 `:78`「不延长任何 TTL」；`:91`「不延长 TTL」；Host `SourceReadCoordinator.cs:586` `_clock()+300` 未动 |
| 不得长期通行证 | **保留** | C-06 `:40`「**不得**作为长期通行证复用」未改；无任何「长期/永久」授权措辞 |

### B4 安全性结论

- 每次续期 = **新 grant + 新一次 `AuthorizeSourceReadForRun`**；mint 内部重走 `Registry.Authorize`+facts（撤销/漂移/根替换 typed 停止）；不延 TTL、不扩 scope、不绕撤销、无自动恢复入口；任一页失败整请求拒绝且零映射写入。**安全实质成立。**
- 未发现 P0/P1 级语义放宽。唯一需要 DSH 明确的是 dispatch 锚对「重复建立」的适用方式（R1-005）：建议低成本路径 = **不改契约字节**，在载体 §3/§6 追加一句「首次建立仍须在 Run dispatch 前；mid-run 重复建立不改变该锚，只对其后的读取/提交生效，且不为已 dispatch 命令事后放行」，并在实现卡 AC 落判别；这样 2 pins 不变。若选择改字节，则必须重算 2 pins + delta 复核。

## C. 不变量零改动 —— **PASS**

| 检查 | 结果 | 证据 |
|---|---|---|
| C-05/C-15/C-17/C-07/M2-C1 零字节 | PASS | 均不在 `git diff --name-only HEAD`；`doc/contracts` 无 diff |
| 其余 16 契约零字节 | PASS | 仅 5 个 plan 文件变更；16 个契约未被 touch |
| 无新字段/命令/能力/错误码/wire 字段 | PASS | 两契约 diff 仅 4 hunk/份；C-16 §0 能力（`:22-23`）、§2 wire 请求（`:43-67`）、§6 错误闭集、`:16` `PROTOCOL_MINOR=3` 零 diff |
| 无 TTL 变更 | PASS | C-06 `:40`、C-16 `:78/:91` 未改；Host `+300` 未动（背景只读：`SourceReadCoordinator.cs:586`） |
| 无 schema/依赖变更 | PASS | diff 无 schema/依赖行 |
| C-06 grant 形状/§3 约束零改动 | PASS | grant 字段行 `:39`、§3 `:62-72` 无 diff |
| §2.3 命令行零改动 | PASS | `:56` `AuthorizeSourceReadForRun` 行无 diff |

## D. pin 可复算 —— **PASS（事实）/ FAIL（证据项）**

| 对象 | 期望（记录/载体） | 实测 | 判定 |
|---|---|---|---|
| C-06 sha256 | `8cb153d5e5c7b4cd877f917596bf06c36228a81afd3d15907b1a47ae80692e16` | 同值 | ✅ |
| C-06 `git hash-object` | `9f6bb0e6b0d2a09b7c47dac69e953f1e9db734a3` | 同值 | ✅ |
| C-16 sha256 | `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0` | 同值 | ✅ |
| C-16 `git hash-object` | `f8f31f55ca29aea1ceb8cb7d7ab73b7123630211` | 同值 | ✅ |
| pre 值 = HEAD 冻结字节 | `99831a20…`（C-06 v1.2）/ `a7f57ebd…`（C-16 v1.5） | HEAD blob 实测同值 | ✅ |
| `verify_pins.ps1` | 18/18 | 重跑 `PIN AUDIT: PASS (all 18)` | ✅ |
| 其余 16 契约与 HEAD pin 相同 | 逐项不变 | 抽查 8 项：C05 `f6e6f3cb1fe1`、C07 `3fdb44e49afe`、C10 `ec8fd862f95f`、C13 `8faf1e805eac`、C14 `05056cbf65f9`、C15 `f9e376a0ed4c`、C17 `aefa0fa5b17e`、FEA01 `0370c18932b1`，与 `pins.log` 逐项一致 | ✅ |
| `other-16-pins.txt` | 载体 `:54`、卡 `:80`、复核要求 D 均引用 | **文件不存在**（证据目录仅 7 文件） | ❌ P2（R1-003） |

## E. 冻结记录/矩阵一致性 —— **FAIL**

**自洽部分**：FROZEN-C06/C16 的 `冻结版本`、`sha256`、`hash-object`、`blob 内容 sha256`、§7/§10 触发/授权/修订/`pending`/历史 pin/其他 pin 均自洽；矩阵版本格 C-06 `v1.3`、C-16 `v1.6`；载体 §6 `pending`；**无预填 approved**（记录/载体/矩阵均未声称 v1.3/v1.6 已 approved）。

**缺陷（P2/P3）**

- **P2（R1-001）**：FROZEN-C16 §2 行 8 为 **5 列**（表头 4 列，`:42`），且第 5 列引用的是 **v1.5 的载体与 v1.5 证据目录**（`CONTRACT-UNFREEZE-2026-11-07-C16-V15.md`、`verification/FEA-11-L-S4-B-PREREQ-1/logs/pins.log`），与本批 v1.6 无关；行 7 又缺证据列。
- **P2（R1-002）**：行 7 历史核准记录被静默瘦身（`（P0=0/P1=0/P2=0/P3=0）` 与证据列被删），违反「历史记录不得静默替换」的冻结纪律。
- **P3（R1-007）**：矩阵条件/依赖列未随版本更新——C-06 行 `:24` 仍「独立 byte-level 复核 r3 approved（未标 v1.2）」、C-16 行 `:37` 仍「①v1.5 独立…approved」且依赖列 `C-06 v1.2/C-15 v1.5`。版本格与条件列不同版本，读者易误读为当前版本已核准。
- **P3（R1-008）**：C-06 冻结记录缺 v1.3 的 §1B 复核字节行与 §2 条件行（C-16 已有 ⏳ 行）；C-16 §1B 亦无 v1.6 行；C-06 §7 `:92` 历史 pin 用「…」占位（v1.1/v1.0 实值仍保留在 §1B）。当前因 §7/§10 标 pending，不构成事实错误；approved 后应补齐。

## F. 载体/卡不夸大 —— **PASS**

- 载体 `:3-5` 明示「须独立复核 + DSH 重新冻结后方为最终字节」；`:11` 目标限「契约层允许…实现侧 Host-only」；§4 列风险与回退；**未**宣称实现完成/产品可用/任意长 Run 可用。
- 卡 `:40-41` 状态 `ready`「契约前置；只起草 + 独立复核 + 重冻；不实现」；D-7 `:54`「L-G1 只降级不关闭」并保留子限制清单（单步 >300s/续期失败/L-G2/L-G9/L-R1/L-G16）；实现卡 `FEA-11-RUN-GRANT-2C` 为 `proposed`，AC-2C-7 禁止「任意长 Run 可用/自动恢复/自动重新授权」。
- **P3（R1-011）**：载体未以**独立句**明写「契约就绪 ≠ 实现/产品可用」「L-G1 只降级不关闭」；两句仅出现在 §5 ⑥ 的复核要求括号内（`:44`）。建议 §4 或 §5 加一行，避免 AC-T5 字面争议。
- **P3（R1-004）**：卡 I-2 `:67`「§2.3/§3/§4/§5 零改动」与 AC-T1 `:88`「C-06 v1.3 只含 I-2（§2.2 一句 + 头部）」同实际 §5 `:88` 新增条件 ⑥（载体 §2.A `:18` 已登记）冲突；AC-T1 按字面不可判 MET，须改卡（不动契约字节，pin 不变）。

## G. 证据真实性 —— **PASS（可复现）/ FAIL（清单完整性）**

| 检查 | 结果 | 证据 |
|---|---|---|
| `pre-post.sha256` 值与 HEAD/最终字节一致 | PASS | C-06 pre `99831a20…`、post `8cb153d5…`；C-16 pre `a7f57ebd…`、post `b8f46fb1…`；HEAD 抽取实测同值 |
| `changed-lines.diff` 与 `git diff HEAD -- C-06 C-16` 一致 | **PASS（逐字节相同）** | 两者 10333 chars、`equal_raw=True` |
| `pins.log` 可复现 | PASS | 重跑 `verify_pins.ps1` 输出逐行相同（18 OK + PASS） |
| `check.log` / `check-taskpath.log` 可复现 | PASS | 重跑两模式均 `Governance check: PASS (3 warnings)`，warnings 与日志同 |
| EV 逐文件 sha256 | PASS | `carrier.md 9a3d254e…`、`changed-lines.diff 49f982a7…`、`logs/check*.log 634e0723…`、`logs/pins.log 901510cd…`、`pre-post.sha256 5c05c780…` 全部与 EV 表一致 |
| 证据清单完整性 | **FAIL** | `other-16-pins.txt` 缺失（P2/R1-003） |
| 证据卫生 | P3（R1-010） | `pre-post.sha256` 的 post 值折到下一行（行 2-3、5-6）；日志无命令/时间戳/`reviewed_head` 头；载体 §7 `:55` 列 `carrier.md`、`EV.md` 但未列 `other-16-pins.txt` 缺失 |

## Findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议处置 | 阻断 |
|---|---|---|---|---|---|---|
| R1-001 | **P2** | `FEA-CONTRACT-FROZEN-C16.md:50-51` | §2 行 7 缺证据列（3 cells）、行 8 多出第 5 列；行 8 误引 v1.5 载体/证据 | 表头 4 列（`:42`）；HEAD 行 7 原含 v1.5 证据；工作树行 8 第 5 列即原 v1.5 证据 | 恢复行 7 为 4 列（含 `P0=0/P1=0/P2=0/P3=0` 与 v1.5 证据）；删除行 8 第 5 列 | 是 |
| R1-002 | **P2** | `FEA-CONTRACT-FROZEN-C16.md:50` | 历史核准行被静默瘦身，未在载体 §2.C 登记 | `HEAD` 行 7 有严重度与证据；当前无 | 从 `HEAD` 恢复该行文字；或在载体 §2.C 显式登记该编辑（不推荐） | 是 |
| R1-003 | **P2** | 载体 `:54`；卡 `:80`；复核要求 D | `verification/FEA-11-RUN-GRANT-2C-PREREQ-1/other-16-pins.txt` 不存在 | 证据目录仅 7 文件；`git ls-files --others` 无该文件 | 生成 16 行 `id sha256` 清单（C05…C17/FEA01 等），或删除载体/卡引用并声明以 `pins.log` 为准 | 是 |
| R1-004 | **P2** | 卡 `:67`（I-2）、`:88`（AC-T1） | 卡称 C-06「§5 零改动 / 只含 §2.2+头部」，实际 `:88` 增条件 ⑥；AC-T1 字面不可判 MET | 载体 §2.A `:18`「§5 条件追加 ⑥」；C-06 `:88` 实改 | 卡 I-2 增「§5 ⑥」、AC-T1 改为「§2.2 一句 + §5 ⑥ + 头部 + 变更记录」 | 是 |
| R1-005 | P3 | C-06 `:43`/`:37`/`:56`；C-16 `:78`/`:22` | dispatch 前锚与新「Run 非终态期间」窗口的时态关系未显式调和；scope-r1 结论 `:20-24` 与 §1.1 警告该锚不得降级为叙述文字 | 首句仍「Run dispatch 前」，追加句允许 Run 内重复建立；无「首次 vs 重复」句 | **不改字节**：载体 §3/§6 追加解释句 + 实现卡 AC 判别；若改字节则重算 2 pins + delta 复核 | 否 |
| R1-006 | P3 | C-06 `:43`；C-16 `:78` | 复核要求/AC-T2 的「逐字」短语未逐字命中（重新铸造/扩大 scope/在撤销后/「仍」插入） | 见 B2 表 | 对齐措辞（改字节）或把 AC-T2 改为语义等价判定（不改字节） | 否 |
| R1-007 | P3 | 矩阵 `:24`、`:37` | 条件/依赖列仍指 v1.2 r3、v1.5 与 `C-06 v1.2/C-15 v1.5`；与版本格不符 | 矩阵行文本 | 条件列改「v1.3/v1.6 复核 pending（载体 §6）」；依赖列改 `C-06 v1.3/C-15 v1.5` | 否 |
| R1-008 | P3 | `FROZEN-C06.md:22-49`、`:92`；`FROZEN-C16.md:27-38` | 缺 v1.3/v1.6 §1B 复核字节行与 C-06 §2 条件行；C-06 §7 历史 pin 用「…」 | 文件行 | approved 后补 §1B/§2（C-16 已有 ⏳ 行可仿）；§7 历史 pin 写实值 | 否 |
| R1-009 | P3 | C-06 `:88` | 条件 ⑥ 并入列表项 5，Markdown 渲染为同一项 | 「5. `check.ps1` PASS；6. …」同一行 | 拆行（`5.`/`6.` 两行） | 否 |
| R1-010 | P3 | `pre-post.sha256:2-3/5-6`；`logs/*` | post 值折行；日志无命令/时间戳/head 元数据 | 文件字节 | 一行一 hash；日志加命令、日期、`reviewed_head` | 否 |
| R1-011 | P3 | 载体 `:44` | 「契约就绪 ≠ 实现/产品可用」「L-G1 只降级不关闭」仅出现在 §5 ⑥ 括号内，非独立句 | 载体 §5 | §4 或 §5 增独立一句（不动契约字节） | 否 |
| R1-012 | P3 | 载体 `:32`；卡 `:50`/D-4 | 「每次续期…不自动重新授权」与「Host 周期重铸 grant」字面易读成矛盾 | 载体 §3；卡 In/D-4 | 写明「不自动重新授权 = 撤销/漂移后不恢复、不新增用户级授权入口；周期重铸仅重走同一冻结 `{command, scope}` 的 Registry.Authorize + facts」 | 否 |

## Verdict

**`changes_requested`**（P0=0 / P1=0 / P2=4 / P3=8）。

- **不阻断的安全结论**：v1.3/v1.6 的 mid-run 重复建立语义在实质安全面上**没有**放宽 ≤300s、scope、撤销、facts 重验、失败闭集；没有新增自动重新授权/恢复入口/长期通行证语义；2 pins 与 16 项不变 pin 全部实测成立。
- **阻断原因**：R1-001…R1-004（记录/证据/卡的准确性）。其中 R1-001/002 只改 FROZEN-C16 记录，**不改契约字节**；R1-003 只补证据文件；R1-004 只改卡。修复后 C-06/C-16 的 `8cb153d5…`/`b8f46fb1…` 与 18/18 均不变，无需重算 pin。
- **若采纳 R1-005/R1-006 的契约措辞增补**：C-06/C-16 字节改变 → 必须重算 2 pins、重跑 `verify_pins`，并做 delta 复核（本报告不覆盖改后字节）。建议优先采用「不改字节 + 载体/卡解释句」路径。
- **approved 落盘顺序**：修复 P2 → 重跑 `verify_pins.ps1` + `check.ps1`（默认与 `-TaskPath`）→ 在本报告或 r2 复核新字节（若改契约）→ 载体 §6 追加 r1/r2 结论（append-only，附本 session `f54a7234-2633-410d-8f89-e95298e54e00` 与 `reviewed_head c1e19ed82`）→ FROZEN §7/§10 把 `pending` 改为 approved 记录 → 再提交。

## 真实性声明与 NOT_RUN

- 本报告是本次任务**唯一写入**的文件；未改 `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`、`FEA-C16_SOURCE_READ_WIRE_DRAFT.md`、两份 FROZEN、矩阵、载体、卡、证据；未 `git add/commit/push`；未改任何 `src/**`、`apps/**`、`tests/**`。
- 事实以**工作树最终字节**为准；HEAD 仅用于历史对比。所有 pin/hash 均为本机实测，非引用记录。
- **NOT_RUN**：pytest/.NET 全量基线（本包为纯文档变更，`src/**` 零 diff；卡 D-9 基线属实现卡）；`tools/generate_api_inventory.py --check`（未涉及 API 面）；gated IPC / fake-clock 测试（实现面，尚未释放）；ZCode/Codex 外部会话 ID（`cbdf231a-…` 等）的可核验性（无法从本仓库字节核验，仅确认其在卡/载体中被引用）；`pre-post.sha256`/`changed-lines.diff` 的再生成（改为核验其值与实时字节一致）。
- 本报告写入后，`git status` 会新增本文件为 untracked；它不属于被审 UNFREEZE 包，也未改变被审字节。

## 附：关键实测命令与值（可复现）

```text
git rev-parse HEAD                       -> c1e19ed82dc89a0e42af5e27d9803434794586f1
git diff --name-only HEAD                -> 5 plan files (C-06/C-16/FROZEN-C06/FROZEN-C16/matrix)
git ls-files --others --exclude-standard -> 载体 + verification/FEA-11-RUN-GRANT-2C-PREREQ-1/** (7)
sha256(C-06)                             -> 8cb153d5e5c7b4cd877f917596bf06c36228a81afd3d15907b1a47ae80692e16
git hash-object C-06                     -> 9f6bb0e6b0d2a09b7c47dac69e953f1e9db734a3
sha256(C-16)                             -> b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0
git hash-object C-16                     -> f8f31f55ca29aea1ceb8cb7d7ab73b7123630211
verify_pins.ps1                          -> PIN AUDIT: PASS (all 18)
check.ps1 (+ -TaskPath)                  -> Governance check: PASS (3 warnings)
changed-lines.diff vs git diff           -> equal_raw=True (10333 chars)
HEAD C-06/C-16 raw sha256                -> 99831a20… / a7f57ebd…（= pre-post 的 pre 值）
```
