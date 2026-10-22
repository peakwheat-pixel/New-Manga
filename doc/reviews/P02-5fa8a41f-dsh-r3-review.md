# Review：P02 Stage A Safe Foundation — r3 定向修订（非作者正式复审）

| 字段 | 值 |
|---|---|
| task_id | `P02`（**Stage A 切片 Review**；Task `status: in_progress`，本 Review 不代表 P02 完成） |
| reviewer | DeepSeek Harness（非作者） |
| author / Owner | Antigravity ｜ Integrator: Codex |
| repository / worktree | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` |
| branch | `agent/antigravity/P02-real-webview-harness` |
| base_commit | `5de8d44c784cbd20b23bcd41a8f1a7258c7addff` |
| **reviewed_head** | `5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e` ✔ 与 `refs/heads/agent/antigravity/P02-real-webview-harness` 逐字一致 |
| parent | `9b82e97b8aadc5b6b8710e03b5128a608697f56e`（r2）✔ reflog 单提交链 `972049f9 → 9b82e97b → 5fa8a41f` |
| **reviewed_tree（期望 `ce6e44c9…`）** | **不可核验**（无 shell/hash 工具，见 §9） |
| 本 r3 提交时刻 | `1791530921 +0800` = `2026-10-09T07:28:41Z` = `15:28:41+08`；证据日志 `15:28:13+08` ⇒ 证据先于提交 **28 秒** |
| scope contract SHA-256 | **不可核验** |
| 前序 | r1 `972049f9` `changes_requested`(0/1/6/5)；r2 `9b82e97b` `changes_requested`(0/0/2/8) |
| **decision** | **`approved_with_conditions`**（Stage A 切片；按 `doc/templates/REVIEW.md` 四值口径即 `approved` + 条件） |
| findings | **P0/P1/P2/P3 = 0 / 0 / 0 / 10**（开放 10，全部 P3：3 项为 r2 残余、7 项为 r3 新发现） |
| 审查方式 | 纯只读：源码/证据/文档/契约阅读 + 只读 Git 元数据 + 独立 WCAG 复算。**未修改任何文件**；**未运行** Cargo/Tauri/sidecar build、未运行探针/harness/runner、未运行 Vitest/前端构建；**未做**真实 WebView2/GUI 操作；**未接触**用户库/生产数据/凭据 |

---

## 1. 固定对象核验（含明确不可核验项）

**已核验（只读 Git 元数据）**
- `.git/refs/heads/agent/antigravity/P02-real-webview-harness` = `5fa8a41f…` ✔ 与请求的 reviewed HEAD 一致。
- `.git/worktrees/…/logs/HEAD`：`… → 5de8d44c → 972049f9`（r1）`→ 9b82e97b`（r2）`→ 5fa8a41f`（r3，「fix(P02): address DSH r2 review findings and refine Stage A harness (r3)」）⇒ **parent = r2**、base 为直接祖先 ✔。
- `refs/heads/main = 5de8d44c…` ⇒ live main 仍等于 diff base；根工作区 `G:\CODEX\New Manga` 即 base 检出，可用于 base 侧契约比对。

**不可核验（本会话环境限制）**
1. `pwsh` 完全不可用（沙箱准备 workspace 授权失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P02-real-webview-harness-antigravity)`；对任意 workdir 复现）⇒ **未能运行** `git rev-parse HEAD^{tree}` / `git status` / `git diff` / `hash-object`。
2. 因此 **reviewed tree `ce6e44c9…` 未能独立复核**；r2 tree `7fe67d0f…`、base tree `f27d12a7…` 同样未能复核；**所有 SHA-256 值（含 `key_source_files_sha256` 7 项与 Codex 复算的 3 项）我无法独立重算**。
3. **Owner 声明的「branch clean at this exact HEAD」无法独立核验**。可获得的唯一状态证据是 r3 运行期自证的 `is_clean: false` 与 13 条 porcelain（`probe-execution.log:25-40`、`env-identity-report.json:30-32`）——那是**提交前**的脏工作区，符合「先生成证据后提交」的既定模式；提交后是否 clean 我无法验证。
4. 未以 `git diff base..HEAD` 形式取得 r3 变更清单；改用「r3 自带 porcelain 完整枚举 + 逐文件读取」。
5. 未复核 r3 的 source hash 是否与工作区字节相符（无 hash 工具）；仅确认其格式为 64 位十六进制且由 `hashlib.sha256(read_bytes())` 生成（`harness:42-47`）。

---

## 2. 审查覆盖

