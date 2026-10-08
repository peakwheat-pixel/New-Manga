# P03 正式非作者 Review（R4）

- `task_id` = **P03**
- `reviewer` = **DeepSeek Harness**（非作者；`author`/`owner`=Antigravity，`integrator`=Codex）
- `author` = **Antigravity**
- `base_commit` = `31abde9bf4b73aea2851931dcd48faa0f750b318`
- `reviewed_head` = `d717c049a41544a6d592943a0b0fe1b76a41a050`
- `decision` = **approved**（Architecture：PASS；Verification：PASS with conditions；未解决 P0/P1 = **0 / 0**）
- 边界声明：本 Review **不是** Codex integration Gate；**不代 Codex 置 Task `done`**；不把 R3 批准延伸到任何新 commit；本批准仅覆盖上述固定 `base..reviewed_head`。

---

## 0. 环境限制与执行口径（必读）

本会话 shell 通道全程不可用：每次 `pwsh` 在沙箱 workspace 准备阶段即失败——`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P03-review-prep-85482c5b)`；随后按规则对同一命令做一次升级重试，返回 `sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`，即 fail-closed。**因此所有 git / pytest / 构建 / Gate / 哈希计算命令一律记 `NOT_RUN`，我不声称自己运行过任何一条。**

替代手段（DSH 自行执行的只读文件检查，非 git 命令、非 Codex 日志转述）：

| 核对项 | DSH 自行手段 | 结果 |
|---|---|---|
| HEAD | 读 worktree `.git` → `gitdir: G:/CODEX/New Manga/.git/worktrees/P03-review-prep-85482c5b` → 读该 gitdir `HEAD`（`ref: refs/heads/codex/P03-integration-4c04459`）→ 读 `.git/refs/heads/codex/P03-integration-4c04459` = `d717c049a41544a6d592943a0b0fe1b76a41a050` | **HEAD == reviewed_head**（独立确认） |
| branch | 同上 HEAD 文件 | `codex/P03-integration-4c04459` |
| common-dir / worktree | 读 `.../worktrees/P03-review-prep-85482c5b/commondir` = `../..` → `G:/CODEX/New Manga/.git` | 与 Task/RESUME 记录一致 |
| 祖先链 | 读 `.git/logs/refs/heads/codex/P03-integration-4c04459`（16 条线性 reflog）与 worktree `logs/HEAD`（18 条） | 末条 = `423ea5f1 → d717c049  commit: docs(p03): record r3 condition closeout`（1791494110） |
| **main ref（新增事实）** | 读 `.git/HEAD`（`ref: refs/heads/main`）与 `.git/refs/heads/main` | **`main` 已 = `d717c049…`（== reviewed_head）**；`.git/logs/refs/heads/main` 第 402/403 行：`0a31bbc5 → 423ea5f1 merge …: Fast-forward`、`423ea5f1 → d717c049 merge …: Fast-forward`（1791494122） |
| 未提交文件 | glob 全树 + trace 21 | 未跟踪：`integration/run-2de124f3-finalhead-423ea-py314/**`、`integration/build-logs/21,22`、`integration/dsh-review-r4.{prompt.md,stdout.jsonl,stderr.log}`；**均不计入 reviewed diff** |

**NOT_RUN（原因：pwsh 沙箱 Win32 5 + 无审批通道）**：`git rev-parse HEAD`／`--abbrev-ref HEAD`／`--git-common-dir`／`--show-toplevel`、`git status --porcelain`、`git worktree list`、`git diff --name-only base..head`、`git diff --check base..head`、`git cat-file`／`git show`、`pytest`（40 项）、`check_snapshots.py`（16 项）、`run_clean_start_e2e.py`（28 项 Gate）、`npm ci/npm run build`、`build_sidecar.ps1`、`npx @tauri-apps/cli@2 build`、`normalize_gate_logs.py --verify-only`、`verify_normalization.py`、**任何 SHA-256 复算（含 ZIP 内部文件哈希）与 ZIP 解包**。

---

## 1. 范围与依据

依据文件：`AGENTS.md`、`doc/09_COLLABORATION.md`（§3/§4/§5/§6，含 §6.12 证据纪律）、`doc/templates/REVIEW.md`、`doc/tasks/P03.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md`、4 份 P03 Handoff、`verification/P03-PACKAGED-SFX-ENTRY/{RESUME.md,integration/RESUME.md,integration/build-manifest.json}`、`integration/dsh-review-r3.{md,stdout.jsonl,exit,prompt.md}`、build-logs 02／11／12／14／15／16／17／18／19／20／21／22、finalhead Gate 原始 JSON、两份实现文件、`packaging/m2ac5/core_sidecar.spec`、`packaging/release-gate/run_release_gate.py`、`apps/desktop/src-tauri/src/main.rs`。

