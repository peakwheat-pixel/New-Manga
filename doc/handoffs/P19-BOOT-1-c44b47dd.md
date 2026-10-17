---
task_id: P19-BOOT-1
author: Codex
recipient: DeepSeek Harness
base_commit: 04d7beedc4a390ff67130eab0baa5b5ee78140cc
delivery_head: c44b47dd9852121e18496502870f4e4cbaf5c737
status: in_review
---

# Handoff：P19-BOOT-1

## 交付结果

修复 Core 在 catalog 文件已存在、preview namespace lock/binding 不完整时跳过初始化并崩溃的问题。实现提交：

- `daabedccd101b1993bbaf33f78d4dd1092fbb670`：启动时检查 lock；缺失或不可解析时，持有独占锁并只从 canonical catalog binding 安全恢复；catalog 无 binding 时交给原有受限 initializer；更新误导性 GC 日志。
- `607595165e722425030f031e56bec15c60bf51d4`：共享租约入口将竞态下缺锁转换为类型化资源错误，并增加反例。
- `c44b47dd9852121e18496502870f4e4cbaf5c737`：增加长非 JSON 损坏锁用例，验证恢复会截断旧内容且不会留下尾部字节。

修改路径：

- `src/bootstrap/core_service.py`
- `src/infrastructure/resource_channel/catalog_store.py`
- `src/infrastructure/resource_channel/handle_resolver.py`
- `tests/core/test_core_namespace_bootstrap.py`

修复不改变共享/独占 lease 的 share mode、lock handle 的 reparse/path identity 检查、catalog binding 身份校验或 GC 顺序。损坏 lock 仅在已取得独占 lock handle、canonical catalog row/schema 及 catalog/derived 路径与 volume/file identity 全部验证后才会重写；写入后截断旧尾部。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC2–AC5 / Gate Core 套件 | `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe -m pytest tests/core -q -p no:cacheprovider` | Windows；TEMP/TMP 指向本 worktree 的 `verification/P19-BOOT-1/core-tests-temp-final`；`c44b47dd9852121e18496502870f4e4cbaf5c737` | PASS：515 passed、0 skipped、1 warning、exit 0；基线 508 | `verification/P19-BOOT-1/core-suite.log` |
| AC1 Cargo host build | `cargo build --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` | 当前 worktree；`c44b47dd9852121e18496502870f4e4cbaf5c737` | PASS：exit 0 | `verification/P19-BOOT-1/cargo-build.log` |
| AC1 WebView build | `cargo build --locked --features tauri/custom-protocol --manifest-path apps/desktop/src-tauri/Cargo.toml`；之前执行 `npm run build` | 当前 worktree；同一 source head | PASS：两条命令 exit 0；custom protocol 用来让 debug host 加载前端资产 | `cargo-build-custom-protocol.log`、`frontend-build.log` |
| AC1 真实启动与四页可达 | 先运行 `prepare_partial_state.py`，确认 catalog 存在且 derived 空；启动 `target/debug/m2rc1-desktop.exe`；真实鼠标点击四个导航项并逐页截图；正常关闭窗口 | Cargo debug Tauri host + `M2RC1_SRC_ROOT=src` 的 Python Core source sidecar；所有应用数据在 `verification/P19-BOOT-1/runtime-final6`；实现 head `c44b47dd9852121e18496502870f4e4cbaf5c737` | PASS：exit 0；WebView UIA 标题可见；四页均有窗口截图；stderr 无裸 `FileNotFoundError`、`JSONDecodeError` 或误导性 busy 文案 | `real-startup-final.json`、`real-startup-final-run.log`、`final-app.stderr.log`、四张 `ui-*-real-window.png` |
| AC2 首次绑定 | 真实启动后检查 lock 和 catalog row | 同一真实运行实例；runtime-final6 | PASS：有效 lock JSON；唯一 catalog binding row 与 lock 内容、catalog/derived 的路径及文件身份匹配 | `runtime-binding-final.json` |
| AC2 缺锁失败关闭反例 | `test_missing_lock_fails_closed_with_typed_resource_error` | Core pytest；固定实现 head | PASS：`TypedResourceChannelError`，无裸 `FileNotFoundError` | `core-suite.log` |
| AC3 损坏锁反例 | `test_damaged_lock_is_restored_from_verified_catalog_binding`（空、非 JSON、字段不可解析及 8192 字节长非 JSON）；`test_damaged_lock_does_not_rebind_catalog_to_a_different_derived_identity` | Core pytest；固定实现 head | PASS：正确 binding 恢复并截断旧尾部，身份 mismatch 类型化失败且保留损坏 lock | `core-suite.log` |
| AC5 catalog 存在且 derived 空 | `test_catalog_exists_with_empty_derived_root_gets_controlled_first_binding`；另以相同 partial state 执行真实 app 启动 | 进程内 Core pytest + 真实 Tauri debug host/source sidecar | PASS：受控 initializer 写入 binding；真实 app 启动到四页 | `core-suite.log`、partial-state JSON、real-startup JSON 与截图 |
| AC4 lease / identity / reparse / GC | 检查固定实现 diff 与既有 lease/open/GC 路径；不改锁 share mode 或 GC 顺序 | `04d7beedc4a390ff67130eab0baa5b5ee78140cc..c44b47dd9852121e18496502870f4e4cbaf5c737` | PASS：独占 handle 持有期间验证后恢复；原有 identity 与 reparse 校验仍生效 | `real-startup-evidence.md`、固定 source commit |

