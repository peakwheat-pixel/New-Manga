# GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 AC7 书面裁决

- 裁决者: adjudicator-decl（独立上下文子 agent）
- 裁决时间: 2026-11-16T12:26+08:00
- 被审 head: `517072586`（branch `main`；git status clean，0 行 porcelain 输出）

---

## 0. 结论摘要

| 裁决问题 | 结论 | 一句话依据 |
|---|---|---|
| **1. AC7 判定** | **`BLOCKED`** | 测试命令 `EXIT=1`（3 failures），AC7 的集成验证不成立；解除阻塞必须动历史字节/冻结政策，均在本卡权限之外 |
| **2(a) 清理 160 处非裁定错误（改历史卡/证据）** | **不可行** | 直接违反 AGENTS.md:27/:32 字节保留、`doc/09_COLLABORATION.md:112-113,234`、本卡禁止范围 `doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md:64-66`；且有现成活 pin 会被改坏（见 §2a 实证） |
| **2(b) 放宽硬编码 7** | **作为 AC7 解卡：不可行；作为独立设计改进：部分可行，需另案** | 只放宽测试 :154 后 :157 仍失败（实测），要继续变绿只能删除/弱化真实失败的断言 = 改测试为变绿；但 AC5 原文「不以绝对计数为断言」与代码硬编码 7 确有口径冲突，属真实设计缺陷，应另立卡按 §4.4 先核验 |
| **2(c) 保持 BLOCKED + 另立 `GOV-DECLARATION-SCAN-CLEANUP-1`** | **可行（推荐路径）** | 唯一不动历史字节、又能恢复 fail-closed 语义的通道；需先拿 3 项 DSH 前置裁决（见 §2c） |
| **3. `test_user_data_root_is_now_protected` 是否独立缺陷** | **否——同一根因的下游症状**；但暴露 2 个独立风险（R-1 索引当前未保护 3 根、R-2 机器路径硬编码） | 受控实验证明：只要错误集合回到「7 条裁定身份」，真实 APPDATA 三根 100% 注册（errors=0 / residual warnings=7 / hits=1×3） |
| **是否需另立卡** | **需要**：①清理卡（必须）②绝对计数不变量设计卡（建议）③APPDATA 机器绑定可移植性小卡（建议） | 三层阻塞中，只有清理卡能解 AC7；②防回归；③是本裁决顺带发现的独立设计缺陷 |

**三条与委托方描述不一致、需纠正的事实**（详见正文）：

1. `test_user_data_root_is_now_protected` **不是**与 167 无关的独立问题：它失败是因为 residual 解释层整段未执行（先被 HIE 层 `SOURCE_DRIFT` 早退、再被 `len(index.errors)==7` 拒绝），保护根从未注册（§3）。
2. 167 的第一层阻塞不是「160 条历史声明错误」，而是 **冻结的 HIE 政策与 P22 快照 tracked 状态漂移**（`clean_workspace.py:1986-1988` 早退）。只清 160 条而不修 HIE 漂移，测试仍红。
3. 干净交付时点的 `errors=7 → 0` 证据存在**一处不可复现疑点**（GOV-UNTRACKED-BACKLOG-1.md 的 `CON` 声明表），建议在新卡 phase 0 复核（§6）。

---

## 1. AC7 判定

### 1.1 AC7 原文与实测

`doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md:52` 的 AC7 要求三命令实跑并记录命令与 EXIT、固定 head 交独立 Reviewer、集成复验后才 done。2026-11-16 本裁决者独立实测（输出见 §5）：

| # | 命令 | 结果 | EXIT |
|---|---|---|---|
| ① | `python -B tools/governance/tests/test_residual_runtime_identity.py` | Ran 12 tests / `FAILED (failures=3)` | **1** |
| ② | `pwsh -NoProfile -File tools/governance/check.ps1` | `PASS (3 warnings)` | 0 |
| ③ | `git diff --check` | 无输出 | 0 |

三个失败与委托方描述一致：

- `test_all_seven_errors_are_resolved`（`tools/governance/tests/test_residual_runtime_identity.py:133-136`）：`index.errors` 实得 167 条（断言 `== []`）。
- `test_protection_set_did_not_shrink`（同文件 `:149-157`）：`:154` 断言 `len(before.errors) == 7`，实得 167。
- `test_user_data_root_is_now_protected`（同文件 `:138-141`）：`catalog`/`data`/`derived` 的 `index.evaluate()` 全为 `[]`。

AC7 是**验证型 AC**：它不产出功能，只要求「三命令 + 独立 Review + 集成复验」这套验证链成立。该链条当前断在 ①，故不可能判 `MET`。

### 1.2 归因：不是本卡实现回归，是交付后仓库演化（关键新证据）

