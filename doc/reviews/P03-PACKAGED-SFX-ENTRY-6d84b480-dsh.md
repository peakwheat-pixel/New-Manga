---
task_id: P03
reviewer: DeepSeek Harness
author: Antigravity
base_commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
reviewed_head: 6d84b480d5996d6374192bbbba07807848b8ebde
decision: approved
---

# Review：P03 Packaged 第五 SFX 入口验收补齐

作者：Antigravity（Owner）；非作者 Reviewer：DeepSeek Harness；Integrator：Codex。

- **Task base / Review base**：`31abde9bf4b73aea2851931dcd48faa0f750b318`
- **固定 reviewed HEAD**：`6d84b480d5996d6374192bbbba07807848b8ebde`
- **Owner 开工 HEAD（控制面）**：`0a31bbc52447b87a3f04145df62a5ad19baa4b44`
- **Build source HEAD**：`51f6b10c9621c07d5ad7087918d1b904106f0218`
- **Fresh NSIS installer SHA-256**：`af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada`
- 本 Review worktree 为独立 linked worktree；`.git` → `gitdir: G:/CODEX/New Manga/.git/worktrees/P03-dsh-review-6d84b48`，common dir = `G:/CODEX/New Manga/.git`（与 P03 要求一致）。

## 范围与依据

审查对象为固定 Review 全范围 `31abde9..6d84b48`，并以 `0a31bbc..6d84b48` 隔离 Owner 交付差量；Codex 预释放的 Task / Plan / Status / 索引 / 路线图元数据（release commit `ece87654`、同步检查点 `0a31bbc5`）属控制面状态，未计入 Owner 越界。

