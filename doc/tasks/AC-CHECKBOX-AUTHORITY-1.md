---
task_id: AC-CHECKBOX-AUTHORITY-1
owner: DSH
status: in_progress
created: 2026-11-15
scope: 全项目 AC 勾选一致性清理（用户 2026-11-15 指示：AC 勾选要成为权威信号）
---

# AC 勾选成为权威信号：清理规范与执行

**用户指示（2026-11-15）**：「希望 AC 勾选成为权威信号，需一次全项目一致性清理」。

## 1. 精确范围（已实测）

```powershell
# 遍历 doc/tasks/*.md：status ∈ {done, closed_with_limitations} 且 "- [ ]" 数>0 且 "- [x]" 数=0
```

| 项 | 数 |
|---|---|
| **需要清理的卡** | **40 张** |
| **AC 总数** | **260 条** |
| 其中 `evidence_dir` 存在 | 31 张 / 208 条 |
| 其中 `evidence_dir` **不存在** | **1 张 / 5 条**（`V11R-C-RESEARCH-1`） |
| 其中**无** `evidence_dir` 字段 | 8 张 / 47 条 |

**全部 40 张**（按 AC 数降序）：`V11R-C-2`(12)、`CHAPTER-MANUAL-SORT`(10)、`V11R-D-1`(10)、`UI-DESIGN-1`(9)、`FEA-04`(8)、`V11R-C-1`(7)、`V11R-B-5`(7)、`V11R-B-4`(7)、`V11R-B-3`(7)、`V11R-B-2`(7)、`V11R-B-1`(7)、`V11R-A-2`(7)、`P20-AC4-FPS-1`(7)、`P02`(7)、`V11R-F0-1`(7)、`GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1`(7)、`GATE3-COVERAGE-MATRIX`(6)、`GOV-PIN-LINEAGE-1`(6)、`GOV-RESIDUAL-RUNTIME-IDENTITY-1`(6)、`V11R-A-3`(6)、`V11R-A-1`(6)、`V11R-C-3`(6)、`FEAT-CREATE-2`(6)、`M2-REGION-RETYPE-CORE`(6)、`TASK-053`(6)、`RUN-IPC-1`(6)、`RELEASE-PACKAGE-1`(6)、`M2-SFX-CORRECTION-EXPORTER`(6)、`M2-SFX-DATA-INFRA`(6)、`P15-C1`(6)、`TASK-056`(6)、`EXPORT-IPC-1`(6)、`DIAG-M2-REGIONLESS-LOCK-CHANGED-001`(5)、`V11R-C-RESEARCH-1`(5)、`M2-SFX-MISROUTE-UI-MITIGATION`(5)、`MICA-FIX-1`(5)、`P19`(5)、`FEA-07-AC5-NATIVE-1`(5)、`V1-RELEASE-SIGNING-1`(4)、`P20-MEM-OPT-1`(4)

## 2. ★ 核心原则：**不得凭空打勾**

要 AC 勾选成为**权威信号**，前提是**每个勾都有可审计的依据**。

**⇒ 因此定义三种勾选标注，禁止裸 `[x]`**：

| 标注 | 含义 | 谁可以打 |
|---|---|---|
| `- [x]` + **行内 `<!-- verified: <方式> @ <commit> -->`** | **已自动核实** | 任何人，只要有可复现的核实命令 |
| `- [ ]` + **行内 `<!-- blocked: <原因> -->`** | **未满足/不可自动验证** | 任何人 |
| **完全不改动** | 该卡不在本次范围 | — |

**`<方式>` 允许的取值（必须可复现）**：
- `grep:<pattern>@<path>:<line>` —— 代码/配置存在性
- `test:<test-id>` —— 有对应测试且全量通过
- `file:<path>` —— 有实物产物（含 sha256 更佳）
- `gate:check|pins|inventory` —— 四件套之一通过
- `human:<who>@<date>` —— **必须是人做的判断**（Agent 不得冒充）

## 3. 分批策略（按可自动验证程度）

