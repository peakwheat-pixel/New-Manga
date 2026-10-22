# Review：P02 Stage A Safe Foundation — 定向修订 r2（非作者正式复审）

| 字段 | 值 |
|---|---|
| task_id | `P02`（Task `status: in_progress`；本 Review **不代表** P02 完成） |
| kind | verification（Stage A 交付复审，非范围 Review） |
| reviewer | DeepSeek Harness（非作者） |
| author / Owner | Antigravity |
| integrator | Codex |
| repository / worktree | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` |
| branch | `agent/antigravity/P02-real-webview-harness` |
| base_commit（diff base） | `5de8d44c784cbd20b23bcd41a8f1a7258c7addff` |
| reviewed_head（r2） | `9b82e97b8aadc5b6b8710e03b5128a608697f56e` |
| reviewed_tree（作者声明） | `7fe67d0fb9bfc95e579c0fbda539de85eb73e4f4`（**本次未能独立复核**，见 §9） |
| 前序 head（r1） | `972049f991b5c119555647eeea816e89dd4769f3` / tree `657095fa6790b6d21091dd58f9f862bc08818455` |
| P02 行为基线 | `241ff3b70b6fc0490ea238efd486cc707f849031`（Task frontmatter 未变） |
| scope contract SHA-256 | `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`（**未能独立复核**） |
| 前序 decision | `changes_requested`（P0/P1/P2/P3 = 0/1/6/5，F-01–F-12 open；报告 `doc/reviews/P02-972049f9-dsh-review.md`） |
| **本 r2 decision** | **`changes_requested`** |
| **本 r2 计数** | **P0/P1/P2/P3 = 0 / 0 / 2 / 8**（open = 10；F-01–F-12 中 9 项 closed、1 项仍 open、2 项 partial） |
| 审查方式 | 纯只读；**未运行** Cargo/Tauri/sidecar build、UI 自动化、任何测试；**未修改/创建/删除/暂存任何文件**；**未接触**用户漫画库/生产数据/Lock/Revision/凭据 |

---

## 1. 范围与覆盖

**审查对象**：`base 5de8d44c → HEAD 9b82e97b` 的完整 diff 面（r2 单提交，父节点为 r1 `972049f9`）。逐项核对 r1 的 F-01–F-12 是否真正闭合，并检查 r2 新增/改动内容是否越界。

**已读取（只读）**
- 候选侧：`doc/tasks/P02.md`（全文）、`doc/handoffs/P02-stage-a-foundation-handoff.md`、`verification/P02/{p02-harness-results.json,p02-harness-results.txt,env-identity-report.json,env-identity-report.txt,probe-execution.log,run-webview.ps1,RESUME.md}`、`verification/P02/harness/workbench_cdp_harness.py`、`verification/P02/probes/{env_identity_probe.py,static_control_probe.py}`、`verification/P02/fixtures/workbench_synthetic_data.json`、`apps/desktop/frontend/e2e/workbench_driver_protocol.ts`。
- base/契约侧（根工作区 `G:\CODEX\New Manga` = base 检出）：`apps/desktop/frontend/src/region/{types.ts,client.ts}`、`src/workbench/WorkbenchPage.tsx:672-721`、`src/**` hex 检索、`doc/reviews/P02-972049f9-dsh-review.md`（r1 正式 Review，位于根工作区，未在本 worktree 内）。
- 只读 Git 元数据：worktree `HEAD`/`logs/HEAD`、`refs/heads/agent/antigravity/P02-real-webview-harness`、`refs/heads/main`、`packed-refs`。

**未覆盖**：未以 `git diff base..HEAD` 形式取得 r2 变更清单（无 shell），改用「r2 自带 `git status --porcelain` 快照 + 逐文件读取」；未重新执行 r1 那次全树 base↔head 逐文件比对（base 未变，r1 的 base 侧结论仍适用）；未复核任何 tree/SHA-256。

---

## 2. 对象绑定与只读取证

| 证据 | 内容 |
|---|---|
| `.git/refs/heads/agent/antigravity/P02-real-webview-harness` | `9b82e97b8aadc5b6b8710e03b5128a608697f56e` ✔ 与 reviewed HEAD 逐字一致 |
| `.git/worktrees/…/logs/HEAD` | `5de8d44c → 972049f9`（"feat(P02): implement Stage A safe foundation…"）→ `972049f9 → 9b82e97b`（"fix(P02): address DSH Stage A review findings and whitespace diagnostics (r2)"，epoch `1791529598 +0800` = `2026-10-09T06:28:04Z`→实际 `07:06:38Z`） |
| `.git/refs/heads/main` | `5de8d44c784cbd20b23bcd41a8f1a7258c7addff` —— live `main` 仍 = diff base ⇒ 根工作区 = base，可用于内容比对 |
| r2 自证时刻 | `probe-execution.log:3` `Date: 2026-10-09T15:03:12+08:00`；报告 `timestamp: 2026-10-09T07:03:13Z` = `15:03:13+08`；**r2 提交发生于 `15:06:38+08`** ⇒ 证据产生于 **r2 提交前约 3.5 分钟**，被测字节 = r1 提交 + r2 工作区未提交改动 |

---

## 3. 前序 finding F-01–F-12 逐项核对（不以作者闭合表为准）

| ID | 原级别 | r2 处置核对 | 结论 |
|---|---|---|---|
| F-01 | P1 | harness/TS/Handoff/Task 四处称谓全部改写为「preflight / verdict report generator」；`target_exe`/`cdp_port` 与死导入已删 | **closed** |
| F-02 | P2 | 真实 F Token 与 live inline palette 分离、逐项标注 `source_file:line`、`token_mapping: UNMAPPED` | **closed** |
| F-03 | P2 | Handoff 不再手写数值，改为引用机器报告 | **closed** |
| F-04 | P2 | 模型检查更名 `PRE-03`；AC6 仅保留运行时 `BLOCKED`；`token_mapping`/`contrast_result` 已产出 | **closed** |
| F-05 | P2 | 新增 `provenance` 块，但 `source_head/source_tree` = **r1**；无交付 commit；`evidence_carrier` 自引用 | **仍 open（P2）** |
| F-06 | P2 | `exit_code=None`/`null`；新增带版本头与逐步 EXIT 的执行日志；失败传播 | **closed**（残余见 G-03） |
| F-07 | P2 | RESUME 新增当前检查点（r2 状态 + 12 项处置 + 下一步），历史段保留 | **closed** |
| F-08 | P3 | 改为从夹具读 hex；实现 `blend_alpha` 与自检；但 live 底色仍硬编码 | **partial（仍 open，P3）** |
| F-09 | P3 | GUID 修正并限定查询；`npm.cmd` 探测 + 错误显式化；解释器统一 | **partial（仍 open，P3）** |
| F-10 | P3 | 真实 Region wire 字段/枚举、补齐 page-102、AC4 三操作区分 + readback、删除 `$schema` | **closed**（残余见 G-07） |
| F-11 | P3 | layer union 扩展为 6 值；TS 头部标注 Stage A 契约 | **closed** |
| F-12 | P3 | Task 测试表按 preflight PASS / runtime BLOCKED 分行并链接证据 | **closed** |

### F-01（P1）→ closed
`harness:1-14` docstring：「Stage A preflight and verdict report generator. NOTE: Interactive CDP and live WebView2 behavioral driving are NOT yet active in Stage A」；`__init__(self)`（`:112`）已无 `target_exe`/`cdp_port`；导入仅 `json/platform/subprocess/sys/time/pathlib`（`:18-23`），`os`/`urllib.request` 死导入已删；AC1–AC6 由 `register_runtime_blocked_scenarios()`（`:282-317`）显式登记，不再有硬编码 `build_barrier_active` 开关。TS 头部（`ts:1-8`）声明「specifies Stage A data contracts… Full interactive CDP / WebView behavioral driving is NOT yet active」。Handoff:28 与 `P02.md:107` 同步改写。**残余（非 finding）**：文件名仍为 `workbench_cdp_harness.py`，建议 Stage B 实现 CDP 或改名，避免再次歧义。

### F-02（P2）→ closed
夹具 `visual_direction_f_tokens.tokens`（`fixture:227-252`）为真实 F 值 `bg_page #1a1a1d`、`ink #ececee`、`ink_2 #a9a9b3`、`ink_3 #91919c`、`ink_dis #70707b`、`accent #4d63e8`，与 `doc/design/tokens-cand-f.json` 逐值一致；原无来源的 `#58a6ff` 已全部移除；`#2a3038` 现标注 `App.tsx:488`——**我逐行核实为真**：`App.tsx:474 color:#d8e0e8`、`:475 background:#101418`、`:486 background: view==="console" ? "#1c2430" : "#161b22"`、`:488 border:"1px solid #2a3038"`、`PageListPanel.tsx:53 color:#8a94a2`、`ViewerPanel.tsx:152 var(--bg-canvas, #0b0e12)` 全部吻合。live 组标注 `token_mapping_status: UNMAPPED`，报告逐项输出 `token_mapping/contrast_result`。**说明**：r1 报告中「`#2a3038` 在 `src/**` 无来源」一项经复核不成立（当时我未检索该值），r2 已给出正确来源，此处如实更正。

### F-03（P2）→ closed
Handoff:50 引用 `ink 14.72:1、ink-2 7.45:1、ink-3 5.57:1、ink-dis 3.55:1、accent 3.53:1`、内联 `#d8e0e8 13.87:1`，与 `p02-harness-results.json:59,67,75,83,91,101` 逐字一致。**我按 WCAG 2.1 独立复算全部命中**：`#ececee`/`#1a1a1d`=14.72、`#a9a9b3`/`#1a1a1d`=7.45、`#91919c`/`#1a1a1d`=5.57、`#70707b`/`#1a1a1d`=3.55、`#4d63e8`/`#1a1a1d`=3.53、`#d8e0e8`/`#101418`=13.87、`#8a94a2`/`#101418`=6.02、`#161b22`/`#101418`=1.07、`#1c2430`/`#101418`=1.18、`#2a3038`/`#101418`=1.39、`#0b0e12`/`#101418`=1.05（注意取 max/min 排序）。r1 的 `14.28/5.76` 已完全消失。

### F-04（P2）→ closed
`PRE-03 f_token_and_palette_math_model`（`json:49-53`、`layer: TOKEN_MODEL`、`PASS`）与 `AC6 runtime_computed_color_extraction`（`json:221-234`、`BLOCKED`、`exit_code: null`）已彻底分离；`token_mapping`（MAPPED/UNMAPPED）与 `contrast_result`（PASS/FAIL）已分列记录（`:61-62,102-103` 等）；`P02.md:110` 与 Handoff:31 一致。AC6 不再出现任何 PASS。

### F-05（P2）→ **仍 open**
- `p02-harness-results.json:5-11`：`provenance.source_head = 972049f9…`、`source_tree = 657095fa…`、`branch`、`behavior_baseline_commit = 241ff3b7…`、`evidence_carrier = "verification/P02/p02-harness-results.json"`。
- `env-identity-report.json:26-32`：同一 `head/tree`，`is_clean: false`，porcelain 列出 **12 个 ` M` + 1 个 `??`**（正是 r2 的 harness/fixture/probes/runner/reports 与新增 `probe-execution.log`）。
- AC1–AC6 的 `details`（`json:151-155…`）也内嵌 `source_head = 972049f9…`。
- **交付出货的 r2 head `9b82e97b…` / tree `7fe67d0f…` 在全部 artifact 中零出现**；Handoff frontmatter（`:11-15`）只有 `base_commit`、`reviewed_head_r1`、`dsh_decision_r1`，**没有 r2 的 `reviewed_head`/`reviewed_tree`**；无任何 artifact SHA-256。

**判定（回应本任务重点 1）**：
1. **报告没有标识实际被测字节**。被测字节 = r1 提交 + r2 未提交改动（`probe-execution.log:3` 的 `15:03:12+08` 与 r2 提交 `15:06:38+08` 的时间差、以及 porcelain 中列出的 12 个 ` M` 共同证明）。而 `source_head/source_tree` 描述的是 **r1**；`657095fa` 这棵树**不可能**包含产生 `PRE-03` 与 live palette 结果的 r2 harness/fixture（r1 的 harness 没有 PRE-03、没有 palette 评估、没有 alpha 合成）。**记录的 provenance 与被测内容自相矛盾**，Git HEAD/tree 无法描述脏工作区内容。
2. **没有绑定到 r2 交付**：交付 commit/tree 完全缺席，交付物也没有任何内容哈希；因此「AC7 源码/二进制 Hash」仍不成立。
3. **存在自引用环**：`evidence_carrier` 指向证据文件自身，而该文件正是这 12 个 dirty 文件之一（其 bytes 只能存在于 r2 工作区/提交中，而不存在于它自称的 `972049f9` 里）。要确定被测字节就必须读该 carrier，而 carrier 本身又是被测字节之一——指针无法钉住被测量的内容。
4. **加重情节**：`env-identity-report.txt`（人读版本）**丢掉了 `is_clean` 一行**（r1 的 txt 曾打印 `Git Clean Status: False`），即脏工作区这一关键事实只存在于 JSON，见 G-02。

### F-06（P2）→ closed
`record_verdict(..., exit_code: int | None, ...)`（`harness:124`），运行时场景 `exit_code=None` 并注释「Observed exit is None since scenario was blocked before process launch」（`:306`）；txt 打印 `Exit: null`（`:371`，实测 `p02-harness-results.txt:15-20` 全部 `Exit: null`）；`main()` 返回 `0 if preflight_ok else 1`（`:383-388`）。`run-webview.ps1` 新增 `Execute-Step`（`:39-65`）：记录 `Command`/`OUTPUT`/`EXIT`，`$exitCode -ne 0` 时 `Write-Error` + `exit $exitCode`（失败传播）；日志头含 `Date/PowerShell 5.1.26100.9549/Python C:\Python314\python.exe (Python 3.14.6)/Node v24.15.0/npm 12.0.1/Worktree`（`probe-execution.log:1-9`），三步 `EXIT: 0`（`:29,42,67`）。满足 `doc/templates/REVIEW.md:51` 的「EXIT + shell 头」要求。**残余**：日志记录的是各步骤 EXIT，runner 自身聚合退出码未落盘；`git diff --check EXIT=0` 无证据文件（G-03）。

### F-07（P2）→ closed
`RESUME.md:3-29` 新增「当前检查点：P02 Stage A 定向修订已完成；等待 DSH 复审与 Codex 隔离构建 Gate」：登记行为基线、scope SHA、r1 reviewed_head 与 decision、F-01–F-12 处置、PRE-01/02/03 PASS 与 AC1–AC6 BLOCKED、硬构建屏障，以及「下一条直接执行」。历史检查点段（`:31-56`）完整保留，未抹除旧记录。

### F-08（P3）→ partial（仍 open）
已闭合部分：`hex_to_rgb`（`:51-55`）从夹具读值；`blend_alpha`（`:58-68`）实现 `a*fg+(1-a)*bg`；`calculate_contrast` 在 fg 为 4 元组时合成（`:84-87`）；`self_test_contrast_math()`（`:96-108`）断言 `#000/#fff=21.0`、同色=1.0、`rgba(0,0,0,0.5)` on white ≈3.98，并在 `__init__` 中执行（`:116`）；TS 侧同步新增 `blendAlpha`（`ts:94-105`）且 `calculateContrastRatio` 改为必带 alpha（`:141-151`）。
**残留（仍 open）**：`harness:242` 硬编码 `live_bg_hex = "#101418"`，而夹具 `:258-263` 已把 `#101418` 声明为 `app_base_background`（来源 `App.tsx:475`）。因此 F-08 自身的验收口径「改动夹具色值能直接联动改变计算结果」对 live palette 组**不成立**——改夹具的 base background 不会改变任何 live 结果。最小修正：从 `live_inline_palette` 中按 role 取 base background。

### F-09（P3）→ partial（仍 open）
已闭合部分：`env_identity_probe.py:59-85` 只查询已验证 GUID `{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`（HKLM WOW6432Node/HKCU/HKLM 三处）并回退到 `FS_*` 目录；`:116` 的死 GUID 分支已重写为 `if "{F3017226-…}" in k`（`:129`），报告的 `verified_client_guid`（`env-identity-report.json:18`）与日志 `:17` 一致；`get_npm_version()`（`:103-110`）用 `shutil.which("npm.cmd")` 并返回 `ERROR: exit=…, stderr=…` 而非空串，报告得 `npm: 12.0.1`（`:24`）；`python_executable` 已记录（`:22`）；runner 用单一 `$PythonExe = (Get-Command python).Source`（`run-webview.ps1:21`）驱动三步。
**残留（仍 open）**：
(a) `harness:203-216` 仍以 `subprocess.run([sys.executable, static_control_probe.py])` **再次执行**静态探针，而 `run-webview.ps1:76-78` 的 Step 2 已经执行过一次 ⇒ 静态探针与其两份报告每次运行产出两遍；Handoff:36 的闭合声明「不重复调用静态探针」**不成立**。
(b) `env_identity_probe.py:11` 的 `import os` 仍是死导入（全文件未使用）。

### F-10（P3）→ closed
- 真实 wire 形状（对照 `src/region/types.ts`）：`RegionSummary`（`:59-66`）= `region_id / region_type / sfx_policy / origin / revision_no / geometry?{bbox,polygon}`，夹具 `:70-139` 逐字段吻合；`geometry.bbox` 为归一化 4 元组（`types.ts:46-51`），夹具 `[0.08,0.08,0.25,0.12]` 等 ✓。
- 真实枚举：`REGION_TYPE_VALUES = ["speech","narration","sfx","title","note","other"]`（`types.ts:14-21`），夹具使用 `speech/narration/sfx` ✓，r1 的假名 `dialogue/thought` 已消除；`SfxPolicy = skip|translate|manual`（`:33`）夹具用 `skip/translate` ✓；`RegionOrigin = machine|user|imported|restored`（`:37`）夹具用 `user/machine` ✓。
- 补齐数据：`synth-page-102` 的 `has_regions: true` 现有对应区域 `synth-reg-03`（`fixture:116-139`）✓。
- AC4 三操作已区分且对应真实 IPC：`retype` → `set_region_type`，参数 `{regionId,newRegionType,expectedRevision}` 与 `region/client.ts:110-120` 完全一致；`undo` 标注 `operation_name: undo_retype` + `ui_action: trigger_undo` + 底层 `restore_region_revision {regionId,revisionNo,expectedRevision}` —— **我核实 UI 实现确实如此**：`WorkbenchPage.tsx:684-688` `clients.region.restoreRegionRevision(offer.regionId, offer.previousRevisionNo, offer.expectedRevision)`；`restore` → `restore_region_revision`（`client.ts:165-173`）✓；三者均带 `post_write_readback`（`list_regions` + `expected_sequence` + `max_quiet_period_delay_ms`）✓；`$schema` 已删除（`fixture:1-2`）✓。
- **残余（见 G-07）**：`revisions[]` 条目缺 `RevisionSummary` 的 4 个字段。

### F-11（P3）→ closed
`ts:39-45` 的 `layer` 联合已扩展为 `REAL_WEBVIEW2 | REAL_WEBVIEW_MOCK_IPC | FILESYSTEM | STATIC_AST | TOKEN_MODEL | BLOCKED_NO_BUILD`，覆盖报告实际产出的三种前置层；`exitCode: number | null`（`:46`）。

### F-12（P3）→ closed
`P02.md:66-83` 测试表已重写：环境探针 / PRE-01 / PRE-02 / PRE-03 / AC1–AC6 / Stage A Runner 分行，分别记 `PASS / EXIT=0` 与 `BLOCKED / EXIT=null`，并逐行链接 `env-identity-report.json`、`probe-execution.log`、`workbench_synthetic_data.json`、`static-control-report.*`、`p02-harness-results.json`。`P02.md:105-119` 补充 r1 交付、r2 定向修订与逐项处置。**frontmatter（`:1-18`）逐字未变**（`status: in_progress`、`base_commit=241ff3b7…`、`scope_contract_sha256`、branch/worktree、`integration_commit: null`）；AC1–AC7（`:37-45`）与允许/禁止范围（`:47-59`）与 base/r1 **逐行相同**，未擅自修改 AC 或基线。残余见 G-04。

---

## 4. 新增 findings（G 系列）

| ID | 级别 | 文件/行 | 状态 |
|---|---|---|---|
| G-01 | **P2** | `doc/handoffs/P02-stage-a-foundation-handoff.md:22,32`；`verification/P02/RESUME.md:14`；`doc/tasks/P02.md:111` | open |
| G-02 | P3 | `verification/P02/env-identity-report.txt:1-15`（对比 `env-identity-report.json:26-32`） | open |
| G-03 | P3 | `handoff:40`、`RESUME.md:22`、`P02.md:119`；无证据 artifact | open |
| G-04 | P3 | `doc/tasks/P02.md:78` vs `verification/P02/probe-execution.log:44-67` | open |
| G-05 | P3 | `harness/workbench_cdp_harness.py:230,255` | open |
| G-06 | P3 | `harness/workbench_cdp_harness.py:11,58-68`；`fixture:219-301` | open |
| G-07 | P3 | `fixtures/workbench_synthetic_data.json:82-138` vs `src/region/types.ts:94-105` | open |

**G-01（P2）闭合表声称已记录「交付 commit」与「工件 hash」，但两者在证据中都不存在**
Handoff:32 写「报告明确区分行为基线 `241ff3b7…`、被测源码 commit 与 tree、测试命令及**工件 hash**。在探针中准确采集并记录当前检出对象。」；RESUME:14 写「F-05: 纠正 provenance，明确区分行为基线、被测 source commit、tree 与**交付 commit**」；`P02.md:111` 亦称「修正 provenance 与测试命令记录（F-05）」。
**证据**：`p02-harness-results.json:5-11` 只有 `source_head/source_tree/branch/behavior_baseline_commit/evidence_carrier`，**无交付 commit、无任何 hash 字段**；`env-identity-report.json` 同样；全 `verification/P02` 无 SHA-256 记录。被测「source commit/tree」是 r1 且与实际被测脏字节不符（§3 F-05）。**影响**：集成方据闭合表会认为 F-05 已闭合、provenance 已可追溯，从而可能接受一个仍无法绑定被审修订的证据集；这正是 r1 F-01 同类「表述与实际不符」缺陷的再现，只是范围更窄。**最小修正**：删除/改写该断言，或在证据中真实补上交付 head/tree 与逐 artifact SHA-256 后再声明。

**G-02（P3）人读报告隐藏了脏工作区事实（相对 r1 回退）**
`env-identity-report.txt:8-11` 打印 `Git Branch / Source HEAD / Source Tree / Behavior Baseline`，但**不打印 `is_clean`**；该字段仅存在于 JSON（`:30`）。r1 的 txt 曾打印 `Git Clean Status: False`。**影响**：只读文本报告的读者（本 Task 的主要人读证据）无法看出「被测字节 ≠ 记录的 HEAD」，而 12 个 ` M` 的 porcelain 也只在 JSON 中。**最小修正**：txt 增补 `Git Clean Status` 与 porcelain 条目（或明确写「tested bytes = dirty working tree, see porcelain」）。

**G-03（P3）`git diff --check EXIT=0` 无证据 artifact；且提交的生成器在 Windows 上不可复现纯 LF 日志**
Handoff:40 / RESUME:22 / `P02.md:119` 均声明「统一纯 LF、去除 trailing-whitespace、`git diff --check` 返回 `EXIT=0`」，但 `verification/P02/**` 内**没有任何 diff-check 日志或退出码记录**（违背 `doc/templates/REVIEW.md:51` 的证据纪律口径）。
**我的替代核查（只读字节检查）**：对 r2 全部交付文件（harness/probes/runner/4 份 report/`probe-execution.log`/fixture）做 `[ \t]+$` 与 `\r$` 检索，并对 `workbench_driver_protocol.ts`、`doc/**/P02*.md` 同做检索，**均无命中**；`probe-execution.log` 亦无 BOM（`^\x{FEFF}` 无命中）。即**声明在交付字节上成立**，但：日志由 `run-webview.ps1:37,47,48,56,59` 的 `Set-Content`/`Add-Content` 生成，Windows PowerShell 5.1 默认 CRLF，故该日志的「纯 LF」状态看不出由提交的生成器产生（更像事后转换）；在 Codex 复算或 Owner 重跑时可能重新引入 CR，使 `git diff --check` 再次失败。**最小修正**：把 `git diff --check` 输出与 EXIT 落盘为证据；若要求纯 LF 可复现，生成器改用 `newline="\n"`（Python 侧）或显式 `-NoNewline`/`[IO.File]::WriteAllText` 写入。

**G-04（P3）Task 记录的 runner 命令与实际执行不符**
`P02.md:78` 记录命令为 `powershell -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1 -ProbeOnly`，证据指向 `probe-execution.log`；但该日志包含 `--- [Step 3: Stage A Verdict Harness] ---`（`:44-67`）且全文件无 `ProbeOnly` 字样 ⇒ 产生该日志的是**完整运行**，不是 `-ProbeOnly`。**影响**：AC7「命令」记录与证据不对应，读者据 Task 表复现会得到不同的执行面（`-ProbeOnly` 会跳过 Step 3，从而不产出 `p02-harness-results.json`）。**最小修正**：Task 表改记实际命令（完整 runner 或 `-ProbeOnly` 另跑一次并分别归档日志）。

**G-05（P3）PRE-03 的阈值语义与 AC6 不一致（未翻转任何判定）**
`harness:230`：`min_target = 4.5 if "text" in role and "primary" in role else 3.0`；`harness:255`：live palette 一律 `>= 3.0`。结果：`ink_2`（secondary_text）与 `ink_3`（tertiary_text）被记录 `min_required: 3.0`，而 AC6（`P02.md:44`）规定「**文本**至少 4.5:1，禁用文字/非文本至少 3.0:1」；live 组中 `#d8e0e8`（app_primary_text）与 `#8a94a2`（pagelist_muted_text）也按 3.0 判定。另 live 组包含 `nav_inactive_button_background`/`nav_button_border`/`viewer_background` 三个**背景/描边 vs 背景**配对，其语义（WCAG 1.4.11 非文本对比 vs 文本对比）未在 `role` 之外说明。
**判定影响**：无 PASS/FAIL 翻转——`ink_2` 7.45、`ink_3` 5.57 均 ≥4.5；`#d8e0e8` 13.87、`#8a94a2` 6.02 亦 ≥4.5；四个 FAIL（1.05/1.07/1.18/1.39）无论阈值都 FAIL。故为记录口径缺陷，非结论错误。**最小修正**：按 AC6 的 role→阈值映射（text=4.5，disabled/非文本=3.0）显式配置，或在 `details` 标注每对的配对语义与所依据的契约条款。

