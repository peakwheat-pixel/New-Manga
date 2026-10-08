---
task_id: M2-RUNNER-SNAPSHOT-DEBT
reviewer: DeepSeek Harness（非作者）
author: Codex
integrator: Codex
review_base: 2b780120d1eb94f93afadf073790f65899a618e6
reviewed_head: 5c2d047804eb4a802c04e53b5e8e5e5459570b24
code_delivery_head: 3d532c1f99e49da703d2076bd67d46b710866637
evidence_commit: ce5ff3fc21bcba082b995ea716a983d2fd4c6a89
decision: approved
---

# Review：M2-RUNNER-SNAPSHOT-DEBT（runner 快照债务）

## 范围与依据

**固定口径（已实测确认，非引用摘要）**

| 项 | 值 | 确认方式 |
|---|---|---|
| review_base | `2b780120d1eb94f93afadf073790f65899a618e6` | `G:/CODEX/New Manga/.git/refs/heads/main` 内容逐字节相等；reflog 该提交为 `docs: resume runner debt after ICU gate recovery` |
| reviewed_head | `5c2d047804eb4a802c04e53b5e8e5e5459570b24` | `refs/heads/codex/M2-RUNNER-SNAPSHOT-DEBT`；worktree `HEAD` → `refs/heads/codex/M2-RUNNER-SNAPSHOT-DEBT` |
| code_delivery_head | `3d532c1f99e49da703d2076bd67d46b710866637` | 分支 reflog：`bc337fcb → 3d532c1f`（`merge main`）；随后 `ce5ff3fc`（`docs: package runner debt AC4 review evidence`）→ `5c2d0478`（`docs: bind runner review evidence commit`） |
| evidence_commit | `ce5ff3fc...` | 同上 reflog |
| branch / worktree / common-dir | `codex/M2-RUNNER-SNAPSHOT-DEBT` / `G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex` / `G:/CODEX/New Manga/.git` | `.git` 文件指向 `worktrees/RUNNER-SNAPSHOT-DEBT-codex` |