Canonical Evidence 的逐文件 SHA-256 见 [evidence-manifest.json](../../verification/P19-BOOT-1/evidence-manifest.json)；启动环境、构造方式、exit code、stderr 与 UI 限制见 [real-startup-evidence.md](../../verification/P19-BOOT-1/real-startup-evidence.md)。

## 接收方式

- 分支：`codex/P19-BOOT-1`
- worktree：`G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1`
- base：`04d7beedc4a390ff67130eab0baa5b5ee78140cc`
- 固定实现 head：`c44b47dd9852121e18496502870f4e4cbaf5c737`
- 运行方式：按 `real-startup-evidence.md` 在 `runtime-final6` 的隔离状态复现；验证脚本不会触碰用户 `%APPDATA%`。
- `apps/desktop/**` 产品代码、契约、Schema、依赖清单、`doc/STATUS.md` 和 `doc/REBASELINE_PLAN.md` 均未改动。

## 下一任务建议（必填）

- Task ID / 标题：`P19-BOOT-1` 独立 Review（固定 `delivery_head`）。
- 推荐 Agent / Reviewer：DeepSeek Harness；Owner Codex，不得自审。
- 推荐原因与前置依赖：实现和验证已固定，需独立核对 AC、Core 调用链、并发/身份保护、测试与真实启动证据后才能进入 approved。
- Recovery point：仓库 `G:/CODEX/New Manga`；当前实现分支 `codex/P19-BOOT-1`、worktree `G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1`；base `04d7beedc4a390ff67130eab0baa5b5ee78140cc`；head `c44b47dd9852121e18496502870f4e4cbaf5c737`。Reviewer 的独立 worktree 尚未创建，待 Codex 创建。
- 允许修改路径：Review 仅写 `verification/P19-BOOT-1/review-c44b47dd.md`；生产实现、Task 需求与共享契约不得改动。
- 禁止范围：不得 push/merge/reset；不得修改 `apps/desktop/**`、Schema、依赖或主工作区数据；不得审核后自行改实现。
- 交付物：固定 reviewed head 的独立 Review，引用实际文件/行和测试证据；逐项记录 PASS/FAIL/BLOCKED/NOT_RUN、finding 与 disposition。
- 验证命令、环境与完成 Gate：复核 `core-suite.log`、Cargo/build 与真实启动 artefacts；必要时在独立 Windows worktree 重跑 `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe -m pytest tests/core -q -p no:cacheprovider`。P0/P1 未解决或关键证据不符时不得批准。
- 可直接转发给 Agent 的指令：

  > 请独立 Review P19-BOOT-1，固定审查 base `04d7beedc4a390ff67130eab0baa5b5ee78140cc` 到 head `c44b47dd9852121e18496502870f4e4cbaf5c737`。在待 Codex 创建的独立 worktree 中只读检查 `src/bootstrap/core_service.py`、`src/infrastructure/resource_channel/catalog_store.py`、`src/infrastructure/resource_channel/handle_resolver.py`、`tests/core/test_core_namespace_bootstrap.py`、Task 和 `verification/P19-BOOT-1/**`；Review 报告写入 `verification/P19-BOOT-1/review-c44b47dd.md`。重点核对受控绑定、损坏锁恢复/失败关闭、租约 share mode、binding/file identity、reparse point、GC 顺序和真实启动证据；不得改生产代码或共享契约。报告须逐项标注状态及未验证边界，未解决 P0/P1 不得批准。

## 风险与遗留

- 已按任务要求验证 Cargo debug host 和 Python Core source sidecar；未验证冻结 PyInstaller sidecar/安装包。`target/core-sidecar` 是指向共享主仓库 target 的既有 junction，自动审批策略拒绝了删除尝试，因此未改变该 junction。详见真实启动证据。
- `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222` 未提供可用 CDP endpoint；本 Task 的 UI 可达性由实际窗口截图与 UIA WebView 标题证明，未把 CDP attach 记为通过。
- 回退：恢复实现 commits 前的 source commit `04d7beedc4a390ff67130eab0baa5b5ee78140cc`；不需要数据迁移。启动 fixture 与所有应用数据均隔离在 `verification/P19-BOOT-1/runtime-final6`。
