# 20 个具名未提交文件：内容差异评估（Coordinator）

- **触发**：用户 2026-10-18 裁决 —— "先对 20 个文件做内容差异评估，再统一处置"
- **执行**：Coordinator = dsh，epoch 8
- **方法**：只读量化分析（`git diff --numstat` / `git cat-file -s` / `git hash-object` / `git log --find-object` / 字节级 CRLF 分解 / 治理要素关键词计数）。**未修改、未恢复、未暂存任何文件。**

## 1. 结论摘要（**更正前一版报告的推断**）

前一版 [`provenance-investigation.md`](provenance-investigation.md) 依据"同一秒批量写入 + 内容更旧"推断这批文件是**一次性回退**。**本轮字节级分析推翻该单向结论**：

> 这 20 个文件是**方向混合、长期累积**的未提交状态；`2026-10-17 20:30:51` 那次批量操作**很可能只刷新了 mtime**（或只回退了其中一部分），而不是把 20 个文件统一改写为旧版本。

证据：去掉 CRLF 影响后，**12 个文件的工作区内容多于 HEAD，8 个少于 HEAD**；且其中既有"工作区更完整"（`AGENTS.md`、`templates/TASK.md` = 项目**当前正在使用**的 lifecycle v2 治理内容），也有"工作区落后"（`doc/tasks/P02*.md` 仍描述 Build Task 未启动）。

**因此：不存在"统一恢复"或"统一保留"的安全选项，必须逐文件判定。** 本轮不执行任何处置。

## 2. 量化证据表

`wsB` = 工作区字节；`crlf` = 工作区 `\r\n` 数；`wsLF` = `wsB - crlf`（折算为 LF 后的内容字节）；`headB` = git blob 字节（LF 存储）；`REALDIFF` = `wsLF - headB`（**真实内容差异**，已剔除 CRLF 干扰）。