- 实现对交付 pin 字节未变（我逐一复算，等于 Canonical Evidence 表 `:99-105` 的 EV-05/06/07）：
  - `tools/governance/clean_workspace.py` sha256 = `a9b32959…d1b295` = EV-06
  - `tools/governance/residual-runtime-identity.json` sha256 = `2ce5cc2e…07dc384` = EV-05
  - `tools/governance/tests/test_residual_runtime_identity.py` sha256 = `03cd671d…1f06a7c2` = EV-07
- `git log d4ac54525..HEAD -- <上述三文件>` = **0 个提交**。即：测试与守卫自交付后从未被改过。
- 167 条 = **7 条裁定身份**（RRI-01…RRI-07 绑定错误，逐条在扫描结果中恰好出现 1 次，已验证）+ **160 条非裁定错误**。
- 160 条按「文件是否存在于交付树 `d4ac54525`」归因（我实测）：

| 归因 | 条数 | 文件数 | 说明 |
|---|---:|---:|---|
| 交付后新增的文件 | **154** | 105 | 状态：done 75、closed_with_limitations 13、JSON 证据 12、**陈旧** in_progress 2、**陈旧** in_review 2、无 frontmatter 1 |
| 交付前已存在且此后未改动的文件 | **6** | 5 | P09 closeout ×2、P14 self-review r1/r2 ×2（FILE_UNREADABLE）、GOV-UNTRACKED-BACKLOG-1 ×1（`CON` bare name）、HIE 政策自身 SOURCE_DRIFT ×1 |

按错误码（全部 167）：`TABLE_SCHEMA_INCOMPLETE 53 / DECL_RELATIVE_UNRESOLVED 27 / DECL_ENV 20 / DECL_GLOB 16 / DECL_DESTINATION_UNRESOLVED 12 / TABLE_DELIMITER 10 / DECL_UNKNOWN_DISPOSITION 10 / DECL_TRAVERSAL 7 / FILE_UNREADABLE 4 / DECL_RELATIVE_AMBIGUOUS 2 / JSON_PARSE 2 / DECL_BARE_NAME·DECL_MISSING_SOURCE·SOURCE_DRIFT·TABLE_ROW_ARITY 各 1`；按目录 `doc/ 139、verification/ 27、tools/ 1`。与委托方数字一致。

**「当前在办零命中」基本成立，但需修正口径**：当前 STATUS 指定的 `MAINT-1-RELEASE-MONITOR` 0 命中；但仍有 2 张 frontmatter 停在 `in_progress` 的旧卡（`INSTALLER-MATRIX-1`、`SIDECAR-REBUILD-1`）各 1 条、1 张 `in_review`（`GIT-CLEAN-PUBLICATION-1`）2 条命中——它们是**陈旧状态**，不是当前在办工作，但清理时必须显式确认其活性，不能按文件名批处理。

### 1.3 三层阻塞（这是 AC7 无法在卡内解除的真正原因）

**L1（第一层，冻结政策漂移）**：`tools/governance/historical-evidence-interpretation.json` 把 `verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md` 绑定为 **untracked** 的 NUL/不可读历史件（政策 `:233-235` 记录的错误消息是 `untracked markdown ... contains NUL bytes`；文件本身 sha256=`7ebd7d40…`，与 `doc/tasks/P22.md:95` 一致）。但该文件在 **2026-10-22 17:45:50** 的提交 `ee755d4bb`（"verification: commit the remaining 406-file evidence backlog"）中被入库，变成 tracked。扫描器因此产出 `SOURCE_DRIFT: historical input tracking changed`（我实测唯一一条，`file=tools/governance/historical-evidence-interpretation.json`）。

而 `tools/governance/clean_workspace.py:1986-1988` 规定：只要 index 里出现 HIE/广播保全政策的错误，**residual 层直接 `_finish_declaration_scan` 早退**。于是：7 条裁定身份没有被降为 warning、APPDATA 三根没有被注册、`DECL_RESIDUAL_RUNTIME_PRESERVED` warning 数为 **0**（审计实测）。**这单独一条 SOURCE_DRIFT 就足以让 test 1/2/3 全红。**

**L2（第二层，历史声明债务）**：即便 L1 修好，residual 层走到 `clean_workspace.py:2172-2173` 时仍会因 `len(removed) == 7 and len(index.errors) == 7` 不成立而 `ERROR_MISMATCH`；异常路径 `:2206-2211` 只给原 index 追加一条错误并返回，`:2148` 暂存的 `pending_protective` 全部丢弃。所以 154 条新增声明错误必须先被清理或经裁定绑定。

**L3（第三层，结构性绝对计数耦合）**：`:2172` 的 `len(index.errors) == 7` 与 `:2189` 的 `require(not staged.errors)` 把「residual 层可应用」绑定到「全仓声明错误数恰好为 7」。仓库只会继续增长，**任何后续卡新增一条声明错误都会再次击穿**（2026-10-22 之后已经实际发生了一次：154 条）。这不是一次性数据债，是设计缺陷。注意 AC5 原文（`:50`）明确写「不以绝对计数为断言，遵守 r2 口径条款」——**实现与 AC5 口径互相矛盾**，该矛盾必须在 L3 裁决中处理。