**固定范围（复核 Codex trace 21，非 DSH 运行）**：`git diff --name-only 31abde9b..d717c049` = **132 paths**、`OUT_OF_SCOPE_COUNT=0`、`git diff --check` 输出空、`DIFF_CHECK_EXIT=0`（`build-logs/21`，`Fixed review candidate=d717c049…`，`Tracked working tree before checks: clean`）。
我逐条读完 132 条路径并对该清单做反向检索 `^(src/|apps/|contracts/|requirements|packaging/release-gate|packaging/m2ac5/core_sidecar.spec|packaging/m2ac5/build_sidecar.ps1|package.json|Cargo)` → **零命中**。清单构成：`doc/**`（P03 Task、4 份 P03 handoff、6 个 Codex 维护的导航文件）、`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_packaged_fifth_sfx_entry.py`、`verification/P03-PACKAGED-SFX-ENTRY/**`。**`src/**`、`apps/**`、contracts、Schema、依赖、build spec/script、release-gate runner 零差量成立**（基于 Codex trace + 我的反向检索，非 DSH 自跑）。

**范围自洽校验（DSH 独立推导）**：trace 11=`2d114480`=114 → 12=`fb5782c5`=117 → 15=`41be59e9`=120 → 17=`423ea5f1`=122 → 21=`d717c049`=132。对 17 与 21 的清单逐项求差，**`21 \ 17` 恰为 10 条证据/文档路径**：`build-logs/{17,18,19,20}`、`raw-finalhead-gate-output.zip`、`dsh-review-r3.{exit,md,prompt.md,stderr.log,stdout.jsonl}`；两条代码/测试路径（`run_clean_start_e2e.py`、`test_packaged_fifth_sfx_entry.py`）在两个清单中均在，且 `d717c049` 的提交信息为 `docs(p03): record r3 condition closeout`。⇒ R3-01/R3-02 的收口提交在路径层面是**纯证据/文档**（内容级恒等无法证明，见 §7 残余风险②）。

---

## 2. 视角状态

- **Architecture** = `executed`：范围冻结、依赖方向、fail-closed 语义、调用链一致性、数据/AppData 隔离、集成边界。
- **Verification** = `executed`（DSH 自跑全为 `NOT_RUN`；采用只读复核 + 静态可判定性 + 手工计数交叉校验，见 §4）。
- **Spec** = `executed`：AC1–AC5 与 Task 输入表/测试计划逐项对照。Standards 视角按模板 2026-09-18 口径不强制，未单列。

---

## 3. Architecture 判定：**PASS**

