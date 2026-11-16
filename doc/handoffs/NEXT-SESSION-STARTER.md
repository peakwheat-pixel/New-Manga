# 新会话启动包 — New Manga 目标续接

- 生成时间：2026-11-16 11:25 (+08:00)（本版为 R2 之后更新）
- 生成者：DSH（lead）
- **当前 head：`8b00f3474`**（main，**已 push**，upstream = origin/main，ahead/behind = 0/0）
- 工作区：干净（`git status --porcelain` 为空）
- **R1**：`9ce819ae7` → `dd029b73f`（7 commit，目标 A/B/D 达成）
- **R2（本轮）**：`dd029b73f` → `8b00f3474`（8 commit）—— 目标 C 闭合 **10 条** AC

> 本文是**给下一个会话的唯一起点**。不要重读历史对话；按「下一步队列」推进即可。

---

## 0. 三十秒状态快照

| 项 | 状态 |
|---|---|
| HEAD | `8b00f3474`（main，已 push，0/0） |
| 四件套 | **全绿**：`check.ps1` PASS(3w) / `verify_pins` 18/18 / `api_inventory` 1/80/6=87 / `test.ps1` EXIT=0 **1585/1633 passed, 48 skipped**（App 965/0/4，基线 955/0/11 不退化） |
| 上一 goal | 已用尽 100 轮（见 `GOAL-WRAPUP-R100.md`） |
| 本 goal | 60 轮上限 |
| 目标 C | 可行动项 41 → **闭合 18 / open 23** |

复跑四件套：

```powershell
cd "G:\CODEX\New Manga"
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
$env:NEWMANGA_WORKSPACE_ROOT = "G:\CODEX\New Manga.workspace"
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1
```

⚠️ **`test.ps1` 会改写 `verification/READER-OVERLAY-HEADLESS-PNG-1/{immersive-reader.png, render-info.md}`**
（测试副作用）。跑完必须 `git checkout -- verification/READER-OVERLAY-HEADLESS-PNG-1/` 再提交。

---

## 1. 原目标与达成情况（R2 更新）

| 目标 | 状态 | 缺口 |
|---|---|---|
| **A** 四件套持续通过 | ✅ **达成** | — |
| **B** Release Gate 六条逐条判定 + 映射表 | ✅ **达成（R1）** | — 见 `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` |
| **C** 已登记技术债清零 | ⚠️ **未达成（R2 推进 41→18 闭合 / 23 open）** | 剩 **23 条**：`FEA-04` 8（需另立实现卡）+ `V11R-B-5` 3 + `GOV-RESIDUAL` 2 + `GATE3-COVERAGE-MATRIX` 2 + `V11R-C-1` 2 + 其余 6 条各 1 |
| **D** 剩余仅 HUMAN-REQUIRED 登记 | ✅ **达成（R1，R2 又收窄 H-02）** | `MICA-FIX-1` AC2 判定并入 `H-01`；新增 `H-10`（阅读器 overlay）；`H-08` 签名表述更正；**`H-02` 由 3 大项收窄为 3 小项**（ADJ §7.21） |

---

## 2. 下一步队列（按建议顺序，可直接接手）

### 队列 1 —— **目标 C：剩余 23 条可闭合 AC**（R2 后，仍是最高优先）

素材：
- `doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`（41 条可行动项）
- `verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md`（384 行，**逐条明细 + 判定依据**）
- `doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md`

**R2 已闭合 10 条**（不要重复做）：
`RELEASE-PACKAGE-1` AC6 / `CHAPTER-MANUAL-SORT` AC10 / `M2-REGION-RETYPE-CORE` AC6 / `MICA-FIX-1` AC4 /
`FEA-07-AC5-NATIVE-1` AC-N2 + AC-N5 / `V11R-B-3` AC4 / `V11R-B-4` AC4 / `V11R-B-5` AC4 / `V11R-C-1` AC4。

**剩余 23 条，按可动手性排序**：