**读取对象**：`doc/tasks/P02.md`（131 行全文）、`doc/handoffs/P02-stage-a-foundation-handoff.md`、`verification/P02/RESUME.md`、`verification/P02/{p02-harness-results.json,.txt 由日志回显核对}`、`env-identity-report.json`、`probe-execution.log`、`run-webview.ps1`、`harness/workbench_cdp_harness.py`、`probes/{env_identity_probe.py,static_control_probe.py(未改,承接 r2 版)}`、`fixtures/workbench_synthetic_data.json`、`apps/desktop/frontend/e2e/workbench_driver_protocol.ts`（关键片段）。
**契约/base 侧**：`src/region/types.ts`、`src/region/client.ts`（r2 已核）、`src/region/RegionOverlay.tsx:30-59`、`src/workbench/relabelMachine.ts`（全文）、`src/library/types.ts`、`src/workbench/WorkbenchPage.tsx`（r2 已核）、`doc/templates/REVIEW.md`、`doc/reviews/P02-9b82e97b-dsh-r2-review.md`（r2 正式报告，位于根工作区）、根工作区 `verification/P02/r2-clean-commit-validation.md`。
**说明**：请求提到的 `verification/P02/r2-clean-commit-validation.md` **不在被审 HEAD 内**；它只存在于根工作区（未跟踪），我读取了该副本作为 Codex 复算证据，并据此评价 exact-commit replay 关注点。

---

## 3. 前序 findings 逐项处置核对（不以作者闭合表为准）

### 3.1 r2 遗留 open 项（F-05、F-08、F-09、G-01–G-07）

| ID | r2 级别 | r3 处置 | 结论 |
|---|---|---|---|
| F-05 | P2 | provenance 改为运行期 HEAD/tree + 7 个关键源文件 SHA-256 + 明确「delivery commit 事后由 Codex Gate 核验」；删除 `evidence_carrier` 自引用 | **closed** |
| F-08 | P3 | 底色改为按 role 动态查找；alpha 合成应用于真实源码 rgba，并有单测与 NOT_VERIFIABLE 分支 | **closed** |
| F-09 | P3 | PRE-02 改为消费报告（缺报告才回退执行）；死导入 `os` 已删 | **closed**（残余 → H-02） |
| G-01 | P2 | 删除「已记录交付 commit/工件 hash」的不实断言；改为如实描述 + 交付 commit 延后核验 | **closed** |
| G-02 | P3 | `env-identity-report.txt` 恢复 `Git Clean Status` 并新增 `Porcelain Status`（`env_identity_probe.py:185-189`，实测 `probe-execution.log:25-40`） | **closed** |
| G-03 | P3 | 纯 LF 改为内存缓冲 + `.Replace("`r`n","`n")` + `WriteAllText`（`run-webview.ps1:67-69,90-92,105-107`）；我复测 r3 交付文件 `\r$`/`[ \t]+$` **零命中** | **partially closed**（`git diff --check` 输出/EXIT 仍未入库；BOM 语义见 §6） |
| G-04 | P3 | Task 测试表拆为 `-ProbeOnly`（:78）与完整运行（:79）两行 | **partially closed**（`-ProbeOnly` 行的证据仍指向 Full 模式日志，见 H-01③） |
| G-05 | P3 | 容器背景/边框改为 `contrast_ratio: null` + `NOT_VERIFIABLE` + 原因（`harness:346-356`，实测 `json:183-209,219-227`） | **partially closed**（非 primary 的**文本**角色阈值仍记 3.0，见 H-01①） |
| G-06 | P3 | `synthetic_alpha_cases` 对真实 `RegionOverlay.tsx` rgba 执行合成；docstring 表述与实现一致 | **closed**（配对/命名瑕疵 → H-04） |
| G-07 | P3 | `revisions[]` 补齐 `created_at/region_type/sfx_policy/is_current` 等全部 10 个 `RevisionSummary` 字段（`fixture:71-84,97-110,125-138`），并由 PRE-01 断言（`harness:233`） | **closed** |

### 3.2 早期已闭合项在 r3 未被回退（抽查确认）

F-01（Stage A 定位、死代码/未用参数）、F-02（真实 F token + live palette 分离与来源）、F-03（数值单一事实源）、F-04（`PRE-03` 与 AC6 分离、AC6 无 PASS）、F-06（未执行场景 `exit_code: null` + 带版本头/EXIT 的执行日志）、F-07（RESUME 检查点，r3 已续写 `RESUME.md:3-25`）、F-10（真实 wire/枚举/AC4 三操作）、F-11（layer union）、F-12（Task 测试表分行）——**均保持闭合**。r3 未回退 `apps/desktop/frontend/src/**`、`package.json`、`src-tauri/**`、Python Core、共享契约、依赖或 P03 runner。

### 3.3 关键复核证据（我独立完成的部分）