**G-06（P3）「包含 Alpha Blending 底色合成」的表述超出模型实际覆盖**
`harness:11` docstring 与 Handoff:35 / `P02.md:114` 均声称模型含 alpha blending 底色合成。实际上 `blend_alpha` 只在 fg 为 4 元组时被调用（`:84-87`），而夹具中**所有** F token 与 live palette 条目都是不透明 6 位 hex（`fixture:227-300`）⇒ 真实评估路径**从未触发**合成；唯一触发点是 `self_test_contrast_math()` 内的人工 `(0,0,0,0.5)`（`:107`）。同时模型只覆盖 F 契约 42 色令牌中的 5 个（仅 dark），未覆盖 `UI_UX_GUI_DESIGN.md §7.2` 明确要求按「`*-soft` 为 rgba、以 alpha 叠加 panel 合成后与文字令牌比较、阈值 4.5:1」审计的徽标合成对——而这恰是需要 alpha 的场景。**影响**：AC6 仍是 BLOCKED、报告已正确标注 `TOKEN_MODEL`，故不构成产品 PASS 冒充；但「含 alpha 合成」的能力表述不实，且模型对该契约条款无覆盖，容易让 Stage B 误以为该口径已实现。**最小修正**：改为「alpha 合成函数已实现并在自检中验证；尚未对任何真实令牌应用」；若要覆盖 §7.2，需在夹具加入 `*-soft`（rgba）与 panel 底色并逐一审计。

