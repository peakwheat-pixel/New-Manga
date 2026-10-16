---
task_id: ENV-BUNDLE-1-FU1
author: Codex
recipient: Coordinator
base_commit: 3bf2604dc9e8ef6be47bd80897e4df05cae077b3
delivery_head: 998200d48e10899e2916a73143578c69bceb30cf
status: ready_for_review
---

# Handoff：ENV-BUNDLE-1-FU1

## 交付结果

已在 `codex/ENV-BUNDLE-1-FU1-packaged-acceptance` 的独立 worktree 完成 packaged sidecar 验收实现与证据，尚未被独立 Review 或接受。

| AC | 结果 | 交付说明 |
|---|---|---|
| AC1 | PASS | 在本 worktree 用既有隔离 venv 完整重建 frozen bundle，并生产构建 frontend；固定路径、大小、SHA-256 和 Core protocol 2.3。 |
| AC2 | PASS | 新增与既有 source-backed 用例分离的测试路径；六项规定场景真实启动 frozen executables，6/6 通过。 |
| AC3 | BLOCKED | Frozen Core 的 `OpenHostSession` 成功；`RegisterImportSource` 返回 `REF_EXPIRED`，未修改产品实现。 |
| AC4 | PASS | 将 task build 的 ignored bundle/dist 镜像到主仓 ignored 目标；主仓 Core smoke 返回协议 2.3。 |
| AC5 | PASS | 仅改动测试注册与新增 AC2 测试文件；无产品语义、契约、Schema 或依赖改动；Cargo 生成的行尾噪音已恢复。 |
| AC6 | PASS | 原 19 项主仓 dirty 的 status 与 `git diff --binary` 指纹前后相同；并发主仓 HEAD 变更已记录。 |
| AC7 | PASS | 实现固定于 delivery head；本 Handoff 和 Canonical Evidence 后续提交补齐固定交接。未 push/merge。 |

实现提交：`998200d48e10899e2916a73143578c69bceb30cf`（`test(ENV-BUNDLE-1-FU1): drive frozen sidecar scenarios`）。变更路径：

- `apps/desktop/src-tauri/src/main.rs`：仅增加 `#[cfg(test)]` 模块声明，让现有 Rust 测试 harness 编译独立的 packaged 测试模块。
- `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs`：新增六项独立 AC2 用例；从当前 worktree 的 frozen bundle 启动 `core_service.exe`、`host_bridge.exe`、`catalog_loader.exe`，记录环境、路径、字节数、SHA-256 和结果。没有更改原六项 source-backed 测试的语义。
- `doc/tasks/ENV-BUNDLE-1-FU1.md` 与 `verification/ENV-BUNDLE-1-FU1/**`：Task 状态、运行记录和可复核证据。

只有上述两个 `apps/desktop/src-tauri/src/**` 文件含代码改动。构建生成的二进制、frontend dist、`node_modules` 和隔离 venv 都未提交；任务与主仓的 ignored build outputs 按 Resource Manifest 保留。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 sidecar build | `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` | 既有 `G:/CODEX/New Manga.task-envs/m2ac5-build`；实现基线 `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`；未使用 `-SkipWeights` | PASS，exit `0` | `verification/ENV-BUNDLE-1-FU1/ac1-build-sidecar.log` |
| AC1 frontend | `npm ci --no-audit --no-fund`; `npm run build` | Node `v24.15.0` / npm `12.0.1`；lockfile SHA 前后相同 | PASS，两个命令均 exit `0` | `ac1-npm-ci.log`、`ac1-frontend-build.log`、`ac1-bundle-and-frontend-manifest.md` |
| AC1 frozen Core smoke | 直接启动 bundle 内 `core_service.exe`，发送 `core.ping`、`core.shutdown` | `M2RC1_PACKAGED=1`；`M2RC1_SRC_ROOT` / `M2RC1_PYTHON` unset | PASS，protocol 2.3；exit `0` | `ac1-core-service-smoke.log` |
| AC2 six packaged scenarios | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1` | Cargo 测试进程环境 `M2RC1_PACKAGED=1`、`M2RC1_SRC_ROOT=<unset>`、`M2RC1_PYTHON=<unset>`；每项启动路径都在本 worktree bundle 内；核心 exe SHA `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` | `6 passed; 0 failed; 0 ignored; 77 filtered out`，exit `0` | `ac2-packaged-six-tests.log`、`ac2-packaged-six-test-results.md` |
| AC3 HostControl | 临时 packaged probe：`OpenHostSession` 后由 `StdioLibraryChannel::import_from_path` 经 `host_issuer.rs` 注册 import source | 同一 frozen Core；source env unset | BLOCKED：Core 返回 `REF_EXPIRED`；combined run exit `101`。不能把 `ImportPages` 标成通过。 | `ac2-ac3-combined-attempt.log`、`ac3-host-control-blocked.md` |
| AC4 main ignored outputs | 将 task build 的 `target/core-sidecar` 和 `frontend/dist` 用 Robocopy `/MIR /COPY:DAT /DCOPY:DAT` 镜像到已验证为 gitignored 的主仓目标；对主仓 Core 做隔离 ping/shutdown | 源与目标 build 输入 `src`、`apps/desktop`、`packaging` 一致；目标 Core SHA 与 AC1 相同 | PASS；Robocopy 两项 exit `3`、零复制失败；Core protocol 2.3、exit `0` | `ac4-copy-sidecar-to-main.log`、`ac4-copy-frontend-to-main.log`、`ac4-main-core-smoke-after.log`、`main-artifacts-after.md` |
| AC5 scope / generated files | 检查 Task diff 与 staged path；比对 27 个 Cargo 自动生成文件的 `git diff`，逐项恢复纯行尾变化 | 本 task worktree | PASS；无业务实现、契约、Schema 或依赖改动；生成文件内容 diff 为空 | `ac5-generated-side-effects.md` |
| AC6 main protection | 前后读取主仓 `HEAD`、`git status --porcelain --untracked-files=no` 和 `git diff --binary`；按原 19 路径计算 SHA-256 | 主仓 `G:/CODEX/New Manga` | PASS；原 19 项 status SHA `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a` 和 diff SHA `fde78be03b5e5be8a01d10050703c2b2e587756b8d77a39be6bce05d1e7bfe35` 前后相同 | `main-status-comparison.md`、before/after snapshots |

主 frozen bundle：`G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1/apps/desktop/src-tauri/target/core-sidecar/core-sidecar`，5,563 files / 1,287,287,472 bytes。被测 `core_service.exe` 为 68,717,156 bytes，SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`，protocol 2.3。