### 1.4 为什么是 `BLOCKED` 而不是 `PARTIAL`

- 治理规则：`doc/09_COLLABORATION.md:130-135` 规定 `[ ]` 只允许 `PARTIAL`/`BLOCKED`；`:165-234`（§4.3.1）规定「部分子项未达成 / NOT_RUN / PARTIAL → `blocked`，并点名缺哪项」。AC7 行内已用 `<!-- blocked: ... -->`，与此一致。
- `PARTIAL` 的语义是「本卡范围内还有可继续的残余工作」。这里剩余工作全部在卡外：(i) 修 HIE 政策并重批 digest；(ii) 清理/解释 159 条历史声明；(iii) 裁决绝对计数不变量。三者都被本卡 `:62-68` 禁止范围或 `:56`（不改既有解析/判定/错误码语义）挡住，且需要 DSH 书面裁定与新卡授权。
- 点名缺口：①测试命令 EXIT=1（`test_all_seven_errors_are_resolved`、`test_protection_set_did_not_shrink`、`test_user_data_root_is_now_protected`）；②154 条交付后新增声明错误；③P22 tracked 化的冻结政策漂移；④真实 APPDATA 三根当前不在保护索引中。
- 附带治理问题（不改变判定，但必须记录）：卡 frontmatter `status: done` 与 AC7 原文「集成复验后才 done」冲突；且 `check.ps1` 默认只检查 14 个当前文档 + STATUS 指定的当前 Task（`tools/governance/check.ps1:208-223,229-248,996-997`），**本卡不在其 scope 内**，所以「check.ps1 PASS (3 warnings)」不能作为本卡 AC 的证据。按 §4.3.1 权威优先级（`doc/09_COLLABORATION.md:211-216`），AC 行内注释优先于 `status`/`evidence_dir`——应以 AC7 的 `blocked` 注释为准。

---

## 2. 三条修复路径逐条评估

### 2(a) 清理 160 处非裁定错误（改历史卡与历史证据里的声明表/JSON）——**不可行**

违反的条款（逐条已核实）：

1. **AGENTS.md:27、:32**：「历史署名、冻结 Review、**日志、manifest 和 evidence pin 保持原字节**」；2026-10-31 裁决同句「历史 Review、署名与 evidence pin 保持原字节」。
2. **AGENTS.md:23**：「历史 Task 文件保留为证据；只有 Rebaseline Plan 明确激活且范围已冻结的 Task 才允许实施。」
3. **`doc/09_COLLABORATION.md:112-113`**：「v1/v2 Task 保持原状，**不回溯补标**」；`:234`：「清理边界。只允许追加行内注释与勾选符号；不得改写 AC 正文、`status` 或 `evidence_dir`。」——160 条错误的修复必然要改写声明表行/JSON 字段，超出「追加注释」边界。
4. **本卡自身**：`:64`「不修改 `doc/tasks/P19.md`、`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`、`verification/P19-UI-FIX-1/resource-manifest.json` 或**任何历史原件字节**」；`:66`「不全局忽略任何错误码」；`:56`「不改任何既有解析、判定、错误码语义」。

**实证（不是抽象条款）**：`doc/tasks/FEA-11-RENDITION-1.md:198` 有 EV-7 **CANONICAL** pin：`verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` @ `3eda60ac8`，sha256=`8ded4d9ba786dbabf5a9705455c6ef91cd09353024c8272e3656cc260ebd26f8`。我实测该文件当前 sha256 **恰好等于**该 pin（bytes=5784），而它正是 160 条错误里的 2 条（`DECL_DESTINATION_UNRESOLVED` + `DECL_GLOB`）。改它 → 立即毁掉一个已冻结的 CANONICAL evidence pin；要「修好」就得回头改写一张 `done` 卡的 Canonical Evidence 表——正是字节保留禁止的动作。同类情况还有 12 个 JSON 证据文件、2 个 JSON_PARSE（`verification/FEA-07-AC5-NATIVE-1/evidence/displays-baseline-20261109-08390{8,9}.json`）、4 个 FILE_UNREADABLE（NUL 字节历史件）。

**正确的修复机制本来就不是改字节**：仓库已有三层「解释/例外」政策——`tools/governance/historical-evidence-interpretation.json`（raw non-declaration bindings）、`non-declaration-json-exceptions.json`（path+sha256 字节绑定豁免）、`broad-root-preservation.json`（broad-root 保全）——它们的存在意义就是**在不改历史字节的前提下，把已知历史形态解释成非声明/已保全**。因此 (a) 的可行版本是「扩展解释层政策 + 重批 digest」，不是「编辑历史卡」。

**结论：不可行**（在现有授权与卡范围内）；把一个 160 条的字节编辑包说成「清理数据债」会同时破坏 pin 体系与历史可审计性。

### 2(b) 放宽 `test_residual_runtime_identity.py` 的硬编码 7——**作为 AC7 解卡不可行；作为独立设计改进部分可行（需另案）**