| 优先 | 卡 | 未勾 AC | 性质 | R2 已核实的入手点 |
|---:|---|---|---|---|
| 1 | `FEA-04` | AC1–AC8（8） | **实现** | **需另立实现卡**；范围已冻结、实现未开始 |
| 2 | `V11R-B-5` | AC1 / AC2 / AC3（3） | DOC + IMPL | AC1 = `doc/plan/V11R_SCREEN_SPECS.md` 缺导出预检/术语章节；AC2 = 上下文保留断言；AC3 = 六态 |
| 3 | `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | AC6 / AC7（2） | IMPL + RERUN | AC7 **实际不可闭合**：需清理 160 处历史声明错误（7 处裁定身份必须保留），会碰历史证据字节 ⇒ 建议改判 `BLOCKED` 并写明 |
| 4 | `GATE3-COVERAGE-MATRIX` | AC2 / AC4（2） | DOC（大） | AC2 已有 progress 稿 `verification/GATE3-COVERAGE-MATRIX/ac2-four-cells-progress.md`（4 格已补），但整张矩阵仍缺逐行断言说明；AC4 需核 100 项 NOT_RUN 归因 |
| 5 | `V11R-B-4` | AC3（1） | IMPL | 六态（partial 状态无断言，赋值点已存在） |
| 6 | `V11R-C-1` | AC6 / AC7（2） | IMPL+DOC | 引擎卡；AC6 = 单测/截图，AC7 = 证据目录整理 |
| 7 | `MICA-FIX-1` | AC2（1） | RERUN | 需跑 `--diagnostics` 留原始日志（会起 GUI，Agent 可用 `[System.Diagnostics.Process]::Start`） |
| 8 | `V11R-A-3` | AC4（1） | IMPL | `CommandParityContractTests` 66 条 parity 断言 |
| 9 | `RUN-IPC-1` | AC4（1） | IMPL | typed 拒绝单测 + allowlist 断言 |
| 10 | `V11R-C-3` | R1（1） | IMPL | 建回滚 tag `v11r-pre-retire` 并跑 `-DryRun` |
| 11 | `M2-SFX-CORRECTION-EXPORTER` | AC4（1） | IMPL | T1b 批量产物尚不存在，需先生产 |

⚠️ **R2 发现的重要事实**：
- `RELEASE-PACKAGE-1.md` **实测 NUL=0** ⇒ 队列 5 的「NUL 字节」债项**不存在**，已结案；
- `V11R-B-3/B-4/B-5/C-1` 四张卡有**先存 v2 结构性欠账**（无 Canonical Evidence 表 / Resource Manifest /
  `evidence_dir` 有未登记文件），`-TaskPath` 会 FAIL。**这不是本轮引入的**，需单独立卡补表；
  全局 `check.ps1` 不受影响（仍 PASS）。
- 裸值类 AC 的准确口径是「**无未登记**的裸间距」，由两个可执行测试守护
  （`V2StudioConformanceTests` 白名单 + `R14ContractTests`），不是「零裸值」。

### 队列 2 —— 目标 B 的延伸（可选）

`doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` §6 指出**条件 6 是唯一 Agent 可独立关闭**的一条，
差 4 项（冻结 head / MAINT-1 补 Canonical Evidence 载体 / 登记 GATE-CONDITION-6 Review / 修三指针精度）。
若想推进 Gate，这是最有性价比的一块（无需人）。

### 队列 3 —— 队列 5 小债（低优先）

- `doc/tasks/M2-REGION-RETYPE-CORE.md` 重复 `integration_commit` 键
- `doc/REBASELINE_PLAN.md` 第 56/58 行漂移（**注意：PLAN 已 6990/7000 bytes、64/64 lines，行数已满，改前先压缩**）
- `test.ps1` 改写 `verification/READER-OVERLAY-HEADLESS-PNG-1/` 下 2 个文件（已在本卡登记，未修）
- ~~`doc/tasks/RELEASE-PACKAGE-1.md` 含 NUL 字节~~ → **R1 实测 NUL=0，已不存在**

### 队列 4 —— HUMAN-REQUIRED 等待项（不阻塞 Agent）

`doc/reviews/HUMAN-REQUIRED-2026-11-15.md` 现有 `H-01`…`H-10`，
六条 Gate 条件的剩余动作已逐条映射（见 `RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` §8.2）。
**不要因等待人回复而停顿。**

---

## 3. R1 本轮完成的事（避免重复劳动）

| # | 事项 | 结果 |
|---|---|---|
| 1 | **`HOST-CONCURRENCY-FLAKY-1` AC6 二次+三次复核** | 三轮独立上下文复核：`reviewer-hcf`（CHANGES）→ `reviewer-hcf2`（CHANGES，代码侧放行）→ `reviewer-hcf3`（**ACCEPTED**）；定案 **`closed_with_limitations`**，AC1–AC6 全 MET，保留 L-1…L-4 limitation |
| 2 | 新增回归测试 | `HostFileIdNormalizationTests`（3 facts）——固定 53 位常量与 wire 口径；**做过回退红测**（`:414` 改回 raw ⇒ 红 ⇒ 还原绿）；`%TEMP%` 探针拿不到 `raw > 2^53` 样本时**直接 FAIL**（拒绝假绿） |
| 3 | 三次复核 P2 清扫 | 行号**第三次**同步（`:414/:638`、`TileChannel.cs:457`）、AC5 双数、控制字符 18 处、旧「并行」叙述四处作废标注 |
| 4 | **目标 B** | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md`（六条逐条：定义/判定/证据 commit+行号/剩余动作/归属） |
| 5 | **目标 D** | `HUMAN-REQUIRED` 更新：AC2 并入 H-01、新增 H-10、更正 H-08 签名表述 |
| 6 | 证据卫生 | 该卡 22 行 EV 全量校验（`git cat-file blob` + sha256，22/22 匹配）；发现并修复「`core.autocrlf=true` ⇒ 工作区 sha ≠ blob sha」的陷阱 |