逐项 AC2 结果：

1. `real_core_sidecar_round_trip` — PASS：frozen `catalog_loader.exe` 初始化 catalog；frozen `host_bridge.exe` issue/resolve/revoke；验证 `REF_REVOKED` 并发送 shutdown。
2. `real_library_sidecar_round_trip_and_eof` — PASS：frozen Core protocol 2.3、`ListBooks` 空结果及进程结束后的 `CORE_UNAVAILABLE`。
3. `real_core_sidecar_rc4_commands_round_trip_typed_errors` — PASS：revision list/restore/rerender 返回 `TARGET_NOT_FOUND`。
4. `real_core_sidecar_retype_pair_empty_page_and_typed_rejection` — PASS：未知 page 返回空 regions；未知 region 返回 `TARGET_NOT_FOUND`。
5. `real_core_sidecar_settings_round_trip_and_typed_rejection` — PASS：合法设置写入并读回；非法值返回 `INVALID_REQUEST`，且原值保留。
6. `real_core_sidecar_answers_startup_ping_on_fresh_catalog` — PASS：新 catalog 上 startup ping 返回 protocol 2.3 并创建 catalog。

两次早期尝试的失败日志也保留且不计入最终 AC2 结果：首次新增 helper 编译失败（修正测试代码后重跑）；一次合并 AC2/AC3 的探测中六项 AC2 全过，但 AC3 的 grant 注册失败。Handoff 只引用最终独立 AC2 命令的 6/6 通过结果。