先拆清楚「硬编码 7」有两处、性质不同：

- **测试侧**：`:154` `assertEqual(len(before.errors), 7)` 是 `test_protection_set_did_not_shrink` 的**前置基线断言**；真正被测的不变量是 `:155-157`（保护集合超集 + 严格变大）。
- **生产侧**：`clean_workspace.py:2172` `len(removed) == 7 and len(index.errors) == 7` 与 `:2189` `require(not staged.errors)` 是**治理语义**（fail-closed 的全仓零错误要求）。

**实测关键事实**：把 `:154` 单独放宽也不会让 `test_protection_set_did_not_shrink` 变绿——我实测生产扫描与「屏蔽 residual 层」的扫描都是 `errors=167 / protected=5582`，于是 `:157` 的 `assertGreater(5582, 5582)` = `False`。要继续变绿，只能连 `:157` 一起删除/弱化——而那正是「residual 层没生效、3 根用户数据未保护」的真实失败。这就是判据的分水岭。

**判据（改进测试 vs 为变绿改测试）**——建议 DSH 用这 5 条：

1. **检测力**：改动后，原缺陷类（residual 层中止 / 保护根缺失 / warning 数不是 7）是否仍会变红？
2. **生产路径**：被断言的性质是否仍在**生产代码路径**上验证，而不是只搬进 fixture？
3. **生产行为**：改动后生产侧是否仍在同样的错误状态（audit EXIT=2、3 根未保护）？若是，则只是把探测器关掉。
4. **规格先行**：AC/规格是否先经 DSH 书面裁定与独立 Review 修改，再改实现/测试（§4.4 `doc/09_COLLABORATION.md:236-251`：改变校验语义前必须定义受影响全集、实测基线矩阵）？
5. **可诊断性**：失败信息是否仍指向真实缺口（而不是被「容忍 159 条无关错误」的规则淹没）？

按此判据：**现在把 7 放宽 = 绿洗**（1/2/3/4 全不满足，且 154 条无关错误并非「环境噪声」而是真实声明完整性缺口）。但反过来，`len(index.errors) == 7` 这种绝对计数确实与 AC5 `:50` 的「不以绝对计数为断言，遵守 r2 口径条款」**口径冲突**，是一个应当独立裁决的设计缺陷：更符合规格的形态是「**相对不变量**」——精确移除 7 条绑定错误且每条各出现一次、其余基线错误**原样透传**、保护集合只增不减、residual warning 恰 7 条；同时 audit 仍应对剩余错误保持 EXIT=2（错误不被掩盖）。这一改动是**治理语义变化**，必须另立卡、按 §4.4 先核验、独立 Review，并且**必须先完成 L2 数据清理**，否则改完也不可能让 AC7 的 `errors == []` 变绿。

**结论**：作为 AC7 解卡手段——**不可行，且不建议**；作为独立设计改进——**部分可行，需另案**（先清数据、再改不变量、再重跑 AC7）。

### 2(c) 保持 AC7 BLOCKED，另立 `GOV-DECLARATION-SCAN-CLEANUP-1` 做清理——**可行（推荐）**

这是唯一「不改历史字节、又能恢复 fail-closed 与 APPDATA 保护」的通道。**前置裁决清单**：

1. **Ruling A（跟踪状态语义）**：P22 快照 `ee755d4bb` 被 tracked 化，与冻结 HIE 绑定（untracked 形态）冲突。必须裁定三选一：(i) 更新 HIE 绑定到 tracked 形态并重批 `HISTORICAL_EVIDENCE_DIGEST`（同时核验 P14/P09 等绑定是否仍匹配——HIE 政策里确有 P09/P14 的绑定条目）；(ii) 恢复 untracked（`git rm --cached` 保留工作区字节）——与「406-file backlog」的入库决策正面冲突，需说明；(iii) 重新设计绑定为 tracking-agnostic。**不做 A，后面全白做**。
2. **Ruling B（历史声明债务分类口径）**：159 条（160 − HIE 自身 1 条 SOURCE_DRIFT）逐条归入：B1「历史形态，可由解释层绑定为非声明/已保全」（如 53 条旧式 Canonical Evidence 缺 path 列 → 对应 225/608 张终态卡的结构性历史形态，我实测 608 张终态卡中 225 张无 `## Canonical Evidence` 节，与委托方数字吻合）；B2「真实缺陷，需修数据但不得毁 pin」（须先确认该件是否仍被活 pin 引用）；B3「扫描器规则误报，需单独裁定规则」（不得用按错误码/前缀/正则的整体忽略——本卡 `:66` 已禁止，且是 r208 失败模式重演）。**判定口径必须先冻结再实施**，否则就是「为清零而清零」。
3. **Ruling C（持久化不变量）**：是否把 L3 的绝对计数耦合改为 §2b 描述的相对不变量。按 §4.4，必须先在**不动生产**的前提下产出：受影响全集（`:2172`/`:2189`/`:2191-2195`/`:2840` 的调用面）、代表性/边界样本实测、基线错误矩阵；核验结果与假设不符则假设作废。若不做 C，清理完成当天 audit 会再绿，下一张卡再红——这已经发生过一次。

