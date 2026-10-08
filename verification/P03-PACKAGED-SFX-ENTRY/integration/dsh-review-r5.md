已完成只读审查。以下是 P03 R5 正式审查报告。

---

# P03 DSH Formal Review R5 — 审查报告

## 0. 审查目标与结论摘要

| 项 | 值 |
|---|---|
| Task | `P03` — Packaged 第五 SFX 入口验收补齐 |
| base | `31abde9bf4b73aea2851931dcd48faa0f750b318` |
| reviewed head | `7677e9c324da2fde618e7cd6fdba2363abeb1f1b` |
| branch | `codex/P03-integration-4c04459` |
| 独立 HEAD 核验 | ✅ 通过（非 `git rev-parse`，见 §1） |
| Architecture | **PASS** |
| Verification | **PASS**（含 1×P3、4×P4 记录项，均非阻断） |
| 未解决严重度 | **P0=0 / P1=0 / P2=0 / P3=1 / P4=4** |
| **决定** | **`approved`**（针对 exact head `7677e9c3…`；不含 Task done / 集成闭合） |

R4 记录的 `R4-01..07` 与 Codex `C-004/C-005` 逐项独立复核**全部成立**（见 §3/§4）；AC1–AC4 与源码/测试/日志/manifest 逐项吻合；AC5 按设计仍开放，等 Codex 集成闭合。

---

## 1. 环境限制与实际执行口径（必读）

本会话 shell 通道**全程不可用**，与 R3/R4 同因：每次 `pwsh` 在沙箱 workspace 准备阶段即失败
`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P03-review-prep-85482c5b)`；
按规则对同一命令做一次升级重试，返回 `sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`（fail-closed）。

**我实际执行的只读手段**（非 git 命令、非转述 Codex 日志结论）：

| 核对项 | 手段 | 结果 |
|---|---|---|
| HEAD | 读 worktree `.git` → `gitdir: G:/CODEX/New Manga/.git/worktrees/P03-review-prep-85482c5b` → 读该 gitdir `HEAD` = `ref: refs/heads/codex/P03-integration-4c04459` → 读 `.git/refs/heads/codex/P03-integration-4c04459` | **`7677e9c324da2fde618e7cd6fdba2363abeb1f1b`** ✅ 与 reviewed head 逐字节相同 |
| 提交链 | 读 worktree `logs/HEAD`（20 条 reflog） | 末条 `051c0868 → 7677e9c3  commit: docs(p03): save exact head closeout checks`；其前 `d717c049 → 051c0868 commit: docs(p03): close r4 review findings and evidence` |
| **main ref（新增事实）** | 读 `.git/refs/heads/main` | **`main` = `d717c049a41544a6d592943a0b0fe1b76a41a050`** ⇒ 本候选 `7677e9c3` **未集成**，且 `d717c049` 确在主线（R4-02 的历史 fast-forward 属实） |
| 文件内容 | `read`/`glob`/`grep` 逐文件精读 | Task、两份 RESUME、manifest、logs 19–27、runner、两份测试、handoff 目标文件、Plan/Status/协作协议 |
| 手工计数 | 日志内 `[PASS]`/用例 ID 计数 | Gate 28 = 3+2+3+3+7+4+2+4；定向 40 = 32+8；两 verifier 各 6；两 zip 各 11 条清单 |

**`NOT_RUN`（原因：pwsh 沙箱 Win32 5 + 无审批通道，不声称运行过）**：
`git rev-parse/status/diff --name-only/diff --check/cat-file/show`、`pytest`（40 项）、`check_snapshots.py`（16 项）、`run_clean_start_e2e.py`（28 项 Gate）、`npm ci/build`、`build_sidecar.ps1`、`npx @tauri-apps/cli@2 build`、`normalize_gate_logs.py --verify-only`、`verify_normalization.py`、**任何 SHA-256 复算与 ZIP 解包/逐字节比对**。