1. **PRE-03 数值全部可由「提交的夹具 + 提交的算法」复现**（WCAG 2.1，`0.04045` 阈值对本例无影响）：
 F token（底色 `#1a1a1d`）：`#ececee`**14.72**、`#a9a9b3`**7.45**、`#91919c`**5.57**、`#70707b`**3.55**、`#4d63e8`**3.53** —— 与 `json:131-172` 全部一致。
 live palette（底色 `#101418`，由 `role=app_base_background` 动态取得）：`#d8e0e8`**13.87**、`#8a94a2`**6.02** —— 与 `json:174-218` 一致。
 alpha 用例：`rgba(126,178,135,0.16)` over `#101418` 合成 (34,45,42) ⇒ vs `#d8e0e8` = **10.66**；`rgba(251,191,36,0.16)` 合成 (54,47,26) ⇒ **9.98** —— 与 `json:229-248` 一致；自检三项（21.0 / 1.0 / ≈3.98）与 NOT_VERIFIABLE 分支（`harness:146-161`）数学正确。
2. **wire 契约逐字段核对通过**：`BookSummary`（`library/types.ts:12-25` `book_id/original_title/is_favorite/is_archived/page_count/created_at/updated_at`）、`ChapterNavSummary`（`:53-57`，**`chapter_number` 确为 string**）、`PageNavSummary`（`:60-63` `page_id/source_filename/sort_order`）、`RegionSummary`（`region/types.ts:59-66`）、`RevisionSummary`（`:94-105` 10 字段）——夹具 `fixture:4-141` 逐字段吻合 ✔（r2 的 `has_regions`、`dialogue/thought`、数字 `chapter_number` 等非 wire 内容已全部移除）。
3. **AC4 `retype` 合法性已按源码状态机验证**：`relabelMachine.ts:76-90` 仅允许 `speech↔sfx`，其余转移显式禁用并给理由；`:174-180` 规定 speech→sfx 直接执行、sfx→speech 走确认对话框。夹具已由 r2 的非法 `speech→narration` 改为 `speech→sfx`（`fixture:144-169`）✔，且 `harness:239` 断言 `newRegionType == "sfx"` ✔。
 **`undo` 映射亦被源码证实**：`relabelMachine.ts:116`「undo uses revision restore, never reverse retype」+ `WorkbenchPage.tsx:684-688` 调用 `restoreRegionRevision` ⇒ 夹具 `undo` 用 `restore_region_revision` 正确 ✔。
4. **overlay rgba 来源行核对通过**：`RegionOverlay.tsx:45` = `PILL_WARN_BG = "var(--warn-soft, rgba(251, 191, 36, 0.16))"`、`:47` = `PILL_SKIP_BG = "var(--skip-soft, rgba(126, 178, 135, 0.16))"` ⇒ 夹具的 line 与 rgba 字面量准确 ✔（语义命名瑕疵见 H-04）。
5. **live palette 来源行沿用 r2 已核实结果**：`App.tsx:474/475/486/488`、`PageListPanel.tsx:53`、`ViewerPanel.tsx:152` ✔。
6. **Codex exact-commit replay 证据存在且内容自洽**（根工作区 `verification/P02/r2-clean-commit-validation.md`）：在 `git -c core.autocrlf=false worktree add --detach … 9b82e97b` 的独立 worktree 上运行 `-ProbeOnly`（EXIT=0）与直接运行 harness（EXIT=0），并记录三条 SHA-256；其 §边界 明确指出 `-ProbeOnly` 不产生 PRE-01/03，与 Task 旧表述不符 —— 与我的 r2 G-04 判断一致，且已被 r3 的表格拆分部分采纳。

---

## 4. Findings（r3 全部为 P3；无 P0/P1/P2）

### H-01（P3）闭合表与 r2 报告在 finding 编号/事实/强度上不一致

- **文件/行**：`doc/handoffs/P02-stage-a-foundation-handoff.md:24-45`（尤其 `:26-27`「彻底闭合了全部 open findings」、`:39-45` 的 G-01…G-07 映射、`:43` 的 `#30363d`）；`verification/P02/RESUME.md:10-16`；`doc/tasks/P02.md:121-130`。
- **问题与影响**：
 ① **编号语义漂移**：r2 报告定义的 G-01…G-07 与 r3 交付文档所使用的 G-01…G-07 **不是同一组缺陷**（例：r2「G-03」= `git diff --check` 无证据，r3 交付中「G-03」= `retype` 违反状态机；r2「G-07」= `revisions[]` 缺字段，r3 交付中「G-07」= PowerShell CRLF）。集成方按 r3 表逐条核对 r2 报告时无法一一对应。
 ② **hex 事实错误**：`handoff:43` 写「边框（如 `#30363d`）」，而夹具与报告的实际边框值是 `#2a3038`（`App.tsx:488`，`fixture:291-296`）；`#30363d` 在本片任何 artifact 中都不存在。
 ③ **过度闭合声明**：`:26-27` 称「彻底闭合全部 open findings」，但 G-03（`git diff --check` 证据）、G-04（`-ProbeOnly` 证据）、G-05（文本阈值）仍有残余（本报告 H-01①/§3.1）。