**新卡必须写死的边界**：

- `allowed_paths`：`tools/governance/historical-evidence-interpretation.json`（+ 新政策文件如需要）、`clean_workspace.py` 的 digest 常量与（若 Ruling C 批准）不变量代码、`tools/governance/tests/**`、`verification/GOV-DECLARATION-SCAN-CLEANUP-1/**`、本卡/Handoff/STATUS/PLAN/LEDGER。
- **禁止**：修改任何历史卡、历史证据、`RESOURCE-MANIFEST.json` 的字节；禁止改 7 条 residual 绑定（`tools/governance/residual-runtime-identity.json:10-190` 的 RRI-01…RRI-07 身份必须原样保留）；禁止全局忽略错误码/前缀/正则；禁止缩小保护集合。
- **交付物**：baseline/after 两轮 `--audit-declarations` JSON（`errors` 单调下降、`protected_roots` 不减、`DECL_RESIDUAL_RUNTIME_PRESERVED` 恒为 7）；逐条 disposition 表（159 行，注明 B1/B2/B3、依据、是否被活 pin 引用）；测试日志（含命令/EXIT/解释器头，按 `doc/09_COLLABORATION.md:359` 证据纪律）；`check.ps1`、`git diff --check`。
- **流程**：上下文独立的 Reviewer（2026-10-31 口径：同一会话/实例不得自审，作者可派子 agent）；集成复验后回填 AC7 证据，才能把 AC7 改为 `[x] <<MET>>` 并恢复 `done`。
- **建议拆分**：把 Ruling A 的 HIE 漂移小修与 Ruling B 的 159 条分类拆成两张卡（A 卡 1 天级、B 卡多天级），避免一张卡既改政策又改数据、Review 面过大。

**结论：可行**。这是本裁决推荐的唯一主路径。

---

## 3. `test_user_data_root_is_now_protected` 是否独立缺陷

**判定：(a) 真实治理缺口（当前索引确实未保护三根），但（就本次失败而言）不是独立缺陷——它是 L1/L2 同一根因的下游症状；不是 (b) 测试前提过期，也不是 (c) 本轮环境问题。**

### 3.1 排除 (b)/(c) 的核实命令与结果

1. **目录真实存在**：`$env:APPDATA` = `C:\Users\49745\AppData\Roaming`；`Test-Path` 对
   `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/{catalog,data,derived}` 三路径全部 `True`。
2. **策略目标当前可解析且与政策一致**：用 `index._resolve_identity()` 逐目标实测，`normalized == real == policy.targets[i].normalized` 三根全部 `match=True`（策略位置：`tools/governance/residual-runtime-identity.json:128-141`（RRI-06）与 `:165-178`（RRI-07））。
3. **当前扫描结果**：`protected_roots=5582`，`evaluate('.../catalog'|'.../data'|'.../derived')` 全为 `[]`；`DECL_RESIDUAL_RUNTIME_PRESERVED` warning = **0**。
4. **代码路径**：`clean_workspace.py:1986-1988` 因 HIE 错误早退；即便 HIE 修好，`:2172` 的 `ERROR_MISMATCH` 也在 `:2174-2195` 之前抛出，`:2206-2211` 的异常路径只对**原 index** 加一条错误并返回，`:2148` 的 `pending_protective` 从未提交 → 三根必然不注册。
5. **受控实验（只读，写在 `%TEMP%`，未改仓库）**：构造临时 git 仓库，放入三份**字节相同**的 origin 文件（P19.md、两份 resource-manifest.json）、真实策略的**真实 APPDATA 绝对目标**（保留不动），只在内存里 `mock.patch` 摘要常量（与本卡自带 fixture 测试同一手法）。结果：
   ```
   errors: 0
   residual warnings: 7
   evaluate(catalog) hits=1
   evaluate(data) hits=1
   evaluate(derived) hits=1
   protected roots: 40
   ```
   即：**当且仅当「错误集合回到恰好 7 条裁定身份」时，真实 APPDATA 三根 100% 注册**。测试断言本身、路径、策略目标都没有缺陷。

### 3.2 因此