**审查范围的建立方式（重要口径声明）**：本会话 `pwsh` 工具在沙箱准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\RUNNER-SNAPSHOT-DEBT-codex)`），`danger-full-access` 无审批通道；委派子代理复现同一失败。**因此本轮无任何 git 命令执行，我不声称现场重跑任何 Gate。** 差量改用等价只读手段重建：

1. main 检出**恰好位于 review_base**（`refs/heads/main` = `2b780120`），故 `G:/CODEX/New Manga` 下同路径文件即 **base 侧内容**；
2. worktree 检出**恰好位于 reviewed_head**（分支 ref = `5c2d0478`），其文件即 **head 侧内容**；
3. 对两处 runner 文件逐 hunk 比对（两副本分别完整读取）；
4. 分支 reflog 给出完整提交链与每个提交的 subject（`d1c279db fix: align runner protocol and production snapshots`、`cfb5d2ee test: ...`、其余均为 `docs:`）；
5. 已入库证据逐份读取。

**两处 runner 实际差量（逐 hunk 核对，非摘要）**

`verification/M2-RC2/run_e2e.py`（base 636 行 → head 651 行，净 +15）：
- 模块 docstring 用法行加 `[--output-dir PATH]`（:27）；产物段改为 `--output-dir` + fresh lab（:29-30）；
- `import tempfile`（:44）；
- `PRODUCTION_EXPECTED` 9 → 15 条（:313-329），并新增 2 行注释（:311-312）；`PROBE_EXPECTED` **逐条未变**（7 条，:333-341）；
- `run_interactive_phase` docstring `3 production commands` → `15`（:375）；
- `main()`：`global RAW, LAB`（:498）、新增 `--output-dir`（default=RAW，:503）、`RAW = args.output_dir.resolve()`（:505）、`LAB = Path(tempfile.mkdtemp(prefix="m2rc2-lab-"))`（:506）。

`packaging/m2ac5/run_clean_start_e2e.py`（base 885 行 → head 884 行，净 −1）：
- docstring 用法行加 `[--output-dir <path>]`（:33）、产物段改述（:35）；
- `envelope()` 注释 6 行 → 2 行（:443-444），**请求体 `{"major":1,"minor":3}` 原样保留**（:448）；
- CS-L1 响应断言 `{"major":1,"minor":6}`（:500，base 为 `1.3`）；
- `main()`：`global RAW`（:735）、`--output-dir`（default=RAW，:738）、`RAW = args.output_dir.resolve()`（:740）。`lab = tempfile.mkdtemp("m2ac5-cleanstart-")` 在 base 已存在，非本轮引入。

**未审到 / 无法覆盖**：`git` 原生命令输出（含 `diff --stat`、`--name-only`、`--check`）；真实 Windows Gate 现场重跑；`apps/**` 中 `node_modules`、`target/` 等 ignored 产物；worktree 当前未提交状态（见下）。

**观察（非 finding）**：`verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/dsh-r4-events.jsonl` 与 `dsh-r4-stderr.log` 是**本次派发 harness 实时写入**的会话证据（内容含本会话事件），非本 Reviewer 产出；本 Reviewer 未写入、未修改、未新增任何文件。

### 视角状态声明（可选视角）

- **Standards（本仓库记录标准）：executed（轻量）** — 对照 `AGENTS.md`（角色/交付、产品边界、保护用户数据）、`doc/09_COLLABORATION.md`（非作者 Review、固定 head、证据入库）、Task `allowed_paths` / 禁止范围。未发现硬性项违规。
- **Spec（来源 AC）：executed** — 对照 `doc/tasks/M2-RUNNER-SNAPSHOT-DEBT.md` AC1–AC6 与"来源、实际证据与冻结目标""禁止与停止条件"。
- Fowler smell baseline 仅作判断项，见 Findings R-005（已标注为判断项）。

## Architecture

**判断：通过（PASS）**，无分层/契约/依赖/安全/持久化风险。

1. **分层正确**：变更只落在验收工具层（`packaging/m2ac5/**` 打包验收 runner 与 `verification/M2-RC2/**` Dev 验收 runner）。生产层 `src/**`、`apps/**`、`tests/**`、Schema、依赖**无差量**（证据见 Verification V-01/V-02/V-08）。
2. **契约方向正确（关键）**：Task 要求"不修改产品以迎合过时 runner，不从被测回包动态生成期望"。实现符合：
   - `main.rs:53-77` 的 `PRODUCTION_COMMANDS` 有序 15 条与 head `PRODUCTION_EXPECTED` 逐条、逐序相等（我直接读源核对，非依赖 runner 自述）；
   - `src/bootstrap/core_service.py:143,168` `PROTOCOL_MAJOR=1 / PROTOCOL_MINOR=6`，runner 断言为**精确 dict 相等**，非长度/包含/任意 minor；
   - 期望值来源为**手工冻结字面量**（`check_snapshots.py:36-42` 注释明确"不得从任一 runner 或运行时回包推导"），方向为由产品源码 → 冻结 oracle，未出现反向自证。
3. **快照债务的护栏被真正加上**：`check_snapshots.py` 用 AST 从**两个 runner 源文件**抽取实际谓词（`ALLOWLIST_RE`/`PRODUCTION_EXPECTED`/`PROBE_EXPECTED`/`check_announcement`/`Gate`/`run_library_probe`）并对 `main.rs`、`core_service.py` 做源码对齐断言（:43、:52）。这是一个可运行的**判别性**护栏，而不是把实现复制成无判别测试。
4. **隔离设计正确**：`--output-dir` 决定 `RAW`，`main()` 内 `resolve()` 后所有写盘一律经 `RAW / ...`；lab 每次 `mkdtemp`；packaged runner 把 `APPDATA`/`TEMP`/WebView2 UDD/安装目录全部钉进该次 lab（`probe_env`/`ac1_env`/`production_env`、`install_dir = lab/"install"`）；host 真实 `%APPDATA%` 仅**只读哈希前后比对**（`dir_tree_hashes`，CS-Z4）。对用户数据/历史证据无写风险。
5. **未引入新框架/依赖/registry**，符合 Task"先复用已有常量/断言模式"的约束。
6. **残余架构债务（不阻断，已披露）**：命令面仍有多份手工维护视图（`main.rs PRODUCTION_COMMANDS`、`run_e2e.py PRODUCTION_EXPECTED`、`check_snapshots.py frozen`）；本轮以 oracle 把漂移变成可判别失败，但未消除漂移类别——Task 已明确禁止建通用 registry，属可接受取舍。

## Verification

**判断：通过（PASS）**。所有"现场重跑"类场景在本会话为 `NOT_RUN`（无 shell，见上），结论**完全基于已入库、带 EXIT 与环境头的真实日志**；我未声称任何现场重跑。

| ID | 场景 | 实际执行内容 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|---|
| V-01 | ref/范围解析 | 只读 `.git/refs/heads/main`、`refs/heads/codex/M2-RUNNER-SNAPSHOT-DEBT`、`worktrees/.../HEAD`、两份 reflog | base/head 固定 | PASS | 文件内容逐字节；reflog 链路完整 |
| V-02 | 两处 runner 差量 | base（main 检出）与 head（worktree）两份文件**逐 hunk**比对 | `2b780120` vs `5c2d0478` | PASS（统计口径见 R-004） | 文件行号对照，净 +15 / −1 |
| V-03 | 15 条生产命令精确有序且独立于回包 | 读 `main.rs:53-77` 与 head `run_e2e.py:313-329` 逐条比对 | head | PASS | 15/15 逐条逐序相等 |
| V-04 | probe 7 条未扩张 | base/head `PROBE_EXPECTED` 逐条比对 | head | PASS | 7 条文本完全相同 |
| V-05 | minor-3 请求保留 + 严格断言 minor=6 | 读 `run_clean_start_e2e.py:443-448,500`；读 `check_snapshots.py:84`（断言所有请求 version=1.3）、`:100`（PASS 当且仅当响应=1.6） | head | PASS | 代码 + oracle 断言双证 |
| V-06 | 判别 oracle 有判别力 | 读 `check_snapshots.py:57-101`（序反/少 6 条/多 1 条/混入 probe_exit/空集；响应 1.3、1.7、null、capabilities 空、status=starting、error） | head | PASS | `raw/resume/check-snapshots.log`（16 用例、含逐条 PASS/FAIL、`EXIT=0; ELAPSED=0.2s`） |
| V-07 | AC4 证据绑定 source head | 读 5 份日志头 + `build-fingerprint.json` | `3d532c1f` | PASS | 全部日志 `HEAD=3d532c1f99e49da703d2076bd67d46b710866637` |
| V-08 | 禁止范围零差量（文件级替代证明） | main 工作区=review_base；`requirements.txt` 逐行、`build_sidecar.ps1` 265 行、`core_sidecar.spec` 500、`requirements-build.txt` 59、`README.md` 152、5 个 `entries/*.py` 全文一致；`src/bootstrap/*.py`、`tests/m2_acceptance/*.py`、`src-tauri/src/*.rs` 文件名集合一致；`main.rs`/`core_service.py` 行锚一致；`verification/M2-RC2/raw/` 文件集合一致 | base vs head | PASS（带 R-002 保留） | 直接文件/行号核对；reflog 分支仅 `d1c279db` 为代码提交；`closeout-validation.log:48` 的 `git diff --name-only b3860981 HEAD -- src apps tests` 输出为空 |
| V-09 | installer SHA 三点一致 + 与 NSIS 日志尺寸互证 | 读 `build-fingerprint.json`、`packaged/cleanstart-gate.json`、`STATUS/Handoff`、`nsis-build-r1.log` | `3d532c1f` | PASS | 三处均 `ef617573…fa75`；579,545,058 B ÷ 1048576 = 552.70 MiB = 构建日志 "(552.70 MiB)" |
| V-10 | 五入口 Sidecar + ICU 遮蔽守卫 | 读 `raw/resume/sidecar-build.log` | `3d532c1f` | PASS | 5 个 entry 全分析；`verified 0 shadowing ICU binaries`；`EXIT=0; ELAPSED=348.5s` |
| V-11 | Packaged 26/26 + EXIT=0 | 读 `packaged-runner.log` + `cleanstart-gate.json` 逐条计数 | `3d532c1f` | PASS | 26 个 scenario 全 PASS（含 CS-L1 minor 6）；`GATE: PASS`；`EXIT=0; ELAPSED=70.3s` |
| V-12 | Dev Gate 10 phase + probe 13/13 + 15/7 allowlist | 读 `dev-runner.log`、`dev/e2e-gate.json` | `3d532c1f` | PASS | 10 gate 全 PASS、`failed: []`、probe 13/13、production allowlist 恰 15 条、probe 恰 7 条；`EXIT=0; ELAPSED=36.2s` |
| V-13 | 输出隔离 / 历史证据未被覆盖 | worktree 与 base 对比 `verification/M2-RC2/raw/` 文件集合；新日志全部位于 `raw/resume/**` | base vs head | PASS | 新旧 `raw/`、`raw/resume/` 并存；`raw/resume/packaged/`、`raw/resume/dev/` 独立 |
| V-14 | 历史 FAIL 原样保留 | 读 `result-summary.json`、`checkpoint.md`、Task 历史段 | `cfb5d2ee` 时期 | PASS | `packaged_pass:20 / packaged_fail:1 / task_status:"blocked"`、旧 installer SHA `1cecca95…`、5 项 NOT_RUN 逐条列明 |
| V-15 | 无效尝试如实记录 | 读 `nsis-build.log` | `3d532c1f` | PASS | wrapper 参数错误、构建未启动、`EXIT=1; ELAPSED=0.0s`，明确不计 Gate |
| V-16 | 现场重跑 Windows Gate（Reviewer 侧） | — | — | **NOT_RUN** | 沙箱 `Win32 5` 失败，无 shell；不替代性声称 |
| V-17 | 依赖/Schema 差量 | `requirements.txt` 逐行一致；Schema=`doc/contracts/**` 无版本差量声明 + 无产品常量改动（`PROTOCOL_MINOR` base=head=6） | base vs head | PASS | 见 V-08 |

**证据纪律核对**：`check-snapshots.log`、`dev-runner.log`、`packaged-runner.log`、`sidecar-build.log`、`nsis-build-r1.log`、`nsis-build.log` 均带 `HOST=...; HARNESS_PYTHON=...; CWD=...` 头、`HEAD=` 行与 `EXIT=...; ELAPSED=...` 尾行（由 `run_step.py:14-20` 统一生成）；无 skip（r4 全部 PASS）；历史 26 = 20 PASS + 1 FAIL + 5 NOT_RUN 的**总数与差值解释**已在 `result-summary.json` 与 Task §"实施结果与阻塞"同处给出。

**已知限制表述一致性**：R2-03 in-page IP/IA matrix 未机器验证、host simulation 不替代干净 Windows 分发验收、PyInstaller 可选模块警告（`torch.utils.tensorboard`、`torchvision.image/_C`、`scipy.special._cdflib`）、`python.exe: 8` 为非归因观察值——在 Task（:197）、Handoff（:32）、`STATUS`（:13）、`dev-runner.log`（:54）、`cleanstart-gate.json`（CS-Z3）中表述一致，无夸大。

**前置 ICU Gate 未被替代**：ICU 任务 installer SHA 为 `f2a4e2e7…`（`resume-after-icu-fix.md:11`），本 Task fresh 构建为 `ef617573…`，两者不同 → 本 Task AC4 确为自身 fresh 构建产物；Task（:179）、STATUS（:9）亦明确声明不借用前置 Gate。

## Findings

**在本次审查范围内未发现 P0/P1。** 下列 4 项 P2 + 1 项判断项均为非阻断，不改变批准结论。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `verification/M2-RC2/run_e2e.py:503`；`packaging/m2ac5/run_clean_start_e2e.py:738` | `--output-dir` 为**可选**，默认仍指向历史 tracked 目录（`verification/M2-RC2/raw/`、`verification/M2-AC5/raw/`）。本次运行已传隔离目录、历史证据文件集合未变；但后续任何不带该参数的重跑会覆盖历史 raw 证据（正是本 Task 想消除的风险类别） | 两文件 default=RAW；V-13 文件集合对比 | 由 Codex 在集成/后续 Task 中约定"必须显式传 `--output-dir`"，或另行授权把该参数设为 required（本轮不改，避免扩大范围） | open（非阻断，建议集成期登记） |
| R-002 | P2 | `verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/**` | r4 证据包**未入库范围 diff 命令产物**：无 `git diff --name-only 2b780120..3d532c1f -- src apps tests packaging Schema requirements` 与 `git diff --check` 的日志。AC5"无生产/wire/Schema/依赖差量、diff 检查通过"因此只能由 Reviewer 用文件级替代手段 + 分支 reflog 论证；另 `reviewed_head`(5c2d0478) 比证据所绑 `code_delivery_head`(3d532c1f) 多两个 `docs:` 提交，其"未触碰两处 runner"亦仅有 subject/Task 声明 | 对该目录 grep `git diff|--name-only|--check` 无命中；`closeout-validation.log` 的旧范围检查针对 `15cd788f` | 集成时补录一次范围/空白检查并把输出入库；同时确认 `ce5ff3fc`/`5c2d0478` 对两处 runner 零差量 | open（非阻断；本 Review 已用替代手段独立核对，结论未受影响） |
| R-003 | P2 | `packaging/m2ac5/run_clean_start_e2e.py:66-71`（`SIDECAR_EXES`） | packaged Gate 安装后只断言 **4** 个 sidecar（host_bridge/core_service/acceptance_bridge/catalog_loader），而 `build-fingerprint.json` 记录 **5** 个入口（含 `sfx_detect_probe.exe`）；"五入口 ↔ installer" 的绑定只在构建侧，装载侧未验证第 5 个 | base 与 head 的 `SIDECAR_EXES` 相同（4 项）；`cleanstart-gate.json` CS-I1 detail 只有 4 个名字 | 属 base 已有行为、非本轮引入；如需闭环应另开范围把第 5 个入口纳入断言 | open（非阻断，超本轮冻结范围） |
| R-004 | P2 | `doc/handoffs/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f.md:15` | Handoff 称两处 runner 相对审查基线为 "**+27/−13**"；本 Reviewer 由 base/head 两副本逐 hunk 重建为 **+18/−3**（`run_e2e.py`）与 **+8/−9**（`run_clean_start_e2e.py`）= **+26/−12**，相差一对增减（最可能为 EOF 换行归一，或口径取自原 base `968c8f34`）。纯统计口径问题，不影响 Gate 结论 | 逐 hunk 行号对照；无 shell 无法跑 `git diff --stat` 复核 | 集成时以 `git diff --stat 2b780120..3d532c1f -- <两文件>` 复核并把 Handoff 口径改为与 review base 对齐 | open（非阻断，文档精度） |
| R-005 | P2（judgement，非违规） | `verification/M2-RC2/run_e2e.py:498-506` | 新增 `global RAW, LAB`：函数隐式依赖模块级可变状态，属 possible **Global Data / hidden temporal coupling**。当前所有落盘均经 `RAW`、`main()` 为唯一入口，风险低；Task 明确要求"先复用已有常量/断言模式、不建 registry/框架"，故属可接受取舍 | head `main()` 与各写入点（`RAW / ...`）通读 | 无需本轮修改；若将来新增第三个输出根，建议改为显式传参 | open（判断项，不改也可接受） |

## 结论与复审

**决策：`approved`。**

**Architecture：PASS** — 变更限验收工具层，契约方向（产品源码 → 冻结 oracle）正确，隔离与 fail-closed 设计成立，无新产品依赖/Schema/IPC 变更。
**Verification：PASS** — 0 P0/P1；关键 AC 均有已入库、带 EXIT/环境头、相互交叉一致的证据（尤其 installer SHA 在构建指纹、Gate JSON、`STATUS`/Handoff 四点一致，并与 NSIS 日志的 552.70 MiB 尺寸互证）；本轮 Reviewer 侧现场重跑为 `NOT_RUN`，已按证据纪律以日志评估，未作任何现场重跑声明。

**对该 reviewed_head 的批准范围**：`reviewed_head = 5c2d0478`，其两处 runner 内容已完整逐 hunk 审查；运行证据绑定于 `code_delivery_head = 3d532c1f`。

**交 Codex 集成前的必做检查（非本 Review 的返工项，属正常集成 Gate）**
1. 在真实 shell 中执行并入库 `git diff --name-only 2b780120d1eb94f93afadf073790f65899a618e6..5c2d047804eb4a802c04e53b5e8e5e5459570b24`（全量）与 `git diff --check`，确认 `src/**`、`apps/**`、`tests/**`、Schema、依赖零差量（R-002）。
2. 确认 `ce5ff3fc`、`5c2d0478` 两个 `docs:` 提交未改动 `packaging/m2ac5/run_clean_start_e2e.py` 与 `verification/M2-RC2/run_e2e.py`（R-002）。
3. 以 `git diff --stat` 复核并统一 Handoff 的 +27/−13 口径（R-004）。
4. 集成合并后按 AC6 做受影响检查；**不得**因本 Review 批准就把 Task 标 `done`——AC6 的集成后检查尚未发生。

**剩余风险（已披露、非阻断）**：R-001 默认输出目录对历史证据的潜在覆盖；R-003 第 5 个 sidecar 入口未被装载侧断言；Dev in-page IP/IA matrix（R2-03）仍未机器验证；本机 host simulation 不替代干净 Windows 分发验收；本 Reviewer 无法执行 git/Windows Gate，故"零差量"与"+27/−13"两项由替代手段与待复核项共同承载。

**复审约定**：如需追加新 head，仅追加新 `reviewed_head` 与对应 findings disposition，不抹掉本记录；r1/r2/r3 报告保持原字节（本次未发现被改写）。