- **最小修正**：以 r2 报告的 `F-*`/`G-*` 为唯一编号，或显式给出 `r2 ID → r3 处置` 映射表；把 `#30363d` 改为 `#2a3038`；把「彻底闭合」改为逐项状态（closed / partially closed + 残余）。
- **状态**：open

### H-02（P3）PRE-02 消费既有静态报告但未做新鲜度绑定；其 `exit_code` 为合成值

- **文件/行**：`harness:265-296`（`:284` `0 if probe_pass else 1`）；对照 `run-webview.ps1:83-85`（Step 2 先生成报告）。
- **问题与影响**：PRE-02 现在读取既有 `verification/P02/static-control-report.json`，**仅在文件缺失时**才执行探针（`:267-270`）。在 runner 完整/`-ProbeOnly` 流程中该报告是刚生成的，故新鲜；但 Task 测试表把 `harness.run_preflight_checks()` 列为 PRE-01/PRE-03 的执行步骤（`P02.md:69,71`），若评审者**单独运行 harness**，上一轮遗留的报告会被直接当成 PASS 接受，探针失败不会传播。另 PRE-02 的 `exit_code` 是由报告文本推导的合成值，探针的**真实** EXIT 只在 runner 日志 Step 2 中留有记录。
- **最小修正**：在报告中写入运行标识/生成时间或 SHA-256 并在消费时校验，或无条件重跑探针；在 verdict 中区分「观察到的探针 EXIT」与「由报告推导的 pass/fail」。
- **状态**：open

### H-03（P3）PRE-01 的枚举断言是源码枚举的硬编码副本

- **文件/行**：`harness:230`（`assert reg0["region_type"] in ["speech","sfx","narration","title","note","other"]`）；真值源 `src/region/types.ts:14-21`（`REGION_TYPE_VALUES`）。
- **问题与影响**：该断言校验的是**夹具 vs 字面量**，而非**夹具 vs 源码枚举**。若将来 `REGION_TYPE_VALUES` 增删值（或夹具引入源码不存在的值），PRE-01 仍会 PASS —— 与「深度枚举断言、在根部阻断契约漂移」的表述不符（`handoff:44`、`P02.md:128`）。同理 `fixture:226-231` 的 `contrast_thresholds` 与 `fixture:274/281/288/295/302` 的 `expected_background_role` 被声明但**校验器从不读取**（阈值在 `harness:310,336,372` 硬编码）。
- **最小修正**：从 `region/types.ts` 解析 `REGION_TYPE_VALUES` 并断言夹具取值是其子集；或删除声称深度校验的表述。清理未被消费的夹具字段或标注其用途。
- **状态**：open

### H-04（P3）alpha 用例的前景/角色命名未对应被测量的真实表面

- **文件/行**：`fixture:311-328`；`harness:358-374`；来源 `RegionOverlay.tsx:42-48`。
- **问题与影响**：两个用例的前景固定为 `#d8e0e8`（App 正文色），而所引用的表面是"药丸"背景 `PILL_WARN_BG`(`:45`) / `PILL_SKIP_BG`(`:47`)，其**自身**文字令牌分别是 `--st-warn-t #fbbf24`(`:46`) 与 `--st-skip #7eb287`(`:48`)；同时 role 名 `*_region_highlight_overlay` 容易读成「区域高亮描边」（真正的高亮是 `STROKE_REGION/STROKE_SELECTED`，`:42-43`）。因此该用例证明了「alpha 合成链路可算」，但**并未测量该表面的真实文字对比**。补充（我的复算）：真实配对亦通过——`#7eb287` on 合成 (34,45,42) = **5.82**、`#fbbf24` on (54,47,26) = **7.97**。
- **最小修正**：把前景改为该表面自身的文字令牌（或明确标注「合成底 × App 正文色的假设配对」），并把 role 名改为 `*_pill_background_*`。
- **状态**：open

### H-05（P3）夹具中依赖全局配置的期望值未声明前提