- **不需要**为 `test_user_data_root_is_now_protected` 单独立卡：修 L1+L2 后它会自动绿；单独立卡只会把一个症状拆出去重复排查。
- 但本次实测确实暴露 **2 个独立风险**，建议在新卡或独立小卡中显式登记：
  - **R-1（治理缺口，当前生效）**：现 head 的保护索引里没有 3 个真实用户数据根，AC3 的保护保证在真实扫描中未成立。缓解事实：`clean_workspace.py:2840-2864` 在 `index.errors` 非空时整体 `REFUSED`（fail-closed，不会误删），所以**没有数据删除风险**，但治理清理工具当前完全不可用（这本身是可用性/治理完整性问题）。产品侧删除保护由另一套 `ProtectionPolicy`（`src/application/maintenance/ports.py:190`、`src/bootstrap/core_service.py:2045`）承担，本次未跑产品测试、未验证其受影响（见 §6）。
  - **R-2（可移植性缺陷，独立于 167）**：政策 `:128-141/:165-178` 与测试 `tools/governance/tests/test_residual_runtime_identity.py:29` 把用户路径硬编码为 `C:/Users/49745/...`。换用户/机器时，即便全仓 0 声明错误，`require_present` 也会 `RESIDUAL_TARGET_MISSING`，scan 永久红、测试永久红。这是设计缺陷（不是环境问题，因为本机路径存在），建议单独立小卡裁决「机器绑定的历史身份如何跨机表达」（在现政策「不展开环境变量/不通配」的禁令下，需要 DSH 给出新形态，例如按语义路径 + 本机化绑定 + 显式跨机 fail-closed 说明）。
- 顺带确认 **AC6（`:51`）阻塞为真**：7 类负例中「保护集合回退」只有 `:2191-2195` 的正面断言（`test_protection_set_did_not_shrink`），没有构造回退触发 `PROTECTION_REGRESSION` 的负例；AC6 与 AC7 同属「未完成集成验证」，建议一并纳入清理卡的收口（Ruling C 的相对不变量重写顺带补这个负例）。

---

## 4. 按优先级排序的动作清单

| # | 动作 | 谁做 | 大概几步 | 风险 |
|---|---|---|---|---|
| **P0** | 记录本裁决：Task 的 AC6/AC7 保持 `[ ]` + blocked 注释并链接本文；把 `status: done` 与「集成复验后才 done」的冲突落成显式 limitation（或在下一次 DSH 收口时改 `closed_with_limitations`）；STATUS/LEDGER 同步说明 | DSH | 2–3 | 低（只改当前导航/卡面，不碰历史字节） |
| **P1** | 出 3 项前置裁定：Ruling A（P22 tracked 化后冻结绑定怎么办）、Ruling B（159 条历史声明债务的分类口径）、Ruling C（绝对计数不变量是否重写；按 §4.4 先做受影响全集与基线矩阵核验） | DSH | 1 会话（C 需先核验） | 中（Ruling 错 → 后续白做/掩盖真实错误） |
| **P2** | 开卡 `GOV-DECLARATION-SCAN-CLEANUP-1`（建议再拆 A=HIE 漂移小修 / B=159 条分类）：冻结 `allowed_paths`、禁止改历史字节、冻结 7 条绑定、写死验收指标；**phase 0 顺带复核 EV-03/EV-04 可复现性**（§6） | DSH | 2–3 | 低—中（范围写不清会重演字节风险） |
| **P3** | 实施：先修 HIE P22 漂移（policy+digest+tests，验证 P09/P14 绑定恢复）；再按 B1/B2/B3 逐类绑定或修复 159 条；每批验证 `protected_roots` 不减、7 条 residual warning 恒在、`errors` 单调下降、`SOURCE_DRIFT`/`POLICY_*` 仍 fail-closed | Owner（Codex 或 DSH 派发） | 6–10 | 中—高（触碰冻结政策；分类错会掩盖真实缺口） |
| **P4** | 上下文独立 Reviewer 审查固定 head（重点：有没有把真实错误解释掉、有没有缩小保护面、digest 重批是否留证） | 未参与实现的 Reviewer（Codex/ZCode/DSH 子 agent，2026-10-31 口径） | 0.5–1 | 低（相对前序） |
| **P5** | 集成复验：重跑 AC7 三命令并记录命令+EXIT；确认 12/12、audit 0 errors / 7 residual warnings / 保护根≥1945、`check.ps1` PASS、`git diff --check` 0；回填 AC6/AC7 与 Canonical Evidence，再判 `done` | DSH | 2–3 | 低（唯一能让 AC7 变绿的动作） |
| **P6** | 另立「不变量重写」卡：把 `:2172`/`:2189` 改为相对断言（不动历史字节），按 §4.4 出基线矩阵，补「保护集合回退」负例（顺带解 AC6） | DSH + Owner | 3–5 | 中（改 fail-closed 语义，必须独立 Review） |
| **P7** | 另立小卡：APPDATA 机器绑定可移植性（R-2） | DSH | 2–3 | 低—中（动 policy 形状，需重批 digest） |

**明确不建议**：①任何「改测试/删断言让它绿」的动作；②任何编辑历史卡、历史证据、`RESOURCE-MANIFEST.json` 字节的动作；③任何按错误码/前缀/正则的整体忽略（标准错误做法，且直接违反本卡 `:66` 与 r208 教训）；④在未修 L1 前先清 154 条（顺序反了会浪费一轮验证）。

---

## 5. 我实测的命令与输出（原始摘录）

### 5.1 环境/HEAD