已完整阅读：`AGENTS.md`、`doc/09_COLLABORATION.md`（§1/§5.1/§6）、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P03.md`、`doc/handoffs/P03-PACKAGED-SFX-ENTRY-51f6b10c.md`、`doc/templates/REVIEW.md`、`verification/P03-PACKAGED-SFX-ENTRY/antigravity-prompt.md`、`packaging/m2ac5/run_clean_start_e2e.py`（全文，1113 行）、`src/bootstrap/sfx_detect_probe.py`（全文）、`tests/packaging/test_packaged_fifth_sfx_entry.py`（全文）、`tests/packaging/test_runner_output_dir_required.py`（全文）、`verification/P03-PACKAGED-SFX-ENTRY/**`（build-manifest、build-logs/01–07、run-51f6b10c 的 `cleanstart-gate.json` 与两份 SFX JSON、RESUME、release-validation、dispatch-preflight、verify_release.py），并交叉核对前置证据 `verification/M2-PROD-SFX-PROBE-1/**`、`verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`、`experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json`。

### 环境限制（影响本 Review 的验证深度）

本会话 DSH 的 `pwsh` 在任何模式下均于沙箱准备阶段失败，`read`/`glob`/`grep` 可用而 shell 不可用：

```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P03-dsh-review-6d84b48)
```

已尝试三种方式并逐一失败：默认 `workspace-write`、`workdir` 改为平台临时区（仍在会话工作区上 grantWrite）、`sandbox_permissions: danger-full-access`（提示 "requires approval, but no approval channel is available"）。因此**一切需要执行 Git / Python / pytest / 哈希计算的动作均记 `NOT_RUN`**，本报告不含任何"我实跑通过"的断言；替代手段为文件级静态复核 + `.git` 元数据直读（reflog / refs 为文本文件）。

已直读的 Git 事实（静态，非命令输出）：

| 事实 | 值 | 来源 |
|---|---|---|
| Owner 分支 ref | `6d84b480d5996d6374192bbbba07807848b8ebde` | `.git/refs/heads/agent/antigravity/P03-packaged-sfx-entry` |
| 本 Review 分支 ref | `6d84b480…` | `.git/refs/heads/review/deepseek/P03-packaged-sfx-entry-6d84b48` |
| `main` | `0a31bbc52447b87a3f04145df62a5ad19baa4b44` | `.git/refs/heads/main` |
| Owner 提交拓扑 | `31abde9 → ece87654 → ed76bb88 → 0a31bbc5 → 51f6b10c（feat: 实现）→ d8714eb（docs: 证据/日志/Handoff）→ 6d84b480（amend 同上）` | Owner worktree `logs/HEAD` reflog |

## Architecture（结论：成立）

- **分层与边界**：改动只落在打包验收工具（`packaging/m2ac5/`）与新增定向测试；`sfx_detect_probe.exe` 作为既有第五 frozen 入口（`src/bootstrap/sfx_detect_probe.py`）被调用，**未新增 IPC 命令面、未触 Tauri/contracts/Schema**。probe 的 `--page/--out/--label` 参数与模块既有 CLI 一致（`src/bootstrap/sfx_detect_probe.py:307-329`），调用形态与 `catalog_loader` 先例同类。
- **fail-closed 设计**：`Gate.verdict` 语义为"无场景或含 FAIL 即 FAIL"（`packaging/m2ac5/run_clean_start_e2e.py:114-119`），新增两条场景经 `gate.pass_or` 并入同一 verdict（`:892`、`:939`），`main` 以 `verdict` 决定退出码（`:1108-1109`）。判别函数对 exit≠0、marker 数≠1、非 frozen、error≠null、候选≤0、权重 SHA≠pin 全部判 FAIL（`:770-778`、`:817-823`）。
- **环境封闭性有缺口**：新阶段复用 `purged_environment` 产出的 `env`（`:1025`），而该函数只清除 `NEWMANGA_DATA_ROOT`，未清 `NEWMANGA_SFX_WEIGHTS`（`:140-144`）；probe 的权重解析顺序为 `--weights` > `NEWMANGA_SFX_WEIGHTS` > frozen 包内探测（`src/bootstrap/sfx_detect_probe.py:109-121`）。前置 Task 的先例是"ALL NEWMANGA_* cleared"并登记清除名单（`verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py:122,132,141,279`）。→ **R-001（P2）**。
- **单一来源不足**：第五入口名字在 runner 内出现三处（`:66-72`、`:1067-1076`、`:1082-1090`），R-003 缺口的成因（清单分散）未根治 → **R-003（P2）**。
- **数据与用户文件保护**：probe 仅读页面 + 读包内权重，不写用户目录；证据目录由 `--output-dir` 显式隔离（`:945,959`），历史 raw 未被覆盖（本运行全部产物落在 `verification/P03-PACKAGED-SFX-ENTRY/run-51f6b10c/`，与 `verification/M2-AC5/**`、`verification/M2-PROD-SFX-PROBE-1/**` 无交集，grep 该两目录未发现 P03 痕迹）。CS-Z1/CS-Z2/CS-Z4 三条零写入断言实测 PASS（`cleanstart-gate.json:305-327`）。

## Verification（结论：Owner 证据链成立；Reviewer 独立复跑 NOT_RUN）

已静态复核成立的关键断言：

1. **installer SHA 三处严格一致**：`build-manifest.json:7`、`cleanstart-gate.json:4`、`cleanstart-gate.json:38-39`（CS-E2 observed）与 Task `:37,48`、Handoff `:11`、RESUME `:5,14` 全为 `af25a4b7…`；大小 579,539,399 bytes 与 `06-tauri-nsis-build.log:317` 的 `552.69 MiB` 自洽；构建日志内路径与 Gate 传入路径为同一 worktree 同一文件（`06…:315`、`07…:3-4`、`cleanstart-gate.json:3`）。
2. **source HEAD 绑定**：`05-sidecar-build.log:5,566` 记录 `git HEAD=51f6b10c…`，与 `build-manifest.json:3`、Task `:83`、Handoff `:10` 一致。
3. **CS-I1（AC1 安装存在断言）**：observed 明确列出 `resources/core-sidecar/` 下五个 exe（`cleanstart-gate.json:54`），与 `SIDECAR_EXES:66-72`、`:234-237` 的实现一致。
4. **CS-Z3（五个 sidecar 零存活）**：`cleanstart-gate.json:329-339` 记录五者均为 0，断言逻辑在 `:1082-1090`。
5. **CS-S1（正向）**：`cleanstart-gate.json:257-285` = exit 0、marker_count 1、json_parsed、frozen true、error null、n_candidates 1、`weights_sha256_matches_pin: true`、device/sfx_ep/`sfx_ep_fallback` 三键原样（`dml`/`dml`/`null`），并保留 `options`、`elapsed_ms`、`wall_ms`、`page_path`；独立 JSON `run-51f6b10c/sfx-probe-real-page.json` 含 `weights.resolved_from: bundle_probe` 与安装目录内权重路径（`:15-21`），可证明"用了包内权重"。
6. **CS-S2（预期失败）**：`cleanstart-gate.json:288-302` = exit 1、marker 1、frozen true、`error.class=FileNotFoundError`、缺失路径位于隔离 lab 目录；独立 JSON `sfx-probe-missing-page.json:12-16` 同形，`page/weights/provider/result` 均为 null。
7. **既有场景未回退**：Gate 顶层场景 28 条（grep `"id":` 计数，去掉嵌套 `E-01-…`）全部 PASS、verdict PASS、EXIT 0（`cleanstart-gate.json:12`、`07-packaged-e2e-gate.log:56-57`）；`02-snapshot-check.log:28-29` 记 16 cases PASS/EXIT 0；`01-targeted-tests.log` 记 28 passed/EXIT 0，且逐条用例名可复核（其中 `test_runner_output_dir_required.py` 8 项含 `--output-dir` 必填 exit 2 与"解析后即拦截、不做真实工作"两条守卫）。
8. **`check_snapshots.py` 对被改 runner 的真实回归**：该 oracle 直接实例化 runner 的 `Gate` 与 `run_library_probe`（`verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py:93-101`）并 compile 两个 runner（`:102-103`）→ 其 16 PASS 是本次改动未破坏 runner 冻结语义的直接证据。
9. **每命令证据头完整**：01–07 日志均带 `Shell: PowerShell 7.6.6` + 解释器/工具版本 + 完整命令 + `EXIT:`（`grep` 全目录确认 6 处 EXIT 均为 0）。

未成立/不可复核部分：见 Findings 与「验证」表（`git diff --name-only/--check`、pytest、Gate 复跑由 Reviewer 独立执行 = NOT_RUN）。

- **视角状态声明（建议项）**：Architecture = `executed`（静态）；Verification = `executed`（静态复核 Owner artefact，独立执行 `NOT_RUN`）；Standards（可选）= `N/A`（未另立一节，硬性条款按 `AGENTS.md` / 09 §6 / Task allowed_paths 在 Findings 与上文逐条引用）；Spec（可选）= `executed`（按 P03 AC1–AC5 逐项对表，见下）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议（最小修复） | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `packaging/m2ac5/run_clean_start_e2e.py:140-144`、`:1024-1025`、`:864-877`；`src/bootstrap/sfx_detect_probe.py:109-121` | probe 阶段复用的 `env` 未清 `NEWMANGA_SFX_WEIGHTS`（只清 `NEWMANGA_DATA_ROOT`）。宿主若已设置该变量，probe 从**仓库外 dev 权重**解析权重而 Gate 仍 PASS（hash pin 相同），"打包第五入口使用包内权重"的验收命题被静默替换为"使用宿主权重" | 对照先例：`verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py:122,132,141` 清 `NEWMANGA_` 前缀并登记名单；本次实测未触发（`sfx-probe-real-page.json:18` = `bundle_probe`） | 在 `purged_environment` 或 probe 专用 env 中清除 `NEWMANGA_SFX_WEIGHTS`；并断言 `weights.resolved_from == "bundle_probe"` 且 `weights.path` 位于 `install_dir` 下 | open |
| R-002 | P2 | `run_clean_start_e2e.py:846-861`（仅 `is_file()`）、`:284`（observed 仅记 `page_path`）；`src/bootstrap/sfx_detect_probe.py:265` | Gate 层不校验传入页面与 Task pin `28dab503…` 的文件级一致性；证据里的 `page.sha256` 是**rgb24 像素缓冲**哈希（异域），CS-S1 observed 无文件 sha。传入被替换/同名页面同样 PASS | `sfx-probe-real-page.json:13` = `b3b7c4a6…`（像素域）；前置 Task 先例已在 JSON 记文件哈希 `page_file_sha256=28dab503…`（`verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe-results-r1fix.json:48`）；跨 Task 互证：P03 与前置 Task 两次独立运行的像素哈希同为 `b3b7c4a6…`（`run-51f6b10c/sfx-probe-real-page.log:4` vs `M2-PROD-SFX-PROBE-1/raw/sp-l2-real-page.log:4`） | runner 内加 K07 文件 SHA 常量比对（不匹配即 FAIL），并把文件 sha 记入 observed | open |
| R-003 | P2 | `run_clean_start_e2e.py:66-72`、`:1067-1076`、`:1082-1090`；`tests/packaging/test_packaged_fifth_sfx_entry.py:67-97` | 第五入口名字三处重复；survivor 测试在测试体内**重抄**断言表达式而不调用 runner 逻辑 → 删除 `:1087` 的存活断言不会被任何测试发现（AC1"退出检查对五个 sidecar 断言零存活"缺判别力测试） | `test_survivor_reaping_judgement_includes_fifth_sfx_entry` 全程只操作本地 `survivors_all_clean` 字典；只有 `:54-64` 对 `SIDECAR_EXES` 是真断言 | 提取模块级函数（`def sidecars_reaped(survivors) -> bool`）并在测试中直接调用；`survivors` 名字元组由 `SIDECAR_EXES` 派生 | open |
| R-004 | P2 | `verification/P03-PACKAGED-SFX-ENTRY/build-manifest.json:9-12`；`doc/handoffs/P03-PACKAGED-SFX-ENTRY-51f6b10c.md:77,79` | manifest 记录 node `v22.14.0`/npm `10.9.2`/rustc `1.85.0`/cargo `1.85.0`，而实际构建日志为 Node `v24.15.0`/npm `12.0.1`/rustc `1.98.1`/cargo `1.98.1`；四项全部矛盾且 handoff 复述。AC3 明确要求"记录解释器/工具版本"，按 manifest 复现会换用不同工具链 | `build-logs/06-tauri-nsis-build.log:2-3`、`build-logs/03-frontend-npm-ci.log:2`、`04-frontend-npm-build.log:2`；全仓 grep `v22.14.0`/`1.85.0` 仅命中 manifest 与 handoff（无第三方来源） | 以 06/03/04 日志实测值更正 `manifest.tools` 与 handoff 两行 | open |
| R-005 | P3 | `run_clean_start_e2e.py:747-756`、`:806-815` | `json.loads` 成功但返回非 dict（如 `[1,2]`、`"x"`）时，`(payload or {}).get(...)` 抛 `AttributeError` → runner 崩溃、`cleanstart-gate.json` 不落盘。仍 fail-closed（EXIT≠0），但丢失结构化 verdict | 两个判别函数共用同一模式；测试参数集（`test_…:163-200`、`:228-253`）只覆盖"畸形 JSON"，无"合法非对象 JSON"用例 | 解析后加 `isinstance(payload, dict)` 判定，否则记 FAIL；补一条负向用例 | open |
| R-006 | P3 | `run_clean_start_e2e.py:895-902` | 负向场景先 `rmtree(ignore_errors=True)` 再直接把 `missing_page` 交给 probe，**未显式断言该路径不存在**；"保证不存在"只是构造推断而非自证 | 隔离目录为 `tempfile.mkdtemp()` 新建（`:962`），本次必然不存在（`sfx-probe-missing-page.json:15` = Errno 2）；推断性前置条件未落证据 | 调用前 `assert not missing_page.exists()`，或把 `path_precondition: absent` 写入 observed | open |
| R-007 | P3 | `run_clean_start_e2e.py:761-762` | `isinstance(n_candidates, int) and n_candidates > 0` 接受 JSON `true`（Python `bool ⊂ int`）作为"1 个候选"；实际 probe 输出为 `len()` 整数，触发面窄 | 测试只覆盖 `n_candidates: 0`（`test_…:172`） | 改为 `type(n_candidates) is int and n_candidates > 0`；补 `true`/`1.0` 负例 | open |
| R-008 | P3 | `build-logs/06-tauri-nsis-build.log:310`；`build-logs/03-frontend-npm-ci.log:5-11`；`doc/handoffs/P03-PACKAGED-SFX-ENTRY-51f6b10c.md:54` | (a) rustc 6 个 warnings、npm deprecated / install-scripts blocked 未在 Task/Handoff 如实登记；(b) AC5 要求的 `git diff --check … EXIT=0` 只有文字声称，`build-logs/**` 无该命令的归档 artefact（Q-009：判别力 artefact 缺失即记 NOT_RUN） | `06…:310` "generated 6 warnings"；`03…:5-11` 三条 warn；`build-logs/` 目录枚举无 git-diff 日志 | 增加 `08-git-diff-check.log`（shell/命令/EXIT）并在 Handoff 登记 warning 计数 | open |
| R-009 | P3 | `run_clean_start_e2e.py:1024-1025`；`run-51f6b10c/cleanstart-gate.json:13-341` | opt-in 设计下，不带 `--sfx-real-page` 时 S1/S2 完全缺席而 Gate 仍 PASS；Gate JSON 无 `sfx_real_page` 字段，读者无法区分"未要求"与"要求但漏跑" | 本次两条场景确在场（`cleanstart-gate.json:257,288`；`07…:44-46`），但该事实只能靠人工比对命令行 | Gate JSON 顶层记录 `sfx_real_page` 入参（None / 路径） | open |
| R-010 | P4 | `doc/handoffs/P03-PACKAGED-SFX-ENTRY-51f6b10c.md:74`；`build-manifest.json:16-27` | 外部输入（K07、v2b weights）"开跑前重算核验"无落盘 artefact，只有"终端预检记录"字样；manifest 仅留声明值，第三方无法独立复核 | grep `28dab503` 在 `verification/P03-PACKAGED-SFX-ENTRY/**` 仅命中 `build-manifest.json:20`、`RESUME.md:13` | 预检输出入库，或由 runner 自身断言页/权重 pin（与 R-002 同批） | open |

P0 未解决：**0**；P1 未解决：**0**；P2 未解决：**4**；P3/P4 未解决：**6**。以上均为"应修但不阻塞集成"级；无一项推翻 AC1–AC4 的达成事实。

## AC 逐项核对（Spec 视角）

| AC | 判定 | 依据与缺口 |
|---|---|---|
| AC1 | **PASS（测试面附 R-003）** | `SIDECAR_EXES` 5 项（`:66-72`）→ 安装断言（`:234-237`）→ CS-I1 observed 列全五者（`cleanstart-gate.json:54`）；CS-Z3 五者 0（`:329-339`）；`--output-dir` 必填与"解析后即拦截"守卫由既有 8 项测试保持（`01-targeted-tests.log:32-39`）。缺口：survivor 定向测试无判别力（R-003） |
| AC2 | **PASS（判别力附 R-001/R-002）** | 同一 fresh installer 下 CS-S1/S2 实测（`cleanstart-gate.json:257-302`），frozen/候选>0/权重 pin/error=null/device=dml/sfx_ep=dml/fallback=null 与原样记录齐备；失败场景隔离路径 + 非空结构错误齐备；stdout/stderr/exit 落日志（`run-51f6b10c/sfx-probe-*.log`） |
| AC3 | **PASS（记录附 R-004）** | source HEAD `51f6b10c` 与构建日志一致；installer SHA/大小三处一致；指纹先于 Gate 固化（manifest vs gate 一致）。缺口：`tools` 四项版本记录错误（R-004） |
| AC4 | **PASS（附 R-008）** | 同一 installer SHA 上 28/28 场景 PASS、GATE PASS、EXIT 0；snapshot 16 PASS；定向 28 PASS；每命令有 shell/解释器/命令/EXIT 头。缺口：warnings 未登记、git-diff artefact 缺失 |
| AC5 | **Reviewer 侧部分达成** | 固定 delivery/review head ✓（ref = `6d84b48`）；非作者 Review 由本报告完成；实现差量范围**无法独立证明**（`git diff` NOT_RUN，仅间接证据：`sfx-real-page\|packaged_fifth\|CS-S1\|CS-S2` 全仓 grep 只命中 `packaging/m2ac5/run_clean_start_e2e.py`、新增测试、`verification/P03-…/**`、`doc/tasks/P03.md`、`doc/handoffs/P03-…`、`doc/REBASELINE_PLAN.md`（Codex 控制面），未出现于 `src/**`、`apps/**`、`contracts/**`；`check_snapshots.py` 对 `src/bootstrap/core_service.py` 与 `apps/desktop/src-tauri/src/main.rs` 的结构性对齐 PASS）。Codex 集成时必须补齐 scope diff 复核 |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| Git common dir / 分支归属 | 直读 `.git`（文件）与 `.git/refs/**` | review worktree @ `6d84b48` | **PASS（静态）** | `.git` = `gitdir: G:/CODEX/New Manga/.git/worktrees/P03-dsh-review-6d84b48`；Owner ref = `6d84b480…`；main = `0a31bbc5` |
| 提交拓扑 / delivery head | 直读 Owner worktree `logs/HEAD` reflog | — | **PASS（静态）** | `0a31bbc5 → 51f6b10c（feat）→ d8714eb（docs）→ 6d84b480（amend）` |
| `git diff --name-only 31abde9..6d84b48` | 需 shell | — | **NOT_RUN** | `pwsh` 沙箱失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`；替代=全仓标识 grep + snapshot oracle 间接证据（见 AC5） |
| `git diff --check 31abde9..6d84b48`（与 `0a31bbc..6d84b48`） | 需 shell；且 Owner 侧无归档 artefact | — | **NOT_RUN** | 同上；Owner 声称见 `handoff:54`（文字，无 `build-logs/**` 证据）→ R-008 |
| `python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py` | Reviewer 独立复跑 | — | **NOT_RUN** | 同上；Owner artefact = `build-logs/01-targeted-tests.log`（28 passed / EXIT 0，逐用例名可复核） |
| `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | Reviewer 独立复跑 | — | **NOT_RUN** | Owner artefact = `build-logs/02-snapshot-check.log`（16 cases / EXIT 0） |
| Packaged clean-start Gate 复跑（含 `--sfx-real-page`） | Reviewer 独立复跑（需 installer，579,539,399 B） | — | **NOT_RUN** | Owner artefact = `build-logs/07-packaged-e2e-gate.log` + `run-51f6b10c/cleanstart-gate.json`（28/28 PASS，EXIT 0） |
| installer SHA-256 独立复算 | 需哈希计算 | — | **NOT_RUN** | 三处记录一致（`build-manifest.json:7`、`cleanstart-gate.json:4,39`、`06…:315-317` 路径/大小自洽） |
| 外部输入 K07 / v2b weights SHA 复核 | 需哈希计算 + 读取 worktree 外文件 | — | **NOT_RUN** | 声明值互洽：`build-manifest.json:20,25` = Task `:46-47` = `RESUME.md:13` = runner `:73` = `tests/…:24`；页内容由跨 Task 像素哈希一致间接佐证（R-002 证据行） |
| 判别逻辑负向矩阵（多 marker / 无 marker / 畸形 JSON / 非 frozen / error 非空 / 零候选 / 哈希漂移 / exit≠1） | 静态阅读用例与实现 | `6d84b48` | **PASS（静态）** | `test_…:163-200`、`:228-253` 与 `evaluate_*`（`:770-778`、`:817-823`）逐条对应；缺口 = 非对象 JSON / `bool` 候选（R-005/R-007） |
| 历史 raw 零触碰 | grep + 目录枚举 | `6d84b48` | **PASS（静态，间接）** | `verification/M2-AC5/**` 无 P03 痕迹；本运行产物仅在新目录 `run-51f6b10c/` |
| 全新 Windows 物理机安装验收 | — | — | **N/A（Task 明确排除）** | 属 M2 最终发布 Gate；`RESUME.md:42` 与 Handoff §风险 1 已登记 NOT_RUN |

## 结论与复审

**Architecture：成立。** 改动面干净地限于打包验收工具与定向测试，复用既有 frozen 入口与既有 `--output-dir` 隔离机制，未扩 IPC/契约/Schema/依赖面；fail-closed verdict 语义正确并入既有 Gate。存在的性质是"验收工具的环境封闭性与清单单一来源不足"（R-001/R-003），非方向性缺陷。

**Verification：Owner 证据链成立，Reviewer 独立复跑全部 NOT_RUN（沙箱 ACL 限制）。** installer SHA、source HEAD、外部输入 pin、Gate 场景集（28/28）、snapshot oracle（16）、定向测试（28）六项在文件层面互相自洽且可逐条复核；`git diff` 洁净性与测试复跑需由 Codex 在集成侧补齐（协议 §6.9 已要求 Codex 核对 head 与路径范围）。

**决定：`approved`** —— 0×P0、0×P1，可交 Codex 集成。理由：AC1–AC4 的达成事实在静态复核下成立，缺口全为 P2 及以下的证据准确性与判别力问题，不推翻任何 AC；P2 各项（尤其 R-004 工具版本更正、R-001 环境变量封闭、R-002 页 pin 断言）修复成本极低，建议与集成同批处置。

**剩余风险与未覆盖**：

1. Reviewer 无法独立执行 Git/Python/pytest/Gate/哈希（R-001 之外的第 11 项系统性风险）；上述"PASS"均限定为静态复核结论。
2. `Build source HEAD`(`51f6b10c`) ≠ `reviewed HEAD`(`6d84b48`)：reflog 显示后者为文档/证据提交（含一次 amend），但**无法用 diff 证明其未触碰 `packaging/**` 与 `tests/**`** → 需 Codex 在集成侧确认。
3. opt-in Gate 的"缺席即 PASS"（R-009）与 probe 环境封闭性（R-001）叠加时，存在"运行了 Gate 但第五入口未被真实覆盖"的沟通风险；本次证据已明确记录两条场景在场。
4. 真机/全新干净 Windows、GUI 视觉、模型质量均不在本 Task 范围，维持 NOT_RUN（`RESUME.md:41-44`、Handoff §风险）。
5. 本报告不覆盖任何 P03 之外的既有行为；历史 raw 与前置 Task 证据仅作只读交叉引用。

**复审指引**：Owner 若以新 commit 处置 R-001/R-002/R-004，须追加对应新 head 与 findings disposition，本报告记录不予抹除；`base_commit` 与 `reviewed_head` 保持固定，不延用旧批准。
