---
task_id: P03
title: Packaged 第五 SFX 入口验收补齐 (r1 修订交付)
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
base_commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
release_commit: ece8765461ce19f7493ce636ff7d69ae6a3e1c4b
start_head: 6d84b480d5996d6374192bbbba07807848b8ebde
build_source_head: 29024a21939917c6d8eb15f1a2bb9ff46cd5bf23
installer_sha256: d21e89b6d9f81c3499840a687da0f68d1cad6f9e11e9058078e510ecfa0d8721
status: in_review
---

# Handoff：P03 Packaged 第五 SFX 入口验收补齐 (r1 修订交付)

## 交付概览

本交接文档针对初轮 DeepSeek Harness (DSH) 审查报告（`G:/CODEX/New Manga.worktrees/P03-dsh-review-6d84b48/doc/reviews/P03-PACKAGED-SFX-ENTRY-6d84b480-dsh.md`，session `session-c52e715d-8f4b-4aa8-98bb-48e71e1f5317`）提出的 R-001 ~ R-010 共 10 项 findings 进行轻量但彻底的验收可信度修订。

在严格遵守禁止修改范围（零修改 `src/**`、`apps/**`、contracts、Schema、依赖、build spec/script；保留第一轮证据 `run-51f6b10c/**` 与 `build-logs/**` 原样）的前提下，所有第二轮修订证据均隔离存放于 `verification/P03-PACKAGED-SFX-ENTRY/revision-2/**`。

---

## Review Findings 逐项处置 (Disposition)