---

## 3b. R2（本轮）完成的事 —— 目标 C 闭合 10 条 AC

| # | AC | 卡 | 依据要点 |
|---:|---|---|---|
| 1 | AC6 | `RELEASE-PACKAGE-1` | 五判据全满足：`check -TaskPath` PASS / `test.ps1` EXIT=0 / pytest 3569P·0F·10S vs 基线 3360P·10S / 9 条 pin / Handoff 已有。**并澄清** B1-DOC-CLOSE-1 那次 3 failed 是 sidecar schema v6 vs 数据根 v14 的**环境问题**，非代码回归 |
| 2 | AC10 | `CHAPTER-MANUAL-SORT` | App 962/0/4 + CoreClient 256/0/0 + pytest 3569P/0F/10S，skip 未增 |
| 3 | AC6 | `M2-REGION-RETYPE-CORE` | pytest 三套件 **1665P/0F/4S**（基线 650/1）+ `m2_acceptance` **37**（要求 35）；cargo/vitest 旧壳退役 ⇒ NA |
| 4 | AC4 | `MICA-FIX-1` | `test.ps1` 1582/1630 0 failed；pytest **failed 3→0**；旧壳 vitest ⇒ NA（`apps/desktop/package.json` 不存在） |
| 5 | AC-N2 | `FEA-07-AC5-NATIVE-1` | **新增 `V2KeyDispatchOnceTests`（3 facts）+ 变红验证**：注入重复全局手势 ⇒ 3/3 红且报「按键冲突 Ctrl+1」 |
| 6 | AC-N5 | `FEA-07-AC5-NATIVE-1` | **独立复核 `reviewer-fea07b` ACCEPTED（带 limitation）**；并修掉该卡 3 类 pin 缺陷（commit 错配 / WORKTREE 口径 / 旧版 README） |
| 7–9 | AC4 ×3 | `V11R-B-3` / `V11R-B-4` / `V11R-B-5` | 由**两个可执行一致性测试**守护（`V2StudioConformanceTests` 白名单 + `R14ContractTests`），裸值均在**已登记白名单**内 |
| 10 | AC4 | `V11R-C-1` | 引擎卡无 `.axaml` ⇒ 子项 NA；唯一 hex `#1F1F1F` 经核为**冻结 Fluent baseline 的 theme-layer 常量**（注释明写故意不入 token 字典） |

**R2 踩到并更正的错误（务必记住）**：
1. 我先按「分类行的行号」统计，报出 **33 条 open**，实际逐卡核对后是 **23 条** ——
   分类文档的行号已漂移、且部分条目早已 `[x]`。**统计必须逐卡读真实 checkbox，不能信派生快照。**