- **文件/行**：`fixture:144-169`（`retype.expected_result.sfx_policy: "translate"`）；依据 `relabelMachine.ts:121-124`（「retype re-snapshots from the current global config, so translate is reachable」）。
- **问题与影响**：post-retype 的 `sfx_policy` 是**当前全局 SFX 配置的再快照**，并非 speech→sfx 的必然结果；夹具没有声明任何全局配置，却把 `translate` 写成期望值。Stage B 依此驱动时，若全局配置为 skip，实际读回是 `skip`，会被误判为失败。
- **最小修正**：在夹具中显式声明该场景的全局 SFX 配置前提（或把 `expected_result.sfx_policy` 标为 `any_of`/`config_dependent`）。
- **状态**：open

### H-06（P3）Task 交付记录中早期行仍为未来时/矛盾状态

- **文件/行**：`doc/tasks/P02.md:102-103`（「正式实现启动消息**将在**本状态checkpoint集成…后发出」「正式 Review 仍 NOT_RUN」）对照 `:105-130`（r1/r2/r3 均已交付、三轮 Review 已发生）。
- **问题与影响**：同一节内早期历史行与后续记录互相矛盾，且未标注为历史；重新进入该 Task 的读者会误判「实现消息尚未发出/正式 Review 未开始」。
- **最小修正**：把这些行标为历史快照（或改写为已完成状态），保持其余内容不变。
- **状态**：open

### H-07（P3）TS 契约的字段命名与机器产出格式不一致

- **文件/行**：`apps/desktop/frontend/e2e/workbench_driver_protocol.ts:36,39-46,51`（`acId` / `scenarioName` / `exitCode` / `blockerReason` / `timingData` / `contrastData`）对照 `p02-harness-results.json`（`scenario_id` / `scenario_name` / `exit_code` / `blocker_reason`，且无 `timingData/contrastData`）。
- **问题与影响**：TS 侧自称定义「Stage A data contracts / 固定格式」，但字段名与真实证据 artifact 的键名不一致，无法用该类型校验或解析产出；`timingData`/`contrastData`/`findings` 从未被任何产出填充（同为惰性契约面，`tsconfig.json:19` 仍排除 `src` 之外）。
- **最小修正**：把接口字段改为与 emission 一致的 snake_case（或明确声明二者为不同层并给出映射），删除未使用的惰性字段。
- **状态**：open

---

## 5. Architecture 结论

**通过（分层、契约、依赖、安全）。**

- **范围**：r3 变更面由**其自带运行期 porcelain 完整枚举**（`probe-execution.log:28-40` / `env-identity-report.json:32`）：13 个 ` M`，全部落在 `verification/P02/**`、`apps/desktop/frontend/e2e/**`、`doc/handoffs/P02-*.md`、`doc/tasks/P02.md`；**无 `??`、无 ` D`**（说明 `probe-execution.log` 已纳入版本控制、无新增越界文件、无删除）。**禁止路径零触碰**：`src/**`、`package.json`/`package-lock.json`、`src-tauri/**`、Python Core、SQLite schema/migration、共享 IPC/Schema、依赖清单、设计 token/契约、P03 runner、打包产物均未出现在 porcelain 中。
- **零构建、零依赖扩张**：日志三步只运行两个探针与 harness；`frontend/dist` 与 `cargo-target` 均 `Exists: False`；Python 仅标准库（`hashlib/json/platform/subprocess/sys/time/pathlib/shutil/winreg/re`）；TS 零 import；`package.json` 未变。**Hard Build Barrier 被真实遵守**。
- **AC/基线/契约未变**：`P02.md:1-18` frontmatter 逐字未变（`status: in_progress`、`base_commit=241ff3b7…`、`scope_contract_sha256=27DC31A8…`、branch/worktree、`integration_commit: null`）；未修 UI/对比度/token/debounce；F token 取自冻结 `tokens-cand-f.json`，live 值标 `UNMAPPED`，未反向改设计。
- **数据与进程安全**：夹具全为 `synth-*` 合成数据；探针只读单个 GUID 注册表子键、只读列举 EdgeWebView 目录、只读 `git rev-parse/status`、`node -v`、`npm.cmd -v`；harness 以 `sys.executable` 调用本仓探针（仅作缺失回退）；无 `shell=True`、无网络、无删除/移动、无用户库/SQLite/凭据访问；写操作限于 `verification/P02/`。
- **架构级改进**：alpha 合成与 `known_base_rgb` 语义在 Python 与 TS 两侧一致实现（`harness:119-143`、`ts:137-161`），并把「无法确定合成底」显式建模为 `NOT_VERIFIABLE` —— 与 AC6 的契约语言一致，属正确的 seam 设计。

---

## 6. Verification 结论

**r3 把 r2 的封堵点（证据绑定）实质解决，标签纪律保持正确；残余为准确性与可复算证据的 P3。**

