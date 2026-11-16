# 新会话启动包 — New Manga 目标续接

- 生成时间：2026-11-16 10:30 (+08:00)（上一版 08:45，本版为 R1 之后更新）
- 生成者：DSH（lead）
- **当前 head：`27639beaf`**（main，**已 push**，upstream = origin/main，ahead/behind = 0/0）
- 工作区：干净（`git status --porcelain` 为空）
- **本轮（R1）起点**：`9ce819ae7` → **终点 `27639beaf`**，6 个 commit 已推送

> 本文是**给下一个会话的唯一起点**。不要重读历史对话；按「下一步队列」推进即可。

---

## 0. 三十秒状态快照

| 项 | 状态 |
|---|---|
| HEAD | `27639beaf`（main，已 push，0/0） |
| 四件套 | **全绿**：`check.ps1` PASS(3w) / `verify_pins` 18/18 / `api_inventory` 1/80/6=87 / `test.ps1` EXIT=0 **1582/1630 passed, 48 skipped**（App 962/0/4，基线 955/0/11 不退化） |
| 上一 goal | 已用尽 100 轮（见 `GOAL-WRAPUP-R100.md`） |
| 本 goal | 60 轮上限，已用 1 轮 |

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

## 1. 原目标与达成情况（R1 更新）

| 目标 | 状态 | 缺口 |
|---|---|---|
| **A** 四件套持续通过 | ✅ **达成** | — |
| **B** Release Gate 六条逐条判定 + 映射表 | ✅ **达成（R1）** | — 见 `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` |
| **C** 已登记技术债清零 | ⚠️ **未达成** | **AC blocked 剩 33 条可闭合项**（分类 DOC 8 / RERUN 5 / IMPL 20；`FEA-04` 独占 8 条需另立实现卡） |
| **D** 剩余仅 HUMAN-REQUIRED 登记 | ✅ **达成（R1）** | `MICA-FIX-1` AC2 判定部分已并入 `H-01`；新增 `H-10`（阅读器 overlay）；`H-08` 签名表述已更正 |

---

## 2. 下一步队列（按建议顺序，可直接接手）

### 队列 1 —— **目标 C：剩余 33 条可闭合 AC**（R1 后升为最高优先）

素材：
- `doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`（41 条已核实可闭合，8 条已处置 ⇒ 剩 33）
- `verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md`（384 行，**逐条明细 + 判定依据**）
- `doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md`（33 条中仅 1 条确属 HUMAN，1 条含 HUMAN 子项）

分类（按 classification-v2）：
| 批 | 类别 | 条数 | 风险 |
|---|---|---:|---|
| B1 | `DOC` 纯文档补齐 | 8 | 低 |
| B2 | `RERUN` 重跑取证 | 5 | 中（依赖测试环境） |
| B3 | `IMPL` 小额缺口（裸间距/断言/负例） | 12 | 中 |
| B4 | `FEA-04` 8 条 | 8 | **高（是实现而非补证据，需另立实现卡）** |

⚠️ **实际待做 6 条 DOC 已逐条核实当前状态**（R1 已定位，可直接接手）：
- `V11R-B-5` AC1（需在 `doc/plan/V11R_SCREEN_SPECS.md` 补导出预检/术语章节）
- `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` AC7（需真实跑三命令 + 独立 Reviewer；**实为 RERUN+IMPL**）
- `GATE3-COVERAGE-MATRIX` AC2（补 4 格 `测试名 (文件:行)`+断言；已有 progress 稿 `verification/GATE3-COVERAGE-MATRIX/ac2-four-cells-progress.md`）
- `GATE3-COVERAGE-MATRIX` AC4（逐条核实 100 项 NOT_RUN 归因）
- `RELEASE-PACKAGE-1` **AC6（当前在 L46，注意行号已从 L45 漂移）** —— 缺 Handoff 文件，可补写
- `FEA-07-AC5-NATIVE-1` AC-N5（补独立 Review 并翻转 AC5 行）

⚠️ 另：`RELEASE-PACKAGE-1.md` **实测 NUL=0**，队列 5 的「NUL 字节」债项**不存在**（可结案）。

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

## 4. 关键技术事实（R1 新增/更正）

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

**目标 A/B/D 已达成（R1）；只剩目标 C 的 33 条可闭合 AC。**
**最高优先是队列 1 —— 其中 6 条 DOC 的当前状态已在本文 §2 逐条定位，可直接开工；`FEA-04` 8 条需另立实现卡。**