| Finding ID | 级别 | 问题摘要 | 修复与处置细节 | 证据/测试证明 |
|---|---|---|---|---|
| **R-001** | P2 | 权重来源封闭验证 | 1. 在 `purged_environment()` 清除键中加入 `NEWMANGA_SFX_WEIGHTS`，并在执行 probe 时显式 `pop` 该环境变量，彻底屏蔽外部 env 覆盖；<br>2. `evaluate_sfx_probe_success` 显式断言 `weights.resolved_from == "bundle_probe"`，且校验权重绝对路径必须位于本次安装目录 `install_dir` 之内；<br>3. 在 `observed` 中记录 `weights_resolved_from`、`weights_path` 与 `weights_in_install_dir`；<br>4. 增加单元测试 `test_evaluate_sfx_probe_rejects_external_env_or_outside_weights`，证明外部 env、外部 arg 或安装目录外的权重均会被判定拒绝。 | [`test_packaged_fifth_sfx_entry.py`](../../tests/packaging/test_packaged_fifth_sfx_entry.py)；Gate observed 中 `weights_resolved_from: bundle_probe`，`weights_in_install_dir: true` |
| **R-002** | P2 | K07 文件 SHA-256 pin 校验 | 1. 在 runner 中定义固定常量 `K07_REAL_PAGE_SHA256 = "28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4"`；<br>2. 在运行 probe 之前对真实页面文件按字节计算 SHA-256，若文件不存在或 hash 不匹配，直接记录结构化 `FAIL` 且不启动 probe；<br>3. 匹配时在 observed 中记录 `page_file_sha256`，与 probe JSON 报告的 RGB24 像素域 hash `page_pixel_sha256` 明确区分命名。 | [`run_clean_start_e2e.py`](../../packaging/m2ac5/run_clean_start_e2e.py)；Gate observed 中 `page_file_sha256: 28dab503...` 与 `page_pixel_sha256: b3b7c4a6...` 分开记录 |
| **R-003** | P2 | 真实清理断言测试 | 1. 抽取最小的真实判定函数 `evaluate_sidecar_survivors(survivors, expected_exes=SIDECAR_EXES)`，runner 的 `CS-Z3` 直接调用该函数；<br>2. `SIDECAR_EXES` 成为唯一清单源，进程轮询 `SURVIVOR_POLL_PROCESSES = SIDECAR_EXES + ("python.exe",)`；<br>3. 单元测试 `test_survivor_reaping_judgement_includes_fifth_sfx_entry` 直接调用 `evaluate_sidecar_survivors` 判定函数，断言其在 `sfx_detect_probe.exe > 0` 或缺键时返回 False。 | [`test_packaged_fifth_sfx_entry.py`](../../tests/packaging/test_packaged_fifth_sfx_entry.py)；[`run_clean_start_e2e.py`](../../packaging/m2ac5/run_clean_start_e2e.py) |
| **R-004** | P2 | 工具版本与构建日志警告记录 | 1. 第二轮构建 manifest 与 Handoff 严格记录本轮构建日志实测版本：Node `v24.15.0`、npm `12.0.1`、Rust/Cargo `1.98.1`、Python build `3.12.3`、PyInstaller `6.22.3`；<br>2. 如实记录 npm deprecated `whatwg-encoding@3.1.1`、npm blocked install script for `esbuild@0.21.5`；<br>3. 如实记录 Tauri 打包过程中编译 `m2rc1-desktop` 生成的 6 条 Rust 编译器 warning（1 unused import, 2 dead code structs, 1 dead code associated items, 1 dead code associated function, 1 dead code methods）。不修改第一轮已归档产物。 | [`build-manifest.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-manifest.json)；[`03-frontend-npm-ci.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/03-frontend-npm-ci.log)；[`06-tauri-nsis-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/06-tauri-nsis-build.log) |
| **R-005** | P3 | 非 dict JSON payload 解析边界 | 1. 在 `evaluate_sfx_probe_success` 与 `evaluate_sfx_probe_failure` 中解析 JSON 后，若顶层不是 dict（如 list、string、int、bool 等），将 `payload` 置为 None，返回结构化 FAIL，杜绝 `AttributeError`；<br>2. 补充多项非 dict payload 负向测试。 | [`test_packaged_fifth_sfx_entry.py`](../../tests/packaging/test_packaged_fifth_sfx_entry.py) 覆盖 list/string/integer/bool payload 均判 FAIL |
| **R-006** | P3 | missing-page 隔离前置断言 | 负向场景启动前显式检查 `missing_page.exists()`，若意外存在则直接记录结构化 `FAIL` 且不运行 probe；保证不存在时在 observed 记录 `path_precondition: "absent"`。 | [`run_clean_start_e2e.py`](../../packaging/m2ac5/run_clean_start_e2e.py)；Gate observed 中 `path_precondition: "absent"` |
| **R-007** | P3 | strict int candidates 与 error key 校验 | 1. `n_candidates` 使用严格类型判定：`type(n_candidates) is int and n_candidates > 0`，拒绝 `bool`（如 Python 中的 `True`）及浮点数；<br>2. 成功判据必须包含 `"error" in payload and payload["error"] is None`；<br>3. 补充对应负向测试（`True`、`1.5`、缺少 error key、error 非空等）。 | [`test_packaged_fifth_sfx_entry.py`](../../tests/packaging/test_packaged_fifth_sfx_entry.py) 参数化测试全部通过 |
| **R-008** | P3 | git diff --check 日志归档 | 运行针对 `base..delivery` 的 `git diff --check`，完整输出保存到 `08-git-diff-check.log`，EXIT=0。 | [`08-git-diff-check.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/08-git-diff-check.log) |
| **R-009** | P3 | opt-in 可见性结构化标识 | 在 `cleanstart-gate.json` 顶层增加 `sfx_verification` 对象，明确包含 `requested`、`page_path`、`scenarios_executed` 与 `verdict`，杜绝审核者将未传 `--sfx-real-page` 的运行误读为 SFX 场景已验证。 | [`cleanstart-gate.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21/cleanstart-gate.json) |
| **R-010** | P4 | 输入预检日志归档 | 执行 PowerShell 预检脚本，记录环境、路径、字节数、预期/实际哈希与匹配结论，保存为 `00-input-preflight.log`，EXIT=0。 | [`00-input-preflight.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/00-input-preflight.log) |

---

## 验证与证据矩阵