**认可（含我的独立复核）**
1. **provenance 已可绑定被测检出**：`json:5-20` 记录运行期 `source_head=9b82e97b`、`source_tree=7fe67d0f`、`branch`、行为基线 `241ff3b7`，以及 **7 个关键源文件 SHA-256**（由 `hasher` 对工作区字节实算，`harness:31-47,62-73`），并显式声明「delivery commit 在这些文件生成之后才创建，由 Codex Gate 核验」；**自引用 `evidence_carrier` 已移除**。这同时满足了「绑定实际 HEAD/tree 与关键源哈希」「避免自引用」「区分 pre-commit 被测字节与后续交付 commit」三点。r2 的阻塞理由（证据无法绑定被审修订）**已不再成立**。
2. **独立复算证据存在**：Codex 在 clean detached worktree 上以 `core.autocrlf=false` 检出 r2 exact commit 复跑（`r2-clean-commit-validation.md:7-13`），EXIT=0，并归档 stdout/SHA-256；harness 在该固定 commit 上记录相同 head/tree，结果为 `3 PASS / 0 FAIL / 6 BLOCKED / 0 NOT_RUN`。
3. **人机报告一致**：`env-identity-report.txt` 与 `.json` 现在都披露 `Git Clean Status` 与 porcelain（`env_identity_probe.py:185-189`，`probe-execution.log:25-40`）；`p02-harness-results.txt` 与 `.json` 的 HEAD/tree/baseline/9 场景/Exit 逐项一致（日志 `:63-82` 回显与 JSON 相同）。
4. **命令/模式/EXIT 记录准确**：日志含 `Mode: Full Stage A`(`:9`)、每步完整命令行、`OUTPUT`、`EXIT`(`:45,58,83`)，以及聚合结论句(`:85`)；runner 在失败时 `Write-Error` + `exit $exitCode`(`run-webview.ps1:64-71`)，并区分 `-ProbeOnly`(`:87-94`) 与完整运行(`:100-108`)。
5. **LF/空白卫生在交付字节上成立**：我对 r3 全部交付文件（harness/probes/runner/4 份报告/日志/fixture）检索 `\r$` 与 `[ \t]+$` **零命中**；runner 通过内存缓冲 + CR→LF 归一化 + `WriteAllText` 生成日志，**从代码层解决了 CRLF 可复现性问题**（不再是事后转换）。
6. **AC6 语义符合 Task 要求**：所有 **文本**判定使用 `>=4.5`（primary text 与 alpha 用例；见 H-01① 的例外口径问题）、禁用文字/非文本使用 3.0、**无独立文本配对的容器背景/边框判 `NOT_VERIFIABLE` 并附原因**、背景 alpha **仅在提供已知不透明底色时**才合成、`token_mapping` 与 `contrast_result` 始终分列。
7. **PRE-01/PRE-02 有意义化**：PRE-01 由「键存在」升级为 wire 主键、枚举、revisions 结构、AC4 转移合法性断言（`harness:213-239`）；PRE-02 不再重复执行静态探针（`harness:265-296`）。
8. **无产品 AC 冒充**：`REAL_WEBVIEW2`/`REAL_WEBVIEW_MOCK_IPC` 场景全部 `BLOCKED` 且 `exit_code: null`（`json:254-342`、`log:77-82`）；PASS 仅存在于 `FILESYSTEM`/`STATIC_AST`/`TOKEN_MODEL` 前置层；Handoff/Task/RESUME 均按「preflight only / AC1–AC6 BLOCKED」记录（`handoff:53-63`、`P02.md:68-79`、`RESUME.md:17-23`）。
9. **数值无造假**：见 §3.3 的逐项复算（14.72/7.45/5.57/3.55/3.53/13.87/6.02/10.66/9.98 全部命中）。

**未达标/残余**：H-01（编号/事实/闭合强度）、H-02（报告新鲜度与合成 exit_code）、H-03（枚举副本）、H-04（alpha 配对命名）、H-05（配置依赖期望值）、H-06（Task 历史行）、H-07（TS/JSON 键名）。另有 G-03 的**证据侧**残余：`git diff --check` 的 stdout/EXIT 仍未入库（`P02.md:120`、`handoff:45` 均为断言）；且 `[System.Text.Encoding]::UTF8` 在 PowerShell 5.1 下通常会写出 UTF-8 **BOM**（`run-webview.ps1:69,92,107`），与「纯 LF 且干净」的目标不完全一致 —— 我无法用现有工具确认 BOM 是否存在（`grep` 默认剥离 BOM），故按**未核验**处理；建议改用 `New-Object System.Text.UTF8Encoding($false)`。

**本 Review 未执行**：未运行 Cargo/Tauri/sidecar build；未运行 `run-webview.ps1`、两个探针或 harness；未运行 Vitest/前端构建；未做真实 WebView2/GUI/CDP 操作；未执行任何 git 命令；未计算或校验任何 SHA-256。以上「已认可」项均来自**只读阅读 + 我的独立数学/契约复算**，不包含任何我未亲自执行的运行结果。