**Web/Desktop 可见性**：本审查不产生该声明，也未核验（`manifest.dsh_r*.desktop_web_visibility="unverified"`，与之一致）。

---

## 2. Architecture 结论：**PASS**

1. **第五入口单一来源、无第二份枚举**：`packaging/m2ac5/run_clean_start_e2e.py:66-72` 的 `SIDECAR_EXES` 恰 5 项并含 `sfx_detect_probe.exe`；安装文件断言 `:243/:246` 与进程收尾 `:1156` 同源消费该常量。
2. **fail-closed 语义正确**：`evaluate_sidecar_survivors`（`:747-756`）先判**缺键**返回 `False`，再判非零泄漏；`main()`（`:1148-1161`）以 `SIDECAR_EXES` 调用并对五个 sidecar 断言零存活，`python.exe` 为 record-only（`:1151-1155` 注释与 AC4 口径一致）。
3. **R-003 修复在 head 真实存在并可判定**：`weights_in_install_dir` 初值 `False`（`:791`），仅当路径可解析且 `is_relative_to(install_dir)` 时为真（`:792-798`），且**无条件**进入 `passed` 合取（`:820`）；调用者恒传 `install_dir=install_dir`（`:955`）。省略即 FAIL（测试 `:144-147`）。
4. **AC2 谓词与文本一一对应**：成功 `:811-821`（exit0 ∧ marker恰1 ∧ payload 为 dict ∧ frozen ∧ `error` 键存在且为 null ∧ `type(n_candidates) is int` 且 >0（排除 bool）∧ 权重 sha==pin ∧ `resolved_from=="bundle_probe"` ∧ 路径在安装目录内）；失败 `:867-873`（exit1 ∧ marker恰1 ∧ payload ∧ frozen ∧ 非空 dict error）；缺页**启动前**断言路径不存在（`:963-980`）。
5. **K07 输入只读且带前置 pin**：`run_sfx_probe_phase` 启动前复算 K07 SHA（`:910-921`），不匹配即 FAIL，不启动探针；探针 env 显式剔除 `NEWMANGA_SFX_WEIGHTS`（`:896`）。AC2 文本"正向运行前校验 K07 页面字节级 SHA-256 pin"**成立**。
6. **用户数据隔离方向正确**：`HOST_USER_ROOT`（`:76-81`）仅被 `dir_tree_hashes` 只读快照（`:1116-1132`），无任何写入/删除路径；应用 APPDATA 被 pin 进 lab。逐行检查 runner 的文件访问面仅为：installer、`--output-dir` RAW、lab 临时目录、host APPDATA 只读、K07 只读 —— **无任何"用户漫画源目录"访问路径**。AC4 的 R4-06 澄清与实际代码一致。
7. **集成边界未被误称**：`main` = `d717c049`；Task/Plan/STATUS/manifest 均把 `integration_commit` 记为 `d717c049`，并把 R4 前的 fast-forward 记作历史事实；AC5 仍 `[ ]`、Task 仍 `in_review`。**没有任何提交件把 `7677e9c3` 说成已集成**。✅
8. **范围外同源第二处（登记不改，确认仍在范围外）**：`packaging/release-gate/run_release_gate.py` 与 `apps/desktop/src-tauri/src/main.rs` 注释的四 sidecar 表述，均不在 base..d717 的 132 路径与 base..051c0868 的 144 路径内（§6 反向检索零命中），R3-03 归 P20 的登记自洽。

---

## 3. Verification 结论：**PASS**

### 3.1 R4 / Codex findings 逐项独立复核

