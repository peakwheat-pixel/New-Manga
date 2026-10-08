# P03 正式非作者 Review（R3）

- `task_id` = **P03**
- `reviewer` = **DeepSeek Harness**（非作者；作者/`owner`=Antigravity，`integrator`=Codex）
- `author` = **Antigravity**
- `base_commit` = `31abde9bf4b73aea2851931dcd48faa0f750b318`
- `reviewed_head` = `423ea5f196e6276f007bd3f96e381fa893985eb9`
- `decision` = **approved**（Architecture：PASS；Verification：PASS with conditions；未解决 P0/P1 = **0/0**）
- 边界声明：本 Review **不是** Codex integration Gate；不代 Codex 置 Task `done`；不覆盖后续任何新 commit。

---

## 0. 环境限制与执行口径（必读）

本会话 shell 通道不可用：每次 `pwsh` 调用在沙箱初始化阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P03-review-prep-85482c5b)`），`workspace-write` 与 `danger-full-access` 升级均返回「无审批通道」。因此**所有 shell 命令一律记 `NOT_RUN`**，我不声称运行过任何 git / pytest / 构建 / Gate 命令。

替代手段（DSH 自行执行，只读文件读取，非 git 命令）：

| 核对项 | 手段 | 结果 |
|---|---|---|
| HEAD | 读 `G:\CODEX\New Manga.worktrees\P03-review-prep-85482c5b\.git`（gitdir 指到 `.git/worktrees/P03-review-prep-85482c5b`）→ 读 `worktrees\...\HEAD`（`ref: refs/heads/codex/P03-integration-4c04459`）→ 读 `.git\refs\heads\codex\P03-integration-4c04459` = `423ea5f196e6276f007bd3f96e381fa893985eb9` | HEAD **等于** reviewed_head |
| common-dir / worktree | `.git/worktrees/.../commondir` = `../..` → `G:/CODEX/New Manga/.git` | 与 Task/RESUME 记录一致 |
| 祖先链 | 读 `.git\logs\refs\heads\codex\P03-integration-4c04459`（15 条 reflog，线性） | `4c04459→1dc90475→db2c1e93→14ed25be→2da76b1d→19f5348f→a7161ca3→a3aaf229→39bd2793→08c7d4fa→2e8d6c07→2d114480→fb5782c5→41be59e9→423ea5f1` |
| 未提交文件 | 工作树 glob | `integration/dsh-review-r3.{prompt.md,stdout.jsonl,stderr.log}` 与 `build-logs/{17,18}` 为未跟踪文件，**不计入** reviewed diff |

`git rev-parse`、`git diff --name-only base..head`、`git diff --check base..head`、`git cat-file`、pytest、Gate 均为 **NOT_RUN**，只以 Codex 保存日志为证据（下述每条均标注来源）。

---

## 1. 范围与依据

依据文件：`AGENTS.md`、`doc/09_COLLABORATION.md` §6（含 §6.12 证据纪律）、`doc/templates/REVIEW.md`、`doc/tasks/P03.md`、`verification/P03-PACKAGED-SFX-ENTRY/{RESUME.md,integration/RESUME.md,integration/build-manifest.json}`、`doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md`、两份实现文件、全部 build/Gate 证据。

**exact head 范围（Codex trace，DSH 复核其内容，非自行运行）**：`integration/build-logs/17-final-review-head-scope-diff-check.log` 绑定 `423ea5f1…`，`PATH_COUNT=122`、`OUT_OF_SCOPE: none`、`DIFF_CHECK_EXIT=0`。我逐条读完 122 条路径：仅 `doc/**`（Task、4 份 P03 Handoff、6 个 Codex 维护的导航治理文件：`00_INDEX.md`、`12_ROADMAP.md`、`REBASELINE_PLAN.md`、`STATUS.md`、`tasks/README.md`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md`）、`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_packaged_fifth_sfx_entry.py`、`verification/P03-PACKAGED-SFX-ENTRY/**`。对 trace 17 做反向检索 `^(src|apps|contracts|requirements|...core_sidecar.spec|...build_sidecar.ps1|packaging/release-gate)` → **零命中**。故 `src/**`、`apps/**`、contracts、Schema、运行时依赖、build spec/script **零差量**成立（基于 Codex trace，非 DSH 命令）。

**范围一致性自洽校验（DSH 独立推导）**：trace 11（`2d114480`）=114 → trace 12（`fb5782c5`）=117（+09/10/11）→ trace 15（`41be59e9`）=120（+12/13/14）→ trace 17（`423ea5f1`）=122（+15/16）。`423ea5f1` 相对其父仅新增 `build-logs/15,16`（均在证据目录内）⇒ head 的代码/测试内容 = `41be59e9` 的内容。四个 trace 的计数与新增集合逐项吻合，无缺口。

**历史 checkpoint trace 绑定（R-002 复核）**：`build-logs/11` 明确写 `Fixed reviewed candidate: 2d114480…`（114 paths）；`build-logs/12` 写 `fb5782c5…`（117 paths）；`build-logs/15` 写 `41be59e9…`（120 paths）；三者均 `OUT_OF_SCOPE none` + `DIFF_CHECK_EXIT=0`。R-002 所指「11 是 candidate 2d114480 的完整 trace」**成立**，exact 复验在 12/15/17。

---

## 2. 视角状态

- **Architecture** = `executed`：分层/依赖方向、范围冻结、fail-closed 语义、调用链一致性、数据保护。
- **Verification** = `executed`（DSH 自跑为 `NOT_RUN`，采用只读复核 + 静态可判定性论证，见 §5）。
- **Spec** = `executed`（AC1–AC5 逐项对照）。Standards 视角按模板 2026-09-18 口径不强制，未单列。

---

## 3. Architecture 判定：**PASS**

1. **fail-closed 语义正确**：`evaluate_sidecar_survivors`（`run_clean_start_e2e.py:747-756`）先查缺键返回 `False`，再查非零泄漏；`main():1156` 以 `SIDECAR_EXES`（恰 5 项，`:66-72`）调用，产出 `CS-Z3` 五入口断言。安装断言 `:243` 同源使用 `SIDECAR_EXES`，清单单一来源，无第二份重复枚举。
2. **R-003 修复在 head 真实存在**：`weights_in_install_dir` 初值 `False`（`:791`），仅在 `weights_path_str and install_dir is not None` 时可能置真（`:792-798`），且**无条件**进入 `passed` 合取（`:820`）。省略 `install_dir` → `False` → FAIL。调用者 `run_sfx_probe_phase` 恒传 `install_dir=install_dir`（`:955`），即修正是对「未来调用者」的防护，不改变既有 Gate 行为。
3. **成功谓词与 AC2 文本逐一对应**：exit==0、marker 数恰 1、payload 为 dict、`frozen is True`、`error` 键存在且为 `null`、`type(n_candidates) is int and >0`（排除 `bool`）、权重 sha 等于 pin、`resolved_from=="bundle_probe"`、路径在安装目录内。失败谓词 `:867-873` 对应 exit==1/恰一 JSON/frozen/非空 dict error。
4. **依赖方向与数据保护无回归**：新增能力只落在验收工具与测试（`packaging/m2ac5/**`、`tests/packaging/**`），不进入 `src/**`、不经 WebView/IPC，不新增依赖；`--output-dir` 仍 `required=True`（`:1026`），历史 raw 覆盖防护保持；K07 与 ONNX 明确只读、不入库。
5. **调用者一致性**：全仓检索 `evaluate_sfx_probe_success|evaluate_sfx_probe_failure|evaluate_sidecar_survivors|SIDECAR_EXES`，生产者仅 `run_clean_start_e2e.py`，消费者仅新测试文件与既有 snapshot oracle（后者经 AST 抽取 `Gate`/`run_library_probe`，与 P03 改动兼容）。`tests/packaging/test_runner_output_dir_required.py` 未改（不在 122 路径内）却仍全绿，属独立回归面。
6. **唯一残留（范围外，登记不改）**：`packaging/release-gate/run_release_gate.py:95-100` 仍只列 4 个 sidecar（该类遗漏的同源第二处）。它不在 P03 允许路径内、也不在 122 路径内，P03 冻结范围**不允许**改它；见 finding R3-03。

---

## 4. Verification 判定：**PASS（含 1 项 P2 集成条件）**

证据核对（**全部为复核 Codex 保存日志**，非 DSH 运行）：

| 断言 | 证据 | DSH 复核结论 |
|---|---|---|
| 40 项定向测试 | `integration/build-logs/01`（`Source HEAD: db2c1e93`，shell/py 头 + `40 passed` + `EXIT=0`） | 成立 |
| C-002 后 40 项重跑 | `integration/build-logs/14`（`fb5782c5 plus uncommitted test-only C-002 fix`，`40 passed`/`EXIT=0`） | 部分成立，见 R3-01 |
| 测试计数自洽 | DSH 手数：新文件 32（1+1+1+1+1+16+1+9+1）+ 回归文件 8 = **40** | 与「40 passed, 0 skipped」吻合 |
| snapshot oracle | `integration/build-logs/02`（`16 actual-predicate cases`、`EXIT=0`） | 口径已解：`check_snapshots.py` 计数 =6（announcement）+2（probe）+8（ping）=**16**；日志可见 8 组 `[FAIL]` 为**期望负例**，末行 `PASS: 16 …` 为准 |
| 构建链 | `build-logs/03`（HEAD `2da76b1d`）、`04`（`19f5348f`）、`05`（`a7161ca3`，五入口 `sfx_detect_probe.exe present=true`、闭包断言、`EXIT=0`）、`06`（Build source HEAD `a3aaf229…`、clean、`EXIT=0`） | R-006 成立（各阶段均记 shell/HEAD/clean status）；`06` 绑定 `a3aaf229` |
| installer 指纹 | `integration/build-manifest.json`（`sha256=2de124f3…`、`size_bytes=579537342`）与 `run-2de124f3-py314/00-packaged-gate.log:9-10` 一致 | 成立；Manifest 在 Gate 前固定 |
| Gate 28/28 | `run-2de124f3-py314/cleanstart-gate.json`：`verdict=PASS`、`installer_sha256=2de124f3…`、28 条 `id` 全 `PASS`（DSH 逐条计数 = **28**）、`sfx_verification.requested=true/verdict=PASS` | 成立 |
| S1 结构化 | `sfx-probe-real-page.json` + gate `observed`：exit 0、marker 1、frozen、`error null`、`n_candidates=1`、sha 匹配 pin、`resolved_from=bundle_probe`、路径在 `…m2ac5-cleanstart-8ftayvd7\install\` 内、`device=dml/sfx_ep=dml/fallback=null` | 成立；且**逐项满足 head 版谓词**（关键：head 代码的正确性由证据反证成立） |
| S2 结构化 | `sfx-probe-missing-page.json` + gate `observed`：`exit=1`、marker 1、frozen、`FileNotFoundError` 非空、`path_precondition="absent"` | 成立 |
| 零触碰 | gate：`CS-Z1 changed_entries=[]`、`CS-Z4 files=4 changed_entries=[]`、`CS-Z2 files=4`、`CS-Z3` 五入口全 0（`python.exe=7` 注明 record-only） | 成立 |
| raw/canonical 双向可逆 | `raw-log-normalization.json`（6 文件、`all_assertions_passed=true`、archive sha `089dd82f…`）+ `07`/`08` 日志 + `build-logs/18`（两 verifier 各 6/6 PASS、`VERIFY_EXIT=0`） | 成立。`normalize_gate_logs.py:143-157` 与 `verify_normalization.py` 均**从归档 raw 重算 canonical 再比对**（非自证）；两份脚本只读无写调用 |
| 规范化脚本本身 | `normalize_gate_logs.py`（`inverse` 断言 105 行）、`verify_normalization.py`（`reconstructed_raw == raw_bytes` 148 行；`07-encoding-normalization.json` char_tokens `6702`/newline `137`） | R-005 成立（无 6704 残留；与 r3 Handoff 表一致） |
| R-001 | Task 输入表 `:61-63` 三指纹分列，`d21e89b6…` 标注「已被取代」 | 成立 |
| C-001 | `P03.md:114` 与 `verification/P03-PACKAGED-SFX-ENTRY/RESUME.md` 链接均解析到 `doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md` | 成立 |
| C-003 | `P03.md:62` 记同 installer 28/28；`RESUME.md` 命名当前状态 | 成立 |
| 治理文档无假 PASS/DONE | `STATUS.md:7` 明写「AC5仍待最终固定head的DSH正式Review及Codex集成Gate」；`P03.md:39` AC5 仍为 `[ ]`；Plan/Index/Roadmap 均记 `in_review` | 成立，无越级 `done` |

**C-002 独立确认**：新测试 `test_evaluate_sfx_probe_success_negative_cases`（`:249-284`）为每例提供**有效** `install_dir` 与目录内 weights path，先断言 baseline PASS（`:273-274`）再施加单一负条件；我逐条推演 16 个成功负例与 9 个失败负例，**全部具有判别力**（无被其它条件遮蔽），且日志 14 的参数化 ID 与顺序与 head 提交内容**逐条一致**（16+9），足以认定「日志 14 所测内容 = head 提交内容」。`test_evaluate_sfx_probe_success_valid:144-147` 保留独立缺省 `install_dir` fail-closed 断言。**C-002 关闭成立**。

---

## 5. Findings

命名沿用历史序列避免冲突，本 Review 新发现记为 `R3-xx`。

### 本次新发现

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R3-01 | P2 | `P03.md:50`、`integration/build-manifest.json:237-244`（称 fix_commit=`41be59e9` 且 40/40）vs `integration/build-logs/14-targeted-regression-tests.log:2`（`fb5782c5` + **uncommitted** test-only fix） | 40/40 与 28/28 均**未绑定 reviewed_head**：40/40 绑 `db2c1e93` 与 `fb5782c5+未提交`；packaged Gate 绑 `08c7d4fa`。文档措辞暗示 40/40 已在 `41be59e9` 上跑过，实际无该 artefact ⇒ 证据与 commit 的绑定存在自述成分 | 日志 14 头行自陈偏差；grep 全部 `integration/build-logs/*.log` 无 `41be59e9`/`423ea5f1` 的测试日志 | Codex 在 integration commit 上重跑 40 项定向测试与 packaged Gate，并把结果写入 manifest/Task；或提供「未提交态 ≡ `41be59e9`」的哈希/字节绑定 | **open（P2，属 AC5 集成边界，非代码缺陷）** |
| R3-02 | P3 | `P03.md:105-107`（test plan 止于 15/16）；`integration/build-manifest.json:218-260`（无 exact-review-head 段）；`build-logs/17,18` 未跟踪；`STATUS.md:7`、`tasks/README.md:5` 仍以 `2e8d6c07` 为 checkpoint head | exact reviewed head 的「122 paths / out-of-scope=0 / diff-check EXIT=0」与两份 normalization 结论目前只存在于**未提交**文件，且 Task/manifest/STATUS 未登记 `423ea5f1` ⇒ 复核材料尚未版本化、指针陈旧 | glob 显示 17/18 存在；trace 17 自身路径表**不含** `build-logs/17,18` ⇒ 该时点未提交 | Codex 集成收口时把 17/18 与 `423ea5f1` 的结论登记进 Task/manifest，并把 STATUS/README 指针推到最终 head | **open（P3）** |
| R3-03 | P3 | `packaging/release-gate/run_release_gate.py:95-100`（`SIDECAR_EXES` 仍 4 项）；同源 `apps/desktop/src-tauri/src/main.rs:568` 注释仍列四入口 | 第五入口遗漏在**另一个** Gate runner 中依然存在（该文件与 `run_release_gate.py` 的安装/存活断言因此仍不覆盖 `sfx_detect_probe.exe`）；同源历史登记 P4-1 亦未闭 | grep 命中 `:95-100` 仅四名；trace 17 无 `packaging/release-gate/**` ⇒ P03 未改（符合冻结范围） | **不在本 Task 修改**（越界）；由 Codex 另开范围或并入 release-gate/P20 前置项登记，保持 `src-tauri` 零 diff 纪律 | **open（P3，out-of-scope by design）** |

### 历史 findings disposition 独立复核

| ID | 级别 | 复核结论 | 依据 |
|---|---|---|---|
| R-001 | P2 | **fixed 确认** | Task `:61-63` 三指纹分列且 `d21e89b6…` 标「已被取代」；`2de124f3…` 在 manifest+gate log+gate json 三处一致 |
| R-002 | P2 | **fixed 确认** | 11=`2d114480`(114)、12=`fb5782c5`(117)、15=`41be59e9`(120)、17=`423ea5f1`(122)，均 out-of-scope 0、diff-check EXIT=0 |
| R-003 | P2 | **fixed 确认（代码面）** | `:791-798`+`:820` 无条件要求；`test:144-147` 负例；测试 40/40 含该例 |
| R-004 | P3 | **deferred 合理，风险保留** | `evaluate_sfx_probe_success` 只采信 payload 自述 `weights.sha256`，不对安装目录内 ONNX 独立重算；AC2 文本未要求，属额外保证。包 SHA 固定 + 路径在安装目录内已构成可接受链；建议在 P20/release gate 面补独立重算 |
| R-005 | P3 | **fixed 确认** | `07-encoding-normalization.json:207-208` = 6702 / 137，与 r3 Handoff 表一致，全仓无 6704 |
| R-006 | P3 | **fixed 确认** | `03/04/05/06` 均含 Shell/HEAD/clean status；`06:3` = `a3aaf229…` |
| C-001 | P2 | **fixed 确认** | 相对链接解析正确（§4） |
| C-002 | P2 | **fixed 确认** | §4「C-002 独立确认」；参数化 ID 与提交内容逐条一致 |
| C-003 | P3 | **fixed 确认** | Task `:62` 记 28/28；RESUME 命名当前状态 |

---

## 6. AC1–AC5 逐项

- **AC1（五入口安装与清理断言）= 成立（DSH 复核）。** `SIDECAR_EXES` 恰 5 项（`:66-72`）；安装断言 `:243` 覆盖第五入口；`CS-Z3` 经最小生产判定函数 `evaluate_sidecar_survivors` 对五入口断言零存活，gate `observed` 五项皆 0；缺键与非零均 fail-closed。`--output-dir` 防历史 raw 覆盖行为保持（`:1026` + 回归文件 8 项全绿）。
- **AC2（正向与预期失败对照）= 成立（DSH 复核）。** 同一 `2de124f3…` installer；正向前置校验 K07 文件级 pin `28dab503…`（gate `observed.page_file_sha256`），exit 0/恰一 marker/frozen/error null/`n_candidates=1`(严格正整数)/权重 sha=pin/`resolved_from=bundle_probe`/路径在安装目录内/`device=dml,sfx_ep=dml,fallback=null`；负向运行前断言目标路径不存在（`path_precondition=absent`，`:972-980`），exit 1/恰一 JSON/frozen/非空 `FileNotFoundError`；stdout/stderr/JSON/退出码入隔离目录；Gate `sfx_verification` 元数据 `requested=true, verdict=PASS`。**R-004 保留**：ONNX 未独立重算。
- **AC3（固定 fresh 构建输入）= 成立（DSH 复核）。** Owner 受审 source `29024a21…` / installer `5a14c0a9…`(579,528,233) 与 Codex source `a3aaf229…` / installer `2de124f3…`(579,537,342) 分列；frontend（`2da76b1d`/`19f5348f`）、Sidecar（`a7161ca3`，五入口 + 闭包断言）、Tauri/NSIS（`a3aaf229`）各阶段 HEAD/status/工具版本齐备；installer 指纹在 Gate 前固定于 manifest。
- **AC4（完整受影响 Gate）= 成立（DSH 复核）。** 同一 installer 上 28/28 PASS、`GATE: PASS`、EXIT=0；40 项定向、16 项 snapshot oracle、构建 trace、raw/canonical 双向可逆 6/6 + 6/6 齐备；安装目录零写、host `%APPDATA%` 4 文件零变更、用户源文件字节不变、五 sidecar 零存活。
- **AC5（范围、数据与独立 Review）= 未闭合，边界准确。** `git diff --check EXIT=0` 与零越界由 trace 17 支撑（DSH 命令 `NOT_RUN`）；Task `:39` 仍为 `[ ]`，`STATUS.md:7` 明示待 DSH 正式 Review + Codex 集成 Gate。本 Review 提供前一半；**Codex 仍须完成**：(a) R3-01 的 head 绑定重跑，(b) R3-02 的证据登记与指针推进，(c) 集成范围/installer-source 绑定复核，(d) 集成后受影响 Gate 复跑。**不得凭本 Review 置 `done`。**

---

## 7. P0/P1、执行命令、环境限制、残余风险

**未解决 P0/P1 = 0 / 0。** 未解决 P2 = 1（R3-01，属 Codex 集成必办义务，非代码缺陷）；未解决 P3 = 2（R3-02、R3-03）。

**DSH 实际执行**：仅只读文件/内容检查（`read`/`glob`/`grep`），含 Git 元数据文件核对（`.git`、`HEAD`、reflog、`packed-refs`）与全部证据日志逐条阅读、手数校验（122 路径、28 场景、40 测试、16 oracle 口径、6702/137）。

**NOT_RUN（原因：pwsh 沙箱初始化失败 + 无审批通道）**：`git rev-parse HEAD`、`git rev-parse --abbrev-ref HEAD`、`git rev-parse --git-common-dir`、`git worktree list`、`git cat-file -t <base>`、`git diff --name-only base..head`、`git diff --check base..head`、`git status --porcelain`、`pytest`（40 项）、`check_snapshots.py`（16 项）、`run_clean_start_e2e.py`（28/28 Gate）、`npm ci/npm run build`、`build_sidecar.ps1`、`npx @tauri-apps/cli@2 build`、`normalize_gate_logs.py --verify-only`、`verify_normalization.py`。

**残余风险**：① 无法自行复算 hash/运行 Gate，范围与零差量结论最终依赖 Codex trace 的可信度（我已用计数自洽与反向检索交叉校验，但非等价于自跑）。② `run_clean_start_e2e.py` 在 Gate 运行 HEAD `08c7d4fa` 之后「未再变化」无直接 artefact，仅有 commit message/manifest 自述 + S1/S2 证据与 head 谓词逐项吻合作为补偿。③ R-004 未独立重算 ONNX。④ R3-03 的 release-gate 同源遗漏。⑤ `main.rs:568` 过时注释（历史 P4-1，零 diff 纪律保留）。⑥ snapshot oracle 日志含 8 行期望 `[FAIL]`，仅靠末行判读，易被误读为失败（建议未来在脚本输出加一行「以上 FAIL 为期望负例」）。⑦ 本 Review 不涉及 DSH Web 可见性声明。

---

## 8. 结论与复审

`base=31abde9b…`、`reviewed_head=423ea5f1…` 范围内：Architecture 与 Verification 双面均通过，**无未解决 P0/P1**，AC1–AC4 证据真实且与 head 实现逐项一致，AC5 边界表述准确（未越权宣称 `done`/集成通过）。据此给出 **`decision=approved`**，作为交 Codex 集成的输入；批准不延用至任何后续 commit，R3-01 必须在集成 commit 上以重跑闭环。

复审触发条件：任何新 commit、R3-01/R3-02 的处置提交、或集成后 Gate 结果与 head 不一致时，须固定新 head 重新派发非作者 Review。