---

## 7. 逐 AC 状态（Stage A 视角；P02 保持 `in_progress`）

| AC | 层级 | r3 记录 | 本次判定 |
|---|---|---|---|
| AC1 真实 WebView2 harness | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED**（无受信隔离构建产物；不接受为 passed） |
| AC2 导航与操作 | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED** |
| AC3 300ms quiet-period/失效窗口 | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED** |
| AC4 写后刷新（retype/undo/restore） | `REAL_WEBVIEW_MOCK_IPC` | BLOCKED / EXIT=null | **维持 BLOCKED**（夹具已合法化，但未执行；符「不得以 NOT_RUN 替代」） |
| AC5 键盘与焦点 | `REAL_WEBVIEW2` | BLOCKED / EXIT=null | **维持 BLOCKED** |
| AC6 F token/对比度 | `TOKEN_MODEL` 前置 + `REAL_WEBVIEW2` 运行时 | PASS（`PRE-03`）/ BLOCKED（运行时） | **AC6 维持 BLOCKED**；`PRE-03` PASS 仅为静态调色板数学，**不构成 AC6 证据**（H-01①/H-04） |
| AC7 固定证据与发现处置 | 证据机制 | 部分 | **基本达标、残留 P3**：provenance/key-source hash/无自引用已建立（F-05/G-01 closed）；交付 commit 与 `git diff --check` 证据仍待 Codex/下一 head 归档 |
| PRE-01 夹具契约（前置） | `FILESYSTEM` | PASS | 认可（wire/枚举/revision/relabel 断言；H-03/H-05 为精度残余） |
| PRE-02 静态源码契约（前置） | `STATIC_AST` | PASS | 认可（断言已在 base 独立复现；H-02 为新鲜度残余） |
| PRE-03 调色板数学（前置） | `TOKEN_MODEL` | PASS | 认可（数值已独立复算；H-01①/H-04 为口径/配对残余） |

**明确声明**：P02 仍 `in_progress`；**AC1–AC6 运行时一律不接受为 passed**；`PRE-01/02/03` 与任何脚手架 Gate PASS **不等于产品 UI/WebView 质量 PASS**；本 Stage A Gate **不等于 Task 完成**。

---

## 8. 范围与禁止路径

- r3 变更集合 ⊆ Owner allowlist（证据：运行期 porcelain 完整枚举 13 项 + 逐文件读取），**无 scope creep**、无删除、无新增越界文件。
- `doc/tasks/P02.md` 仅更新测试表与执行/交付记录；frontmatter、AC1–AC7、允许/禁止范围逐字未变（`P02.md:1-18` 已核）。
- 无构建、无依赖变更、无共享契约/schema/P03 runner/设计 token 改动、无 exe/dist 产物。
- 未接触用户漫画库、SQLite 生产数据、Lock、current/pinned Revision、凭据。
- 给 Integrator 的比对口径提醒：候选为本地 `core.autocrlf=false` 的 LF 检出，跨工作区比对须 `--ignore-cr-at-eol`。

---

## 9. 限制（未能核验项）

1. **无 shell**：`pwsh` 不可用（见 §1），因此 **reviewed tree `ce6e44c9…`、r2 tree `7fe67d0f…`、base tree `f27d12a7…`、scope contract SHA-256、`key_source_files_sha256` 7 项、Codex 归档的 3 项 SHA-256 均未能独立重算**；**`git status`/`git diff`/`git diff --check` 未执行**；**Owner 声称的 exact-HEAD clean 状态未能核验**（唯一状态证据是运行期 `is_clean: false` + 13 条 porcelain）。
2. r3 变更清单未由 `git diff` 取得，依赖运行期 porcelain（该快照**不包含**提交前 28 秒内对 `doc/handoffs`、`doc/tasks`、`RESUME.md` 的写入？——实测 porcelain **包含**这三项，故本次快照完整覆盖；仍无法证明提交后工作区与提交字节一致）。
3. 未重新执行 r1/r2 的全树 base↔HEAD 禁止路径内容比对；r3 的越界判断基于 porcelain + 逐文件读取 + base 侧契约抽查。
4. **BOM 不可判定**：`grep` 默认剥离 UTF-8 BOM，`read` 亦然，故 `probe-execution.log` 是否带 BOM 未核验（代码路径 `[System.Text.Encoding]::UTF8` 提示很可能带）。
5. 未核验：Codex `r2-clean-commit-validation.md` 中三条 SHA-256 与实际文件的一致性；`-ProbeOnly` 在 r3 交付中的实际运行（交付内无 ProbeOnly 日志）；WebView2 版本/OS 信息（直接采信探针输出）。
6. 未审计：P02 之外的历史 Task/证据、`test_assets/**`、`wiki/**`、`.codewiki/**`。