2. 我写的 `UnboundGesture_DispatchesNothing` 断言「Ctrl+D1 在 Studio/Batch 不匹配」**实测红** ——
   因为 `Ctrl+D1` 声明为 `Space=null`（**全局**），每个作用域都绑定。**是断言错，不是产品 bug**；
   已改为正确口径的 `GlobalShortcuts_ResolveInEveryScope_SpaceScopedOnesDoNotLeak`。
3. 一度把 `FEA-07` 的 `EV-AC5-03/04/05` 判为「sha 错」，实为 **WORKTREE 口径**（CRLF）；
   同一文件工作区哈希 = 声明值，而 blob 哈希不同 —— **又一次 `core.autocrlf` 陷阱**。

---

## 4. 关键技术事实（R1/R2 累积）

### 4.1 file identity 53 位契约（已闭环）

- 权威定义：`src/application/importing/referenced/identity.py:3-9/16/20`
- C# 已修点（**行号已稳定**）：
  - `NewManga.CoreClient/Issuer/HostIssuer.cs:563`（file）/ `:596-597`（dir）
  - `NewManga.Host/Sources/SourceReadCoordinator.cs:414` / `:638`（写 wire facts 两处）
  - `NewManga.Host/Sources/SourceSecurity.cs:138`（`CoreFileIdMask`）/ `:154`（`NormalizeFileId`）
- **`SourceSecurity.Identity` 本体保持 raw**（`registry.v1.dat` 兼容），**不要**在里面 mask
- `TileChannel.cs:457` 的 raw index **不参与跨语言比较**（同进程同源自比），无需修；已加契约注释

### 4.2 `core.autocrlf = true` 的两条硬约束

1. **证据 sha256 必须用 BLOB 口径**：`git add` 后 `git cat-file blob :<path>` 算，
   **不能用工作区文件**（工作区是 CRLF，blob 是 LF，哈希不同）。
2. 提交后用 `git cat-file blob <commit>:<path>` 复核（本卡 22/22 就是这么验的）。

### 4.3 新回归测试的「可红性」是硬要求

`HostFileIdNormalizationTests` 的探针建在 **`%TEMP%`**（实测 12/12 的 raw id > 2^53），
**不是** `G:\CODEX\New Manga.workspace`（实测 0/6）。
若把探针放 workspace 卷，强断言永远不触发 ⇒ **绿但什么都没测到**。
这是本卡最贵的教训之一，写测试时务必确认「样本真的能落进回归区间」。

### 4.4 诊断优先读仓库自带 wire log，不要自造 probe