| ID | 级别 | 独立核实依据（我直接读取） | 结论 |
|---|---|---|---|
| R4-01 | P3 | `verification/P03-PACKAGED-SFX-ENTRY/RESUME.md:13` = `../../doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md`（自该目录上溯 2 级 = 仓库根 ✅）；`integration/RESUME.md:13` = `../../../doc/handoffs/…`（上溯 3 级 ✅）；`glob doc/handoffs/P03*` 命中该文件 ✅ | **fixed** ✅ |
| R4-02 | P3 | `doc/tasks/P03.md:16` `integration_commit: d717c049…`；`:60` 明写 R4 前 `423ea5f1→d717c049` 的历史 ff 且"不得用作绕过本候选复审"；`manifest:261-262`、`main_fast_forward_before_r4:525-530`、两份 RESUME 同步；**live `refs/heads/main` = d717c049** ✅ | **fixed** ✅ |
| R4-03 | P3 | logs 21/22 已版本化（在 051c0868 的 144 路径清单内）；`21:13` `PATH_COUNT=132`、`:147-149` `OUT_OF_SCOPE_COUNT=0/ none`、`:151-153` diff-check 输出空 `EXIT=0`；`22:33-34`+`:44-48` 两 verifier 各 6/6、`TRACEABILITY_EXIT=0`/`GATE_NORMALIZATION_EXIT=0`；`manifest:757-771` 段与之一致 | **fixed** ✅ |
| R4-04 | P3 | `build-logs/23:2` `source_head=d717c049…`、`:34` `PASS: 16 actual-predicate cases`、`:35` `EXIT=0`；且带 shell/venv/interpreter/command 头 | **fixed** ✅ |
| R4-05 | P4 | Task `:46` 区分 runner 只记录实测 SHA 与 Task/manifest 外部 pin；**源码证实**：`run_clean_start_e2e.py:1051-1055` CS-E2 只有 `installer.is_file()` + `sha256_file(installer)` 记录、**无期望值常量**；`:1174` gate JSON 同样只记录 | **fixed** ✅（措辞） |
| R4-06 | P4 | Task `:38` 写"lab 内4个模拟 source fixture 字节不变"+"Gate 未访问用户漫画源目录，因此不把 source-fixture 断言表述为用户漫画数据零修改证明"；`manifest:673-687` 并列 `host_appdata_files=4/changed=0`、`lab_source_fixture_files=4`、`manga_source_folder="NOT_ACCESSED_NOT_VERIFIED"`；log 25 `:62-63` 两条断言分列 `CS-Z4` 与 `CS-Z2` | **fixed** ✅ |
| R4-07 | P4 | `tests/packaging/test_packaged_fifth_sfx_entry.py:336` 的 `and "payload is string" in desc` 确为冗余；**我逐例推演全部 9 个失败负例**：该子句对每一例的真值均与 `"list" in desc` 一致（唯一可能被它影响的 `error is string not dict` 因 `"payload is string"` 不成立仍走 else 分支）⇒ 无行为后果、不影响 AC2 | **deferred 属实** ✅ |
| C-004 | P2 | `19:1-5`/`20:1-10` 为**旧格式**（仅 `python=Python 3.14.6`、无 shell/venv 字段）；`24:1-9`/`25:1-15` 含 `shell=PowerShell 7.6.6`、`shell_executable`、`virtualenv=none`、`VIRTUAL_ENV=<unset>`、interpreter 路径+版本、完整 command、末尾 `EXIT=0`（`:24:61`、`:25:69`）；标准依据 `doc/09_COLLABORATION.md:177` Q-009① 确认存在 | **fixed** ✅（19/20 未删，24/25 合规） |
| C-005 | P3 | 两份 RESUME 的"下一条直接指令"均改为 live Git/`git rev-parse HEAD`/`…31abde9b..HEAD`，**无 stale `423ea5f1` 指令**（`423ea5f1` 仅作为 R4-02 的历史说明出现） | **fixed** ✅ |

### 3.2 证据链内部自洽性（独立推导，非转述）