| 文件 | wsB | crlf | wsLF | headB | REALDIFF | 方向 | blob 在历史中 |
|---|---:|---:|---:|---:|---:|---|---|
| `AGENTS.md` | 6250 | 48 | 6202 | 4464 | **+1738** | WS 多 | 否 |
| `.qoder-credits/report.json` | 6860 | 261 | 6599 | 61876 | **−55277** | WS 少 | 否 |
| `doc/00_INDEX.md` | 6453 | 62 | 6391 | 24869 | **−18478** | WS 少 | 是（`aa629c7c7`） |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md` | 12925 | 259 | 12666 | 12416 | +250 | WS 多 | 是（`000cbfe99`） |
| `doc/03_DATA_MODEL.md` | 58184 | 2756 | 55428 | 55009 | +419 | WS 多 | 是（`000cbfe99`） |
| `doc/04_USER_FLOW.md` | 36533 | 2005 | 34528 | 33990 | +538 | WS 多 | 是（`000cbfe99`） |
| `doc/06_TRANSLATION_PIPELINE.md` | 52142 | 3203 | 48939 | 48459 | +480 | WS 多 | 是（`000cbfe99`） |
| `doc/09_COLLABORATION.md` | 23258 | 203 | 23055 | 18946 | **+4109** | WS 多 | 是（`aa629c7c7`） |
| `doc/11_ARCHITECTURE_MAPS.md` | 23560 | 466 | 23094 | 22702 | +392 | WS 多 | 否 |
| `doc/12_ROADMAP.md` | 796 | 13 | 783 | 9594 | **−8811** | WS 少 | 否 |
| `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` | 3346 | 31 | 3315 | 7406 | **−4091** | WS 少 | 是（`aa629c7c7`） |
| `doc/WORKTREE_SAFETY_INVENTORY.md` | 6974 | 51 | 6923 | 17941 | **−11018** | WS 少 | 否 |
| `doc/templates/HANDOFF.md` | 1988 | 50 | 1938 | 1752 | +186 | WS 多 | 否 |
| `doc/templates/REVIEW.md` | 4246 | 59 | 4187 | 3915 | +272 | WS 多 | 否 |
| `doc/templates/TASK.md` | 3179 | 82 | 3097 | 1489 | **+1608** | WS 多 | 否 |
| `doc/tasks/P02.md` | 242662 | 1014 | 241648 | 242183 | −535 | WS 少 | 否 |
| `doc/tasks/P02-NEW-TIME-X6.md` | 43292 | 187 | 43105 | 45073 | −1968 | WS 少 | 否 |
| `doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md` | 12646 | 118 | 12528 | 31198 | **−18670** | WS 少 | 是（`e0b7d869a`，≠ `cb452b7db:path`） |
| `verification/P19/codex-review-r2.md` | 9332 | 51 | 9281 | 8935 | +346 | WS 多 | 否 |
| `verification/PROJECT-ROADMAP-20261008/ROADMAP.md` | 8974 | 94 | 8880 | 8504 | +376 | WS 多 | 否 |

**blob 溯源汇总**：8 个文件的工作区 blob **存在于仓库历史**（说明其内容等于某个历史版本）；12 个为**唯一 blob**（内容不等同于任何历史 commit）。
**治理要素关键词计数**（`governance_version`/`check.ps1`/`Canonical Evidence`/`Resource Manifest` 等）：WS 更贴近现状 **8** 个、HEAD 更贴近 **5** 个、平手 **7** 个 —— 同样不支持单一方向。

## 3. 已确认的关键案例（人工核对内容）

**A. 工作区版本 = 项目当前正在使用的更新版（应保留）**

- `doc/templates/TASK.md`：工作区版包含 `governance_version: 2`、`delivery_head`、`Canonical Evidence`、`Resource Manifest`、`Closeout Record` —— 即 **lifecycle v2 模板**，本项目所有新 Task 均按此格式创建；HEAD 版仅为 v1 模板。
- `AGENTS.md`：工作区版新增"工作区、归档与派生产物"整节（workspaces 治理、Worktree Safety Inventory 前置检查、`archive/` 归档入口）与第 6 条 governance check 要求 —— 这些是**当前实际生效的项目规则**（本会话收到的 AGENTS.md 指令即为工作区版）。
- `doc/00_INDEX.md`：工作区版标题为 "Document Truth Map / 项目文档权威地图" 并含"权威来源与冲突裁决"表；HEAD 版是旧的"项目文档索引与 Source of Truth"。
- `doc/12_ROADMAP.md`：工作区版是精简导航版并显式声明"不定义当前技术架构、READY DAG、Task 状态或实现授权"（符合当前治理口径）；HEAD 版仍是含 P02 历史状态的旧文。

**B. 工作区版本明显落后于 HEAD（与项目现状矛盾）**

- `doc/tasks/P02.md`：工作区版称"当前唯一 READY 节点为 `P02-NEW-TIME-X6-BUILD-CARGO`…等待 Build worktree…preflight PASS 前不启动 Build"；HEAD 版已记录该 Task"已集成并获 convergence APPROVED"。
- `doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md`：工作区 blob `e0b7d869a…` 虽被 `git log --find-object` 命中（`cb452b7db`/`83979dac1`），但**并不等于 `cb452b7db:path` 的 blob**（实测 `cb452b7db:path = 4bcd05bcbe2ad4f83fee028e1a8910c2a7ec4874`）。原文"精确等于 `cb452b7db`"的表述系**误读 `--find-object` 语义**（该参数列出的是"改变该对象出现次数"的 commit，包含删除方），已由 `per-file-verdict.md` 复核更正。

### 更正记录（2026-10-18，依据 `per-file-verdict.md`）

- **方向计数更正为 12 多 / 8 少**（原写 11/9，与本表 REALDIFF 数值自相矛盾）。
- 上述 `BUILD-CARGO.md` 的 blob 关系更正。
- 另：`per-file-verdict.md` 对 20 份文件给出了逐份判定（16 `WS_IS_CURRENT` / 3 `HEAD_IS_CURRENT` / 1 `USER_DATA`），**处置以该报告为准**。
- `doc/tasks/P02-NEW-TIME-X6.md`：工作区 −1968 bytes。

**C. 方向不明，需逐份判断**

- `.qoder-credits/report.json`：工作区 6.5 KB vs HEAD 61.9 KB。工作区版 `generatedAt = 2026-10-08`（Qoder 退出项目当日），HEAD 版 `2026-09-26`。**工作区版时间更晚但内容更少** —— 不排除是 Qoder 退出时生成的"总结版报告"，属**用户侧数据**，处置前必须单独确认。
- `doc/01/03/04/06/11`、`templates/HANDOFF.md`、`templates/REVIEW.md`、`P19/codex-review-r2.md`、`PROJECT-ROADMAP-20261008/ROADMAP.md`：小幅差异（+186 ~ +538 bytes），可能是同一批治理改版的连带更新。

## 4. 处置建议（**本轮不执行**）

1. **禁止统一恢复** —— 会把 A 类文件里"项目当前正在使用的 lifecycle v2 治理内容"一起丢掉，可能直接破坏 Task 生命周期与工作区规则的现行口径。
2. **禁止统一保留** —— 会让 B 类文件的过时描述继续误导 Agent 与审计（例如 `P02*.md` 声称 Build 未启动）。
3. 建议按类分别处置：
   - **A 类**（`templates/TASK.md`、`AGENTS.md`、`00_INDEX.md`、`12_ROADMAP.md` 等）：内容为**现行治理版本**，建议**保留并作为独立提交入库**（提交前逐份核对与当前 `check.ps1` 规则一致）。
   - **B 类**（`P02*.md` 3 份）：内容落后于 HEAD 且与项目现状矛盾，建议**恢复为 HEAD 版本**（`git checkout -- <path>`），恢复前逐份留证。
   - **C 类**（`report.json` 及小幅差异者）：**逐份**判断；`report.json` 属用户侧数据，处置前单独请示。
4. 无论采取哪种处置，都应在**同一批次**内完成，并记录每份文件的改动前后 sha256。

## 5. 未完成的部分（如实声明）

本报告完成的是**量化差异 + 4 份 A 类 / 3 份 B 类的语义确认**；**其余 13 份文件尚未逐份做语义级判断**（未逐份阅读完整 diff）。用户要求的"内容差异评估后再统一处置"要落地，仍需一轮逐文件语义评估。

## 6. 复现命令

```powershell
Set-Location 'G:\CODEX\New Manga'
# 真实内容差异（剔除 CRLF）
$f='doc/templates/TASK.md'
$t=[IO.File]::ReadAllText($f); $crlf=([regex]::Matches($t,"`r`n")).Count
((Get-Item $f).Length - $crlf) - [int](git cat-file -s "HEAD:$f")
# blob 溯源
git hash-object -- $f
git log --all --oneline --find-object=$(git hash-object -- $f)
```