**G-07（P3）夹具 `revisions[]` 不是完整 `RevisionSummary` wire 形状**
`fixture:82-138` 的每条 revision 含 `region_revision_id / revision_no / origin / review_state / is_pinned / restored_from_revision_id`（6 项），而 `src/region/types.ts:94-105` 的 `RevisionSummary` 为 10 项，缺 `created_at`、`region_type`、`sfx_policy`、`is_current`。**影响**：若 Stage B 驱动把这些对象直接投喂 UI，`RegionInspector.tsx:250` 使用的 `revision.is_current` 与渲染用的 `created_at`/`region_type`/`sfx_policy` 将为 `undefined`，可能产生与真实 wire 不同的焦点/状态表现，污染 AC2/AC5 观测。**最小修正**：补齐 4 个字段（`created_at` 用 ISO 字符串、`is_current` 标出当前修订）。

---

## 5. Architecture 结论

**通过（分层、契约、依赖、安全）；无新增架构缺陷。**

- **范围未扩张**：r2 的改动面由证据自带的 porcelain（`env-identity-report.json:32`）完整枚举——12 个 ` M` 全在 `verification/P02/**` 与 `apps/desktop/frontend/e2e/workbench_driver_protocol.ts`，唯一 `??` 为 `verification/P02/probe-execution.log`；无删除项。随后（15:03:13→15:06:38 之间）编辑的 `doc/handoffs/P02-*.md` 与 `doc/tasks/P02.md` 亦在 allowlist 内。**禁止路径零触碰**，包括 `apps/desktop/frontend/src/**`、`package.json`/`package-lock.json`、`apps/desktop/src-tauri/**`、Python Core、SQLite schema/migration、共享 IPC/Schema、依赖清单、设计 token/契约、P03 runner、已打包 EXE/dist。
- **零构建、零依赖扩张**：`probe-execution.log` 三步骤只运行两个探针与 harness；无 Cargo/Tauri/sidecar；`apps/desktop/frontend/dist` 与 `verification/P02/cargo-target` 仍 `exists:false`（`env-identity-report.json:34-48`）⇒ 硬构建屏障被真实遵守。Python 仅标准库；TS 零 import；`package.json` 未变。
- **AC/基线/契约未变**：`P02.md` frontmatter 与 AC1–AC7、允许/禁止范围逐行未变（§3 F-12）；未修 UI/对比度/token/debounce，仅「记录实际呈现并对照已选 F token」（`P02.md:35`）——F token 值取自冻结的 `tokens-cand-f.json`，live 值标注为 `UNMAPPED`，未反向修改设计。
- **数据与进程安全**：夹具全为 `synth-*`；探针只读注册表单一 GUID 子键、只读列举 EdgeWebView 目录、只读 `git rev-parse/status`、`node -v`、`npm.cmd -v`；harness 只以 `sys.executable` 调用本仓探针；无 `shell=True`、无网络、无删除/移动、无用户库/SQLite/凭据访问；写操作限于 `verification/P02/`。
- **分层隔离**：`e2e/*.ts` 仍被 `tsconfig.json:19 "include": ["src"]` 排除且无人 import ⇒ 不进入产物/测试面（仍是惰性契约文件，见 F-01 残余）。