- **132 / 144 / 146 的关系自洽**：log 21（base..`d717c049`）=132；log 26（base..`051c0868`）=144；而 `build-logs/26,27` **不在** 144 清单内（我逐行核对了 144 条清单，`…/build-logs/` 只到 `25`）⇒ 二者系 `051c0868` 之后新增，`146 = 144 + {26, 27}` 与 R5 prompt 的"146 paths"自洽。
- **旧日志 19/20 与 132 清单的关系**：132 清单**不含** `build-logs/15..25`（`grep` 确认清单止于 `14`）⇒ 19/20 在 `d717c049` 时尚未入库，与 C-004"保留原件+另加合规复跑"的处置形态一致。
- **Gate/测试计数**：log 25 我手工计数 `[PASS]` = 28，与 `manifest:599-611` `scenario_count=28` 一致，且 phase 5 顺序 `Z1→Z4→Z2→Z3` 与源码 `:1114/:1123/:1146/:1157` 完全一致；log 24 = 32（新文件：5+16+1+9+1）+ 8（回归文件）= **40**。
- **ZIP 清单一致性**：`manifest:692-755`（d717 归档）11 条逐条列出 size+SHA，`cleanstart-gate.json` 的 `gate_json_sha256=0b07a89e…` 与归档内该条目 SHA 相同 `0b07a89e…` ✅；我另核对了 `423ea5f1` 段（`:392-511`）的 `evidence_files` 与 `raw_output_archive.files` **逐条同值**（此前疑似 `51099dd2` vs `52270d83` 的差异实为分属 423ea 与 d717 两次 Gate，非内部矛盾）。
- **R4 报告事实**：`dsh-review-r4.md:139` 计数 P0=0/P1=0/P2=0/P3=4/P4=3，与 R4-01..07 一一对应；`:25` 的 main fast-forward 与 `refs/heads/main` 实测一致。
- **"runner/test 代码自 d717c049 未变"的旁证**：R4 报告引用的行号在**当前 head 上逐条仍成立** —— runner `:66-72`、`:747-756`、`:791-798`、`:820`、`:955`、`:1023-1033`（`:1026` required）、`:1051-1055`、`:1135-1161`；测试 `:144-147`、`:249-284`、`:336`。行号未漂移，强力支持内容恒等；但仍以 reflog 提交主题（`051c0868`/`7677e9c3` 均为 `docs(p03)`）为辅助，**`git diff` 本体 = NOT_RUN**。

### 3.3 声明是否超出证据

- 绝大多数声明与提交件吻合。**两处未由提交件闭合**，已登记为 R5-01 / R5-03：
  - "Current base..head path count was 146, out-of-scope=0；`d717c049..head` touches 24 paths" 仅存在于**未跟踪**的 `dsh-review-r5.prompt.md:34`；
  - "Codex verified every archived entry byte-for-byte against the retained folder" 在 d717 归档段只有 `all_entry_hashes_verified`，**无** `byte_for_byte_verified` 标志（对照 423ea 段 `:510` 有该标志为 `true`），且对照的保留目录是未跟踪/受保护目录，仓库内不可复现。

---

## 4. AC1–AC5 逐项