`SidecarFixture.cs:312` 一直配着 `WireLogPath`，`test.ps1` 每次自动写 NDJSON 到
`G:\CODEX\New Manga.workspace\task-envs\HOST-RESOURCE-SECURITY-1\evidence-rerun\wire\`，
字段名是 `request` / `response`（小写）。

⚠️ **但该 test 目录每次全量运行都被覆写**（`results-*.trx`、`summary.json` 的 `at_utc`），
依赖旧 `.trx` 的哈希声明**不可复验** ⇒ 证据要么「当日跑当日验」，要么按 run 分目录。

---

## 5. 陷阱区（累计，务必内化）

| # | 错误 | 代价 |
|---|---|---|
| 1 | 把测试夹具副本错认成产品 bundle | 一轮 |
| 2 | 从 `weights not found` 警告推断 `pending` 原因 | 一轮 |
| 3 | probe 用点号命令名 ⇒ 误判「settings 域未挂载」 | 一轮 |
| 4 | probe 自己传 `null` ⇒ 误判「发现 payload bug」 | 一轮 |
| 5 | 给测试插诊断块时把 `return` 放到断言前 ⇒ **断言被跳过、测试假通过** | 一轮 |
| 6 | **把 `dotnet test` 的 `EXIT=0`（含 skipped）当成 passed** | **3 轮方向错误** |
| 7 | 修完 `HostIssuer` 就宣称「唯一产品缺陷已修」 | 一轮 |
| 8 | **写行号引用后改了被引用代码，不重新核实行号** | R1 又犯 2 次（三轮复核各抓一次） |
| 9 | **回归测试探针放错卷 ⇒ 强断言不触发（假绿）** | R1 自查抓到 |

**纪律**：

1. 判断测试通过要看**具体结果行**（`已通过`/`失败`/`已跳过`）；`EXIT=0` 只说明没有失败。
2. 诊断零侵入；优先读仓库已有证据。
3. 修 producer 前先 `grep` 查**有几处**。
4. 改持久化数据的 producer 前先想兼容。
5. 证据 pin 的 `commit` 必须是**实际引入该文件当前内容**的 commit
   （`git log --diff-filter=A` 对新增文件；`git log -1 -- <path>` 对修改过的文件）。
   `check.ps1` **不校验** blob 是否存在，要自己 `git cat-file blob <commit>:<path>` 验。
6. 跑完 `test.ps1` 先 `git checkout -- verification/READER-OVERLAY-HEADLESS-PNG-1/`。
7. 「测试全绿」≠「没 bug」：opt-in 路径（`NEWMANGA_FEA11_IPC=1`）不跑时，绿是假的安全感。
8. 写行号引用后若改了被引用代码，**必须重新核实**；更稳的是「函数名 + 语句特征」而非纯行号。

---

## 6. 治理约束（不可绕过）

- **仓库**：`G:\CODEX\New Manga`（唯一事实来源）；派生**一律**进 `G:\CODEX\New Manga.workspace`
- **可用 Agent**：仅 DSH / Codex / ZCode。**`subagent_agy` 禁用**（Antigravity 已退出）
- **Review 独立性**：按**上下文独立**，不要求非作者。作者可派新子 agent 只读审查
- **AC 标记**（lifecycle v3）：`<<MET>>` / `<<PARTIAL: 原因>>` / `<<BLOCKED: 原因>>` / `<<NOT_APPLICABLE: 原因>>`，
  **严格在行末**；`[x]` 只允许 `MET`/`NOT_APPLICABLE`，`[ ]` 只允许 `PARTIAL`/`BLOCKED`；
  `MET` 不得带原因。门禁在 `in_review/approved/done/closed_with_limitations` 生效
- **DAG**：`ready`/`in_progress`/`blocked`/`in_review`/`changes_requested`/`approved` 六态须登记 DAG；
  终态与 `proposed` 不检查
- **预算**：`doc/STATUS.md` ≤3200 bytes / 45 lines（现 3032/27）；
  `doc/REBASELINE_PLAN.md` ≤7000 bytes / **64 lines（已满，加行前必须先压缩）**
- **提交**：长中文 commit message 用 `git commit -F <file>`

---

## 7. 本次 goal 的关键文件索引

| 用途 | 路径 |
|---|---|
| 本文（启动包） | `doc/handoffs/NEXT-SESSION-STARTER.md` |
| 上一 goal 总账 | `doc/handoffs/GOAL-WRAPUP-R100.md` |
| **Gate 六条映射表（目标 B 交付）** | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` |
| **HUMAN-REQUIRED（目标 D）** | `doc/reviews/HUMAN-REQUIRED-2026-11-15.md`（H-01…H-10） |
| 目标 C 素材 | `doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`、`verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md` |
| 人侧甄别 | `doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md` |
| 已关闭的 HCC 卡 | `doc/tasks/HOST-CONCURRENCY-FLAKY-1.md`（含三轮复核结论 + L-1…L-4） |
| 三轮复核报告 | `verification/HOST-CONCURRENCY-FLAKY-1/review-ac6{,-2nd,-3rd}.md` |
| 当前 DAG | `doc/REBASELINE_PLAN.md`（**行数已满 64/64**） |
| 当前状态 | `doc/STATUS.md` |

---

## 8. 一句话交接

**目标 A/B/D 已达成；目标 C 由 41 条可行动项推进到「闭合 18 / open 23」（R2 闭合 10 条）。**
**最高优先仍是队列 1 —— §2 已按「可动手性」把剩余 23 条排成表并逐条给出入手点。**
**`FEA-04` 的 8 条是实现工作，必须另立实现卡，不要在目标 C 里硬啃。**