```
$ git rev-parse --short HEAD        → 517072586
$ git rev-parse --abbrev-ref HEAD   → main
$ git status --porcelain            → （空，0 行）
$ git show -s HEAD                  → 517072586d90b754e170a4afc7d417aece23dbba 2026-11-16 12:03:03 +0800
```

### 5.2 命令 ①（AC7 第一条）

```
$ python -B tools/governance/tests/test_residual_runtime_identity.py
F.FF
FAIL: test_all_seven_errors_are_resolved ... AssertionError: Lists differ: [...] != []
First list contains 167 additional elements.
FAIL: test_protection_set_did_not_shrink ... AssertionError: 167 != 7
FAIL: test_user_data_root_is_now_protected ... AssertionError: [] is not true : expected protection for catalog
Ran 12 tests in 19.332s
FAILED (failures=3)
EXIT=1
```

### 5.3 命令 ②③

```
$ pwsh -NoProfile -File tools/governance/check.ps1
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\MAINT-1-RELEASE-MONITOR.md
WARN: 存在 12 个非终态 Task（见 TASK_LEDGER）...
WARN: doc/STATUS.md 已达到预算的 80%：3033 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6990 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0

$ git diff --check
（无输出）
EXIT=0
```

### 5.4 审计（AC5 工具，输出到 `%TEMP%`）

```
$ python -B tools/governance/clean_workspace.py --audit-declarations --out %TEMP%/rri-audit-<guid>
declaration audit: 6727 declaration(s), 5582 protected root(s), 167 error(s), 718 warning(s)
...
report: C:/Users/49745/AppData/Local/Temp/.../declaration-audit.json
EXIT=2
```

审计 JSON 复核：`errors=167`；目录分布 `doc:139 / verification:27 / tools:1`；`DECL_RESIDUAL_RUNTIME_PRESERVED` warning = **0**；`schema_version/tool/mode/generated_at/scan/counts/errors/warnings/report_sha256` 字段齐全。

### 5.5 策略与 7 条绑定

```
policy keys: schema_version, purpose, approved_research, bindings
bindings: 7（RRI-01 ALREADY_ABSENT_PATH / doc/tasks/P19.md:112-114 ×3；
          RRI-04 NON_IDENTITY_RECORD · RRI-05 NON_IDENTITY_PROSE ·
          RRI-06 PRESERVE_ROOTS · RRI-07 PRESERVE_ROOTS @ 两份 manifest）
逐条实测：7 条绑定错误在 index.errors 中各出现恰好 1 次（count=1）
RRI-01..03 目标：lexists=False（不存在）
RRI-06/07 目标：_resolve_identity 返回 normalized==real==policy.normalized（match=True），目录存在
```

### 5.6 归因与结构证据

```
impl 三文件 sha256 与 EV-05/06/07 pin 完全一致；git log d4ac54525..HEAD -- <三文件> = 0 commits
167 = 7 裁定身份 + 160 非裁定
160 = 154（交付树 d4ac54525 中不存在的 105 个新文件）+ 6（交付前已存在/未改动文件：
      P09 closeout ×2、P14 r1/r2 ×2、GOV-UNTRACKED-BACKLOG-1 ×1、HIE 自身 SOURCE_DRIFT ×1）
交付后新增文件状态：done 75 / closed_with_limitations 13 / JSON 证据 12 /
      in_progress 2（陈旧）/ in_review 2（陈旧）/ 无 frontmatter 1
冻结证据数字：终态卡 608 张中 225 张无 `## Canonical Evidence`（我实测，与委托方 225/608 吻合）
HIE 漂移：ee755d4bb 2026-10-22 17:45:50 把 verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md 入库
当前 HIE 错误：SOURCE_DRIFT "historical input tracking changed: verification/P22/...snapshot-7ebd7d40.md"
```

### 5.7 2(b) 的实测前提

```
生产扫描：        errors=167 protected=5582
屏蔽 residual 层：errors=167 protected=5582
missing（before 的保护根不在 prod 中）=0
assertGreater(len(prod.protected), len(before.protected)) = (5582 > 5582) = False
→ 只放宽 :154 不会让 test_protection_set_did_not_shrink 变绿
```

### 5.8 §3 受控实验（`%TEMP%`，只读）

```
scanned: {'markdown': 2, 'json': 2, ..., 'declarations': 50, 'errors': 0, 'warnings': 17}
errors: 0
residual warnings: 7
evaluate(catalog) hits=1
evaluate(data) hits=1
evaluate(derived) hits=1
protected roots: 40
```

### 5.9 现成活 pin 与字节冲突实证（2a）

```
verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json sha256 = 8ded4d9ba786dbabf5a9705455c6ef91cd09353024c8272e3656cc260ebd26f8（bytes 5784）
doc/tasks/FEA-11-RENDITION-1.md:198  EV-7 CANONICAL pin 指向同一 sha256 @ 3eda60ac8
该文件对应的 2 条错误：DECL_DESTINATION_UNRESOLVED（'Same source location (...)） / DECL_GLOB（'tests/fea11/test_source_rendition_*.py（tmp_path 运行时生成）'）
```

---

## 6. 未能独立验证的项

1. **EV-03/EV-04 的可复现性疑点（重要）**：冻结证据 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/raw/audit-baseline/declaration-audit.json` 记录 `errors=7`、`.../raw/audit-resolved/declaration-audit.json` 记录 `errors=0`。但我实测：
   - `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` 的 blob 在交付提交 `d4ac54525` 与当前 HEAD **完全相同**（`git rev-parse d4ac54525:<path>` = `HEAD:<path>` = `576f3a5c…`），且 `git diff d4ac54525 -- <path>` 无差异；
   - 该文件 `:141` 的 `CON` 声明行（`| CON (reserved name) | \`CON\` | PRESERVE_REFERENCED | ...`）在当前扫描中产生 `DECL_BARE_NAME`；
   - `DECL_BARE_NAME` 规则在 base `8e31aaa1d` 与交付 `d4ac54525` 的 `clean_workspace.py` 中都已存在（`git grep -c` = 2），而交付版 `clean_workspace.py` sha256 与当前一致（EV-06）。
   → 按「同一 scanner + 同一文件字节」的逻辑，交付时该错误也应出现，与冻结证据的 7/0 冲突。证据 JSON 未记录 `repo_root`/文件集，无法判定当时扫描输入是否不同（例如是否在 linked worktree / 过滤树中生成）。**这不足以否定 AC5，但属证据完整性问题**，建议清理卡 phase 0 用 `git archive d4ac54525` 重建扫描基线复核。