| AC | 判定 | 依据 |
|---|---|---|
| AC1 五入口安装与清理断言 | **成立** | `SIDECAR_EXES:66-72` 恰 5 项；`:243/:246` 安装断言同源；`:1156` 调 `evaluate_sidecar_survivors`；测试 `:56-97` 直接调用生产函数（缺键→False、泄漏→False）；`--output-dir` 回归 8 项在 log 24 全绿 |
| AC2 正向+预期失败对照 | **成立** | 源码谓词 `:811-821`/`:867-873`、K07 前置 pin `:910-921`、缺页前置 `:963-980`；log 25 `CS-S1`（exit0/marker1/frozen/error null/`n_candidates=1`/sha=pin/`bundle_probe`/目录内/dml+dml+null）、`CS-S2`（exit1/FileNotFoundError/`path_precondition=absent`）；stdout/stderr/JSON/退出码写入隔离目录（`:945-949`/`:1007-1011`）；Gate `sfx_verification` 元数据 `:1182-1187` |
| AC3 固定 fresh 构建输入 | **成立**（哈希复算 NOT_RUN） | Owner：`revision-2/build-manifest.json:4,7,8` = `29024a21` / `5a14c0a9…` / 579,528,233 B；`run-5a14c0a9/cleanstart-gate.json:4` 同 SHA。Codex：`manifest:35-51` = `a3aaf229` / `2de124f3…` / 579,537,342 B；frontend/sidecar/NSIS 各阶段 HEAD 与工具版本齐备，指纹在 Gate 前固定 |
| AC4 完整受影响 Gate | **成立** | 同一 installer 上：40/40、0 skipped（log 24，含 shell/venv/EXPIT 头）、oracle 16（log 23）、Gate 28/28 `GATE: PASS` `EXIT=0`（log 25）；零触碰 `CS-Z1/Z4/Z2/Z3` 与 manifest `:673-687` 一致；原始 11 项归档于 `raw-finalhead-d717-gate-output.zip`（committed） |
| AC5 范围、数据与独立 Review | **未闭合（按设计）** | Task `:39` 仍 `[ ]`，Task `in_review`；实现差量在允许路径内、`git diff --check EXIT=0` 由 logs 21/26 支撑（**exact head 未版本化 → R5-01**）；非作者 DSH Review 的 R4 半程对 `d717c049` approved、本 R5 对 `7677e9c3` approved；Codex 集成范围/绑定/集成后 Gate 复跑与 `done` 置位**仍未完成** |

---

## 5. 允许路径与用户数据保护

- **允许路径内**（按 log 26 的 144 条清单逐条比对 Task §允许修改范围）：`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_packaged_fifth_sfx_entry.py`、`verification/P03-PACKAGED-SFX-ENTRY/**`、`doc/tasks/P03.md`、`doc/handoffs/P03-PACKAGED-SFX-ENTRY-*.md`（4 份），加 Codex 维护的 6 个导航文件（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/README.md`、`doc/12_ROADMAP.md`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md`，Task `:91` 明示由 Codex 维护）⇒ **out-of-scope = 0 独立成立**。
- **禁改前缀反向检索**：对 log 21 与 log 26 执行 `^(src/|apps/|contracts/|requirements|package\.json|Cargo|\.github)` → **零命中**；`src/**`、`apps/**`、contracts、Schema、依赖、build spec/script 零差量成立（基于已入库清单；`git diff` 本体 NOT_RUN）。
- **外部输入未入库**：两份清单中 `.onnx|.png|.exe|.sqlite|db` 零命中，只有 2 个证据 `.zip`；K07/ONNX 仅作只读输入被引用（Task `:76-77` 与 manifest `inputs`）。
- **用户数据**：host `%APPDATA%` 仅只读哈希（源码 `:1116-1132`），`CS-Z4 files=4 changed=[]`；未访问真实漫画源目录（源码无该路径访问面 + `manga_source_folder=NOT_ACCESSED_NOT_VERIFIED`）。
- **受保护材料**：我未读取用户漫画文件、数据库/Lock/Revision、K07/ONNX 内容、root checkout 的 24 项 dirty、两个保留 raw Gate 目录内容（`run-2de124f3-finalhead-423ea-py314/`、`…-d717-py314/`）以及其他 Agent 未提交文件；**未修改任何文件**。

---

## 6. Findings