| 批次 | 范围 | 预期 |
|---|---|---|
| **B1 试点** | `CHAPTER-MANUAL-SORT`（10 条，我已逐项核实过 6 项） | **本轮完成** |
| **B2 高置信** | `evidence_dir` 存在 + AC 文本里写了可 grep 的符号（文件/命令/测试名） | 每轮 3–5 张 |
| **B3 需找证据** | 8 张无 `evidence_dir` | 先定位证据，再进 B2 |
| **B4 真问题** | `V11R-C-RESEARCH-1`（`evidence_dir` 不存在） | **单独处理：查明是目录名错还是证据丢了** |
| **B5 需人判断** | AC 文本涉及"手感/视觉/体验" | **标 `blocked: 需人工判断`，不冒充** |

## 4. 本轮（B1 试点）要做的

对 `CHAPTER-MANUAL-SORT` 的 10 条 AC：

- **已有证据的**（AC1/AC2/AC4/AC5/AC6 等）：打 `[x]` + `<!-- verified: ... -->`
- **无法自动验证的**（如 AC8"失败与刷新不假装成功"、AC9"并发保护"需要行为断言）：**标 `[ ]` + `<!-- blocked: ... -->`**
- **不修改其他 39 张卡**（本轮只试点）

## 5. 验收（本卡完成条件）

- [x] **B1 试点完成**：`CHAPTER-MANUAL-SORT` 的 10 条 AC 全部有标注（`verified:` 或 `blocked:`），**无裸 `[x]`** <!-- verified: file:doc/tasks/CHAPTER-MANUAL-SORT.md(10 条 AC：9 verified + 1 blocked，scan_ac.py AC=10 ann=10 bare_x=0) -->
- [x] **B2/B3/B4/B5 有明确清单**（哪张卡进哪批，依据是什么） <!-- verified: file:doc/tasks/AC-CHECKBOX-AUTHORITY-1.md §7.2(W1–W8 批次清单：每批卡清单/条数/依据，覆盖剩余 36 张 233 条) -->
- [x] **新增一条治理规则**：写入 `doc/09_COLLABORATION.md`（或等价位置）—— **"`[x]` 必须带 `verified:` 注释；`evidence_dir` 与 AC 勾选不一致时以 AC 注释为准"** <!-- verified: grep:### 4.3.1 存量 AC 的权威化标注@doc/09_COLLABORATION.md:165(三种标注+依据取值+分层判定+「AC 行内注释与 evidence_dir/status 不一致时以 AC 注释为准」) -->
- [x] **门禁通过**：`check.ps1` / `pins` / `inventory`；**不改任何 pin 与契约字节** <!-- verified: gate:check PASS(3 warnings) + gate:pins 18/18 PASS + gate:inventory 1/80/6=87 OK + App.Tests 955/0/11/966，全部本轮实测；未改任何 pin 与契约字节 -->

## 6. 已知风险

| 风险 | 缓解 |
|---|---|
| **批量改 40 张卡会污染历史** | 分批；每批单独 commit；**不改 AC 文本本身，只在行尾加注释** |
| **"自动验证"可能验证错东西** | 每条 `verified:` 必须写明具体命令/路径，可复现 |
| **我可能又误判**（本会话已 16 次） | 每条 `verified:` 都由我**实际执行**过一次；无法执行的标 `blocked:` |
| **改别人的卡 = 越权？** | 用户已明确指示做全项目清理；但**只改 AC 勾选与注释，不改结论/status** |

## 7. 执行记录（2026-11-15，DSH）

### 7.1 已完成 4 张 / 27 条（不重做）

| 卡 | 条数 | 标注构成 | 处置依据 |
|---|---|---|---|
| `CHAPTER-MANUAL-SORT` | 10 | 9 verified + 1 blocked | B1 试点；AC10 引用全量回归但 Core/Python 本轮未跑 → blocked |
| `V11R-C-RESEARCH-1` | 5 | 4 verified + 1 blocked | `evidence_dir` 原指向不存在目录，已修正为 `doc/design/theming/RESEARCH_V1.md` |
| `V1-RELEASE-SIGNING-1` | 4 | 3 not-applicable + 1 verified:human | 唯一 `human:user@2026-10-21`（真实人工裁决） |
| `FEA-04` | 8 | 8 blocked | **范围冻结卡**：`status:done` 指范围冻结完成，AC 属实现验收 → `实现未开始`；原 `<<PARTIAL>>` 移入注释 |