1. **fail-closed 语义正确**：`evaluate_sidecar_survivors`（`packaging/m2ac5/run_clean_start_e2e.py:747-756`）先对**缺键**返回 `False`，再对非零泄漏判定；`main()` 在 `:1148-1156` 以 `SIDECAR_EXES`（`:66-72`，恰 5 项含 `sfx_detect_probe.exe`）调用并产出 `CS-Z3`。安装断言 `:243` 与 `:246` 同源使用 `SIDECAR_EXES`，清单单一来源，无第二份重复枚举。
2. **R-003 修复在 head 真实存在**：`weights_in_install_dir` 初值 `False`（`:791`），仅在 `weights_path_str and install_dir is not None` 且 `is_relative_to` 成立时才为真（`:792-798`），并**无条件**进入 `passed` 合取（`:820`）；调用者 `run_sfx_probe_phase` 恒传 `install_dir=install_dir`（`:955`）。省略 `install_dir` ⇒ FAIL（回归断言 `test_packaged_fifth_sfx_entry.py:144-147`）。
3. **成功/失败谓词与 AC2 文本逐一对应**：成功 `:811-821` = exit 0 ∧ marker 恰 1 ∧ payload 为 dict ∧ `frozen is True` ∧ `error` 键存在且为 `null` ∧ `type(n_candidates) is int and >0`（排除 bool）∧ 权重 sha == pin ∧ `resolved_from=="bundle_probe"` ∧ 路径位于 install_dir 内；失败 `:867-873` = exit 1 ∧ marker 恰 1 ∧ payload ∧ frozen ∧ 非空 dict error；缺页前置断言在 `:963-980`（`path_precondition=absent`）。
4. **依赖方向与数据保护无回归**：新增能力只落在打包验收工具与测试；不进入 `src/**`、不经 WebView/IPC、不新增依赖；`--output-dir` 仍 `required=True`（`:1026`），历史 raw 覆盖防护保持（回归文件 8 项在 log 19 全绿）；K07 与 ONNX 仅只读、未入库（132 路径无 `.png`/`.onnx`）。
5. **调用者一致性**：生产者仅 `run_clean_start_e2e.py`；消费者为新测试文件与既有 snapshot oracle（AST 抽取 `Gate`/`run_library_probe`，不受 P03 改动破坏）。`tests/packaging/test_runner_output_dir_required.py` 未在 132 路径内（未改）却仍全绿，属独立回归面。
6. **范围外同源第二处（登记不改）**：`packaging/release-gate/run_release_gate.py:95-100` 的 `SIDECAR_EXES` 仍只列 4 个；`apps/desktop/src-tauri/src/main.rs:567-568` 注释仍写 `host_bridge / core_service / acceptance_bridge / catalog_loader`（而 `packaging/m2ac5/core_sidecar.spec:4-21` 已冻结 FIVE 且含 `sfx_detect_probe.exe`）。两者均**不在** 132 路径内，P03 未暗改；见 R3-03 与 §5。
7. **集成边界（登记项，见 R4-02）**：`refs/heads/main` 已 = `d717c049`（fast-forward，reflog 402/403），Task/manifest/STATUS/README/Plan 仍写 `integration_commit = 423ea5f1`。

---

## 4. Verification 判定：**PASS（含 3 项 P3 记录项）**

### 4.1 R3-01（P2）— **fixed 确认**