### R5-01 — exact reviewed head 的范围/空白证据未版本化
- **级别**：P3（非阻断） | **状态**：open
- **位置**：`verification/P03-PACKAGED-SFX-ENTRY/integration/build-logs/26-r4-closeout-fixed-head-scope-diff-check.log:2`（`source_head=051c0868…`）对比 reviewed head `7677e9c3…`；`integration/build-manifest.json:757-771`（登记 d717=132）、`:772-793`（登记 051c0868=144）；claim 仅见于未跟踪的 `integration/dsh-review-r5.prompt.md:34`
- **触发**：审阅 `7677e9c3` 自身的差量范围/空白时
- **影响**：AC5 要求"固定 delivery/review head；实现差量严格在允许路径内，`git diff --check` EXIT=0"，但该结论的最新版本化 artefact 绑定的是**上一个** commit（144 paths）；exact head 的 146/24/runner-code-empty 三个数字**仓库内不可追溯**，复核者只能依赖推理（同为 R4-03 的同类形态），违反 `doc/09_COLLABORATION.md:177` Q-009② "判别力证据必须入库"
- **可复现依据（我自跑）**：`grep '7677e9c3'` 于 `doc/` → **0 命中**；于 `verification/P03-PACKAGED-SFX-ENTRY` → 仅 `dsh-review-r5.prompt.md`（未跟踪）与 `dsh-review-r5.stdout.jsonl`（本会话实时捕获）；`build-logs/26` 的 144 条清单**不含** 26/27 ⇒ 增量恰为 2 条（`146=144+2`）
- **最小处置**：Codex 在 AC5 收口提交中，对最终 head 版本化 `git diff --name-only 31abde9b..HEAD` 与 `git diff --check` 日志（或显式写明"head→已核对 commit 的增量仅为 logs 26/27，二者均在 `verification/P03-PACKAGED-SFX-ENTRY/**` 内"），并把 24 路径/代码零差量落到 manifest 段
- **缓解事实**：reflog 显示 `051c0868`、`7677e9c3` 提交主题均为 `docs(p03)`；两份新增日志位于允许路径内；R4 报告引用的 runner/测试行号在 head 上逐条未漂移

### R5-02 — 状态标签落后一个 commit
- **级别**：P4 | **状态**：open（收口时刷新）
- **位置**：`verification/P03-PACKAGED-SFX-ENTRY/RESUME.md:3`、`integration/RESUME.md:3`（`ExecutionState=R4_DISPOSITIONS_RECORDED_R5_CANDIDATE_PENDING`）；`integration/build-manifest.json:3`（`phase=r3_conditions_closed_r4_review_pending`）、`:261`（`candidate_head=d717c049`）
- **触发**：恢复者只读提交件时
- **影响**：可能误以为"R5 候选尚未固定"，而 reviewed head `7677e9c3` 已是 R5 候选；无产品/门禁影响
- **依据**：以上三处逐字读取 vs live HEAD
- **最小处置**：收口提交同步 `ExecutionState`/`phase`/`candidate_head`

### R5-03 — d717 归档的"逐字节验证"声明超出 manifest 记载且仓库内不可复现
- **级别**：P4 | **状态**：open
- **位置**：`integration/dsh-review-r5.prompt.md:33`（"Codex verified every archived entry byte-for-byte against the retained folder"）vs `integration/build-manifest.json:692-755`（d717 段仅 `all_entry_hashes_verified: true`，**无** `byte_for_byte_verified`；对照 `:510` 的 423ea 段有该标志）
- **触发**：复核归档与原目录一致性时
- **影响**：读者可能高估可复现强度；对照的保留目录未跟踪，外部复核者无法重现该比对（我亦无法解压/复算 → NOT_RUN）
- **最小处置**：在 manifest 补 `byte_for_byte_verified` 标志（附对账方式），或把表述限定为"SHA 清单 + 逐条哈希已核对"
- **缓解**：11 条 size+SHA 清单齐备，`cleanstart-gate.json` 的 `gate_json_sha256` 与归档条目同值，内部自洽

### R5-04 — `CS-Z2` 场景 ID 名仍为 `user-source-files-byte-identical`
- **级别**：P4 | **状态**：accepted/deferred（cosmetic；既有 Gate 行为，非 P03 引入）
- **位置**：`packaging/m2ac5/run_clean_start_e2e.py:1146`（哈希对象为 lab `probe/scope/derived` 的合成 fixture）
- **触发**：仅读 Gate 日志者
- **影响**：名称可被误读为"真实用户源文件"；产品/门禁无影响
- **最小处置**：保留 ID（冻结标识，改名属行为变更），依赖 Task `:38`/manifest `:677-678` 的澄清；可选在场景 `observed`/注释加"lab fixture"字样