### 7.2 剩余 36 张 / 233 条的批次清单（§5 验收项 2）

| 批 | 卡 | 条数 | 依据与处理口径 |
|---|---|---|---|
| **W1** | `V11R-D-1`、`V11R-A-1`、`V11R-A-2` | 23 | `evidence_dir` 完整；DesignSystem 与 Run 契约实现卡，逐条核测试方法+日志 |
| **W2** | `V11R-B-1`…`B-5`、`V11R-C-1` | 42 | 6 张屏幕实现卡 AC 文本同构，但证据须**逐卡**核实（测试类/截图各不相同） |
| **W3** | `V11R-A-3`、`V11R-C-3`、`V11R-F0-1`、`UI-DESIGN-1` | 28 | 契约/退役/编辑命令；`UI-DESIGN-1` 属**设计冻结型**（逐条判：产出文档→verified，实现验收→blocked） |
| **W4** | `EXPORT-IPC-1`、`FEAT-CREATE-2`、`RUN-IPC-1`、`P15-C1`、`RELEASE-PACKAGE-1` | 30 | IPC/契约/打包；含旧 Tauri 面的架构归属判定 |
| **W5** | `GATE3-COVERAGE-MATRIX`、`GOV-PIN-LINEAGE-1`、`GOV-RESIDUAL-RUNTIME-IDENTITY-1`、`-IMPL-1` | 25 | 治理/矩阵；`GOV-PIN-LINEAGE-1` 卡面已自陈「未实施任何 AC」，原 `<<BLOCKED>>` 移入注释 |
| **W6** | `P02`、`M2-REGION-RETYPE-CORE`、`M2-SFX-MISROUTE-UI-MITIGATION`、`TASK-056` | 24 | 无 `evidence_dir`；旧架构（Tauri/WebView2）与范围冻结/设计卡 |
| **W7** | `M2-SFX-CORRECTION-EXPORTER`、`M2-SFX-DATA-INFRA`、`TASK-053`、`DIAG-M2-REGIONLESS-LOCK-CHANGED-001` | 23 | 无 `evidence_dir`；须先查卡面引用的实物是否存在（不存在即 blocked） |
| **W8** | `P20-AC4-FPS-1`、`MICA-FIX-1`、`P19`、`P20-MEM-OPT-1`、`FEA-07-AC5-NATIVE-1` | 26 | 度量/原生；`FEA-07-AC5-NATIVE-1` 已自陈 PARTIAL，原标记移入注释 |

**批次划分依据**（§3 的 B2–B5）：W1/W2/W4 属 B2（`evidence_dir` 存在且 AC 文本有可 grep 的符号）；
W3/W5/W8 属 B3（需先定位证据）；W6/W7 属 B3 中「无 `evidence_dir`」子集；
范围冻结/设计/旧架构卡（FEA-04、UI-DESIGN-1、M2-REGION-RETYPE-CORE、TASK-056、
M2-SFX-MISROUTE-UI-MITIGATION、P02、V11R-C-RESEARCH-1）按 §3 B5 口径处理为 `blocked`，
**不冒充 verified**。

### 7.3 治理规则落点（§5 验收项 3）

写入 [`doc/09_COLLABORATION.md`](../09_COLLABORATION.md) §4.3.1「存量 AC 的权威化标注（HTML 注释形式）」：
固定三种标注、`grep:/test:/file:/gate:/human:` 依据取值、分层判定口径，
并明确**「AC 行内注释与 `evidence_dir`/`status` 不一致时以 AC 行内注释为准」**。

### 7.4 复核方法（可复现）

```powershell
# 逐卡查看某卡 AC 行号与标注状态（工作区脚本，派生产物，不入 Git）
python "G:\CODEX\New Manga.workspace\tasks\AC-CHECKBOX-AUTHORITY-1\scan_ac.py" <CARD>
# 全量验收：40 张 / 260 条是否全部有可审计标注、正文未改、EOL 未翻转、file: 引用存在
python "G:\CODEX\New Manga.workspace\tasks\AC-CHECKBOX-AUTHORITY-1\verify_final.py"
```

等价的人工复核：`git diff --numstat doc/tasks/<CARD>.md` 的增删数必须等于该卡 AC 条数
（证明只加了注释、无 EOL 翻转、未改正文）。