| 断言 | 证据（均为 DSH 逐字复核 Codex 保存件，非自跑） | 结论 |
|---|---|---|
| 40 项定向测试绑定提交 | `build-logs/19`：`source_head=423ea5f1…`、`installer_sha256=2de124f3…`、`python=Python 3.14.6`、完整 command + pytest 头、`40 passed in 0.57s`、`EXIT=0` | 成立 |
| 测试计数自洽 | DSH 手数：新文件 1+1+1+1+1+16+1+9+1=**32**，回归文件 8 ⇒ **40**；log 19 参数化 ID 顺序与 head 提交内容逐条一致（成功负例 16、失败负例 9） | 成立 |
| 28/28 packaged Gate 绑定同一 head 与同一 installer | `build-logs/20`：`source_head=423ea5f1…`、`installer_sha256=2de124f3…`、`K07_sha256=28dab503…`、TEMP/TMP 隔离、完整 runner 输出、`GATE: PASS`／`EXIT=0`；DSH 手数 `[PASS]` 行 = 3+2+3+3+7+4+2+4 = **28** | 成立 |
| 结构化 28/28 | `raw-finalhead-gate-output.zip`（committed，manifest `sha256=99c135e8…`、`entry_count=11`、`all_entry_hashes_verified=true`）；其未跟踪工作树副本 `run-2de124f3-finalhead-423ea-py314/cleanstart-gate.json`：`verdict=PASS`、`installer_sha256=2de124f3…`、28 条 scenario 全 `PASS`（DSH 逐条计数 28）、`sfx_verification.requested=true/verdict=PASS` | 成立（ZIP 内部字节 DSH 无法复算，见 §7） |
| installer/source/hash 关联 | Task `:64-66` 三指纹分列（`5a14c0a9`／`2de124f3`／`d21e89b6` 标「已被取代」）；manifest `installer.sha256`、gate log 头、gate JSON CS-E2、manifest `r3_01_*` 四处一致 | 成立 |
| S1 真实 K07 正向 | gate `observed` + `sfx-probe-real-page.json`：`exit=0`、marker 1、`json_parsed`、`frozen=true`、`has_error_key` 且 `error=null`、`n_candidates=1`（严格正整数）、`weights.sha256 == expected_sha256 == pin 944e8114…`、`resolved_from=bundle_probe`、`weights.path` 位于 `…m2ac5-cleanstart-2mivzfqv\install\` 内、`page_file_sha256=28dab503…`（K07 pin）、`device=dml`／`sfx_ep=dml`／`fallback=null`、`page.width/height=690/1408` | **真实且正确**；逐项满足 head 版谓词 |
| S2 缺页失败 | `sfx-probe-missing-page.json` + gate `observed`：`exit=1`、marker 1、`frozen=true`、`error.class=FileNotFoundError` 非空、`missing_path` 指 `sfx-probe-missing-isolation\guaranteed-nonexistent-page.png`、`path_precondition=absent`（代码 `:972-980` 启动前断言） | **真实且正确** |
| 零触碰断言匹配 | gate：`CS-Z1 changed_entries=[]`；`CS-Z4 files=4 changed_entries=[]`（host 真实 APPDATA，只读快照）；`CS-Z2 files=4`；`CS-Z3` 五 sidecar 全 0（`python.exe=9` 为 record-only，代码 `:1148-1155` 注释与 Task/AC4 口径一致） | 成立 |
| 日志内 python/EXIT | 19/20 两份日志均带 shell/解释器/命令/EXIT 头（§6.12①） | 成立 |

**结论：R3-01 关闭成立。** 残留表述项见 R4-04（16 项 snapshot oracle 仍绑 `db2c1e93`）。

### 4.2 R3-02（P3）— **fixed 确认**

- `423ea5f1…` 的 scope/diff trace 与两份只读 normalization trace（`build-logs/17`、`18`）**已进入 reviewed head 的提交路径集合**（trace 21 列表 58/59 行）；我更直接读到：17 = `Fixed DSH review head: 423ea5f1…`、`PATH_COUNT=122`、`OUT_OF_SCOPE: none`、`DIFF_CHECK_EXIT=0`；18 = `Fixed DSH review head: 423ea5f1…`，`verify_normalization.py` 6/6 PASS + `normalize_gate_logs.py --verify-only` 6/6 PASS，`VERIFY_EXIT=0`。
- 导航与恢复点：`STATUS.md:3,7`、`REBASELINE_PLAN.md:3,7`、`00_INDEX.md:3,9`、`12_ROADMAP.md:3`、`tasks/README.md:5`、`P03.md:16,53` 均指向集成 head `423ea5f1…`／`codex/P03-integration-4c04459`／`in_review`，并指向当前 RESUME。
- **无「DSH 跑过未运行命令」的假述**：`P03.md:125` 明写「DSH's own shell/Git/test/Gate commands were `NOT_RUN` due Win32 5」；`integration/RESUME.md:9-10` 同口径；manifest `dsh_r3.desktop_web_visibility=unverified`；R3 报告 §0 自陈。✅
- **未能闭合的部分**：R4 新 head `d717c049` 自身的 21/22 trace 未入库，且提交树中无任何文件写 `d717c049`（DSH 全仓 grep：仅未跟踪的 21/22 与 R4 prompt/jsonl 命中）→ 见 **R4-03**（结构性、非阻断，Codex 收口时应提交）。

### 4.3 R3-03（P3，明确范围外）— **登记属实、未越界，建议保留给 P20**

- `run_release_gate.py:95-100`（`SIDECAR_EXES` 4 项，另 `:956-959` 同源安装断言）与 `main.rs:567-568` 注释仍写四入口 —— **确认仍在**。
- 两处均不在 132 路径内（反向检索零命中）→ **P03 未暗中修改范围外文件**。✅
- 登记确实存在且为非阻断/范围外：`P03.md:54`、`manifest.r3_findings_disposition["R3-03"]="deferred_non_blocking_out_of_scope: … forward the release-gate runner concern to P20 task-scope registration"`、`STATUS.md:3,7`、`REBASELINE_PLAN.md:7`、`integration/RESUME.md:11`。P20 = 「最终 Windows 发布 Gate」（Plan `:59`，`proposed/未释放`，依赖 P19+P03+P06），把 release-gate 第五 sidecar 遗漏挂到 P20 范围登记是**自洽**的。
- **对 P20 的建议（不要求本 Task 越界）**：P20 释放时需在冻结范围中显式包含 `packaging/release-gate/**` 与 `apps/desktop/src-tauri/src/main.rs` 注释，并要求新建的 release-gate scope trace 覆盖第五入口；同时把已登记的 R-004（ONNX 独立重算）一并纳入 P20 门。**不得**在 P03 内改这两处。

### 4.4 既有 R-001–R-006 / C-001–C-003 逐项复核

| ID | 级别 | DSH 独立结论 | 依据（DSH 直接读取） |
|---|---|---|---|
| R-001 | P2 | **fixed** | 输入表 `:64-66` 三指纹分列 + `d21e89b6…` 标「已被取代」；`2de124f3…` 在 manifest `:35-51`、log 20 头、gate JSON `:4,48`、manifest `:312-313` 一致 |
| R-002 | P2 | **fixed** | 11=`2d114480`(114)、12=`fb5782c5`(117)、15=`41be59e9`(120)、17=`423ea5f1`(122) 均 `OUT_OF_SCOPE none` + `DIFF_CHECK_EXIT=0`（我直接读到 11/12 头与 17 全文、15 计数行） |
| R-003 | P2 | **fixed（代码面）** | `:791-798`+`:820` 无条件要求 `weights_in_install_dir`；`:144-147` 负例；40/40 含该例 |
| R-004 | P3 | **deferred 合理，风险表述基本准确** | 成功谓词只采信 payload 自述 `weights.sha256`（`:785-786`），不对安装目录内 ONNX 独立重算；AC2 文本未要求。**唯一措辞瑕疵**：Task `:46` 称「a hash-pinned fresh installer」，而 runner 的 CS-E2 只**记录** installer sha（`:1051-1055`），代码内无 installer pin → 见 R4-05（P4） |
| R-005 | P3 | **fixed** | r3 Handoff `:63` = `6,702` CHAR tokens、`137 / 2` NL/Trailing；log 22/18 的 03 文件 raw 14,601 B／canon 7,627 B 与表一致；与 manifest/`07-encoding-normalization.json` 口径一致 |
| R-006 | P3 | **fixed** | `build-logs/03`（`2da76b1d`）、`04`（`19f5348f`）、`05`（`a7161ca3`）、`06`（`a3aaf229…`）均含 shell/HEAD/clean status |
| C-001 | P2 | **在 reviewed head 已不成立（disposition 过期/回退）** | Task `:49` 称「P03 RESUME now links to `../../doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md`」，但 `verification/P03-PACKAGED-SFX-ENTRY/RESUME.md`（全文 33 行）与 `integration/RESUME.md`（全文 53 行）均**无任何 handoff 引用**（DSH 对该目录 grep `handoffs` 零命中于两份 RESUME）。handoff 仍可经 `doc/tasks/P03.md:117-120` 到达 → 见 **R4-01** |
| C-002 | P2 | **fixed 确认（敏感度修复真实）** | 测试 `:249-284` 每例先构造**有效** `install_dir` 与目录内 weights path（`:253-255` 并 `mkdir`），**先断言未修改 baseline PASS**（`:273-274`），再施加单一负条件；16 个成功负例 + 9 个失败负例逐条推演均具判别力（无被其它条件遮蔽）；缺省 `install_dir` fail-closed 断言独立保留（`:144-147`） |
| C-003 | P3 | **fixed** | Task `:62` 记同 installer 28/28；RESUME 命名当前状态与 head |

---

## 5. Findings

命名沿用历史序列，本 Review 新发现记为 `R4-xx`。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据（DSH 只读） | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R4-01 | **P3** | `doc/tasks/P03.md:49`（C-001 disposition） vs `verification/P03-PACKAGED-SFX-ENTRY/RESUME.md:1-33` | Task 在 head 上声称 RESUME 已链接 r3 handoff，但两份 RESUME 均无 handoff 引用 ⇒ disposition 文本与提交树不一致；未来仅读 RESUME 的恢复者失去 4 份 handoff 指针（Task 仍可达，故影响低）。R3 报告 `:80` 的同一结论也已不适用于新 head | 全文读取两份 RESUME；对 `verification/P03-PACKAGED-SFX-ENTRY` grep `handoffs` → RESUME 零命中；`140a6686` grep → 仅命中 Task/Handoff/R3 证据/trace 路径表 | Codex 收口时二选一：①在 RESUME 恢复 handoff 链接；②把 `:49` 改写为「修复已由 Task handoff 段承载，RESUME 修订后不再保留该链接」，避免 stale claim | open（P3，文档准确性） |
| R4-02 | **P3** | `.git/refs/heads/main`、`.git/logs/refs/heads/main:402-403` vs `doc/tasks/P03.md:16`、`verification/.../integration/build-manifest.json:261-262`、`doc/STATUS.md:3,7`、`doc/tasks/README.md:5`、`doc/REBASELINE_PLAN.md:3,7`、`doc/00_INDEX.md:9` | `main` 已在 **1791494122** fast-forward 到 `d717c049…`（== reviewed_head），即 reviewed diff 事实上已落在主线；但所有文档仍写 `integration_commit/集成commit/集成head = 423ea5f1…`，且没有任何提交件记录该 ff 或真正的集成 tip ⇒ **Task 与集成边界记录不准确**（`in_review` 状态本身没错，错的是指针落后一个 commit） | DSH 读 `.git/HEAD`、`.git/refs/heads/main`、main reflog（`423ea5f1 → d717c049 merge …: Fast-forward`）；manifest `candidate_head/integration_commit` 均为 `423ea5f1`；全仓 grep `d717c049` 无 committed 命中 | Codex 在 AC5 收口时记录 `integration_commit`（≥`d717c049`）与 ff 事实，并说明「先 ff 候选再审查/收口」是否为 P03 既定集成口径（reflog 显示 `423ea5f1` 亦先 ff 后被 R3 审查） | open（P3，治理/指针） |
| R4-03 | **P3** | 未跟踪 `verification/P03-PACKAGED-SFX-ENTRY/integration/build-logs/21-finalfixedhead-scope-diff-check.log`、`22-finalfixedhead-normalization.log`；对照 `build-manifest.json:279-292`（仅登记 17/18） | R4 精确 head 的「132 paths／out-of-scope=0／diff-check EXIT=0」与两份 normalization 6/6 结论目前**只存在于未提交文件**（即 R3-02 同类形态在新 head 复现）；提交树内无任何文件写 `d717c049`，复核材料不可版本化追溯 | glob 显示 21/22 存在但不在 trace 21 的 132 路径内；全仓 grep `d717c049` 仅命中 21/22、R4 prompt/jsonl（均未跟踪） | Codex 收口提交时把 21/22（或等价结论段）入库，并在 manifest 增补 `r4_fixed_head_checks` 段（head/count/EXIT）；§5 允许 Handoff 后置引用先前 head | open（P3，证据版本化） |
| R4-04 | **P3** | `integration/build-logs/02-snapshot-check.log:4`（`Source HEAD: db2c1e93…`） vs `doc/tasks/P03.md:38,100` | AC4 把「受影响的 Runner Snapshot oracle（16 passed）」列为与 40 项定向测试并列的通过项，但该 oracle 的最后一次 artefact 绑定在 `db2c1e93`，**未在 `423ea5f1`／`d717c049` 重跑**；manifest 亦无对应条目（`:246-260` 只有 C-002 段）。head 适用性依赖「`run_clean_start_e2e.py` 自 `db2c1e93` 未再变化」这一仅由提交信息/路径计数支撑的前提 | log 02 头行 + 全 `verification/P03-PACKAGED-SFX-ENTRY` grep `check_snapshots`（仅 02 与 Owner 侧旧日志）；manifest 无 snapshot 段 | 二选一：①在收口 head 复跑 `check_snapshots.py` 并按 19/20 格式入库；②在 Task/manifest 明确写「oracle 绑定 `db2c1e93`，其后无 `run_clean_start_e2e.py` 内容变更（附依据）」 | open（P3，证据绑定） |
| R4-05 | **P4** | `doc/tasks/P03.md:46`（R-004 措辞）；`packaging/m2ac5/run_clean_start_e2e.py:1051-1055`（CS-E2） | 「a hash-pinned fresh installer」易被读成 runner 内断言 installer pin；实际 runner 只记录实测 sha，pin 由 manifest/Task 承载 ⇒ 未来读者可能高估 Gate 的自校验强度（无实际安全回退，因为 gate log/JSON/manifest 三处 sha 一致且被人工比对） | 读 CS-E2 代码：`gate.pass_or(installer.is_file(), …, {"sha256": sha256_file(installer)})`，无期望值常量；grep runner 无 installer pin | 措辞改为「installer sha 由 runner 记录并与 manifest 比对一致」；若要更强保证，可在 runner 增 `--expected-installer-sha` 可选参数（非本 Task 必需） | open（P4，措辞） |
| R4-06 | **P4** | `packaging/m2ac5/run_clean_start_e2e.py:1135-1146`（CS-Z2）；`doc/tasks/P03.md:38`（「用户源文件字节不变」） | CS-Z2 哈希的是 lab 内 `probe/scope/derived` 的**合成 fixture**，并非真实用户文件；真实用户数据保护实际由 CS-Z4（host 真实 `%APPDATA%` 只读快照）+ APPDATA pinned into lab + 外部 K07 只读构成。措辞可能让读者误以为 Gate 触及并保护了真实用户漫画库 | 读 CS-Z2 实现与 gate `observed {"files":4}`；CS-Z4/E2/R2 与 gate JSON `appdata_isolation` | 在 Task/AC4 或注释中标明「用户源文件=lab 模拟 fixture；真实用户数据隔离证据见 CS-Z4」 | open（P4，口径澄清；属既有 Gate 行为，非 P03 引入） |
| R4-07 | **P4** | `tests/packaging/test_packaged_fifth_sfx_entry.py:336` | `if "list" in desc or "string" in desc and "payload is string" in desc:` 的 `and` 子句冗余（`"list" in desc or ...` 已覆盖），属可读性/潜在误读，无行为影响 | 全文读取该文件；9 个失败负例在 log 19 全绿 | 简化为 `if "list" in desc or "payload is string" in desc:`（可选，纯清理） | open（P4，cosmetic） |

---

## 6. AC1–AC5 逐项

- **AC1（五入口安装与清理断言）= 成立（DSH 复核）。** `SIDECAR_EXES` 恰 5 项（`:66-72`）；安装断言 `:243` 经同一清单覆盖第五入口；`CS-Z3` 经**最小生产判定函数** `evaluate_sidecar_survivors` 对五入口断言零存活（gate `observed` 五项皆 0，`python.exe=9` 为 record-only 且已披露）；缺键与非零均 fail-closed；`--output-dir` 防历史 raw 覆盖行为保持（`:1026` + 回归文件 8 项在 log 19 全绿）；新测试直接调用生产判定函数（`:80-94`）。
- **AC2（正向与预期失败对照）= 成立（DSH 复核）。** 同一 `2de124f3…` installer 启动安装后的 `sfx_detect_probe.exe`；正向前置校验 K07 文件级 pin（gate `page_file_sha256=28dab503…`），exit 0／恰一 marker／frozen／error null／`n_candidates=1`（严格正整数）／权重 sha=pin／`resolved_from=bundle_probe`／路径在安装目录内／`device=dml,sfx_ep=dml,fallback=null`；负向启动前断言目标路径不存在（`path_precondition=absent`），exit 1／恰一 JSON／frozen／非空 `FileNotFoundError`；stdout/stderr/JSON/退出码均落隔离证据目录（`sfx-probe-real-page.log` 含 `exit=… --- stdout --- --- stderr ---`）；Gate `sfx_verification.requested=true/verdict=PASS`；复跑原文逐字节归档于 `integration/raw-finalhead-gate-output.zip` + manifest SHA 索引。**R-004 保留**：内置 ONNX 未独立重算（R-004/R4-05）。
- **AC3（固定 fresh 构建输入）= 成立（DSH 复核）。** Owner source `29024a21…`／installer `5a14c0a9…`(579,528,233 B，`revision-2/build-manifest.json:8` 与 `run-5a14c0a9/cleanstart-gate.json` 一致) 与 Codex source `a3aaf229…`／installer `2de124f3…`(579,537,342 B) 分列；frontend（`2da76b1d`/`19f5348f`）、Sidecar（`a7161ca3`，五入口+闭包断言）、Tauri/NSIS（`a3aaf229`）各阶段 HEAD/status/工具版本齐备；installer 指纹在 Gate 前固定于 manifest。历史 `d21e89b6…` 仅出现在 `run-29024a21/cleanstart-gate.json` 与 Task「已被取代」行，未被任何被接受的 AC2/AC4 证据引用。
- **AC4（完整受影响 Gate）= 成立（DSH 复核）。** 同一 installer 上 28/28 PASS、`GATE: PASS`、`EXIT=0`；40 项定向测试 head 绑定；raw/canonical 双向可逆 6/6 + 6/6、`VERIFY_EXIT=0`；安装目录零写、host `%APPDATA%` 4 文件零变更、lab 源 fixture 字节不变、五 sidecar 零存活。**唯一绑定缺口**：16 项 snapshot oracle 仍绑 `db2c1e93` → R4-04。
- **AC5（范围、数据与独立 Review）= 仍未闭合，边界表述准确。** Task `:39` 仍为 `[ ]`；`STATUS.md:3,7`、`Plan:3,7`、`README.md:5` 均保持 `in_review` 且明示「下一 Gate = 新 head 的 DSH 正式 Review 与 Codex 独立复核，再收口」。`git diff --check EXIT=0` 与零越界由 trace 21 支撑（DSH 命令 `NOT_RUN`）。本 Review 提供「非作者 DSH Review」这一半（0 未解决 P0/P1）；**Codex 仍须完成**：(a) R4-01/02/03/04 的最小处置或书面登记，(b) 集成范围与 installer/source 绑定复核，(c) 集成后受影响 Gate 复跑，(d) 回填真实 `integration_commit` 与 AC5。**不得凭本 Review 置 `done`。**

---

## 7. P0/P1、执行命令、环境限制与残余风险

**未解决严重度计数**：**P0 = 0；P1 = 0**；P2 = 0（R3-01 已闭、C-002/R-003/R-001/R-002 已闭；C-001 回退按 P3 登记，理由见 §5 R4-01：handoff 仍可经 Task 到达，无产品/门禁影响）；P3 = 4（R4-01/02/03/04）；P4 = 3（R4-05/06/07）。

**DSH 本轮实际执行**：仅只读 `read`/`glob`/`grep`。含：worktree `.git` 链路与 `refs/heads/{main,codex/*}`、两份 reflog、worktree `logs/HEAD` 的核对；上述全部文档、日志、manifest、ZIP 内文件名检索（ripgrep 二进制命中 `cleanstart-gate.json`）；实现/测试文件精读；手工计数（132/122/120/117/114 路径、28 场景、40 测试=32+8、16=6+2+8）。**未运行任何 git/pytest/Gate/构建/哈希命令。**

**残余风险**：
1. **无法自跑/自算**：所有哈希（含 ZIP 内 11 项、gate JSON、日志）与 Gate 结论均依赖 Codex 保存件的自洽性与可信度；我以「计数自洽 + 反向检索 + 三处 sha 交叉」补偿，但不等价于自跑。
2. **`run_clean_start_e2e.py` 在 `423ea5f1..d717c049` 间的内容恒等未获 artefact 证明**：仅证明路径集合增量恰为 10 条证据/文档（§1）；R4-03 入库 21/22 后可显著降低此风险。
3. **AC4 的 snapshot oracle 绑定**（R4-04）。
4. **R-004**：安装包内 ONNX 未独立重算（建议并入 P20）。
5. **R3-03**：`run_release_gate.py` 与 `main.rs:567-568` 第五 sidecar 遗漏仍在（P03 范围外）。
6. **R4-01**：C-001 的 RESUME 链接在 reviewed head 不存在。
7. snapshot oracle 日志含 8 行**期望负例** `[FAIL]`，仅末行 `PASS: 16` 判读（易误读；建议脚本加一行说明）——纯可读性。
8. 本 Review 不涉及 DSH Web 可见性声明；`dsh-review-r4.stdout.jsonl` 为该会话的实时捕获，非本次审查输入。

---

## 8. 结论与复审

在 `base=31abde9b…`、`reviewed_head=d717c049…` 固定范围内：**Architecture = PASS；Verification = PASS**，**无未解决 P0/P1**；R3-01/R3-02 的处置以 head 绑定证据真实成立（日志 19/20 + 原始 Gate ZIP + manifest SHA 索引 + 17/18 已入库），R3-03 如实登记为范围外 P20 风险且未越界修改，AC1–AC4 证据与 head 实现逐项吻合，AC5 边界表述准确（未越权宣称 `done`/集成通过）。

据此给出 **`decision = approved`**，作为交 Codex 完成集成/Gate 收口的输入。本批准**不延用**至任何后续 commit，也**不代替** Codex 的 integration Gate；§5 的 4 项 P3 应在 AC5 收口提交中处置或书面登记。

**复审触发条件**：任何新 commit（含 21/22 入库、C-001 处置、真实 `integration_commit` 回填）；或集成后 Gate/installer 与 head 证据不一致；或 `main` 指针再次变动。

**推荐下一步（供 Codex）**：在同一 worktree 提交 `build-logs/21–22` 与 `r4` 收口记录，回填 `integration_commit=d717c049`（或其后新 tip），按 R4-01/04 做最小文档/复跑处置，随后完成 AC5 集成核验、置 Task `done`，再按 §5.1 复核依赖并释放 **P01**（Plan `:7` 已写明「P03 完成后先重新核对并释放 P01」）；本 Review 无需 DSH 再做动作。