### R5-05 — log 23 含 8 行期望负例 `[FAIL]`，仅末行判定 PASS
- **级别**：P4 | **状态**：noted（R4 §7.7 已披露）
- **位置**：`integration/build-logs/23-finalhead-snapshot-oracle.log:13-33`（`:34` `PASS: 16 actual-predicate cases`）
- **影响**：易被误读为 oracle 失败；无判定影响
- **最小处置**：可选在脚本输出加一行说明；不阻断

**R4-07 复核结论**：其"冗余条件、无行为后果"的定性**准确**（见 §3.1），维持非阻断 cosmetic 延期。**未发现新的 P0/P1/P2。**

---

## 7. 决定

**`approved`** —— 针对 `base=31abde9bf4b73aea2851931dcd48faa0f750b318`、`reviewed_head=7677e9c324da2fde618e7cd6fdba2363abeb1f1b`：

- R4-01..07 与 C-004/C-005 的处置**逐项核验成立**；AC1–AC4 由源码+测试+已入库日志/manifest 支撑（哈希复算类为 `NOT_RUN`）；AC5 边界表述准确（未越权宣称集成/完成）。
- 未解决 **P0=0 / P1=0 / P2=0**；P3=1（R5-01，证据版本化）、P4=4（R5-02..05，均非阻断）。
- 本批准**不延用**至任何后续 commit；**不代替** Codex 的 integration Gate，也**不把 P03 置为 done**。
- 复审触发：任何新 commit（尤其 AC5 收口提交）、最终 head 的范围/空白复核结果与本次推理不符、或集成后 Gate/installer 与 head 证据不一致。

---

## 8. 推荐下一步

P03 尚未闭合，尚无"已完成 Task 后应释放的下一 Task"；当前唯一应执行的动作是 **Codex 的 AC5 集成收口**（无需 DSH 再动作）。可直接转发给 Codex 的指令：

> **P03 AC5 收口（Codex，branch `codex/P03-integration-4c04459`，worktree `G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`）**
> 1. 把 DSH R5 对 `7677e9c324da2fde618e7cd6fdba2363abeb1f1b` 的 `approved`（含 R5-01..05）与 reviewed head 记入 `doc/tasks/P03.md` 与 `integration/build-manifest.json`；R5 报告/prompt/JSONL/exit 归档为 `integration/dsh-review-r5.md` 等。
> 2. 对最终待集成 head 版本化 `git diff --name-only 31abde9b..HEAD`、`git diff --check` 与两份只读 normalization verifier 日志（日志 28/29 或等价段），并把"24 路径 / runner+test 代码零差量"写入 manifest（关闭 R5-01）。
> 3. 刷新 `ExecutionState`/`phase`/`candidate_head`、d717 归档的 byte-for-byte 标志（R5-02/R5-03）。
> 4. 独立复核集成范围与 installer/source 绑定，复跑受影响 Gate；全过后置 AC5 `[x]`、Task `done`。
> 5. 然后按 [REBASELINE_PLAN](doc/REBASELINE_PLAN.md) 重核依赖并释放 **P01**（Owner=Codex、Reviewer=DSH、Integrator=Codex），同步 STATUS/Plan/ROADMAP/RESUME/README。
> 6. 不 push/外发/部署；保留 root 24 项 dirty、P08/旧 DSH raw、Qoder 文件、Owner worktree、K07/ONNX 与用户数据原样。

（若冻结的 AC 与流程不要求第 2 步的额外日志，Codex 也可按 R4-03 先例在 Task/manifest 书面登记"exact head 增量仅为两份允许路径内日志"并说明依据，作为 R5-01 的等价最小处置。）