2. 未检查 linked worktree `G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` 的实际状态（本裁决只读主 checkout，未 add/checkout/worktree 操作）。
3. 未跑产品侧删除保护测试：产品删除走 `ProtectionPolicy`（`src/application/maintenance/ports.py:190`、`src/bootstrap/core_service.py:2045`），与 `clean_workspace.py` 的 `ProtectionIndex` 是两套实现；只确认了后者在 errors 非空时 `:2840-2864` 整体 `REFUSED`（fail-closed，无删除风险），未验证前者是否受影响。
4. 未运行完整治理测试套件（只跑了本卡测试、`check.ps1`、`git diff --check`）；未跑 `--apply`/任何删除路径；未跑 `test_path_header_compat.py` / `test_ac_gate.py`（交付日志曾跑，本次未复跑）。
5. 未逐条核对 159 条非裁定错误的具体政策分类（只做文件级/状态级/错误码级归因）；B1/B2/B3 的逐条判定属于清理卡的工作量。
6. 未验证「154 条新增文件错误全部来自历史卡与历史证据」的逐文件结论，只验证了「105 个文件均不在交付树中 + 其 105 个文件的状态分布」；其中 4 个文件 frontmatter 呈 `in_progress`/`in_review`（陈旧），其活性需清理卡确认。
7. 未评估 `TABLE_SCHEMA_INCOMPLETE`（53 条）与「225/608 张无 Canonical Evidence」的精确对应关系（只验证了两个独立计数；未逐卡映射）。

---

## 声明

- 本裁决署名 **adjudicator-decl**，为全新独立上下文的子 agent；被审 head 为 `517072586`，审查期间仅使用只读命令（`git rev-parse`/`git log`/`git ls-tree`/`git cat-file`/`git grep`/`git diff`、文件读取、`python -B` 扫描与 fixture 实验）与一次 `--audit-declarations --out "%TEMP%"`（输出落 `%TEMP%`，不在仓库内）。
- **未修改仓库任何文件**：无 `git add`/`commit`/`checkout`/`reset`/`stash`/`rm`/`restore`、无写仓库文件、无删除/迁移/归档；`git status --porcelain` 审查前后均为空。本文件的写入目标是 `G:/CODEX/New Manga.workspace/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/adjudication-ac7-2026-11-16.md`（仓外工作区，不属于仓库文件）。
- 本裁决只基于仓内可复核事实与实测输出，不依据任何被裁方期望的结论；对委托方提供的三点描述，已在 §0/§1/§3 中逐条核实并纠正（test3 与 167 同根、L1 不是 160 条本身、清 160 条不足以让 AC7 变绿）。
- 未参考未来状态或未实现的修复；`BLOCKED` 判定在「L1+L2+L3 任一未裁决」的前提下成立；若 P1 裁决完成并落地 P3–P5，本裁决应作废并由新的 Reviewer 在固定 head 上重新判定 AC7。

FINAL: BLOCKED — 三命令中测试 EXIT=1 且 3 个生产断言真实失败；impl 字节与交付 pin 一致、交付后 0 次改动，根因是交付后 154 条新增声明错误 + P22 tracked 化导致冻结 HIE 绑定漂移 + 绝对计数零错误耦合，解除须在卡外做历史声明债务清理与不变量裁决，非本卡权限内可完成。