---

## 6. Verification 结论

**记录质量较 r1 实质改善，标签纪律正确；但 AC7 的证据绑定仍不成立。**

**已认可（含我的独立复核）**
1. **无数值造假**：`PRE-03` 的 11 个对比度全部可由「提交的夹具 + 提交的算法」复现（§3 F-03 列出逐一复算值），`self_test_contrast_math` 的三个断言（21.0 / 1.0 / ≈3.98）在 WCAG 数学上正确。
2. **无产品 AC 冒充**：`REAL_WEBVIEW2`/`REAL_WEBVIEW_MOCK_IPC` 层场景**一律 BLOCKED 且 `exit_code: null`**；PASS 仅出现在 `FILESYSTEM`/`STATIC_AST`/`TOKEN_MODEL` 前置层；AC6 无 PASS。
3. **屏障依据仍成立**：`tauri-build-side-effects-investigation-r1.md` 与 `build-preflight-lf-r1.md` 的结论未被 r2 削弱；候选树仍无 `apps/desktop/src-tauri/target/`（sidecar 输入缺失）。
4. **PRE-02 断言在 base 复现**：`WorkbenchPage.tsx:85` 的 `resolveDebounceMs = 300, regionDebounceMs = 300`、`App.tsx:479/482/499` 的 `app-nav`/`nav-console`/`nav-workbench`。
5. **环境/版本/退出码证据成形**：日志头含 PowerShell 5.1.26100.9549 / Python 3.14.6(exe 路径) / Node v24.15.0 / npm 12.0.1，三步各自 `EXIT: 0`；WebView2 身份三重一致（已验证 GUID `{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}` + FS 目录 `154.0.4258.62` + `detected_version 154.0.4258.62`）。
6. **文本/JSON 一致**：`p02-harness-results.txt` 与 `.json` 的 HEAD/Tree/Baseline/9 场景/Exit 逐项一致；`env-identity-report.txt` 与 `.json` 的版本与 HEAD 字段一致（差异仅 G-02 的 `is_clean` 缺失）；`static-control-report.*` 与 harness 内嵌 PRE-02 stdout 一致。
7. **空白卫生**：r2 交付文件无 CR、无 trailing whitespace、无 BOM（检索证据见 G-03）。