### 7.5 门禁（§5 验收项 4）

`check.ps1` PASS(3 warnings)｜`verify_pins.ps1` PASS(18/18)｜`generate_api_inventory.py --check` OK(1/80/6=87)｜
`dotnet test App.Tests` **955 通过 / 0 失败 / 11 跳过 / 966**（与 STATUS 基线一致）。**未改任何 pin 与契约字节。**

### 7.6 W4 批次（IPC/契约/打包，30 条）

| 卡 | 条数 | 结果 | 要点 |
|---|---|---|---|
| `EXPORT-IPC-1` | 6 | 6 verified | 旧 Tauri 面历史交付（AD-002 已取代，仅存档）；四处同步 commit `a4c8f9ac05`、Rust 88 passed、4 条 Canonical sha256 磁盘复算 4/4 |
| `FEAT-CREATE-2` | 6 | 6 verified | 未知字段 fail-closed、零长度上限、白名单响应；`pytest tests/core` 535 passed（基线 515） |
| `RUN-IPC-1` | 6 | 5 verified + 1 blocked | AC4 缺成功路径与 host 层 typed 拒绝单测、AC4-3 真实往返 NOT_RUN（`evidence-layering.md` 层3 诚实缺口） |
| `P15-C1` | 6 | 6 verified | 契约文件交付（`8d083ee18` 仅 1 file/330 insertions，零产品代码）；G25 开放 4 行 / 禁用 11 行 |
| `RELEASE-PACKAGE-1` | 6 | 5 verified + 1 blocked | AC6 **缺 Handoff**（`doc/handoffs/` 无 `RELEASE-PACKAGE-1-*.md`，实测 `Test-Path=False`） |

### 7.7 全量结果（40 张 / 260 条）

| 标注 | 条数 | 占比 |
|---|---|---|
| `verified` | **184** | 70.8% |
| `blocked` | **70** | 26.9% |
| `not-applicable` | **6** | 2.3% |
| **无裸 `[x]`** | 0 | — |

**验收器实测**（`verify_final.py`）：40/40 卡、260/260 条均有可审计标注；
AC 正文未改（两类已批准例外见下方）；`git diff --numstat` 逐卡增删数 == 该卡 AC 条数（无 EOL 翻转）；
所有 `file:` 引用实测存在。

**Lead 逐项裁决**（8 个独立子 agent 的 20+ 项「需裁决」）记录在
`G:\CODEX\New Manga.workspace\tasks\AC-CHECKBOX-AUTHORITY-1\LEAD-DECISIONS.md`，要点：
- **降级 4 条**：`V11R-D-1` AC8（D-12 旧壳 reduced-motion 不生效）、`M2-SFX-CORRECTION-EXPORTER` AC4
  （T1b 产物不存在）、`MICA-FIX-1` AC1/AC2（**独立复核 r1 发现**：A/B 截图的 solid 帧实为 ChatGPT
  桌面窗口、`titlebar_pixel=-1`；AC2 证据是 JSON 内自述字符串而无原始日志）→ 说明 verified 判定确有对抗性复核。
- **升级 2 条**：`M2-REGION-RETYPE-CORE` AC1/AC4（实现在树内 + 被新壳消费 + 历史回归记录）。
- **维持 blocked 的关键拒绝**：`V11R-A-3` AC4（跨卡联合满足 ≠ 本卡达成）、`V11R-C-3` R1（tag 后 dry-run 未补）、
  `P19` AC1（正文要求 D+，用户已批准 D 替代）、`P20-MEM-OPT-1` AC2（正文 350MB，实测 443.3MB）。
- **与用户初始提示的 2 处偏离并说明理由**：`UI-DESIGN-1`（9 条）与 `M2-SFX-MISROUTE-UI-MITIGATION`（5 条）
  经逐条读 AC 文本确认为**设计交付物**，实物齐备且独立 Review 逐 AC PASS → 判 `verified`；
  该例外已写入 `09_COLLABORATION.md` §4.3.1「两类例外」第 1 条（独立复核 r1 的 P3-06）。

### 7.9 独立复核与返修（r1，verdict CHANGES_REQUESTED → 已处置）