| 序号 | 验证项目 | 实际执行命令 | 状态与结果 | 证据路径 |
|---|---|---|---|---|
| **0** | 外部输入 Preflight | `powershell -NoProfile -ExecutionPolicy Bypass -File verification/P03-PACKAGED-SFX-ENTRY/revision-2/preflight.ps1` | **PASS**（K07 真实页面与 v2b SFX 模型权重字节/SHA-256 均与 pin 一致，EXIT=0） | [`00-input-preflight.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/00-input-preflight.log) |
| **1** | 定向单元测试 | `python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py` | **PASS**（40 passed in 0.52s，包含所有 R-001/R-003/R-005/R-007 补充用例） | [`01-targeted-tests.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/01-targeted-tests.log) |
| **2** | 快照护栏回归 | `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py` | **PASS**（16 actual-predicate cases，EXIT=0） | [`02-snapshot-check.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/02-snapshot-check.log) |
| **3** | 前端 Fresh 构建 | `npm ci --no-audit --no-fund` & `npm run build` (CWD=`apps/desktop/frontend`) | **PASS**（Node v24.15.0, npm 12.0.1, EXIT=0） | [`03-frontend-npm-ci.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/03-frontend-npm-ci.log)<br>[`04-frontend-npm-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/04-frontend-npm-build.log) |
| **4** | Sidecar Fresh 构建 | `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` | **PASS**（Python 3.12.3 / PyInstaller 6.22.3, 5 个 sidecar 打包完成，EXIT=0） | [`05-sidecar-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/05-sidecar-build.log) |
| **5** | Tauri NSIS 打包 | `npx --yes @tauri-apps/cli@2 build` (CWD=`apps/desktop/src-tauri`) | **PASS**（rustc 1.98.1, cargo 1.98.1, EXIT=0, 生成 579,527,358 bytes 安装包） | [`06-tauri-nsis-build.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/06-tauri-nsis-build.log) |
| **6** | 构建指纹固化 | 写入第二轮 build manifest | **PASS**（installer SHA `d21e89b6...`，实测工具链版本记录完整） | [`build-manifest.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-manifest.json) |
| **7** | Packaged Clean-Start E2E Gate | `python packaging/m2ac5/run_clean_start_e2e.py --installer apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe --output-dir verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21 --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"` | **PASS**（GATE: PASS，全量 28 个场景全部通过，EXIT=0） | 控制台: [`07-gate-run.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/07-gate-run.log)<br>Gate JSON: [`cleanstart-gate.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21/cleanstart-gate.json)<br>正向 log: [`sfx-probe-real-page.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21/sfx-probe-real-page.log)<br>正向 json: [`sfx-probe-real-page.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21/sfx-probe-real-page.json)<br>负向 log: [`sfx-probe-missing-page.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21/sfx-probe-missing-page.log)<br>负向 json: [`sfx-probe-missing-page.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/run-29024a21/sfx-probe-missing-page.json) |
| **8** | Diff Check 归档 | `git diff --check 31abde9b..29024a21` | **PASS**（零空白错误，EXIT=0） | [`08-git-diff-check.log`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/build-logs/08-git-diff-check.log) |

---

## 关键指纹与交付边界

- **Worktree**：`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`
- **Branch**：`agent/antigravity/P03-packaged-sfx-entry`
- **Fixed Base Commit**：`31abde9bf4b73aea2851931dcd48faa0f750b318`
- **Release Commit**：`ece8765461ce19f7493ce636ff7d69ae6a3e1c4b`
- **Build Source HEAD**：`29024a21939917c6d8eb15f1a2bb9ff46cd5bf23`
- **Fresh NSIS Installer 路径**：`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
- **Fresh NSIS Installer SHA-256**：`d21e89b6d9f81c3499840a687da0f68d1cad6f9e11e9058078e510ecfa0d8721`（579,527,358 bytes）
- **Gate JSON 记录 Installer SHA-256**：`d21e89b6d9f81c3499840a687da0f68d1cad6f9e11e9058078e510ecfa0d8721`（完全匹配）
- **Gate Verdict**：`PASS`（28/28 scenarios passed）

### 范围与保护集合核验

1. `git diff --name-only ece87654..HEAD` 检查：仅包含允许路径（`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_packaged_fifth_sfx_entry.py`、`doc/tasks/P03.md`、`doc/handoffs/**`、`verification/P03-PACKAGED-SFX-ENTRY/**`）。
2. `src/**`、`apps/**`、contracts、Schema、依赖、spec/script 保持零修改。
3. 历史 raw、第一轮证据（`run-51f6b10c/**`、`build-manifest.json`、`build-logs/**`）及派发文件（`antigravity-dispatch.json` 等）原样保留。

---

## 复现指令

非作者 Reviewer `DeepSeek Harness` 可在独立 worktree 执行以下命令进行复现验证：

```powershell
# 1. 运行定向单元测试 (40 passed)
python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py

# 2. 运行快照回归 (16 passed)
python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py

# 3. 运行完整 Clean-Start Gate (包含 28 个场景)
python packaging/m2ac5/run_clean_start_e2e.py `
    --installer "apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe" `
    --output-dir "$env:TEMP/p03-dsh-recheck" `
    --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
```

---

## 结论与流转建议

所有 10 项 findings（R-001 ~ R-010）均已按照协作规范以最小侵入改动彻底解决。定向测试扩展至 40 项全过，全新 NSIS 安装包构建成功并在全量 28 项 Gate 场景下 100% 通过。

Task 推进至 `in_review`，交由非作者 Reviewer `DeepSeek Harness` 进行复审。