**不可批准的部分**：交付证据**不能标识被测字节、也不绑定到被审修订**（F-05），且交付文档**声称已记录交付 commit 与 artifact hash —— 实际没有**（G-01）。对以「固定证据与源码 Hash」为 AC7 的验证型 Task，这属于「关键验证缺失」，故本 head 仍不可交 Codex 集成。8 项 P3 不影响安全边界，可在同一修订轮一并处理。

**本次未执行**：未运行 Cargo/Tauri/sidecar build、未运行探针/harness/runner、未运行 Vitest/前端构建、未做真实 WebView2 或 GUI 操作、未生成或校验任何 SHA-256、未做 `git diff --check`。

---

## 7. 逐 AC 状态（保留 BLOCKED；P02 保持 in_progress）

| AC | 层级 | r2 记录状态 | 本次 Review 判定 |
|---|---|---|---|
| AC1 真实 WebView2 harness | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED**（无受信隔离构建产物；未演示；不接受为 passed） |
| AC2 导航与操作 | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED** |
| AC3 300ms quiet-period/失效窗口 | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED** |
| AC4 写后刷新（retype/undo/restore） | `REAL_WEBVIEW_MOCK_IPC` | BLOCKED / EXIT=null | **维持 BLOCKED**（符 AC4 禁以 `NOT_RUN` 替代） |
| AC5 键盘与焦点 | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED** |
| AC6 F token/对比度 | `TOKEN_MODEL` 前置 + `REAL_WEBVIEW2` 运行时 | PASS（`PRE-03` 模型）/ BLOCKED（运行时） | 模型 PASS **不构成 AC6 证据**（G-05/G-06）；**AC6 维持 BLOCKED** |
| AC7 固定证据与发现处置 | 证据机制 | 部分 | **未达标**：provenance 未绑定被审修订（F-05）、闭合表不实（G-01）、命令与证据不符（G-04）、diff-check 无证据（G-03） |
| PRE-01 夹具契约 | `FILESYSTEM` | PASS / EXIT=0 | 认可（7 个 section 校验；键与报告一致） |
| PRE-02 静态源码契约 | `STATIC_AST` | PASS / EXIT=0 | 认可（断言已在 base 独立复现） |
| PRE-03 F token/Palette 数学模型 | `TOKEN_MODEL` | PASS / EXIT=0 | 认可为**前置模型**（数值已独立复算）；阈值与覆盖口径见 G-05/G-06 |