---

## 10. 必须由 Codex 处理的治理下一步

1. **exact-commit replay 需覆盖 r3**：现有归档针对 r2（`9b82e97b`）。请在 clean detached worktree（`core.autocrlf=false`）对 **`5fa8a41f`** 复跑 Stage A probes + harness，归档 command/stdout/stderr/EXIT 与结果文件 SHA-256，并**一并归档 `git diff --check` 的 stdout 与 EXIT**（关闭 G-03 证据侧）。
2. **登记与解阻**：在 `STATUS`/`REBASELINE_PLAN`/`ROADMAP` 登记 P02 Stage A r3 head 与本 Review 决策；按 `build-preflight-lf-r1.md` 先登记隔离 scratch worktree、可信 sidecar 输入来源/临时路径与 Hash 复算方式及准确命令，**再**开放 Cargo/Tauri 构建；此前不得在 Owner worktree 构建。
3. **状态文档同步**（Owner allowlist 之外）：`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:3`、`doc/12_ROADMAP.md:3`、`doc/00_INDEX.md:3`、`doc/tasks/README.md:5`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md:3,5` 仍称「实现消息待发送 / AC1–AC7 全部 NOT_RUN」，与 r1–r3 已交付不一致；同步时保持 `in_progress` 与「运行时 AC 未执行」口径。
4. **不得据此释放 P07**：Stage A 未证实任何用户可见产品缺口。
5. **P3 债务处置**：将 H-01–H-07 与 G-03/G-04/G-05 残余登记为 accepted debt 或要求在下一 head 修正；**在 P02 进入 `done` 前必须全部关闭**。

---

## 11. Final verdict

```
decision: approved_with_conditions        (Stage A only)
reconciled (r2 open items):
  F-05 closed | F-08 closed | F-09 closed | G-01 closed | G-02 closed
  G-03 partially closed | G-04 partially closed | G-05 partially closed
  G-06 closed | G-07 closed
new (all P3): H-01 … H-07
counts:  P0/P1/P2/P3 = 0 / 0 / 0 / 10   (open = 10, 全部 P3)
```

**条件（不阻塞 Stage A 脚手架继续，但必须在 P02 `done` 前关闭）**：
1. **Codex**：对 `5fa8a41f` 完成 clean detached exact-commit replay，并归档 `git diff --check` 的 stdout/EXIT（或明确将其列为豁免并说明依据）。
2. **Owner（下一 head）**：修正 H-01（编号/`#30363d`/「彻底闭合」表述）、H-02（报告新鲜度或无条件重跑；区分观察 EXIT 与推导 pass/fail）、H-03（从 `region/types.ts` 派生枚举）、H-04（alpha 配对/命名）、H-05（声明全局配置前提）、H-06（Task 历史行标注）、H-07（TS 键名对齐）；并处理 G-05 的**非 primary 文本阈值**残余（`harness:310,336`，当前对 `ink_2/ink_3/#8a94a2` 记 `min_required=3.0`，与 AC6「文本至少 4.5:1」不一致；不影响判定，因三者实测 7.45/5.57/6.02 均 ≥4.5）。
3. **所有者/集成方**：`[System.Text.Encoding]::UTF8` 建议改为 `UTF8Encoding($false)`，以免日志带 BOM。

**结论**：r3 是一次**高质量的定向修订**。r2 的 P2 阻塞项（F-05/G-01：证据自引用、无法绑定被审修订、以及不实的闭合声明）已被**实质而正确地**解决——provenance 现在记录运行期 HEAD/tree 与关键源文件 SHA-256、显式声明交付 commit 事后核验、移除了自引用；F-08/F-09 的硬编码与重复执行问题已修；G-02/G-06/G-07 已闭合，其中 G-07（wire 字段）与 G-04（AC4 `retype` 合法性）我还借助 `library/types.ts`、`region/types.ts`、`relabelMachine.ts` 的源码独立确认；PRE-03 的 11 个对比度数值我逐个复算全部命中，且**没有任何真实 WebView2/Core 被冒充为 PASS**。剩余 10 项**全部为 P3**，属于文档准确性、校验精度与证据归档完备性范畴，不改变 Stage A 的安全边界与判定结论，因此本切片在**带上述条件**的前提下可交 Codex 继续集成流程。**P02 仍为 `in_progress`；AC1–AC6 运行时维持 `BLOCKED`；Cargo/Tauri/WebView 运行时 AC 不接受为 passed；本 Review 不代表 P02 完成。**