主仓 `core_service.exe` AC4 前后：68,604,146 bytes / SHA-256 `61f128d6878baad1c72fa24f7cda75675b31354ea47b43828861e7d8b2ca91f0` / protocol `1.6` → 68,717,156 bytes / SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` / protocol `2.3`。主仓 frontend dist 从 196,591 bytes 更新至 201,081 bytes；Task build manifest SHA-256 为 `d56249d8a1afc8edd88309a7fb4ad9b4add39ec9c68151dca7850c9012898ea7`。

## 接收方式

- Branch：`codex/ENV-BUNDLE-1-FU1-packaged-acceptance`
- Owner worktree：`G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`
- Base：`3bf2604dc9e8ef6be47bd80897e4df05cae077b3`
- Implementation delivery head：`998200d48e10899e2916a73143578c69bceb30cf`
- 复现 AC2 需保留该 worktree 的 gitignored `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/**`。在 worktree 根目录执行：

```powershell
$env:M2RC1_PACKAGED = '1'
Remove-Item Env:M2RC1_SRC_ROOT -ErrorAction SilentlyContinue
Remove-Item Env:M2RC1_PYTHON -ErrorAction SilentlyContinue
cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1
```

- 任务状态为 `in_review`；Coordinator 路由独立 Review 后再更新权威状态指针。不要将 AC3 记为通过。

## 下一任务建议（必填）

- **Task ID / 标题**：`ENV-BUNDLE-1-FU1` 独立 packaged acceptance Review；启动条件为本 Handoff 与实现提交已固定，依赖本次交付证据。
- **推荐 Agent / Reviewer**：DeepSeek Harness。其职责包含独立 Review；Reviewer 与 Owner Codex 不同。
- **推荐原因与前置依赖**：需要独立核对 frozen 驱动证据、测试范围、AC3 blocker 与主仓保护；Review 通过前不得接受本交付。当前只是建议，需 Coordinator 在 `STATUS` 释放 Review 工作。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；实现 branch `codex/ENV-BUNDLE-1-FU1-packaged-acceptance`；Owner worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`；base `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`；head `998200d48e10899e2916a73143578c69bceb30cf`；Reviewer worktree：待 Codex 创建。
- **允许修改路径**：Review worktree 中独立 Review 报告及其必要验证日志；仅在 Coordinator 释放 Review Task 后写入。当前建议阶段对交付内容只读。
- **禁止范围与新增授权条件**：不得自审；不得触碰主仓 19 项 dirty、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、共享契约或产品代码；不得把 AC3 的 `REF_EXPIRED` 改记为 PASS。若要修复 HostControl，须另立并授权产品实现 Task。
- **交付物**：依 `doc/templates/REVIEW.md` 形成独立 Review，逐项报告 AC1–AC7、发现、阻塞与结论；报告和必要复核日志归档至 Coordinator 释放的证据路径。
- **验证命令、环境与完成 Gate**：核对 `verification/ENV-BUNDLE-1-FU1/**` 的原始日志及 SHA-256、六个 packaged 测试路径与实际 frozen exe、AC3 原始失败、主仓前后 status/diff 指纹；若在 reviewer worktree 重跑 AC2，需将相同 frozen bundle 放入其 ignored target 路径，设置 `M2RC1_PACKAGED=1` 并确认 source env unset，执行上方 cargo 命令。Review Gate：无未解决的 Critical/High 发现；AC3 保持 BLOCKED；无超范围改动或主仓保护问题；Reviewer 与 Owner 不同。测试未跑或阻塞必须如实保留。
- **可直接转发给 Agent 的指令**：

  > 请独立 Review Task `ENV-BUNDLE-1-FU1` 的 packaged acceptance 交付。Recovery point：仓库 `G:/CODEX/New Manga`，branch `codex/ENV-BUNDLE-1-FU1-packaged-acceptance`，Owner worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`，base `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`，实现 head `998200d48e10899e2916a73143578c69bceb30cf`；你的独立 Review worktree 待 Codex 创建。只读检查实现和 `verification/ENV-BUNDLE-1-FU1/**`，特别核验 AC2 六个 frozen 进程的路径/hash/env/逐项结果、AC3 `REF_EXPIRED` blocker、AC4 主仓 ignored outputs 及 AC6 原 19 项 dirty 指纹。不得把 source-backed 测试当 packaged 验收，不得把 AC3 标 PASS，不得改产品代码或主仓用户文件。按 `doc/templates/REVIEW.md` 提交独立 Review 和证据；若重跑 AC2，先把相同 ignored frozen bundle 放入独立 worktree，设置 `M2RC1_PACKAGED=1`、清除 `M2RC1_SRC_ROOT`/`M2RC1_PYTHON`，执行 `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1`；报告实际 exit code 与逐项结果，未跑项写 NOT_RUN/BLOCKED。Gate：无未解决 Critical/High，AC3 保持 BLOCKED，且主仓 19 项状态/diff 指纹未变。此建议尚待 Coordinator 释放，不代表 Review Task 已启动。

## 风险与遗留

- AC3 的真实 HostControl 探测在 `RegisterImportSource` 收到 `REF_EXPIRED`。Core 校验拒绝 `expires_at <= now` 或 `expires_at > now + 300`，host 侧创建 `SystemTime::now() + 300s`。秒级边界差是可能解释，但 wire error 未包含时间戳，精确偏差未测；这是推断。当前 Task 不允许改产品实现，需另立授权修复 Task。
- 本次只运行新增六项 packaged 测试，未运行既有 source-backed 全套 77 项，也未进行 NSIS installer / GUI 安装验收。不能据此声明完整安装流程验收。
- 生成的 frozen bundle、frontend dist、`node_modules` 和隔离 venv 按 `verification/ENV-BUNDLE-1-FU1/resource-manifest.json` 保留；大型文件未入库。
- 未 push、未 merge。主仓 HEAD 在本任务期间由并发 UI-DESIGN-1 文档提交推进；本任务只写入 AC4 授权的 ignored 产物，原 19 项 dirty 指纹前后相同。