**明确声明**：P02 仍 `in_progress`；**AC1–AC6 运行时一律不接受为 passed**；`PRE-01/02/03` 与任何脚手架 Gate PASS **不等于产品 UI/WebView 质量 PASS**；「测试脚手架 Gate PASS 不等于产品 UI 质量 PASS」（`P02.md:45`）。

---

## 8. 范围与禁止路径结论

- r2 变更集合 ⊆ allowlist（依据 r2 自带 porcelain + 逐文件读取 + 提交后文档编辑），**无 scope creep**。
- `doc/tasks/P02.md` 仅更新「实际执行/交付记录」（测试表 + 执行记录），AC/基线/范围/禁止项逐行未变，符合 `P02.md:54` 的限制。
- 构建输出仍为 `exists:false`；未新增依赖；未修改任何共享契约、schema、依赖清单、P03 runner、设计 token。
- 无越界数据访问、无危险进程调用；未接触用户漫画库/生产数据/Lock/Revision/凭据。
- 提醒 Integrator：候选 worktree 为本地 `core.autocrlf=false` 的 LF 检出，跨工作区比对须 `--ignore-cr-at-eol`，否则整树显示为改动。

---

## 9. 限制（本次 Review 未能核验的部分）

1. **无 shell（根本限制）**：`pwsh` 在本会话仍完全不可用（沙箱准备 workspace 授权失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P02-real-webview-harness-antigravity)`）。因此**未运行** `git rev-parse/diff/status/hash-object`，**未计算任何 SHA-256**，**未复跑**探针/harness/runner，**未执行** `git diff --check`。对象绑定仅由「松散引用 + worktree reflog + `refs/heads/main`」交叉确认。
2. **交付 tree `7fe67d0fb9bfc95e579c0fbda539de85eb73e4f4` 未复核**；scope contract SHA-256 未复核；r2 提交的变更清单未由 `git diff` 枚举（改用 porcelain + 文件读取）。
3. 我读取的是**工作区内容**；无法证明候选工作区与 `9b82e97b` 提交逐字节一致。**注意**：`p02-harness-results.json:5-11` 记录的 r1 head 与我这台机器的工作区状态无关；r2 提交后的工作区是否仍等于提交内容，我无法用 git 证明。
4. r2 未重新执行 r1 的全树禁止路径内容比对；本次对 r2 的越界判断依赖「porcelain 完整枚举 + 逐文件读取」，未再对 `frontend/src/**`、`src-tauri/**`、Python Core、`doc/contracts/**`、`doc/design/**`、`packaging/**` 做 base↔r2 全量内容比对（base 侧未变，故 r1 的 base 结论仍有效；且这些路径未出现在 r2 porcelain 中）。
5. 未核验的声明：`probe-execution.log` 的「纯 LF」是否可复现（`Set-Content`/`Add-Content` 的 CRLF 行为未实测）；文档所称「293 条 trailing-whitespace 诊断」的具体计数与来源未核验；WebView2 版本与 OS 信息直接采信探针输出。
6. 未审计范围：P02 之外的历史 Task/证据、`test_assets/**`、`wiki/**`、`.codewiki/**` 等。

---

## 10. 必须由 Codex 处理的治理下一步

1. **不要把本 r2 视为可集成**：F-05 与 G-01 open。请按 §11 要求固定新 head 后复审。
2. **登记与解阻**：在 `STATUS` / `REBASELINE_PLAN` / `ROADMAP` 登记 P02 Stage A r2 head 与本 Review 决策；按 `build-preflight-lf-r1.md` 先登记隔离 scratch worktree、可信 sidecar 输入来源/临时路径与 Hash 复算方式及准确构建命令，**再**开放 Cargo/Tauri 构建；在此之前不得在 Owner worktree 构建。
3. **状态文档同步**（Owner allowlist 之外）：`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:3`、`doc/12_ROADMAP.md:3`、`doc/00_INDEX.md:3`、`doc/tasks/README.md:5`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md:3,5` 仍称「正式实现启动消息待发送/AC1–AC7 全部 NOT_RUN」，与 Stage A r1/r2 已交付不一致；同步时须保持 P02 `in_progress` 与「运行时 AC 未执行」口径，不得把 `BLOCKED`/`NOT_RUN` 写成 `PASS`。
4. **不得据此释放 P07**：本片未证实任何用户可见产品缺口（AC1–AC6 运行时未执行）。
5. **集成口径**：跨工作区比对使用 `--ignore-cr-at-eol`；复算时请保存命令与 EXIT。

---

## 11. 复审口径（供 r3 head 使用）

Owner 需在同一 branch 的新固定 head 上至少完成：**F-05**（记录被测 artifact 的 SHA-256 与/或提交后复跑并以新 HEAD 记录；去掉 `evidence_carrier` 自引用）、**G-01**（删除或兑现「交付 commit + 工件 hash」断言）、**F-08/F-09 残余**（live 底色从夹具取；静态探针只跑一次；清理死导入）、以及 G-02–G-07。之后由本 Reviewer 对新 head 复审，并**追加新 head 与 findings disposition、不抹除本记录**。复审清单：F-01–F-12 与 G-01–G-07 的逐条处置与文件:行证据、新 head 的 tree/artifact 哈希、`run-webview.ps1` 实际命令与带 EXIT/shell 头的日志、`git diff --check` 输出，以及「AC1–AC6 运行时保持 `BLOCKED`」的口径确认。集成后测试由 Codex 另行记录。

---

## 12. Final verdict

```
decision: changes_requested
reconciled: F-01 closed | F-02 closed | F-03 closed | F-04 closed | F-05 STILL OPEN (P2)
            F-06 closed | F-07 closed | F-08 PARTIAL (P3) | F-09 PARTIAL (P3)
            F-10 closed | F-11 closed | F-12 closed
new:        G-01 (P2), G-02…G-07 (P3 ×6)
counts:     P0/P1/P2/P3 = 0 / 0 / 2 / 8   (open = 10)
```

**结论**：r2 是一次**实质性且诚实**的修订——r1 的 P1 与 6 项 P2 中的 5 项已按 hunk 逐一真正闭合（CDP 能力表述、F token 来源、数值单一事实源、AC6 标签、退出码与执行日志、恢复点、TS layer 契约、Task 证据表、夹具 wire 形状与 AC4 三操作区分），PRE-03 的 11 个对比度数值我逐个独立复算全部命中，且**没有任何真实 WebView2 被冒充为 PASS**。但**核心的 F-05 仍未闭合**：证据记录的是 r1 的 `head/tree`，而实际被测字节是 r2 未提交工作区（porcelain 自证 12 个 ` M`），交付的 r2 `9b82e97b`/`7fe67d0f` 在全部 artifact 中零出现，且 `provenance.evidence_carrier` 形成自引用环；Handoff/RESUME/Task 又声称「已记录交付 commit 与工件 hash」——**该断言与证据不符（G-01, P2）**。因此本 Stage A r2 切片**不在当前 head 上批准交 Codex 集成**；请按 §11 修正后固定新 head 复审。**P02 继续 `in_progress`；AC1–AC6 运行时维持 `BLOCKED`；Cargo/Tauri/WebView 运行时 AC 不接受为 passed。**