复核：`ac-review`（独立上下文子 agent，未参与实现），被审 head `0e7bc1fc5`，
报告 `reviews/ac-review-r1.md`（P0/P1/P2/P3 = 0/3/8/8）。

| finding | 处置 |
|---|---|
| **P1-01** `MICA-FIX-1` AC1 证据不成立 | **已修**：AC1 → `blocked`。Lead 亲自读图确认 `titlebar-solid.png` 是 ChatGPT 桌面窗口（左侧 ChatGPT 侧栏、底部 GPT-6.1），画面内无 NewManga；`titlebar_pixel=-1` 亦证明取色失败。这是本轮唯一一处**已发布的虚报**，原样登记不淡化。 |
| **P1-02** 旧 Tauri 11 条 verified 与 §4.3.1 冲突 | **已裁决**：在 §4.3.1 增「两类例外」第 2 条（旧架构历史交付验收），并要求注释以「旧架构（已退出）历史交付」披露（`EXPORT-IPC-1`/`RUN-IPC-1` 已具备）。 |
| **P1-03** FPS 7 条 + MEM AC1 未披露旧架构 | **已修**：8 条注释追加「⚠ 旧架构（React/WebView2，已由 AD-002 退役）历史交付验收，非当前产品能力」。 |
| **P2-01** w4 批次无报告/无裁决时序 | **已修**：`LEAD-DECISIONS` 补 §八（w4 4 项裁决）与本轮 §十；任务卡 §7.6 记录 w4 结果。 |
| **P2-02** `RUN-IPC-1` AC5 无退出码 | **已裁决并披露**：维持 verified（`test result 0 failed` + `PACKAGED_EXIT code=0` 构成绿证），注释显式写明该形式缺口。 |
| **P2-03** `RELEASE-PACKAGE-1` AC1–AC5 未披露卡面 NOT_RUN 表 | **已修**：5 条注释追加「卡面测试要求表为旧计划态，依据是证据目录实物」。 |
| **P2-04** 6 张 gv3 卡 `check.ps1 -TaskPath` FAIL | **已记录不掩盖**：§4.3.1 增「已知门禁边界」段——该 FAIL 在父版本同样存在、非本次引入，消除需另立 Task 给 checker 加历史豁免。 |
| **P2-05** `verify_final.py` 提交后与 HEAD 自比失效 | **已修**：改为 `--base <commit>` / `AC_BASE` 指定基线，并以 `0b517259e`（首个标注提交的父）复跑归档。 |
| **P2-06** `V11R-B-4` AC3 理由错误 | **已修**：实际 `StudioBatchViewModel.cs:673` 有 `State = Projection is null ? Error : Partial` 赋值；理由改为「有赋值路径但无测试断言/无就地呈现」。 |
| **P2-07** 定位符格式（17 裸文件名 + 43 `@:行号`） | **已修**：提交 `895f3c852` 全部展开为完整相对路径，`verify_locators.py` 419/419 行内命中。 |
| **P2-08** MICA AC2 自述证据 | **已修**：AC2 → `blocked`（无原始日志，卡面记 NOT_RUN，同轮采集不可信）。 |
| P3-01…P3-08（8 项） | **已处置**：任务卡计数改为「降级 4 + 升级 2」；§4.3.1 措辞（「不再作为行末门禁标记」）、历史口径、设计卡例外已改；`TASK-056` 引用 :48→:49；`MICA` AC3 删除无关 :57 引用；`V1-RELEASE-SIGNING-1` 的 `human:` 补 `file:` 路径；NUL/CRLF 见 §7.8 与 §九。 |


### 7.8 附带发现：`doc/tasks/**` 控制字符损坏（另立 Task）

全仓库 **65 / 636** 个卡文件含 C 风格转义泄漏（`\v`→`0x0B`、`\a`→`0x07`、`\b`→`0x08`、`\f`→`0x0C`、
`\e`→`0x1B`、`\0`→`0x00`），使卡面文本不可 grep（`verification` 写成 `erification`）。
本任务**只修 AC 行内** 6 处（`V11R-B-1…B-5`、`V11R-C-1` 的 AC7 行，每处 1 字节），
其余 59 个文件与非 AC 行**不动**（超出「只加注释」授权）。详见 `LEAD-DECISIONS.md` §九。


