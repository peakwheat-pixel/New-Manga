---
task_id: P03
title: Packaged 第五 SFX 入口验收补齐
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
base_commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
release_commit: ece8765461ce19f7493ce636ff7d69ae6a3e1c4b
start_head: 0a31bbc52447b87a3f04145df62a5ad19baa4b44
build_source_head: 51f6b10c9621c07d5ad7087918d1b904106f0218
installer_sha256: af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada
status: in_review
---

# Handoff：P03 Packaged 第五 SFX 入口验收补齐

## 交付结果

### 1. 目标与实现范围

本任务闭合 Runner Debt 审查中登记的缺口 R-003：此前 `packaging/m2ac5/run_clean_start_e2e.py` 的安装文件断言和终态进程清理断言仅列四个 sidecar（`host_bridge.exe`, `core_service.exe`, `acceptance_bridge.exe`, `catalog_loader.exe`），已随 M2-PROD-SFX-PROBE-1 构建的第五入口 `sfx_detect_probe.exe` 未纳入安装后 clean-start Gate 验证。

在严格遵守禁止修改范围（零修改 `src/**`、`apps/**`、contracts、Schema、依赖、build spec/script）的前提下，本次交付完成了以下工作：

1. **[`packaging/m2ac5/run_clean_start_e2e.py`](file:///G:/CODEX/New%20Manga.worktrees/P03-packaged-sfx-entry-antigravity/packaging/m2ac5/run_clean_start_e2e.py)**：
   - 将 `sfx_detect_probe.exe` 纳入 `SIDECAR_EXES` 清单，在 NSIS 静默安装后自动校验 5 个 sidecar 可执行文件均存在；
   - 在 Phase 5 终态 sidecar 进程存活检查中，纳入 `survivors["sfx_detect_probe.exe"] == 0` 断言，确保所有 5 个 sidecar 均零存活；
   - 增加 `--sfx-real-page <path>` 选项，只在显式传入该参数时在 Phase 4 之后、Phase 5 之前触发第五入口验证阶段：
     - **真实成功场景 (`CS-S1-packaged-sfx-real-page`)**：调用安装目录下的 `sfx_detect_probe.exe` 对传入的 K07 页面执行推理，传入独立 `--out`，捕获 stdout/stderr/exit；验证 exit 0、恰有一条 `SFX_PROBE_JSON: ` 标记、`python.frozen=true`、`error=null`、`n_candidates > 0`、权重文件 SHA-256 与固定 pin 一致；完整提取并记录 `device`、`sfx_ep`、`sfx_ep_fallback` 等运行时信息，不隐瞒 fallback；
     - **预期失败场景 (`CS-S2-packaged-sfx-missing-page-failure`)**：调用安装目录下的 `sfx_detect_probe.exe` 对隔离目录下保证不存在的路径执行探测，传入独立 `--out`，捕获 stdout/stderr/exit；验证 exit 1、恰有一条 `SFX_PROBE_JSON: ` 标记、`python.frozen=true`、结构化非空 `error`（包含异常类和错误信息）；
     - 两项场景均并入 Gate 结构化判别（PASS/FAIL），失败 fail-closed。
2. **[`tests/packaging/test_packaged_fifth_sfx_entry.py`](file:///G:/CODEX/New%20Manga.worktrees/P03-packaged-sfx-entry-antigravity/tests/packaging/test_packaged_fifth_sfx_entry.py)**（新增）：
   - 单元测试覆盖第五入口纳入 `SIDECAR_EXES` 清单（5 项）；
   - 覆盖进程清理断言（零存活通过，存活时拒绝）；
   - 覆盖成功场景判别逻辑（exit 0、frozen、候选数、权重哈希、fallback 记录）以及各负向违约 case（非 0 exit、多 marker、无 marker、非法 JSON、非 frozen、error 非空、零候选、哈希漂移）；
   - 覆盖预期失败场景判别逻辑（exit 1、frozen、非空 error）及反向违约 case；
   - 覆盖 `--sfx-real-page` 命令行参数解析及原 `--output-dir` 必填守卫。
3. **Fresh 构建与 Gate 闭环**：
   - 源码 HEAD 固定为 `51f6b10c9621c07d5ad7087918d1b904106f0218`，构建生成全新 NSIS 安装包 `af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada`；
   - 运行单一完整 Gate 命令，包含既有所有 clean-start 场景和两条新 SFX 场景全部通过（`GATE: PASS`）。

---

### 2. 代码提交与精确差量

- **Base Commit**：[`31abde9bf4b73aea2851931dcd48faa0f750b318`](file:///G:/CODEX/New%20Manga.worktrees/P03-packaged-sfx-entry-antigravity)
- **Start HEAD**：[`0a31bbc52447b87a3f04145df62a5ad19baa4b44`](file:///G:/CODEX/New%20Manga.worktrees/P03-packaged-sfx-entry-antigravity)
- **Build Source HEAD**：[`51f6b10c9621c07d5ad7087918d1b904106f0218`](file:///G:/CODEX/New%20Manga.worktrees/P03-packaged-sfx-entry-antigravity)
- **实现文件改动统计**：
  - `packaging/m2ac5/run_clean_start_e2e.py`: 229 insertions(+), 6 deletions(-)
  - `tests/packaging/test_packaged_fifth_sfx_entry.py`: 230 insertions(+), 0 deletions(-)
  - `doc/tasks/P03.md`: 状态流转与结果填报
  - `verification/P03-PACKAGED-SFX-ENTRY/RESUME.md`: 检查点更新
- **禁止范围核对**：`src/**`、`apps/**`、contracts、Schema、依赖、spec/script 零修改；`git diff --check` EXIT=0。

---

### 3. Acceptance Criteria 对照

| AC 项 | 目标要求 | 达成事实与状态 |
|---|---|---|
| **AC1** | packaged clean-start runner 的安装文件断言包含 `sfx_detect_probe.exe`；退出检查对五个 sidecar 均断言无存活进程。新增的定向测试检查第五入口不会从任一清单遗漏；既有 `--output-dir` 防历史 raw 覆盖行为保持通过。 | **PASS**：`SIDECAR_EXES` 扩展为 5 个；`CS-Z3` 断言 5 个 sidecar 存活均为 0；定向测试 28 项通过（含缺少 `sfx_detect_probe.exe` 存活时的判定测试）；`test_runner_output_dir_required.py` 8 项测试全过。 |
| **AC2** | 从同一份 P03 fresh NSIS 安装包启动安装后的 `sfx_detect_probe.exe`。正向使用固定 K07 页面，进程 exit=0、恰有一条 `SFX_PROBE_JSON: `、`python.frozen=true`、`error=null`、检测候选数大于 0，且权重文件 SHA 与 pin 一致；记录 device / sfx_ep / fallback。失败对照使用隔离目录下保证不存在的 PNG 路径，进程 exit=1、恰有一条可解析 JSON、`python.frozen=true` 且包含非空错误信息。stdout、stderr、结构化 JSON 与退出码均保存到隔离目录，并由 Gate 记录为 PASS/FAIL。 | **PASS**：同一份 fresh 安装包实测：`CS-S1-packaged-sfx-real-page` 取得 exit 0, n_candidates=1, confidence=0.9047, device=dml, sfx_ep=dml, fallback=null, weights sha256 匹配 pin；`CS-S2-packaged-sfx-missing-page-failure` 取得 exit 1, frozen=true, FileNotFoundError 错误 payload；两项独立 log 与 json 均写入 `run-51f6b10c/` 且 Gate verdict=PASS。 |
| **AC3** | Owner 在自己的实现提交上确认 worktree clean，记录完整 source HEAD、frontend / sidecar / NSIS 构建命令、解释器/工具版本、NSIS 路径及 64 位 installer SHA-256；在写入 source/installer 指纹后才运行验收。fresh installer 是本 Task 的新产物。Packaged Gate JSON 内记录的 installer SHA 必须与同一证据组的 SHA 完全一致。 | **PASS**：在 clean 的 source HEAD `51f6b10c9621c07d5ad7087918d1b904106f0218` 上 fresh 构建；installer 路径 `apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`，大小 579,539,399 bytes，SHA-256=`af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada`；指纹预先固化在 `build-manifest.json`，且 `cleanstart-gate.json` 中记录的 `installer_sha256` 严格匹配。 |
| **AC4** | 在该同一 installer SHA 上运行现有完整 M2-AC5 clean-start Gate，既有所有场景通过，AC1/AC2 第五入口场景也通过；受影响的 Runner Snapshot oracle 与 packaging 定向测试通过。每个命令有 shell、解释器、完整命令、逐项 passed/skipped、EXIT 和保存的日志。 | **PASS**：运行 `python packaging/m2ac5/run_clean_start_e2e.py`，既有所有阶段（CS-E1..E3, CS-I1..I2, CS-L1..L3, CS-P1..P3, CS-A1..A5, CS-R1..R4, CS-Z1..Z4）以及两条新场景（CS-S1, CS-S2）全部 PASS，`GATE: PASS`，EXIT=0；`check_snapshots.py` 16 项通过；定向测试 28 项通过。日志完整入库。 |
| **AC5** | 固定 delivery/review head；实现差量严格在允许路径内，`git diff --check` EXIT=0，`src/**`、`apps/**`、contracts、Schema、依赖与 build spec/script 零修改。非作者 DeepSeek Harness 完成固定 base/head Review 且无未解决 P0/P1；Codex 完成集成范围、installer/source 绑定、证据、集成后受影响 Gate 检查后才可置 done。 | **IN_REVIEW**：delivery HEAD 固定；实现代码与文档严格限定在允许范围，`git diff --check` EXIT=0；等待非作者 DSH Review 及 Codex 集成。 |

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 Commit | 结果 | 日志/产物路径 |
|---|---|---|---|---|
| **外部输入 Preflight** | Python sha256 独立复算脚本 | Python 3.14.6 @ `0a31bbc5` | **PASS** (K07 及 v2b weights 均与 pin 字节级一致) | 终端预检记录 |
| **定向单元测试** | `python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py` | Python 3.14.6 @ `51f6b10c` | **PASS** (28 passed in 0.50s) | [`01-targeted-tests.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/01-targeted-tests.log) |
| **快照护栏回归** | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | Python 3.14.6 @ `51f6b10c` | **PASS** (16 actual-predicate cases, EXIT=0) | [`02-snapshot-check.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/02-snapshot-check.log) |
| **前端 Fresh 构建** | `npm ci --no-audit --no-fund` & `npm run build` | Node v22.14.0 / npm 10.9.2 @ `51f6b10c` | **PASS** (EXIT=0) | [`03-frontend-npm-ci.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/03-frontend-npm-ci.log), [`04-frontend-npm-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/04-frontend-npm-build.log) |
| **Sidecar Fresh 构建** | `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` | Python 3.12.3 / PyInstaller 6.22.3 @ `51f6b10c` | **PASS** (EXIT=0, 5 executables bundled with manga & sfx weights) | [`05-sidecar-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/05-sidecar-build.log) |
| **NSIS 打包** | `npx --yes @tauri-apps/cli@2 build` (CWD=`apps/desktop/src-tauri`) | Rustc 1.85.0 / Cargo 1.85.0 @ `51f6b10c` | **PASS** (EXIT=0, installer generated) | [`06-tauri-nsis-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/06-tauri-nsis-build.log) |
| **构建指纹固化** | Python sha256 计算与 JSON 固化 | Python 3.14.6 | **PASS** (installer SHA `af25a4b7...`) | [`build-manifest.json`](../../verification/P03-PACKAGED-SFX-ENTRY/build-manifest.json) |
| **Packaged Clean-Start E2E Gate** | `python packaging/m2ac5/run_clean_start_e2e.py --installer <fresh installer> --output-dir verification/P03-PACKAGED-SFX-ENTRY/run-51f6b10c --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"` | Python 3.14.6 @ `51f6b10c` | **PASS** (GATE: PASS, 28/28 scenarios passed, EXIT=0) | 控制台日志: [`07-packaged-e2e-gate.log`](../../verification/P03-PACKAGED-SFX-ENTRY/build-logs/07-packaged-e2e-gate.log)<br>结构化 Gate: [`cleanstart-gate.json`](../../verification/P03-PACKAGED-SFX-ENTRY/run-51f6b10c/cleanstart-gate.json)<br>正向 SFX JSON: [`sfx-probe-real-page.json`](../../verification/P03-PACKAGED-SFX-ENTRY/run-51f6b10c/sfx-probe-real-page.json)<br>负向 SFX JSON: [`sfx-probe-missing-page.json`](../../verification/P03-PACKAGED-SFX-ENTRY/run-51f6b10c/sfx-probe-missing-page.json) |

---

## 接收方式

- **工作区**：`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`
- **分支**：`agent/antigravity/P03-packaged-sfx-entry`
- **固定 Base Commit**：`31abde9bf4b73aea2851931dcd48faa0f750b318`
- **Build Source HEAD**：`51f6b10c9621c07d5ad7087918d1b904106f0218`
- **复现 Gate 命令**：
  ```powershell
  python packaging/m2ac5/run_clean_start_e2e.py `
      --installer "apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe" `
      --output-dir "$env:TEMP/p03-verify-gate" `
      --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
  ```
- **复现单元测试命令**：
  ```powershell
  python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py
  python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py
  ```

---

## 下一任务建议（必填）

- **Task ID / 标题**：P03 非作者独立审查（Review）
- **推荐 Agent / Reviewer**：DeepSeek Harness（Reviewer），Codex（Integrator）
- **推荐原因与前置依赖**：P03 的全部实现、定向测试、fresh 构建、指纹固化以及完整 Packaged E2E Gate 已执行完成并 PASS；依赖已全部满足；按照协作协议需要由非作者 DeepSeek Harness 完成独立审查。
- **Recovery point**：
  - 仓库：`G:/CODEX/New Manga`
  - Worktree：`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`
  - 分支：`agent/antigravity/P03-packaged-sfx-entry`
  - Base Commit：`31abde9bf4b73aea2851931dcd48faa0f750b318`
  - Review 目标 HEAD：本次 Delivery 提交（包含代码实现、测试与完整文档/证据日志）
- **允许修改路径**：`doc/reviews/P03-*.md`（Review 报告）
- **禁止范围与新增授权条件**：不得修改生产源码、Schema、依赖或现有测试行为；不得覆写历史 raw 证据；只读审查实现与验证产物。
- **交付物**：DeepSeek Harness 独立审查报告，按照 [Review 模板](../templates/REVIEW.md) 出具意见。
- **验证命令、环境与完成 Gate**：
  ```powershell
  git diff --name-only 31abde9bf4b73aea2851931dcd48faa0f750b318..<delivery_head>
  git diff --check 31abde9bf4b73aea2851931dcd48faa0f750b318..<delivery_head>
  python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py
  python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py
  ```
  核对 `verification/P03-PACKAGED-SFX-ENTRY/run-51f6b10c/cleanstart-gate.json` 与 `build-manifest.json` 中 installer SHA 一致性。
- **可直接转发给 Agent 的指令**：
  ```markdown
  请 Reviewer DeepSeek Harness 在 `G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity` 工作区，对分支 `agent/antigravity/P03-packaged-sfx-entry` 从 base commit `31abde9bf4b73aea2851931dcd48faa0f750b318` 至 delivery head 执行非作者独立审查。重点核对：
  1. `packaging/m2ac5/run_clean_start_e2e.py` 是否完整纳入第五入口 `sfx_detect_probe.exe` 到安装清单与进程清理断言中；
  2. `--sfx-real-page` opt-in 机制是否在同一 fresh 安装包下正确判定正向（K07 页面、exit 0、frozen、候选数>0、权重哈希、DirectML fallback 原样记录）与负向（隔离缺失路径、exit 1、frozen、非空错误）；
  3. `tests/packaging/test_packaged_fifth_sfx_entry.py` 是否充分覆盖各正反用例，且原 `--output-dir` 必填守卫保持通过；
  4. 验证日志与 `cleanstart-gate.json` 中的 installer SHA 是否与 `build-manifest.json` 严格一致；
  5. 检查差量范围是否严格限定在允许路径，`src/**`、`apps/**` 等禁止路径零修改。
  出具审查报告至 `doc/reviews/`。
  ```

---

## 风险与遗留

1. **Host Simulation 局限性**：本次 E2E 验收在开发机上模拟了 PATH 彻底清除 Python 的环境（purged PATH）以及清理 `NEWMANGA_*` 环境变量；真正的全新物理机/干净 Windows VM 验收属于 M2 最终发布 Gate 范围，此处按计划登记为 `NOT_RUN`。
2. **GUI 人工视觉检验**：本次为自动化打包与命令行 probe 验收，WebView 界面视觉渲染不在本 Task 范围内。
3. **主 checkout 原作者脏工作区**：主 checkout 保留的 `.qoder-credits/**` 等未提交内容保持原样只读隔离，未动、未提交。
